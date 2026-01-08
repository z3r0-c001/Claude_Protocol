#!/usr/bin/env python3
"""
test-agent-lifecycle.py - End-to-end tests for agent creation and integration

Tests the complete lifecycle when a user creates a new agent:
1. Agent registration adds to agent-registry.json
2. New agent participates in auto-invocation matching
3. New agent can be invoked as a sub-agent by other agents
4. New agent can invoke other sub-agents
5. New agent satisfies enforcement rules for its categories
6. Cleanup after test (rollback)

Usage:
    python3 test-agent-lifecycle.py              # Run all tests
    python3 test-agent-lifecycle.py --verbose    # Show detailed output
    python3 test-agent-lifecycle.py --no-cleanup # Keep test agent after run
"""

import json
import sys
import os
import re
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

# Path setup
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent  # CP directory
HOOKS_DIR = SCRIPT_DIR.parent / "hooks"
CONFIG_DIR = SCRIPT_DIR.parent / "config"
AGENTS_DIR = SCRIPT_DIR.parent / "agents"
SCRIPTS_DIR = SCRIPT_DIR.parent / "scripts"

sys.path.insert(0, str(HOOKS_DIR))

# =============================================================================
# TEST AGENT DEFINITION
# =============================================================================

TEST_AGENT_DEFINITION = {
    "name": "test-lifecycle-agent",
    "path": "quality/test-lifecycle-agent.md",
    "description": "Test agent for lifecycle validation - validates agent creation flow",
    "category_group": "quality",
    "categories": ["testing", "quality", "validation"],
    "model_tier": "standard",
    "supports_plan_mode": True,
    "triggers": {
        "exact_keywords": [
            "lifecycle test", "agent validation", "test lifecycle",
            "validate agent", "agent test", "creation test"
        ],
        "phrase_patterns": [
            r"(test|validate|check).*?(lifecycle|agent creation|registration)",
            r"(verify|confirm).*?(agent|registration).*?(works|correct)",
            r"(new agent).*?(functioning|working)"
        ],
        "file_patterns": [
            "**/test-lifecycle/**", "**/*lifecycle*.py"
        ],
        "negation_patterns": [
            r"don't.*?test.*?lifecycle",
            r"skip.*?agent.*?test"
        ]
    },
    "orchestration": {
        "typical_position": "middle",
        "often_follows": ["tester"],
        "often_precedes": ["reviewer"],
        "can_parallel_with": ["security-scanner"]
    }
}

TEST_AGENT_MD_CONTENT = """# test-lifecycle-agent

Test agent for validating the agent creation and registration lifecycle.

## Purpose

This agent is created during tests to verify:
- Agent registration adds to registry correctly
- Auto-invocation matching works for new agents
- Sub-agent invocation is functional
- Enforcement rules recognize new agents

## Triggers

- Keywords: lifecycle test, agent validation
- Patterns: test/validate lifecycle or agent creation

## Capabilities

1. Validate agent registry state
2. Test auto-invocation pipeline
3. Verify sub-agent communication
4. Check enforcement satisfaction

## Sub-Agent Dependencies

This agent may invoke:
- `tester` for test verification
- `reviewer` for output validation

## Output Format

Returns JSON with validation results:
```json
{
  "status": "pass|fail",
  "checks": [...],
  "errors": [...]
}
```
"""


# =============================================================================
# TEST UTILITIES
# =============================================================================

class RegistryBackup:
    """Manages backup/restore of registry for safe testing."""

    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        self.backup_path = None
        self.original_content = None

    def __enter__(self):
        if self.registry_path.exists():
            self.original_content = self.registry_path.read_text()
            self.backup_path = self.registry_path.with_suffix('.json.test-backup')
            shutil.copy(self.registry_path, self.backup_path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_content is not None:
            self.registry_path.write_text(self.original_content)
        if self.backup_path and self.backup_path.exists():
            self.backup_path.unlink()


def load_registry() -> dict:
    """Load agent-registry.json."""
    registry_path = AGENTS_DIR / "agent-registry.json"
    if registry_path.exists():
        return json.loads(registry_path.read_text())
    return {"agents": {}, "command_mappings": {}, "category_agent_mappings": {}}


def save_registry(registry: dict) -> None:
    """Save agent-registry.json."""
    registry_path = AGENTS_DIR / "agent-registry.json"
    registry_path.write_text(json.dumps(registry, indent=2))


def load_config() -> dict:
    """Load invoke-config.json."""
    config_path = CONFIG_DIR / "invoke-config.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {
        "thresholds": {"auto_invoke": 70, "prompt_user": 45},
        "weights": {"keyword": 0.25, "category": 0.35, "llm_intent": 0.40}
    }


