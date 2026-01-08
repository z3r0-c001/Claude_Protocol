#!/usr/bin/env python3
"""
agent-auto-invoke.py - Agent Auto-Invocation Hook (UserPromptSubmit)

Implements the 3-layer agent matching system:
- Layer 1: Keyword matching (25% weight)
- Layer 2: Category classification (35% weight)
- Layer 3: LLM intent analysis (40% weight) or heuristic fallback
- Memory adjustment: Apply past learnings from MCP

Based on confidence thresholds:
- >= 85%: Auto-invoke (adds context to invoke agent)
- 60-84%: Prompt user for confirmation
- < 60%: Non-blocking suggestion

Configuration: .claude/config/invoke-config.json
Registry: .claude/agents/agent-registry.json
"""

import json
import sys
import os
import re
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add hooks directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from colors import hook_status
except ImportError:
    def hook_status(*args, **kwargs):
        pass

try:
    from agent_visibility import (
        format_auto_invoke_banner,
        format_prompt_banner,
        format_suggest_banner,
        format_disambiguation_banner,
        format_layer_breakdown,
        print_banner,
        suppress_output
    )
except ImportError:
    # Fallback stubs if visibility module not available
    def format_auto_invoke_banner(*args, **kwargs): return ""
    def format_prompt_banner(*args, **kwargs): return ""
    def format_suggest_banner(*args, **kwargs): return ""
    def format_disambiguation_banner(*args, **kwargs): return ""
    def format_layer_breakdown(*args, **kwargs): return ""
    def print_banner(banner, file=sys.stderr): print(banner, file=file)
    def suppress_output(): return False


# =============================================================================
# CONFIGURATION LOADING
# =============================================================================

def get_project_dir() -> str:
    """Get project directory from environment or cwd."""
    return os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())


def load_config() -> dict:
    """Load invoke-config.json configuration."""
    project_dir = get_project_dir()
    config_path = Path(project_dir) / ".claude" / "config" / "invoke-config.json"

    defaults = {
        "thresholds": {"auto_invoke": 85, "prompt_user": 60, "suggest_only": 0},
        "weights": {"keyword": 0.25, "category": 0.35, "llm_intent": 0.40},
        "llm_analysis": {"enabled": True, "model": "haiku", "timeout_ms": 10000},
        "memory_learning": {"enabled": True, "max_boost": 20, "max_penalty": 25},
        "visibility": {"show_banners": True, "show_confidence_breakdown": True}
    }

    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
            # Merge with defaults
            for key, value in defaults.items():
                if key not in config:
                    config[key] = value
            return config
        except json.JSONDecodeError:
            return defaults
    return defaults


def load_registry() -> dict:
    """Load agent-registry.json with all agent definitions."""
    project_dir = get_project_dir()
    registry_path = Path(project_dir) / ".claude" / "agents" / "agent-registry.json"

    if registry_path.exists():
        try:
            return json.loads(registry_path.read_text())
        except json.JSONDecodeError:
            return {"agents": {}, "command_mappings": {}, "category_agent_mappings": {}}
    return {"agents": {}, "command_mappings": {}, "category_agent_mappings": {}}


# =============================================================================
# LAYER 1: KEYWORD MATCHING
# =============================================================================

def layer1_keyword_match(prompt: str, registry: dict) -> dict:
    """
    Layer 1: Exact keyword matching against agent triggers.

    Returns dict of {agent_name: score} where score is 0-100
    """
    scores = {}
    prompt_lower = prompt.lower()
    agents = registry.get("agents", {})

    for agent_name, agent_def in agents.items():
        triggers = agent_def.get("triggers", {})
        exact_keywords = triggers.get("exact_keywords", [])
        negation_patterns = triggers.get("negation_patterns", [])

        # Check negation first
        negated = False
        for pattern in negation_patterns:
            try:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    negated = True
                    break
            except re.error:
                continue

        if negated:
            scores[agent_name] = 0
            continue

        # Count keyword matches
        match_count = 0
        total_keywords = len(exact_keywords)

        for keyword in exact_keywords:
            if keyword.lower() in prompt_lower:
                match_count += 1

        if total_keywords > 0 and match_count > 0:
            # Score based on match ratio with diminishing returns
            # 1 match = 60, 2 matches = 80, 3+ = 100
            if match_count >= 3:
                scores[agent_name] = 100
            elif match_count == 2:
                scores[agent_name] = 80
            else:
                scores[agent_name] = 60
        else:
            scores[agent_name] = 0

    return scores


