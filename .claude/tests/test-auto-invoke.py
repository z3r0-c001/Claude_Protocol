#!/usr/bin/env python3
"""
test-auto-invoke.py - Real-world tests for agent auto-invocation system

Tests the 3-layer matching pipeline with realistic user prompts to verify:
1. Correct agent selection
2. Appropriate confidence scores
3. Threshold-based actions (auto-invoke, prompt, suggest)
4. Command mapping shortcuts
5. Negation pattern handling
6. Edge cases and ambiguous prompts

Thresholds (from invoke-config.json):
- >= 70%: auto-invoke
- 45-69%: prompt user
- 1-44%: suggest only
- 0%: none

Usage:
    python3 test-auto-invoke.py              # Run all tests
    python3 test-auto-invoke.py --verbose    # Show detailed output
    python3 test-auto-invoke.py --demo       # Interactive demo mode
"""

import json
import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Add hooks directory to path
SCRIPT_DIR = Path(__file__).parent
HOOKS_DIR = SCRIPT_DIR.parent / "hooks"
CONFIG_DIR = SCRIPT_DIR.parent / "config"
AGENTS_DIR = SCRIPT_DIR.parent / "agents"

sys.path.insert(0, str(HOOKS_DIR))

# =============================================================================
# TEST CASE DEFINITIONS
# =============================================================================

@dataclass
class TestCase:
    """A test case for auto-invocation."""
    prompt: str
    expected_agent: str  # Can be single agent or comma-separated list for disambiguation
    expected_action: str  # "auto", "prompt", "suggest", "none"
    min_confidence: float = 0.0
    max_confidence: float = 100.0
    description: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def accepts_agent(self, agent: str) -> bool:
        """Check if the given agent is acceptable (supports comma-separated alternatives)."""
        acceptable = [a.strip() for a in self.expected_agent.split(",")]
        return agent in acceptable


