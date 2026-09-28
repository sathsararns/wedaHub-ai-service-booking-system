"""
Evaluation cases for the AI flow, grouped by which part of the pipeline
they exercise.

Design choice: PLANNER_CASES and BOOKING_AGENT_CASES only exercise
deterministic Python logic (no LLM call, no network) — they always run
and are checked with hard assertions. REQUIREMENT_CASES,
RECOMMENDATION_CASES and the search case call a real LLM and/or the real
Express backend; those are scored with fuzzy substring matching and are
SKIPPED (not failed) if the dependency they need isn't reachable, so the
harness stays runnable without secrets/services configured.

No case creates a real booking — that would leave side effects (real
Booking documents) behind on every run, which isn't appropriate for a
repeatable eval script. Booking-flow correctness is instead measured via
BOOKING_AGENT_CASES, which test the same slot-filling/provider-selection
decisions without ever calling the live create-booking endpoint.
"""

# =========================================================
# Planner decisions (deterministic — no LLM, no network)
# =========================================================

PLANNER_CASES = [
    {
        "name": "greeting",
        "state": {
            "user_input": "hello",
            "requirements": {},
            "booking": {},
            "customer_id": None,
            "recommended_providers": [],
        },
        "expected_action": "general_chat",
    },
    {
        "name": "thanks",
        "state": {
            "user_input": "thanks",
            "requirements": {},
            "booking": {},
            "customer_id": None,
            "recommended_providers": [],
        },
        "expected_action": "general_chat",
    },
    {
        "name": "booking_status_keyword",
        "state": {
            "user_input": "what's my booking status",
            "requirements": {},
            "booking": {},
            "customer_id": "c1",
            "recommended_providers": [],
        },
        "expected_action": "booking_status",
    },
    {
        "name": "book_n_requires_login",
        "state": {
            "user_input": "Book 2",
            "requirements": {},
            "booking": {},
            "customer_id": None,
            "recommended_providers": [],
        },
        "expected_action": "ask_login",
    },
    {
        "name": "book_n_logged_in",
        "state": {
            "user_input": "Book 2",
            "requirements": {},
            "booking": {},
            "customer_id": "c1",
            "recommended_providers": [],
        },
        "expected_action": "book_provider",
    },
    {
        "name": "confirmation_with_complete_booking",
        "state": {
            "user_input": "yes",
            "requirements": {"location": "Kandy"},
            "booking": {
                "provider_id": "p1",
                "service": "Electrician",
                "city": "Kandy",
                "date": "tomorrow",
                "description": "fix my socket",
            },
            "customer_id": "c1",
            "recommended_providers": [],
        },
        "expected_action": "create_booking",
    },
    {
        "name": "confirmation_with_incomplete_booking",
        "state": {
            "user_input": "yes",
            "requirements": {},
            "booking": {},
            "customer_id": "c1",
            "recommended_providers": [],
        },
        "expected_action": "ask_more_information",
        "expected_missing": {"provider", "service", "location", "date", "description"},
    },
    {
        # Input must not match a confirmation word ("ok"/"yes"/"sure"/...) —
        # those are checked earlier and take priority, routing to
        # ask_more_information instead of this "still filling slots" branch.
        "name": "existing_booking_missing_fields",
        "state": {
            "user_input": "what's next",
            "requirements": {},
            "booking": {"provider_id": "p1"},
            "customer_id": "c1",
            "recommended_providers": [],
        },
        "expected_action": "book_provider",
        "expected_missing": {"service", "location", "date", "description"},
    },
    {
        "name": "existing_booking_complete_awaits_confirmation",
        "state": {
            "user_input": "sounds good",
            "requirements": {},
            "booking": {
                "provider_id": "p1",
                "service": "Electrician",
                "city": "Kandy",
                "date": "tomorrow",
                "description": "fix my socket",
            },
            "customer_id": "c1",
            "recommended_providers": [],
        },
        "expected_action": "await_confirmation",
    },
    {
        "name": "ready_to_search",
        "state": {
            "user_input": "find someone for me",
            "requirements": {"service": "Plumbing", "location": "Colombo"},
            "booking": {},
            "customer_id": None,
            "recommended_providers": [],
        },
        "expected_action": "search_services",
    },
    {
        "name": "service_request_missing_info",
        "state": {
            "user_input": "I need a plumber",
            "requirements": {},
            "booking": {},
            "customer_id": None,
            "recommended_providers": [],
        },
        "expected_action": "ask_more_information",
        "expected_missing": {"service", "location"},
    },
]