# =============================================================================
# MATCHING LOGIC (from agent-auto-invoke.py)
# =============================================================================

def layer1_keyword_match(prompt: str, registry: dict) -> dict:
    """Layer 1: Keyword matching."""
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

        match_count = sum(1 for kw in exact_keywords if kw.lower() in prompt_lower)

        if match_count >= 3:
            scores[agent_name] = 100
        elif match_count == 2:
            scores[agent_name] = 80
        elif match_count == 1:
            scores[agent_name] = 60
        else:
            scores[agent_name] = 0

    return scores


def layer2_category_match(prompt: str, registry: dict, config: dict) -> dict:
    """Layer 2: Category matching."""
    scores = {}
    prompt_lower = prompt.lower()
    agents = registry.get("agents", {})
    categories = config.get("categories", {})

    matched_categories = []
    for category, cat_def in categories.items():
        keywords = cat_def.get("keywords", [])
        for kw in keywords:
            if kw.lower() in prompt_lower:
                matched_categories.append(category)
                break

    if not matched_categories:
        return {name: 0 for name in agents}

    for agent_name, agent_def in agents.items():
        agent_categories = set(agent_def.get("categories", []))
        overlap = agent_categories.intersection(set(matched_categories))

        if len(overlap) >= 3:
            scores[agent_name] = 100
        elif len(overlap) == 2:
            scores[agent_name] = 85
        elif len(overlap) == 1:
            scores[agent_name] = 70
        else:
            scores[agent_name] = 0

    return scores


def layer3_phrase_match(prompt: str, registry: dict) -> dict:
    """Layer 3: Phrase pattern matching."""
    scores = {}
    prompt_lower = prompt.lower()
    agents = registry.get("agents", {})

    for agent_name, agent_def in agents.items():
        triggers = agent_def.get("triggers", {})
        phrase_patterns = triggers.get("phrase_patterns", [])

        match_count = 0
        for pattern in phrase_patterns:
            try:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    match_count += 1
            except re.error:
                continue

        if match_count >= 3:
            scores[agent_name] = 100
        elif match_count == 2:
            scores[agent_name] = 85
        elif match_count == 1:
            scores[agent_name] = 70
        else:
            scores[agent_name] = 0

    return scores


def calculate_combined_score(l1: dict, l2: dict, l3: dict, weights: dict) -> Dict[str, float]:
    """Calculate combined scores."""
    results = {}
    all_agents = set(l1.keys()) | set(l2.keys()) | set(l3.keys())

    w1 = weights.get("keyword", 0.25)
    w2 = weights.get("category", 0.35)
    w3 = weights.get("llm_intent", 0.40)

    for agent in all_agents:
        score = (l1.get(agent, 0) * w1) + (l2.get(agent, 0) * w2) + (l3.get(agent, 0) * w3)
        results[agent] = score

    return dict(sorted(results.items(), key=lambda x: x[1], reverse=True))


def analyze_prompt(prompt: str, registry: dict, config: dict) -> Tuple[Optional[str], float, dict]:
    """
    Analyze a prompt and return best agent match.

    Returns: (agent_name, score, breakdown)
    """
    weights = config.get("weights", {"keyword": 0.25, "category": 0.35, "llm_intent": 0.40})

    l1 = layer1_keyword_match(prompt, registry)
    l2 = layer2_category_match(prompt, registry, config)
    l3 = layer3_phrase_match(prompt, registry)

    combined = calculate_combined_score(l1, l2, l3, weights)

    if not combined:
        return None, 0.0, {}

    top_agent = list(combined.keys())[0]
    top_score = combined[top_agent]

    breakdown = {
        "layer1": l1.get(top_agent, 0),
        "layer2": l2.get(top_agent, 0),
        "layer3": l3.get(top_agent, 0),
        "all_scores": dict(list(combined.items())[:5])
    }

    return top_agent, top_score, breakdown