# Real-world test cases organized by category
# Thresholds: auto >= 70, prompt 45-69, suggest 1-44, none = 0
TEST_CASES = [
    # =========================================================================
    # SECURITY AGENT TESTS
    # =========================================================================
    TestCase(
        prompt="Review the authentication code for security vulnerabilities",
        expected_agent="security-scanner",
        expected_action="auto",
        min_confidence=70,
        description="Direct security + auth keywords",
        tags=["security", "high-confidence"]
    ),
    TestCase(
        prompt="Check for XSS and SQL injection security vulnerabilities in the login",
        expected_agent="security-scanner",
        expected_action="auto",
        min_confidence=70,
        description="OWASP vulnerability keywords",
        tags=["security", "owasp"]
    ),
    TestCase(
        prompt="Make sure the API tokens are stored securely",
        expected_agent="security-scanner",
        expected_action="suggest",
        min_confidence=1,
        max_confidence=44,
        description="Indirect security concern - weak signal",
        tags=["security", "low-confidence"]
    ),

    # =========================================================================
    # TESTING AGENT TESTS
    # =========================================================================
    TestCase(
        prompt="Write unit tests for the user service",
        expected_agent="tester",
        expected_action="auto",
        min_confidence=70,
        description="Direct test writing request",
        tags=["testing", "high-confidence"]
    ),
    TestCase(
        prompt="Add jest tests for the payment module with good coverage",
        expected_agent="tester",
        expected_action="auto",
        min_confidence=70,
        description="Specific test framework mention",
        tags=["testing", "framework"]
    ),
    TestCase(
        prompt="Run the tests",
        expected_agent="tester",
        expected_action="prompt",
        min_confidence=45,
        max_confidence=69,
        description="Simple test run request",
        tags=["testing", "simple"]
    ),

    # =========================================================================
    # ARCHITECTURE/DESIGN AGENT TESTS
    # =========================================================================
    TestCase(
        prompt="I want to build a real-time notification system. Help me plan the architecture.",
        expected_agent="brainstormer",
        expected_action="auto",
        min_confidence=70,
        description="'I want to build' pattern triggers brainstormer",
        tags=["design", "brainstormer"]
    ),
    TestCase(
        prompt="Design the system architecture for our microservices",
        expected_agent="architect",
        expected_action="prompt",
        min_confidence=45,
        max_confidence=69,
        description="Architecture request - medium confidence",
        tags=["design", "architect"]
    ),
    TestCase(
        prompt="Design the database schema and data model for e-commerce",
        expected_agent="data-modeler",
        expected_action="auto",
        min_confidence=70,
        description="Database schema design with model keyword",
        tags=["design", "data"]
    ),

    # =========================================================================
    # FRONTEND AGENT TESTS
    # =========================================================================
    TestCase(
        prompt="Create a responsive dashboard component with charts and UI elements",
        expected_agent="frontend-designer",
        expected_action="auto",
        min_confidence=70,
        description="UI component creation",
        tags=["frontend", "component"]
    ),
    TestCase(
        prompt="Create a modal dialog component for the frontend UI layout",
        expected_agent="frontend-designer",
        expected_action="auto",
        min_confidence=70,
        description="Modal/dialog UI pattern with multiple frontend keywords",
        tags=["frontend", "modal"]
    ),
    TestCase(
        prompt="Make the form accessible for screen readers with WCAG compliance",
        expected_agent="accessibility-auditor",
        expected_action="auto",
        min_confidence=70,
        description="Accessibility request",
        tags=["frontend", "a11y"]
    ),
    TestCase(
        prompt="Check accessibility and color contrast for WCAG compliance",
        expected_agent="accessibility-auditor",
        expected_action="auto",
        min_confidence=70,
        description="Color contrast with accessibility keywords",
        tags=["frontend", "a11y", "contrast"]
    ),

    # =========================================================================
    # DEBUGGING AGENT TESTS
    # =========================================================================
    TestCase(
        prompt="Debug why the API returns 500 errors and trace the root cause",
        expected_agent="debugger",
        expected_action="auto",
        min_confidence=70,
        description="Direct debug request",
        tags=["debugging", "error"]
    ),
    TestCase(
        prompt="Find the root cause of the memory leak and debug it",
        expected_agent="debugger",
        expected_action="auto",
        min_confidence=70,
        description="Root cause analysis",
        tags=["debugging", "memory"]
    ),

    # =========================================================================
    # PERFORMANCE AGENT TESTS
    # =========================================================================
    TestCase(
        prompt="The page load is too slow, optimize performance",
        expected_agent="performance-analyzer",
        expected_action="auto",
        min_confidence=70,
        description="Direct performance optimization",
        tags=["performance", "optimization"]
    ),
    TestCase(
        prompt="Profile the database queries for bottlenecks and optimize",
        expected_agent="performance-analyzer",
        expected_action="auto",
        min_confidence=70,
        description="Profiling request",
        tags=["performance", "profiling"]
    ),
    TestCase(
        prompt="Optimize performance by adding caching to reduce latency",
        expected_agent="performance-analyzer",
        expected_action="auto",
        min_confidence=70,
        description="Caching with performance keywords",
        tags=["performance", "caching"]
    ),

    # =========================================================================
    # CODE REVIEW AGENT TESTS
    # =========================================================================
    TestCase(
        prompt="Review my pull request for the auth changes and provide feedback",
        expected_agent="reviewer",
        expected_action="auto",
        min_confidence=70,
        description="PR review request",
        tags=["review", "pr"]
    ),
    TestCase(
        prompt="Review this code and give me feedback on the implementation",
        expected_agent="reviewer",
        expected_action="auto",
        min_confidence=70,
        description="Code review with feedback request",
        tags=["review", "feedback"]
    ),

    # =========================================================================
    # DOCUMENTATION AGENT TESTS
    # =========================================================================
    TestCase(
        prompt="Generate API documentation for the user endpoints",
        expected_agent="documenter",
        expected_action="auto",
        min_confidence=70,
        description="API docs generation",
        tags=["documentation", "api"]
    ),
    TestCase(
        prompt="Update the README with installation instructions and documentation",
        expected_agent="documenter",
        expected_action="auto",
        min_confidence=70,
        description="README update",
        tags=["documentation", "readme"]
    ),
    TestCase(
        prompt="Add JSDoc comments and documentation to the utility functions",
        expected_agent="documenter",
        expected_action="auto",
        min_confidence=70,
        description="Code comments with documentation keyword",
        tags=["documentation", "jsdoc"]
    ),

    # =========================================================================
    # DEVOPS AGENT TESTS
    # =========================================================================
    TestCase(
        prompt="Set up a CI/CD pipeline with GitHub Actions for deployment",
        expected_agent="devops-engineer",
        expected_action="auto",
        min_confidence=70,
        description="CI/CD setup",
        tags=["devops", "cicd"]
    ),
    TestCase(
        prompt="Create a Dockerfile for the Node.js application and containerize it",
        expected_agent="devops-engineer",
        expected_action="auto",
        min_confidence=70,
        description="Docker containerization",
        tags=["devops", "docker"]
    ),
    TestCase(
        prompt="Configure Kubernetes deployment for production infrastructure",
        expected_agent="devops-engineer",
        expected_action="auto",
        min_confidence=70,
        description="K8s deployment",
        tags=["devops", "k8s"]
    ),

    # =========================================================================
    # REFACTORING AGENT TESTS
    # =========================================================================
    TestCase(
        prompt="Refactor this function to reduce complexity and clean up code",
        expected_agent="refactorer",
        expected_action="auto",
        min_confidence=70,
        description="Direct refactor request",
        tags=["refactoring", "complexity"]
    ),
    TestCase(
        prompt="Refactor and extract the validation logic, clean up the code",
        expected_agent="refactorer",
        expected_action="auto",
        min_confidence=70,
        description="Extract pattern with multiple refactor keywords",
        tags=["refactoring", "extract"]
    ),
    TestCase(
        prompt="Refactor and clean up the duplicate code in the handlers",
        expected_agent="refactorer",
        expected_action="auto",
        min_confidence=70,
        description="DRY refactoring with refactor keyword",
        tags=["refactoring", "dry"]
    ),

    # =========================================================================
    # API DESIGN AGENT TESTS
    # =========================================================================
    TestCase(
        prompt="Design a REST API for the inventory management system with endpoints",
        expected_agent="api-designer",
        expected_action="auto",
        min_confidence=70,
        description="REST API design",
        tags=["api", "rest"]
    ),
    TestCase(
        prompt="Add a new endpoint for user preferences",
        expected_agent="api-designer",
        expected_action="prompt",
        min_confidence=45,
        max_confidence=69,
        description="Endpoint addition",
        tags=["api", "endpoint"]
    ),

    # =========================================================================
    # ORCHESTRATOR TESTS
    # =========================================================================
    TestCase(
        prompt="Orchestrate a comprehensive multi-agent workflow for the codebase",
        expected_agent="orchestrator",
        expected_action="auto",
        min_confidence=70,
        description="Multi-agent workflow triggers orchestrator",
        tags=["orchestration", "audit"]
    ),
    TestCase(
        prompt="Orchestrate and coordinate multiple agents to validate everything",
        expected_agent="orchestrator",
        expected_action="auto",
        min_confidence=70,
        description="Orchestrate with coordinate keywords",
        tags=["orchestration", "validate"]
    ),

    # =========================================================================
    # NEGATION PATTERN TESTS
    # =========================================================================
    TestCase(
        prompt="Just implement the login form UI component, don't brainstorm",
        expected_agent="frontend-designer",
        expected_action="auto",
        min_confidence=70,
        description="Frontend wins with component keyword, brainstormer suppressed",
        tags=["negation", "brainstormer"]
    ),
    TestCase(
        prompt="Skip tests for now, just build the UI component",
        expected_agent="frontend-designer",
        expected_action="auto",
        min_confidence=70,
        description="Frontend wins strongly with component keyword",
        tags=["negation", "tester"]
    ),

    # =========================================================================
    # EDGE CASES
    # =========================================================================
    TestCase(
        prompt="Fix it",
        expected_agent="debugger, error-handler",
        expected_action="suggest",
        min_confidence=1,
        max_confidence=44,
        description="Vague request - disambiguation between debugger/error-handler",
        tags=["edge-case", "vague", "disambiguation"]
    ),

    # =========================================================================
    # COMMAND MAPPING TESTS
    # =========================================================================
    TestCase(
        prompt="/validate the codebase",
        expected_agent="orchestrator",
        expected_action="auto",
        min_confidence=100,
        description="Command mapping override",
        tags=["command", "validate"]
    ),
    TestCase(
        prompt="/security scan the auth module",
        expected_agent="security-scanner",
        expected_action="auto",
        min_confidence=100,
        description="Command mapping for security",
        tags=["command", "security"]
    ),
    TestCase(
        prompt="/test the user service",
        expected_agent="tester",
        expected_action="auto",
        min_confidence=100,
        description="Command mapping for test",
        tags=["command", "test"]
    ),
]