# =========================================================
# Booking slot-filling / provider selection (deterministic)
# =========================================================

BOOKING_AGENT_CASES = [
    {
        "name": "select_provider_from_recommendation",
        "state": {
            "user_input": "Book 1",
            "recommended_providers": [
                {"provider_index": 0, "business_name": "Acme Electric"}
            ],
            "providers": [
                {"_id": "p1", "firstName": "Acme", "lastName": "Electric"}
            ],
            "requirements": {"service": "Electrician", "location": "Kandy"},
            "booking": {},
            "customer_id": "c1",
        },
        "check": {
            "booking.provider_id": "p1",
            "booking.provider_name": "Acme Electric",
            "planner.next_action": "book_provider",
            "planner.missing_fields": ["date", "description"],
        },
    },
    {
        "name": "provider_selected_only_date_known",
        "state": {
            "user_input": "tomorrow",
            "booking": {"provider_id": "p1", "provider_name": "Acme"},
            "requirements": {
                "service": "Electrician",
                "location": "Kandy",
                "date": "tomorrow",
            },
            "recommended_providers": [],
            "providers": [],
        },
        "check": {
            "booking.date": "tomorrow",
            "planner.next_action": "book_provider",
            "planner.missing_fields": ["description"],
        },
    },
    {
        "name": "provider_selected_all_fields_ready_to_confirm",
        "state": {
            "user_input": "fix my socket",
            "booking": {"provider_id": "p1", "provider_name": "Acme", "date": "tomorrow"},
            "requirements": {
                "service": "Electrician",
                "location": "Kandy",
                "date": "tomorrow",
                "description": "fix my socket",
            },
            "recommended_providers": [],
            "providers": [],
        },
        "check": {
            "planner.next_action": "confirm_booking",
        },
    },
    {
        "name": "no_provider_selected_yet_booking_stays_empty",
        "state": {
            "user_input": "hi there",
            "booking": {},
            "requirements": {},
            "recommended_providers": [],
            "providers": [],
        },
        "check": {
            "booking": {},
            "planner": None,
        },
    },
]


# =========================================================
# Requirement extraction (LLM — needs GROQ_API_KEY + network)
# =========================================================

REQUIREMENT_CASES = [
    {
        "name": "electrician_matara",
        "input": "I need an electrician in Matara",
        "expected_substrings": {"service": "electric", "location": "matara"},
    },
    {
        "name": "ac_not_working",
        "input": "My AC isn't working",
        "expected_substrings": {"service": "ac"},
    },
    {
        "name": "plumber_sink_leaking_tomorrow",
        "input": "I need a plumber because my sink is leaking tomorrow",
        "expected_substrings": {"service": "plumb"},
        "expected_nonempty": ["date"],
    },
    {
        "name": "painter_in_galle",
        "input": "Looking for a painter in Galle",
        "expected_substrings": {"service": "paint", "location": "galle"},
    },
]


# =========================================================
# Recommendation ranking — calls the recommend_providers TOOL directly
# (app.tools.agent_tools), not through the agent loop, so these test the
# tool's own logic (and its anti-hallucination index-mapping) in
# isolation from whether the LLM decides to call it.
# =========================================================

# Deterministic — no providers means the tool skips the LLM call itself.
RECOMMENDATION_EMPTY_CASE = {
    "name": "no_providers_skips_llm_call",
    "providers": [],
    "requirements": {"service": "Electrician", "location": "Kandy"},
}

