"""
Small evaluation harness for the AI flow.

Run it with:

    python tests/run_eval.py

from the ai-service/ directory (needs the same environment/.env the app
itself uses). It measures whether the deterministic parts of the flow
(planner decisions, booking slot-filling) behave exactly as expected —
hard assertions, always run, no network — and gives a fuzzy pass/fail
plus a similarity score for the LLM-backed parts (requirement
extraction, recommendation ranking, provider search, the tool-calling
agent nodes, and semantic retrieval), which are SKIPPED rather than
failed if GROQ_API_KEY / the backend / the embedding model aren't
reachable, so this stays runnable without every dependency configured.

No case creates a real booking (see eval_dataset.py for why) — the
agentic booking-creation case specifically verifies the tool *refuses*
an incomplete booking before any HTTP call is made.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.planner_agent import planner_agent
from app.graph.booking_agent_node import booking_agent_node
from app.graph.booking_create_node import booking_create_node
from app.graph.booking_status_node import booking_status_node
from app.graph.search_agent_node import search_agent_node
from app.tools.agent_tools import make_tools

from tests.eval_dataset import (
    BOOKING_AGENT_CASES,
    BOOKING_STATUS_NO_BOOKING_CASE,
    CREATE_BOOKING_REJECTION_CASE,
    PLANNER_CASES,
    PROVIDER_TEXT_CASE,
    RECOMMENDATION_EMPTY_CASE,
    RECOMMENDATION_LIVE_CASE,
    REQUIREMENT_CASES,
    SEARCH_AGENT_NODE_CASE,
    SEARCH_LIVE_CASE,
    SEMANTIC_SEARCH_LIVE_CASE,
)


PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"


def _get_path(data, path):
    """dotted-path getter: _get_path({"a": {"b": 1}}, "a.b") -> 1"""
    value = data
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _print_result(category, name, status, detail=""):
    print(f"[{status:4}] {category:12} {name:45} {detail}")


# =========================================================
# Planner decisions
# =========================================================

def run_planner_cases():
    passed = failed = 0

    for case in PLANNER_CASES:
        result = planner_agent(case["state"])
        action = result.get("next_action")

        ok = action == case["expected_action"]
        detail = f"expected={case['expected_action']!r} got={action!r}"

        if ok and "expected_missing" in case:
            missing = set(result.get("missing_fields") or [])
            ok = missing == case["expected_missing"]
            detail += f" | missing expected={case['expected_missing']} got={missing}"

        _print_result("planner", case["name"], PASS if ok else FAIL, detail)
        passed += ok
        failed += not ok

    return passed, failed, 0


# =========================================================
# Booking agent node (slot-filling / provider selection)
# =========================================================

def run_booking_agent_cases():
    passed = failed = 0

    for case in BOOKING_AGENT_CASES:
        result = booking_agent_node(dict(case["state"]))

        mismatches = []
        for path, expected in case["check"].items():
            actual = _get_path(result, path) if "." in path else result.get(path)

            if isinstance(expected, list):
                if set(actual or []) != set(expected):
                    mismatches.append(f"{path}: expected={expected} got={actual}")
            elif actual != expected:
                mismatches.append(f"{path}: expected={expected!r} got={actual!r}")

        ok = not mismatches
        _print_result(
            "booking_agent",
            case["name"],
            PASS if ok else FAIL,
            "; ".join(mismatches),
        )
        passed += ok
        failed += not ok

    return passed, failed, 0


# =========================================================
# Requirement extraction (LLM)
# =========================================================

def run_requirement_cases():
    passed = failed = skipped = 0

    try:
        from app.agents.requirements_agent import requirements_agent
    except Exception as exc:
        for case in REQUIREMENT_CASES:
            _print_result("requirements", case["name"], SKIP, f"import failed: {exc}")
        return 0, 0, len(REQUIREMENT_CASES)

    for case in REQUIREMENT_CASES:
        try:
            result = requirements_agent.invoke({"input": case["input"]})
            extracted = result.model_dump() if hasattr(result, "model_dump") else dict(result)
        except Exception as exc:
            _print_result("requirements", case["name"], SKIP, f"LLM unreachable: {exc}")
            skipped += 1
            continue

        checks_total = 0
        checks_ok = 0

        for field, substring in case.get("expected_substrings", {}).items():
            checks_total += 1
            actual = str(extracted.get(field, "")).lower()
            if substring.lower() in actual:
                checks_ok += 1

        for field in case.get("expected_nonempty", []):
            checks_total += 1
            if str(extracted.get(field, "")).strip():
                checks_ok += 1

        score = checks_ok / checks_total if checks_total else 1.0
        ok = score >= 0.75

        _print_result(
            "requirements",
            case["name"],
            PASS if ok else FAIL,
            f"score={checks_ok}/{checks_total} extracted={extracted}",
        )
        passed += ok
        failed += not ok

    return passed, failed, skipped


# =========================================================
# Recommendation ranking — calls the recommend_providers TOOL directly
# (not through the agent loop), so these test the tool's own logic and
# its anti-hallucination index-mapping in isolation.
# =========================================================

def run_recommendation_cases():
    passed = failed = skipped = 0

    # -- deterministic: empty providers must skip the LLM entirely
    context = {
        "providers": RECOMMENDATION_EMPTY_CASE["providers"],
        "requirements": RECOMMENDATION_EMPTY_CASE["requirements"],
    }
    tools = make_tools(context, session_id="eval-recommendation-empty")
    tools["recommend_providers"].invoke({})

    ok = context.get("recommended_providers") == []
    _print_result(
        "recommendation",
        RECOMMENDATION_EMPTY_CASE["name"],
        PASS if ok else FAIL,
        f"recommended_providers={context.get('recommended_providers')}",
    )
    passed += ok
    failed += not ok

    # -- LLM-backed: ranks real providers and maps them back by index
    case = RECOMMENDATION_LIVE_CASE
    try:
        context = {
            "providers": case["providers"],
            "requirements": case["requirements"],
        }
        tools = make_tools(context, session_id="eval-recommendation-live")
        tools["recommend_providers"].invoke({})
    except Exception as exc:
        _print_result("recommendation", case["name"], SKIP, f"LLM unreachable: {exc}")
        return passed, failed, skipped + 1

    recommended = context.get("recommended_providers") or []
    real_ids = {p["_id"] for p in case["providers"]}

    ok = len(recommended) > 0 and all(r.get("provider_id") in real_ids for r in recommended)

    _print_result(
        "recommendation",
        case["name"],
        PASS if ok else FAIL,
        f"recommended={recommended}",
    )
    passed += ok
    failed += not ok

    return passed, failed, skipped


# =========================================================
# Provider search (live HTTP call to the Express backend)
# =========================================================

def run_search_case():
    from app.tools.provider_tool import ProviderTool

    case = SEARCH_LIVE_CASE

    try:
        result = ProviderTool.search(case["service"], case["location"])
    except Exception as exc:
        _print_result("search", case["name"], SKIP, f"backend unreachable: {exc}")
        return 0, 0, 1

    ok = isinstance(result, list)
    _print_result(
        "search",
        case["name"],
        PASS if ok else FAIL,
        f"providers_found={len(result) if ok else 'n/a'}",
    )
    return int(ok), int(not ok), 0


# =========================================================
# Agentic tool-calling — exercises the LLM tool-calling agent nodes
# end to end (search_agent_node, booking_create_node, booking_status_node).
# Needs GROQ_API_KEY; the search case also needs the Express backend.
# None of these can create a real booking (see eval_dataset.py for why).
# =========================================================

def run_agentic_cases():
    passed = failed = skipped = 0

    # -- agent decides to search, correctly skips ranking when nothing is found
    case = SEARCH_AGENT_NODE_CASE
    try:
        result = search_agent_node(dict(case["state"]))
    except Exception as exc:
        _print_result("agentic", case["name"], SKIP, f"LLM/backend unreachable: {exc}")
        skipped += 1
    else:
        providers = result.get("providers") or []
        recommended = result.get("recommended_providers") or []
        # Nothing should clear the relevance threshold for "Wedding
        # Photography" against a provider catalogue with no such
        # category — and with zero providers, recommend_providers
        # should never even be called.
        ok = providers == [] and recommended == []
        _print_result(
            "agentic",
            case["name"],
            PASS if ok else FAIL,
            f"providers={len(providers)} recommended={len(recommended)}",
        )
        passed += ok
        failed += not ok

    # -- agent decides to call create_booking, but the tool itself refuses
    #    an incomplete booking, so no HTTP call ever reaches the backend
    case = CREATE_BOOKING_REJECTION_CASE
    try:
        result = booking_create_node(dict(case["state"]))
    except Exception as exc:
        _print_result("agentic", case["name"], SKIP, f"LLM unreachable: {exc}")
        skipped += 1
    else:
        ok = (
            result.get("booking_created") is False
            and bool(result.get("booking_error"))
            and result.get("booking_status") == "failed"
        )
        _print_result(
            "agentic",
            case["name"],
            PASS if ok else FAIL,
            f"booking_created={result.get('booking_created')} "
            f"error={result.get('booking_error')!r}",
        )
        passed += ok
        failed += not ok

    # -- agent calls get_booking_status, tool correctly reports nothing to check
    case = BOOKING_STATUS_NO_BOOKING_CASE
    try:
        result = booking_status_node(dict(case["state"]))
    except Exception as exc:
        _print_result("agentic", case["name"], SKIP, f"LLM unreachable: {exc}")
        skipped += 1
    else:
        ok = "No booking found" in (result.get("response") or "")
        _print_result(
            "agentic",
            case["name"],
            PASS if ok else FAIL,
            f"response={result.get('response')!r}",
        )
        passed += ok
        failed += not ok

    return passed, failed, skipped


# =========================================================
# Semantic retrieval (app/rag/provider_index.py)
# =========================================================

def run_rag_cases():
    passed = failed = skipped = 0

    # -- deterministic: pure string construction, no embedding/network
    from app.rag.provider_index import _provider_text

    case = PROVIDER_TEXT_CASE
    text = _provider_text(case["provider"])
    missing = [s for s in case["expected_substrings"] if s not in text]
    ok = not missing

    _print_result(
        "rag",
        case["name"],
        PASS if ok else FAIL,
        f"missing_substrings={missing} text={text!r}" if missing else f"text={text!r}",
    )
    passed += ok
    failed += not ok

    # -- live: real embedding model + real backend, no keyword overlap by design
    from app.rag.provider_index import semantic_search

    case = SEMANTIC_SEARCH_LIVE_CASE
    try:
        results = semantic_search(case["query"])
    except Exception as exc:
        _print_result("rag", case["name"], SKIP, f"embedder/backend unreachable: {exc}")
        return passed, failed, skipped + 1

    if results is None:
        _print_result("rag", case["name"], SKIP, "semantic retrieval unavailable (embedder failed to load)")
        return passed, failed, skipped + 1

    # Must actually find something — an empty list would silently defeat
    # the point of this case (proving semantic, keyword-free matching
    # works), so "no results" is a FAIL here, not a vacuous pass.
    ok = (
        isinstance(results, list)
        and len(results) > 0
        and all(isinstance(p, dict) and 0.0 <= score <= 1.0 for p, score in results)
    )
    _print_result(
        "rag",
        case["name"],
        PASS if ok else FAIL,
        f"matches={[(p.get('firstName'), round(s, 3)) for p, s in results]}",
    )
    passed += ok
    failed += not ok

    return passed, failed, skipped


def main():
    totals = {"pass": 0, "fail": 0, "skip": 0}

    for runner in (
        run_planner_cases,
        run_booking_agent_cases,
        run_requirement_cases,
        run_recommendation_cases,
        run_search_case,
        run_agentic_cases,
        run_rag_cases,
    ):
        p, f, s = runner()
        totals["pass"] += p
        totals["fail"] += f
        totals["skip"] += s
        print()

    print("=" * 60)
    print(
        f"TOTAL: {totals['pass']} passed, {totals['fail']} failed, "
        f"{totals['skip']} skipped"
    )
    print("=" * 60)

    sys.exit(1 if totals["fail"] else 0)


if __name__ == "__main__":
    main()