# =============================================================================
# MATCHING LOGIC (Copied from agent-auto-invoke.py for testing)
# =============================================================================

def load_config() -> dict:
    """Load invoke-config.json configuration."""
    config_path = CONFIG_DIR / "invoke-config.json"

    defaults = {
        "thresholds": {"auto_invoke": 70, "prompt_user": 45, "suggest_only": 0},
        "weights": {"keyword": 0.25, "category": 0.35, "llm_intent": 0.40},
        "categories": {}
    }

    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
            for key, value in defaults.items():
                if key not in config:
                    config[key] = value
            return config
        except json.JSONDecodeError:
            return defaults
    return defaults


def load_registry() -> dict:
    """Load agent-registry.json."""
    registry_path = AGENTS_DIR / "agent-registry.json"

    if registry_path.exists():
        try:
            return json.loads(registry_path.read_text())
        except json.JSONDecodeError:
            return {"agents": {}, "command_mappings": {}}
    return {"agents": {}, "command_mappings": {}}


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

        # Count keyword matches
        match_count = 0
        for keyword in exact_keywords:
            if keyword.lower() in prompt_lower:
                match_count += 1

        if len(exact_keywords) > 0 and match_count > 0:
            if match_count >= 3:
                scores[agent_name] = 100
            elif match_count == 2:
                scores[agent_name] = 80
            else:
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

    # Find matching categories
    matched_categories = []
    for category, cat_def in categories.items():
        keywords = cat_def.get("keywords", [])
        for kw in keywords:
            if kw.lower() in prompt_lower:
                matched_categories.append(category)
                break

    if not matched_categories:
        for agent_name in agents:
            scores[agent_name] = 0
        return scores

    # Score agents based on category overlap
    for agent_name, agent_def in agents.items():
        agent_categories = set(agent_def.get("categories", []))
        matched_set = set(matched_categories)
        overlap = agent_categories.intersection(matched_set)

        if overlap:
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