# =============================================================================
# LAYER 2: CATEGORY CLASSIFICATION
# =============================================================================

def classify_prompt_categories(prompt: str, config: dict) -> list:
    """
    Classify prompt into task categories based on category keywords.

    Returns list of matched category names.
    """
    categories = config.get("categories", {})
    prompt_lower = prompt.lower()
    matched = []

    for category, cat_def in categories.items():
        keywords = cat_def.get("keywords", [])
        for kw in keywords:
            if kw.lower() in prompt_lower:
                matched.append(category)
                break

    return matched


def layer2_category_match(prompt: str, registry: dict, config: dict) -> dict:
    """
    Layer 2: Category-based classification.

    Returns dict of {agent_name: score} where score is 0-100
    """
    scores = {}
    agents = registry.get("agents", {})
    category_mappings = registry.get("category_agent_mappings", {})

    # Classify prompt into categories
    matched_categories = classify_prompt_categories(prompt, config)

    if not matched_categories:
        # No categories matched - all agents get 0
        for agent_name in agents:
            scores[agent_name] = 0
        return scores

    # Score each agent based on category overlap
    for agent_name, agent_def in agents.items():
        agent_categories = set(agent_def.get("categories", []))
        matched_set = set(matched_categories)

        # Calculate overlap
        overlap = agent_categories.intersection(matched_set)

        if overlap:
            # More overlap = higher score
            # 1 category = 70, 2 = 85, 3+ = 100
            overlap_count = len(overlap)
            if overlap_count >= 3:
                scores[agent_name] = 100
            elif overlap_count == 2:
                scores[agent_name] = 85
            else:
                scores[agent_name] = 70
        else:
            scores[agent_name] = 0

    return scores


# =============================================================================
# LAYER 3: PHRASE PATTERN MATCHING (Heuristic LLM Fallback)
# =============================================================================

def layer3_phrase_match(prompt: str, registry: dict) -> dict:
    """
    Layer 3: Phrase pattern matching using regex patterns.

    This serves as a heuristic fallback when LLM analysis is not available.
    Matches phrase_patterns defined in agent triggers.

    Returns dict of {agent_name: score} where score is 0-100
    """
    scores = {}
    prompt_lower = prompt.lower()
    agents = registry.get("agents", {})

    for agent_name, agent_def in agents.items():
        triggers = agent_def.get("triggers", {})
        phrase_patterns = triggers.get("phrase_patterns", [])

        if not phrase_patterns:
            scores[agent_name] = 0
            continue

        # Count pattern matches
        match_count = 0
        for pattern in phrase_patterns:
            try:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    match_count += 1
            except re.error:
                continue

        if match_count > 0:
            # Score based on pattern matches
            # 1 match = 70, 2 = 85, 3+ = 100
            if match_count >= 3:
                scores[agent_name] = 100
            elif match_count == 2:
                scores[agent_name] = 85
            else:
                scores[agent_name] = 70
        else:
            scores[agent_name] = 0

    return scores


# =============================================================================
# MEMORY LEARNING (MCP Integration)
# =============================================================================

def load_memory_adjustments(agent_name: str, prompt: str) -> float:
    """
    Load memory-based adjustments from MCP.

    This is a placeholder that returns 0 if MCP is not available.
    When MCP is available, it searches for past corrections and applies them.

    Returns adjustment value (-25 to +20)
    """
    # MCP integration would go here
    # For now, return 0 (no adjustment)
    return 0.0


# =============================================================================
# SESSION TRACKING FOR ENFORCEMENT
# =============================================================================

def get_session_tracker_path() -> Path:
    """Get path to session-agents.json tracker."""
    project_dir = get_project_dir()
    return Path(project_dir) / ".claude" / "memory" / "session-agents.json"


def load_session_tracker() -> dict:
    """Load or initialize session tracker."""
    tracker_path = get_session_tracker_path()

    if tracker_path.exists():
        try:
            return json.loads(tracker_path.read_text())
        except (json.JSONDecodeError, IOError):
            pass

    return {
        "session_id": None,
        "started_at": None,
        "last_updated": None,
        "detected_context": {
            "prompt_analysis": None,
            "suggested_agents": [],
            "detected_patterns": [],
            "files_touched": [],
            "content_patterns_found": []
        },
        "invoked_agents": [],
        "enforcement": {
            "rules_triggered": [],
            "agents_required": [],
            "agents_satisfied": [],
            "pending_requirements": []
        }
    }