# LLM-backed — needs GROQ_API_KEY + network.
RECOMMENDATION_LIVE_CASE = {
    "name": "ranks_and_maps_real_providers_back_by_index",
    "providers": [
        {
            "_id": "p1",
            "firstName": "Nimal",
            "lastName": "Perera",
            "businessName": "Nimal Electric Works",
            "category": "Electrician",
            "city": "Kandy",
            "rating": 4.8,
            "reviews": 40,
        },
        {
            "_id": "p2",
            "firstName": "Kasun",
            "lastName": "Silva",
            "businessName": "Kasun Electricals",
            "category": "Electrician",
            "city": "Kandy",
            "rating": 3.1,
            "reviews": 2,
        },
    ],
    "requirements": {"service": "Electrician", "location": "Kandy"},
}


# =========================================================
# Provider search (live HTTP call to the Express backend)
# =========================================================

SEARCH_LIVE_CASE = {
    "name": "search_does_not_error_against_backend",
    "service": "Electrician",
    "location": "Kandy",
}


# =========================================================
# Agentic tool-calling (LLM decides whether/which tool to call —
# these exercise app/graph/search_agent_node.py, booking_create_node.py
# and booking_status_node.py end to end, needs GROQ_API_KEY; the search
# case also needs the Express backend reachable)
# =========================================================

# The agent should call search_providers, find nothing relevant for a
# service the provider catalogue has none of, and correctly decide NOT
# to call recommend_providers afterwards. Both the service AND the
# location are made up on purpose: a real city name in the query would
# exactly match a real provider's city text and inflate the similarity
# score regardless of category (see MIN_SIMILARITY's calibration notes
# in app/rag/provider_index.py for the measured numbers) — a nonsense
# location avoids that confound so this actually tests "no relevant
# category", not "no matching city".
SEARCH_AGENT_NODE_CASE = {
    "name": "agent_runs_without_error_and_does_not_over_call_tools",
    "state": {
        "session_id": "eval-search-agent",
        "requirements": {
            "service": "Wedding Photography",
            "location": "Nonexistent City Zzzz",
        },
    },
}

# The agent should decide to call create_booking, and the TOOL ITSELF
# should refuse (no provider_id/date/description present) — this must
# never reach the real backend, so running this case can never create a
# real booking, no matter how many times the suite runs.
CREATE_BOOKING_REJECTION_CASE = {
    "name": "agent_calls_tool_but_tool_rejects_incomplete_booking",
    "state": {
        "session_id": "eval-create-booking-rejection",
        "booking": {"provider_id": "p1"},  # service/date/description missing
        "customer_id": "eval-customer",
    },
}

# No booking_result in state -> the tool has nothing to look up and must
# say so without making an HTTP call.
BOOKING_STATUS_NO_BOOKING_CASE = {
    "name": "agent_calls_tool_with_no_booking_to_check",
    "state": {
        "session_id": "eval-booking-status-empty",
        "booking_result": None,
    },
}


# =========================================================
# Semantic retrieval (app/rag/provider_index.py)
# =========================================================

# Deterministic — pure string construction, no embedding/network at all.
PROVIDER_TEXT_CASE = {
    "name": "builds_readable_text_from_real_fields_only",
    "provider": {
        "firstName": "Nimal",
        "lastName": "Perera",
        "category": "Electrician",
        "city": "Kandy",
        "district": "Kandy",
        "description": "Licensed electrician for rewiring and fault-finding.",
        "rating": 4.8,
        "reviews": 40,
    },
    "expected_substrings": [
        "Nimal Perera",
        "Category: Electrician",
        "Kandy",
        "Rated 4.8 from 40 reviews",
        "rewiring",
    ],
}

# Live — needs the embedding model + the Express backend reachable.
# Shaped exactly like the query search_providers actually builds
# (app/tools/agent_tools.py: "{service} in {location}. Customer
# request: {user_input}") rather than just the bare sentence, so this
# tests the real query format. The "Customer request" clause has zero
# literal keyword overlap with any provider's description on purpose,
# to demonstrate this is semantic, not lexical, matching.
SEMANTIC_SEARCH_LIVE_CASE = {
    "name": "retrieves_relevant_providers_with_no_keyword_overlap",
    "query": (
        "Electrician in Matara. Customer request: "
        "my lights keep flickering and the fuse box smells burnt"
    ),
}