def layer3_phrase_match(prompt: str, registry: dict) -> dict:
    """Layer 3: Phrase pattern matching."""
    scores = {}
    prompt_lower = prompt.lower()
    agents = registry.get("agents", {})

    for agent_name, agent_def in agents.items():
        triggers = agent_def.get("triggers", {})
        phrase_patterns = triggers.get("phrase_patterns", [])

        if not phrase_patterns:
            scores[agent_name] = 0
            continue

        match_count = 0
        for pattern in phrase_patterns:
            try:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    match_count += 1
            except re.error:
                continue

        if match_count > 0:
            if match_count >= 3:
                scores[agent_name] = 100
            elif match_count == 2:
                scores[agent_name] = 85
            else:
                scores[agent_name] = 70
        else:
            scores[agent_name] = 0

    return scores


def check_command_mapping(prompt: str, registry: dict) -> Optional[str]:
    """Check for command mapping."""
    prompt_stripped = prompt.strip()
    command_mappings = registry.get("command_mappings", {})

    for command, agents in command_mappings.items():
        if prompt_stripped.startswith(command):
            return agents[0] if agents else None

    return None


def calculate_combined_score(
    layer1: dict,
    layer2: dict,
    layer3: dict,
    weights: dict
) -> Dict[str, float]:
    """Calculate combined scores for all agents."""
    results = {}
    all_agents = set(layer1.keys()) | set(layer2.keys()) | set(layer3.keys())

    w1 = weights.get("keyword", 0.25)
    w2 = weights.get("category", 0.35)
    w3 = weights.get("llm_intent", 0.40)

    for agent in all_agents:
        l1 = layer1.get(agent, 0)
        l2 = layer2.get(agent, 0)
        l3 = layer3.get(agent, 0)

        score = (l1 * w1) + (l2 * w2) + (l3 * w3)
        results[agent] = score

    return dict(sorted(results.items(), key=lambda x: x[1], reverse=True))