def save_session_tracker(tracker: dict) -> bool:
    """Save session tracker to disk."""
    tracker_path = get_session_tracker_path()

    try:
        tracker_path.parent.mkdir(parents=True, exist_ok=True)
        tracker_path.write_text(json.dumps(tracker, indent=2))
        return True
    except IOError:
        return False


def record_detected_context(
    prompt: str,
    matched_categories: list,
    top_agent: str,
    top_score: float,
    all_scores: dict
) -> None:
    """
    Record detected context to session tracker for enforcement system.

    Called after prompt analysis to track:
    - What agents were suggested
    - What categories matched
    - What the confidence scores were
    """
    tracker = load_session_tracker()

    now = datetime.now().isoformat()
    if not tracker.get("started_at"):
        tracker["started_at"] = now
    tracker["last_updated"] = now

    # Store detected context
    detected = tracker.get("detected_context", {})
    detected["prompt_analysis"] = {
        "timestamp": now,
        "prompt_snippet": prompt[:200] + "..." if len(prompt) > 200 else prompt,
        "matched_categories": matched_categories,
        "top_suggestion": {
            "agent": top_agent,
            "score": top_score
        }
    }

    # Track suggested agents (score > 0)
    suggested = [
        {"agent": name, "score": data["score"]}
        for name, data in all_scores.items()
        if data["score"] > 0
    ][:5]  # Top 5 suggestions
    detected["suggested_agents"] = suggested

    tracker["detected_context"] = detected

    # Load enforcement rules and check if any should trigger
    load_enforcement_requirements(tracker, prompt, matched_categories)

    save_session_tracker(tracker)


def load_enforcement_requirements(tracker: dict, prompt: str, categories: list) -> None:
    """
    Check enforcement rules and set required agents based on context.

    This is called during prompt analysis to pre-populate required agents
    before any work is done.
    """
    project_dir = get_project_dir()
    rules_path = Path(project_dir) / ".claude" / "config" / "enforcement-rules.json"

    if not rules_path.exists():
        return

    try:
        rules_config = json.loads(rules_path.read_text())
    except (json.JSONDecodeError, IOError):
        return

    if not rules_config.get("enabled", True):
        return

    enforcement = tracker.get("enforcement", {})
    rules_triggered = enforcement.get("rules_triggered", [])
    agents_required = enforcement.get("agents_required", [])
    pending = enforcement.get("pending_requirements", [])

    rules = rules_config.get("rules", {})
    prompt_lower = prompt.lower()

    for rule_name, rule_def in rules.items():
        if not rule_def.get("enabled", True):
            continue

        trigger = rule_def.get("trigger", {})
        triggered = False

        # Check prompt patterns
        prompt_patterns = trigger.get("prompt_patterns", [])
        for pattern in prompt_patterns:
            try:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    triggered = True
                    break
            except re.error:
                continue

        if triggered:
            required = rule_def.get("required_agents", [])
            strictness = rule_def.get("strictness", "warn")
            message = rule_def.get("message", f"Rule '{rule_name}' triggered")

            if rule_name not in rules_triggered:
                rules_triggered.append(rule_name)

            for agent in required:
                if agent not in agents_required:
                    agents_required.append(agent)
                    pending.append({
                        "agent": agent,
                        "rule": rule_name,
                        "strictness": strictness,
                        "message": message
                    })

    enforcement["rules_triggered"] = rules_triggered
    enforcement["agents_required"] = agents_required
    enforcement["pending_requirements"] = pending
    tracker["enforcement"] = enforcement


# =============================================================================
# COMBINED SCORING
# =============================================================================