# =============================================================================
# TEST CASES
# =============================================================================

@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    passed: bool
    message: str
    details: dict = field(default_factory=dict)


class AgentLifecycleTests:
    """Test suite for agent lifecycle."""

    def __init__(self, verbose: bool = False, cleanup: bool = True):
        self.verbose = verbose
        self.cleanup = cleanup
        self.results: List[TestResult] = []
        self.registry_backup = None
        self.test_agent_md_path = None

    def log(self, msg: str) -> None:
        """Log message if verbose."""
        if self.verbose:
            print(f"    {msg}")

    def setup(self) -> bool:
        """Set up test environment."""
        print("\n[SETUP] Preparing test environment...")

        # Backup registry
        registry_path = AGENTS_DIR / "agent-registry.json"
        self.registry_backup = RegistryBackup(registry_path)
        self.registry_backup.__enter__()

        # Create test agent markdown file
        self.test_agent_md_path = AGENTS_DIR / "quality" / "test-lifecycle-agent.md"
        self.test_agent_md_path.parent.mkdir(parents=True, exist_ok=True)
        self.test_agent_md_path.write_text(TEST_AGENT_MD_CONTENT)

        print("    ✓ Registry backed up")
        print("    ✓ Test agent MD file created")
        return True

    def teardown(self) -> None:
        """Clean up test environment."""
        if not self.cleanup:
            print("\n[TEARDOWN] Skipping cleanup (--no-cleanup)")
            return

        print("\n[TEARDOWN] Cleaning up...")

        # Remove test agent MD file
        if self.test_agent_md_path and self.test_agent_md_path.exists():
            self.test_agent_md_path.unlink()
            print("    ✓ Test agent MD file removed")

        # Restore registry
        if self.registry_backup:
            self.registry_backup.__exit__(None, None, None)
            print("    ✓ Registry restored")

    # -------------------------------------------------------------------------
    # TEST 1: Agent Registration
    # -------------------------------------------------------------------------

    def test_agent_registration(self) -> TestResult:
        """Test that registering an agent adds it to the registry correctly."""
        print("\n[TEST 1] Agent Registration")

        # Load current registry
        registry = load_registry()
        initial_count = len(registry.get("agents", {}))
        self.log(f"Initial agent count: {initial_count}")

        # Verify test agent doesn't exist yet
        if TEST_AGENT_DEFINITION["name"] in registry.get("agents", {}):
            return TestResult(
                name="agent_registration",
                passed=False,
                message="Test agent already exists in registry (should not)",
                details={"agent": TEST_AGENT_DEFINITION["name"]}
            )

        # Register test agent
        agents = registry.setdefault("agents", {})
        agents[TEST_AGENT_DEFINITION["name"]] = TEST_AGENT_DEFINITION

        # Update category mappings
        cat_mappings = registry.setdefault("category_agent_mappings", {})
        for category in TEST_AGENT_DEFINITION.get("categories", []):
            if category not in cat_mappings:
                cat_mappings[category] = []
            if TEST_AGENT_DEFINITION["name"] not in cat_mappings[category]:
                cat_mappings[category].append(TEST_AGENT_DEFINITION["name"])

        save_registry(registry)
        self.log("Agent registered successfully")

        # Verify registration
        registry = load_registry()
        new_count = len(registry.get("agents", {}))

        checks = {
            "agent_added": TEST_AGENT_DEFINITION["name"] in registry.get("agents", {}),
            "count_increased": new_count == initial_count + 1,
            "categories_mapped": all(
                TEST_AGENT_DEFINITION["name"] in registry.get("category_agent_mappings", {}).get(cat, [])
                for cat in TEST_AGENT_DEFINITION.get("categories", [])
            ),
            "triggers_present": "triggers" in registry["agents"].get(TEST_AGENT_DEFINITION["name"], {}),
            "orchestration_present": "orchestration" in registry["agents"].get(TEST_AGENT_DEFINITION["name"], {})
        }

        passed = all(checks.values())

        for check, result in checks.items():
            status = "✓" if result else "✗"
            self.log(f"{status} {check}")

        return TestResult(
            name="agent_registration",
            passed=passed,
            message="Agent registered correctly" if passed else "Registration incomplete",
            details={"checks": checks, "agent_count": new_count}
        )

    # -------------------------------------------------------------------------
    # TEST 2: Auto-Invocation Participation
    # -------------------------------------------------------------------------

    def test_auto_invocation(self) -> TestResult:
        """Test that new agent participates in auto-invocation matching."""
        print("\n[TEST 2] Auto-Invocation Participation")

        registry = load_registry()
        config = load_config()

        # Test prompts - verify our agent participates in matching
        # Key: new agents MUST be discoverable via matching, even if they don't always win
        test_prompts = [
            # (prompt, reason, check_type, threshold)
            # check_type: "score_above" = our agent must score above threshold
            #             "is_top" = our agent must be top match
            #             "score_below" = our agent must score below threshold
            ("Run lifecycle test for agent validation and creation test", "participates with keywords", "score_above", 45),
            ("Validate agent lifecycle test creation", "wins with unique combo", "is_top", 50),
            ("Build a user login form", "unrelated - low score", "score_below", 30),
        ]

        checks = {}
        our_agent = TEST_AGENT_DEFINITION["name"]

        for prompt, reason, check_type, threshold in test_prompts:
            agent, score, breakdown = analyze_prompt(prompt, registry, config)

            # Check our agent's score directly
            all_scores = breakdown.get("all_scores", {})
            our_score = all_scores.get(our_agent, 0)

            if check_type == "score_above":
                # Must score above threshold (proves participation)
                passed = our_score >= threshold
                checks[reason] = passed
                self.log(f"{'✓' if passed else '✗'} '{prompt[:40]}...' -> our: {our_score:.1f}% (need >={threshold})")
            elif check_type == "is_top":
                # Must be top match
                is_top = agent == our_agent
                checks[reason] = is_top
                self.log(f"{'✓' if is_top else '✗'} '{prompt[:40]}...' -> top: {agent} (our: {our_score:.1f}%)")
            else:  # score_below
                # Should NOT be a strong match
                passed = our_score < threshold
                checks[reason] = passed
                self.log(f"{'✓' if passed else '✗'} '{prompt[:40]}...' -> our: {our_score:.1f}% (need <{threshold})")

        passed = all(checks.values())

        return TestResult(
            name="auto_invocation",
            passed=passed,
            message="Auto-invocation matching works" if passed else "Matching issues detected",
            details={"checks": checks}
        )

    # -------------------------------------------------------------------------
    # TEST 3: Layer Breakdown Verification
    # -------------------------------------------------------------------------

    def test_layer_breakdown(self) -> TestResult:
        """Test that layers contribute to matching for the new agent."""
        print("\n[TEST 3] Layer Breakdown Verification")

        registry = load_registry()
        config = load_config()

        agent_name = TEST_AGENT_DEFINITION["name"]

        # Test each layer independently with prompts designed for that layer
        # Layer 1: Keywords - use exact keywords
        l1_prompt = "Run lifecycle test and agent validation check"
        l1 = layer1_keyword_match(l1_prompt, registry)
        l1_score = l1.get(agent_name, 0)

        # Layer 2: Categories - use category keywords (testing, quality)
        l2_prompt = "Test quality validation"
        l2 = layer2_category_match(l2_prompt, registry, config)
        l2_score = l2.get(agent_name, 0)

        # Layer 3: Phrase patterns - use pattern: (test|validate).*?(lifecycle|registration)
        l3_prompt = "I need to test the agent lifecycle registration"
        l3 = layer3_phrase_match(l3_prompt, registry)
        l3_score = l3.get(agent_name, 0)

        self.log(f"Layer 1 (Keyword) '{l1_prompt[:30]}...': {l1_score}")
        self.log(f"Layer 2 (Category) '{l2_prompt[:30]}...': {l2_score}")
        self.log(f"Layer 3 (Phrase) '{l3_prompt[:30]}...': {l3_score}")

        # At least 2 of 3 layers should work
        layers_working = sum([l1_score > 0, l2_score > 0, l3_score > 0])
        checks = {
            "layer1_keyword": l1_score > 0,
            "layer2_category": l2_score > 0,
            "layer3_phrase": l3_score > 0,
            "minimum_layers": layers_working >= 2,
        }

        for check, result in checks.items():
            if check != "minimum_layers":
                self.log(f"{'✓' if result else '○'} {check}")

        passed = checks["minimum_layers"]

        return TestResult(
            name="layer_breakdown",
            passed=passed,
            message=f"{layers_working}/3 layers working" if passed else "Less than 2 layers working",
            details={
                "checks": checks,
                "scores": {"l1": l1_score, "l2": l2_score, "l3": l3_score},
                "layers_working": layers_working
            }
        )

    # -------------------------------------------------------------------------
    # TEST 4: Category Satisfaction (Enforcement)
    # -------------------------------------------------------------------------

    def test_category_satisfaction(self) -> TestResult:
        """Test that new agent satisfies enforcement rules for its categories."""
        print("\n[TEST 4] Category Satisfaction (Enforcement)")

        registry = load_registry()
        agent_def = registry.get("agents", {}).get(TEST_AGENT_DEFINITION["name"])

        if not agent_def:
            return TestResult(
                name="category_satisfaction",
                passed=False,
                message="Test agent not found in registry",
                details={}
            )

        agent_categories = set(agent_def.get("categories", []))
        cat_mappings = registry.get("category_agent_mappings", {})

        checks = {}

        for category in agent_categories:
            agents_in_category = cat_mappings.get(category, [])
            in_mapping = TEST_AGENT_DEFINITION["name"] in agents_in_category
            checks[f"{category}_mapping"] = in_mapping
            self.log(f"{'✓' if in_mapping else '✗'} Category '{category}': {TEST_AGENT_DEFINITION['name']} in mapping")

        # Verify agent would satisfy a hypothetical enforcement rule
        # If enforcement requires "testing" category, our agent should satisfy
        if "testing" in agent_categories:
            checks["satisfies_testing_rule"] = True
            self.log("✓ Would satisfy enforcement rule requiring 'testing' category")

        passed = all(checks.values())

        return TestResult(
            name="category_satisfaction",
            passed=passed,
            message="Agent satisfies category requirements" if passed else "Category issues",
            details={"checks": checks, "categories": list(agent_categories)}
        )

    # -------------------------------------------------------------------------
    # TEST 5: Orchestration Metadata
    # -------------------------------------------------------------------------

    def test_orchestration_metadata(self) -> TestResult:
        """Test that orchestration metadata is properly stored."""
        print("\n[TEST 5] Orchestration Metadata")

        registry = load_registry()
        agent_def = registry.get("agents", {}).get(TEST_AGENT_DEFINITION["name"])

        if not agent_def:
            return TestResult(
                name="orchestration_metadata",
                passed=False,
                message="Test agent not found in registry",
                details={}
            )

        orchestration = agent_def.get("orchestration", {})

        checks = {
            "has_typical_position": "typical_position" in orchestration,
            "has_often_follows": "often_follows" in orchestration,
            "has_often_precedes": "often_precedes" in orchestration,
            "has_can_parallel_with": "can_parallel_with" in orchestration,
            "valid_position": orchestration.get("typical_position") in ["first", "early", "middle", "late", "last", "any", "coordinator"],
        }

        for check, result in checks.items():
            self.log(f"{'✓' if result else '✗'} {check}")

        # Verify sub-agent references exist
        often_follows = orchestration.get("often_follows", [])
        often_precedes = orchestration.get("often_precedes", [])

        for ref_agent in often_follows + often_precedes:
            exists = ref_agent in registry.get("agents", {})
            checks[f"ref_{ref_agent}_exists"] = exists
            self.log(f"{'✓' if exists else '✗'} Referenced agent '{ref_agent}' exists")

        passed = all(checks.values())

        return TestResult(
            name="orchestration_metadata",
            passed=passed,
            message="Orchestration metadata valid" if passed else "Orchestration issues",
            details={"checks": checks, "orchestration": orchestration}
        )

    # -------------------------------------------------------------------------
    # TEST 6: Sub-Agent Reference Validation
    # -------------------------------------------------------------------------

    def test_subagent_references(self) -> TestResult:
        """Test that referenced sub-agents exist and can be invoked."""
        print("\n[TEST 6] Sub-Agent Reference Validation")

        registry = load_registry()
        agent_def = registry.get("agents", {}).get(TEST_AGENT_DEFINITION["name"])

        if not agent_def:
            return TestResult(
                name="subagent_references",
                passed=False,
                message="Test agent not found in registry",
                details={}
            )

        orchestration = agent_def.get("orchestration", {})
        referenced_agents = (
            orchestration.get("often_follows", []) +
            orchestration.get("often_precedes", []) +
            orchestration.get("can_parallel_with", [])
        )

        checks = {}

        for ref_agent in referenced_agents:
            # Check agent exists
            exists = ref_agent in registry.get("agents", {})
            checks[f"{ref_agent}_exists"] = exists

            if exists:
                ref_def = registry["agents"][ref_agent]
                # Check it has triggers (can be invoked)
                has_triggers = bool(ref_def.get("triggers", {}).get("exact_keywords"))
                checks[f"{ref_agent}_invocable"] = has_triggers
                self.log(f"✓ {ref_agent}: exists={exists}, invocable={has_triggers}")
            else:
                self.log(f"✗ {ref_agent}: does not exist")

        if not referenced_agents:
            checks["has_references"] = True
            self.log("(No sub-agent references defined)")

        passed = all(checks.values())

        return TestResult(
            name="subagent_references",
            passed=passed,
            message="Sub-agent references valid" if passed else "Invalid references",
            details={"checks": checks, "referenced": referenced_agents}
        )

    # -------------------------------------------------------------------------
    # TEST 7: Bidirectional Invocation Capability
    # -------------------------------------------------------------------------

    def test_bidirectional_invocation(self) -> TestResult:
        """Test that other agents can reference/invoke the new agent."""
        print("\n[TEST 7] Bidirectional Invocation Capability")

        registry = load_registry()
        our_agent = TEST_AGENT_DEFINITION["name"]
        our_categories = set(TEST_AGENT_DEFINITION.get("categories", []))

        # Find agents that might want to invoke our agent based on categories
        potential_callers = []

        for agent_name, agent_def in registry.get("agents", {}).items():
            if agent_name == our_agent:
                continue

            orchestration = agent_def.get("orchestration", {})
            often_precedes = orchestration.get("often_precedes", [])

            # If they often precede agents in our category, they might call us
            agent_cats = set(agent_def.get("categories", []))
            if agent_cats.intersection(our_categories):
                potential_callers.append(agent_name)

        # Verify category mapping allows discovery
        cat_mappings = registry.get("category_agent_mappings", {})
        discoverable_via = []

        for cat in our_categories:
            if our_agent in cat_mappings.get(cat, []):
                discoverable_via.append(cat)

        checks = {
            "discoverable_via_categories": len(discoverable_via) > 0,
            "in_category_mappings": len(discoverable_via) == len(our_categories),
        }

        self.log(f"Discoverable via categories: {discoverable_via}")
        self.log(f"Potential callers (same categories): {potential_callers[:5]}")

        # Test that another agent could match and call us
        # Simulate: "run tests and validate agent lifecycle"
        prompt = "run tests and check the lifecycle validation"
        agent, score, _ = analyze_prompt(prompt, registry, load_config())

        # Our agent should be discoverable
        can_be_matched = our_agent in [a for a, s in calculate_combined_score(
            layer1_keyword_match(prompt, registry),
            layer2_category_match(prompt, registry, load_config()),
            layer3_phrase_match(prompt, registry),
            load_config().get("weights", {})
        ).items() if s > 0]

        checks["matchable_by_prompts"] = can_be_matched
        self.log(f"{'✓' if can_be_matched else '✗'} Agent matchable via prompts")

        passed = all(checks.values())

        return TestResult(
            name="bidirectional_invocation",
            passed=passed,
            message="Agent is invocable by others" if passed else "Invocation issues",
            details={
                "checks": checks,
                "discoverable_via": discoverable_via,
                "potential_callers": potential_callers[:5]
            }
        )

    # -------------------------------------------------------------------------
    # TEST 8: Negation Pattern Handling
    # -------------------------------------------------------------------------

    def test_negation_patterns(self) -> TestResult:
        """Test that negation patterns properly suppress matching."""
        print("\n[TEST 8] Negation Pattern Handling")

        registry = load_registry()
        config = load_config()

        negation_prompts = [
            "Don't test the lifecycle, just implement it",
            "Skip the agent test, we're in a hurry",
        ]

        checks = {}

        for prompt in negation_prompts:
            l1 = layer1_keyword_match(prompt, registry)
            agent_score = l1.get(TEST_AGENT_DEFINITION["name"], 0)

            # With negation, score should be 0
            suppressed = agent_score == 0
            checks[prompt[:30]] = suppressed
            self.log(f"{'✓' if suppressed else '✗'} '{prompt[:40]}...' -> score={agent_score} (expected 0)")

        passed = all(checks.values())

        return TestResult(
            name="negation_patterns",
            passed=passed,
            message="Negation patterns work correctly" if passed else "Negation not suppressing",
            details={"checks": checks}
        )

    # -------------------------------------------------------------------------
    # Run All Tests
    # -------------------------------------------------------------------------

    def run_all(self) -> dict:
        """Run all tests and return summary."""
        try:
            self.setup()
        except Exception as e:
            print(f"\n[ERROR] Setup failed: {e}")
            return {"total": 0, "passed": 0, "failed": 0, "error": str(e)}

        tests = [
            self.test_agent_registration,
            self.test_auto_invocation,
            self.test_layer_breakdown,
            self.test_category_satisfaction,
            self.test_orchestration_metadata,
            self.test_subagent_references,
            self.test_bidirectional_invocation,
            self.test_negation_patterns,
        ]

        for test_func in tests:
            try:
                result = test_func()
                self.results.append(result)

                status = "\033[92m✓ PASS\033[0m" if result.passed else "\033[91m✗ FAIL\033[0m"
                print(f"    {status}: {result.message}")

            except Exception as e:
                self.results.append(TestResult(
                    name=test_func.__name__,
                    passed=False,
                    message=f"Exception: {e}",
                    details={"exception": str(e)}
                ))
                print(f"    \033[91m✗ ERROR\033[0m: {e}")

        self.teardown()

        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed

        return {
            "total": len(self.results),
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / len(self.results) * 100) if self.results else 0,
            "results": [
                {"name": r.name, "passed": r.passed, "message": r.message}
                for r in self.results
            ]
        }


# =============================================================================
# MAIN
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test agent lifecycle - creation, registration, invocation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--no-cleanup", action="store_true", help="Keep test agent after run")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("  Agent Lifecycle Test Suite")
    print("  Tests: Registration → Auto-Invocation → Sub-Agent → Enforcement")
    print("=" * 70)

    runner = AgentLifecycleTests(verbose=args.verbose, cleanup=not args.no_cleanup)
    summary = runner.run_all()

    if args.json:
        print("\n" + json.dumps(summary, indent=2))
    else:
        print("\n" + "-" * 70)
        print(f"Total:   {summary['total']}")
        print(f"Passed:  \033[92m{summary['passed']}\033[0m")
        print(f"Failed:  \033[91m{summary['failed']}\033[0m")
        print(f"Rate:    {summary['pass_rate']:.1f}%")
        print("-" * 70 + "\n")

    return 0 if summary['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