def analyze_prompt(prompt: str, config: dict, registry: dict) -> Tuple[str, float, str, dict]:
    """
    Analyze a prompt and return the result.

    Returns:
        Tuple of (agent_name, confidence, action, breakdown)
    """
    # Check command mapping first
    command_agent = check_command_mapping(prompt, registry)
    if command_agent:
        return (command_agent, 100.0, "auto", {"source": "command_mapping"})

    # Run 3-layer matching
    weights = config.get("weights", {"keyword": 0.25, "category": 0.35, "llm_intent": 0.40})
    thresholds = config.get("thresholds", {"auto_invoke": 70, "prompt_user": 45})

    layer1 = layer1_keyword_match(prompt, registry)
    layer2 = layer2_category_match(prompt, registry, config)
    layer3 = layer3_phrase_match(prompt, registry)

    combined = calculate_combined_score(layer1, layer2, layer3, weights)

    if not combined:
        return (None, 0.0, "none", {})

    top_agent = list(combined.keys())[0]
    top_score = combined[top_agent]

    # Determine action based on thresholds (70/45)
    if top_score >= thresholds.get("auto_invoke", 70):
        action = "auto"
    elif top_score >= thresholds.get("prompt_user", 45):
        action = "prompt"
    elif top_score > 0:
        action = "suggest"
    else:
        action = "none"

    breakdown = {
        "layer1": layer1.get(top_agent, 0),
        "layer2": layer2.get(top_agent, 0),
        "layer3": layer3.get(top_agent, 0),
        "weights": weights,
        "all_scores": {k: v for k, v in list(combined.items())[:5]}  # Top 5
    }

    return (top_agent, top_score, action, breakdown)


# =============================================================================
# TEST RUNNER
# =============================================================================

class TestRunner:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.config = load_config()
        self.registry = load_registry()
        self.results = []

    def run_test(self, test: TestCase) -> Tuple[bool, str]:
        """Run a single test case."""
        agent, confidence, action, breakdown = analyze_prompt(
            test.prompt, self.config, self.registry
        )

        # Check expected agent (supports comma-separated alternatives)
        agent_match = test.accepts_agent(agent)

        # Check expected action
        action_match = (action == test.expected_action)

        # Check confidence range
        confidence_in_range = (
            test.min_confidence <= confidence <= test.max_confidence
        )

        passed = agent_match and action_match and confidence_in_range

        # Build failure message
        failures = []
        if not agent_match:
            failures.append(f"agent: got '{agent}', expected '{test.expected_agent}'")
        if not action_match:
            failures.append(f"action: got '{action}', expected '{test.expected_action}'")
        if not confidence_in_range:
            failures.append(f"confidence: {confidence:.1f}% not in [{test.min_confidence}, {test.max_confidence}]")

        message = "; ".join(failures) if failures else "OK"

        return (passed, message, agent, confidence, action, breakdown)

    def run_all(self, tag_filter: Optional[str] = None) -> dict:
        """Run all tests, optionally filtered by tag."""
        passed = 0
        failed = 0
        results = []

        tests = TEST_CASES
        if tag_filter:
            tests = [t for t in tests if tag_filter in t.tags]

        for test in tests:
            success, message, agent, confidence, action, breakdown = self.run_test(test)

            result = {
                "test": test,
                "passed": success,
                "message": message,
                "actual_agent": agent,
                "actual_confidence": confidence,
                "actual_action": action,
                "breakdown": breakdown
            }
            results.append(result)

            if success:
                passed += 1
                status = "\033[92m✓\033[0m"
            else:
                failed += 1
                status = "\033[91m✗\033[0m"

            # Print result
            if self.verbose or not success:
                print(f"{status} [{test.expected_action:7}] {test.prompt[:60]}")
                if not success or self.verbose:
                    print(f"    Expected: {test.expected_agent} ({test.expected_action})")
                    print(f"    Actual:   {agent} ({action}) @ {confidence:.1f}%")
                    if self.verbose and breakdown:
                        print(f"    Layers:   L1={breakdown.get('layer1', 0):.0f} L2={breakdown.get('layer2', 0):.0f} L3={breakdown.get('layer3', 0):.0f}")
                    if not success:
                        print(f"    Reason:   {message}")
                    print()

        return {
            "total": len(tests),
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / len(tests) * 100) if tests else 0,
            "results": results
        }