def calculate_combined_scores(
    layer1_scores: dict,
    layer2_scores: dict,
    layer3_scores: dict,
    weights: dict,
    prompt: str,
    memory_enabled: bool = True
) -> dict:
    """
    Calculate combined confidence scores for all agents.

    Returns dict of {agent_name: {score, breakdown}} sorted by score descending
    """
    results = {}

    all_agents = set(layer1_scores.keys()) | set(layer2_scores.keys()) | set(layer3_scores.keys())

    for agent_name in all_agents:
        l1 = layer1_scores.get(agent_name, 0)
        l2 = layer2_scores.get(agent_name, 0)
        l3 = layer3_scores.get(agent_name, 0)

        # Apply weights
        w1 = weights.get("keyword", 0.25)
        w2 = weights.get("category", 0.35)
        w3 = weights.get("llm_intent", 0.40)

        weighted_sum = (l1 * w1) + (l2 * w2) + (l3 * w3)

        # Apply memory adjustment
        memory_adj = 0.0
        if memory_enabled:
            memory_adj = load_memory_adjustments(agent_name, prompt)

        final_score = max(0, min(100, weighted_sum + memory_adj))

        results[agent_name] = {
            "score": final_score,
            "breakdown": {
                "keyword_score": l1,
                "category_score": l2,
                "llm_score": l3,
                "memory_adj": memory_adj,
                "weights": {"keyword": w1, "category": w2, "llm_intent": w3}
            }
        }

    # Sort by score descending
    sorted_results = dict(sorted(results.items(), key=lambda x: x[1]["score"], reverse=True))
    return sorted_results


# =============================================================================
# DISAMBIGUATION DETECTION
# =============================================================================

def check_disambiguation_needed(
    combined_scores: dict,
    config: dict,
    registry: dict
) -> Optional[list]:
    """
    Check if disambiguation is needed (multiple agents score closely).

    Returns list of options if disambiguation needed, None otherwise.
    Each option is {agent, score, description}.
    """
    disambig_config = config.get("disambiguation", {})
    if not disambig_config.get("enabled", True):
        return None

    gap_threshold = disambig_config.get("score_gap_threshold", 15)
    max_options = disambig_config.get("max_options", 3)
    min_score = disambig_config.get("min_score_for_option", 20)

    # Get sorted agents by score
    sorted_agents = [
        (name, data["score"])
        for name, data in combined_scores.items()
        if data["score"] >= min_score
    ]

    if len(sorted_agents) < 2:
        return None

    top_score = sorted_agents[0][1]

    # Find agents within gap_threshold of top score
    close_agents = [
        (name, score)
        for name, score in sorted_agents
        if top_score - score <= gap_threshold
    ]

    # Only disambiguate if we have 2+ close agents
    if len(close_agents) < 2:
        return None

    # Build options list
    agents_def = registry.get("agents", {})
    options = []
    for name, score in close_agents[:max_options]:
        agent_def = agents_def.get(name, {})
        options.append({
            "agent": name,
            "score": score,
            "description": agent_def.get("description", "")
        })

    return options


# =============================================================================
# COMMAND MAPPING CHECK
# =============================================================================

def check_command_mapping(prompt: str, registry: dict) -> Optional[list]:
    """
    Check if prompt starts with a mapped slash command.

    Returns list of agent names if matched, None otherwise.
    """
    prompt_stripped = prompt.strip()
    command_mappings = registry.get("command_mappings", {})

    for command, agents in command_mappings.items():
        if prompt_stripped.startswith(command):
            return agents

    return None


# =============================================================================
# MAIN HOOK LOGIC
# =============================================================================