def run_demo():
    """Interactive demo mode."""
    print("\n" + "=" * 60)
    print("  Agent Auto-Invocation Demo")
    print("=" * 60)
    print("\nThresholds: auto >= 70%, prompt 45-69%, suggest < 45%")
    print("Enter prompts to see which agent would be selected.")
    print("Type 'quit' to exit.\n")

    config = load_config()
    registry = load_registry()

    while True:
        try:
            prompt = input("\033[96mPrompt>\033[0m ")
        except (EOFError, KeyboardInterrupt):
            break

        if prompt.lower() in ('quit', 'exit', 'q'):
            break

        if not prompt.strip():
            continue

        agent, confidence, action, breakdown = analyze_prompt(prompt, config, registry)

        # Color-coded output
        if action == "auto":
            color = "\033[92m"  # Green
        elif action == "prompt":
            color = "\033[93m"  # Yellow
        elif action == "suggest":
            color = "\033[96m"  # Cyan
        else:
            color = "\033[90m"  # Gray

        print(f"\n{color}Agent: {agent or 'none'}")
        print(f"Confidence: {confidence:.1f}%")
        print(f"Action: {action.upper()}\033[0m")

        if breakdown and "all_scores" in breakdown:
            print("\nTop 5 agents:")
            for name, score in breakdown["all_scores"].items():
                bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
                print(f"  {name:25} [{bar}] {score:.1f}%")

        if breakdown and "layer1" in breakdown:
            print(f"\nLayer breakdown for {agent}:")
            print(f"  L1 (Keyword):  {breakdown.get('layer1', 0):.0f}%")
            print(f"  L2 (Category): {breakdown.get('layer2', 0):.0f}%")
            print(f"  L3 (Phrase):   {breakdown.get('layer3', 0):.0f}%")

        print()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test agent auto-invocation system")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--demo", action="store_true", help="Interactive demo mode")
    parser.add_argument("--tag", type=str, help="Filter tests by tag")
    parser.add_argument("--list-tags", action="store_true", help="List all available tags")

    args = parser.parse_args()

    if args.list_tags:
        all_tags = set()
        for test in TEST_CASES:
            all_tags.update(test.tags)
        print("Available tags:")
        for tag in sorted(all_tags):
            count = sum(1 for t in TEST_CASES if tag in t.tags)
            print(f"  {tag}: {count} tests")
        return 0

    if args.demo:
        run_demo()
        return 0

    print("\n" + "=" * 60)
    print("  Agent Auto-Invocation Test Suite")
    print("  Thresholds: auto >= 70%, prompt 45-69%, suggest < 45%")
    print("=" * 60 + "\n")

    runner = TestRunner(verbose=args.verbose)
    summary = runner.run_all(tag_filter=args.tag)

    # Print summary
    print("\n" + "-" * 60)
    print(f"Total:   {summary['total']}")
    print(f"Passed:  \033[92m{summary['passed']}\033[0m")
    print(f"Failed:  \033[91m{summary['failed']}\033[0m")
    print(f"Rate:    {summary['pass_rate']:.1f}%")
    print("-" * 60 + "\n")

    return 0 if summary['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