def main():
    hook_status("agent-auto-invoke", "RUNNING", "Analyzing prompt")

    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        hook_status("agent-auto-invoke", "OK", "No input")
        sys.exit(0)

    prompt = input_data.get("prompt", "")
    if not prompt:
        hook_status("agent-auto-invoke", "OK", "Empty prompt")
        sys.exit(0)

    # Load configuration and registry
    config = load_config()
    registry = load_registry()

    if not registry.get("agents"):
        hook_status("agent-auto-invoke", "OK", "No registry")
        sys.exit(0)

    # Check for explicit command mappings first
    command_agents = check_command_mapping(prompt, registry)
    if command_agents:
        # Direct command - auto-invoke first agent
        agent_name = command_agents[0]
        if not suppress_output() and config.get("visibility", {}).get("show_banners", True):
            banner = format_auto_invoke_banner(agent_name, 100.0, "EXECUTE", False)
            print_banner(banner)

        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": f"AGENT INVOKE: Use the Task tool to invoke the '{agent_name}' agent. This was triggered by command mapping."
            }
        }
        hook_status("agent-auto-invoke", "OK", f"Command -> {agent_name}")
        print(json.dumps(output))
        sys.exit(0)

    # Run 3-layer matching
    weights = config.get("weights", {"keyword": 0.25, "category": 0.35, "llm_intent": 0.40})
    thresholds = config.get("thresholds", {"auto_invoke": 85, "prompt_user": 60})
    memory_enabled = config.get("memory_learning", {}).get("enabled", True)

    layer1 = layer1_keyword_match(prompt, registry)
    layer2 = layer2_category_match(prompt, registry, config)
    layer3 = layer3_phrase_match(prompt, registry)

    combined = calculate_combined_scores(layer1, layer2, layer3, weights, prompt, memory_enabled)

    # Get top agent
    if not combined:
        hook_status("agent-auto-invoke", "OK", "No matches")
        sys.exit(0)

    top_agent = list(combined.keys())[0]
    top_result = combined[top_agent]
    top_score = top_result["score"]
    breakdown = top_result["breakdown"]

    # Record context to session tracker for enforcement
    matched_categories = classify_prompt_categories(prompt, config)
    record_detected_context(prompt, matched_categories, top_agent, top_score, combined)

    # Determine action based on thresholds
    auto_threshold = thresholds.get("auto_invoke", 85)
    prompt_threshold = thresholds.get("prompt_user", 60)
    visibility = config.get("visibility", {})
    show_banners = visibility.get("show_banners", True)
    show_breakdown = visibility.get("show_confidence_breakdown", True)

    # Check if disambiguation is needed (multiple close scores below auto-threshold)
    if top_score < auto_threshold:
        disambig_options = check_disambiguation_needed(combined, config, registry)
        if disambig_options and len(disambig_options) >= 2:
            # Show disambiguation banner and ask user
            if not suppress_output() and show_banners:
                banner = format_disambiguation_banner(disambig_options, prompt[:50])
                print_banner(banner)

            # Format options for additionalContext
            options_text = ", ".join([
                f"[{i+1}] {opt['agent']} ({opt['score']:.0f}%)"
                for i, opt in enumerate(disambig_options)
            ])

            output = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": f"AGENT CHOICE: Multiple agents match this request. Options: {options_text}. Ask the user which agent they prefer, or use your judgment if the context makes one clearly better."
                }
            }
            hook_status("agent-auto-invoke", "OK", f"Disambig: {len(disambig_options)} options")
            print(json.dumps(output))
            sys.exit(0)

    if top_score >= auto_threshold:
        # AUTO-INVOKE
        if not suppress_output() and show_banners:
            banner = format_auto_invoke_banner(
                top_agent,
                top_score,
                "EXECUTE",
                show_breakdown,
                breakdown
            )
            print_banner(banner)

        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": f"AGENT INVOKE: Use the Task tool to invoke the '{top_agent}' agent with confidence {top_score:.1f}%. This was auto-selected based on keyword, category, and intent analysis."
            }
        }
        hook_status("agent-auto-invoke", "OK", f"Auto: {top_agent} ({top_score:.0f}%)")
        print(json.dumps(output))

    elif top_score >= prompt_threshold:
        # PROMPT USER
        agent_def = registry.get("agents", {}).get(top_agent, {})
        reason = agent_def.get("description", "Matched based on prompt analysis")

        if not suppress_output() and show_banners:
            banner = format_prompt_banner(
                top_agent,
                top_score,
                reason,
                show_breakdown,
                breakdown
            )
            print_banner(banner)

        # Use permissionDecision: ask to prompt user
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "permissionDecision": "ask",
                "permissionDecisionReason": f"Agent '{top_agent}' suggested with {top_score:.0f}% confidence. {reason}"
            }
        }
        hook_status("agent-auto-invoke", "OK", f"Prompt: {top_agent} ({top_score:.0f}%)")
        print(json.dumps(output))

    elif top_score > 0:
        # SUGGEST ONLY (non-blocking)
        agent_def = registry.get("agents", {}).get(top_agent, {})
        reason = agent_def.get("description", "")

        if not suppress_output() and show_banners:
            suggestion = format_suggest_banner(top_agent, top_score, reason)
            print_banner(suggestion)

        # Non-blocking suggestion via additionalContext
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": f"AGENT TIP: The '{top_agent}' agent might be helpful ({top_score:.0f}% confidence). Consider using it if relevant."
            }
        }
        hook_status("agent-auto-invoke", "OK", f"Suggest: {top_agent} ({top_score:.0f}%)")
        print(json.dumps(output))

    else:
        # No match worth mentioning
        hook_status("agent-auto-invoke", "OK", "No confident match")

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Log error but don't block user
        hook_status("agent-auto-invoke", "ERROR", str(e)[:50])
        sys.exit(0)
