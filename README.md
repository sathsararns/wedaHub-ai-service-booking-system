# WedaHub AI Service

A conversational, tool-using booking assistant for WedaHub, a
home-services marketplace. Customers chat in natural language (e.g.
*"my lights keep flickering and the fuse box smells burnt, I'm in
Matara"*), and a multi-step [LangGraph](https://github.com/langchain-ai/langgraph)
workflow extracts what they want, **semantically retrieves** the real
providers whose actual profiles best match that description (not just
whichever category string happens to match exactly), then an LLM bound
to real tools — not hardcoded Python calls — decides when to search,
rank, create the booking, or check its status, walking the customer
through the rest of the booking conversation along the way. All through
one chat endpoint.

This service does not talk to the browser directly. It sits behind the
main Node.js/Express backend, which proxies chat requests to it and which
it, in turn, calls back into to search providers and create bookings.

---

## 1. Project Overview

- **What it does:** turns a free-text chat message into a completed
  booking — service + location + date + description + provider selection +
  confirmation — without the customer filling out a form.
- **Why it exists:** WedaHub already books services through a form
  (`BookingPage.jsx` on the frontend). This service is a conversational
  alternative front door to the exact same booking system.
- **What it does *not* do:** it does not read or write MongoDB directly.
  Every read/write (provider search, booking creation, booking status)
  goes through the Express backend's own REST API over HTTP.

---

## 2. Architecture

```
Browser (React)
   │  axios → http://localhost:3000/api
   ▼
Express backend (port 3000)
   │  POST /api/ai/chat         → aiController.chat()        → aiService.chatWithAI()
   │  POST /api/ai/chat/stream  → aiController.chatStream()  → aiService.streamChat() (piped through)
   │  POST /api/ai/chat/reset   → aiController.resetChat()   → aiService.resetChatMemory()
   │  axios → AI_SERVICE_URL (default http://localhost:8000)
   ▼
This service — FastAPI (main.py)
   │  POST /chat         → app/api/chat.py       → app/services/chat_service.py
   │  POST /chat/stream  → app/api/chat.py       → same chat_service.chat(), streamed out
   │  POST /chat/reset   → app/api/chat.py       → app/memory/store.py
   │
   │  Inside the graph, three nodes hand control to an LLM bound to
   │  real tools (app/agents/tool_runner.py + app/tools/factory.py) —
   │  the LLM decides whether/which tool to call, not a Python if/else:
   │    search_agent_node    -> search_providers, recommend_providers
   │    booking_create_node  -> create_booking
   │    booking_status_node  -> get_booking_status
   │  Each of those 4 tools is what actually calls back into the SAME
   │  Express backend for anything persistent:
   │    GET  /api/providers/search   (provider search)
   │    POST /api/bookings/ai        (create a booking)
   │    GET  /api/bookings/:id       (booking status lookup)
   │
   │  search_providers itself retrieves candidates from an in-memory
   │  semantic index (app/rag/provider_index.py) built from that same
   │  provider data — see section 6.
   ▼
MongoDB — read/written only via the Express backend, never directly
```

### Folder layout

```text
ai-service/
  main.py                         FastAPI entry point
  app/
    api/                          HTTP endpoints
    core/                         Configuration, lazy LLM client, logging, tracing
    agents/                       AI chains, planner, bounded tool runner
    graph/
      workflow.py                 Graph assembly
      router.py                   Routing decisions
      state.py                    Shared graph state contract
      nodes/                      Individual workflow steps
    clients/backend_client.py     All Express HTTP requests
    models/                       Chat request and AI output schemas
    prompts/                      Prompt templates and node system prompts
    services/                     Chat, provider search, booking status operations
    tools/                        Request-scoped LangChain tools and factory
    rag/                          Semantic provider index
    memory/                       Conversation store and implementation
  tests/
    unit/                         Deterministic tests with mocked external calls
    integration/                  Actual graph and HTTP contract tests
  evals/                          Evaluation datasets and runner
  scripts/                        Explicit manual checks
  experiments/                    Dormant alternatives and legacy manual checks
```

Dependencies flow from API routes to services and the graph, then from nodes
through agents/tools to services, retrieval, and the backend client. HTTP
transport belongs in `clients/`; prompts belong in `prompts/`; graph nodes
coordinate those operations. LLM clients and chains initialize on first use,
so importing the application and running mocked tests requires no API key.

The root `main.py` and public HTTP endpoints retain their existing locations.

---

## 3. Flow of a User Request

1. Frontend calls `POST /api/ai/chat` on Express with `{ message, customerId }`.
2. Express (`aiController.chat`) forwards it to this service's `POST /chat`.
3. `app/services/chat_service.py::chat()` loads that session's previous
   state from memory, merges in the new message, and runs it through the
   compiled graph (`app/graph/workflow.py`).
4. Graph execution, node by node:
   - **`requirements`** — extracts `service` / `location` / `date` /
     `description` from the message via an LLM chain, and merges them into
     whatever was already known (never overwrites a known field with an
     empty one).
   - **`planner`** — decides the next action. Mostly deterministic
     (keyword/regex checks for greetings, "booking status", `"Book N"`,
     confirmation words, etc.), with a real LLM call only as a fallback
     when nothing deterministic matches.
   - **Router** — maps the planner's decision to the next node: `search`,
     `booking_agent`, `booking_status`, or straight to `response`.
   - **`search`** (`search_agent_node.py`) — an LLM bound to two tools,
     `search_providers` and `recommend_providers`, decides whether/which
     to call — see section 5 below. `search_providers` itself retrieves
     candidates semantically (section 6) rather than by exact
     category/district matching alone.
   - **`booking_agent` → `booking_confirmation` → `booking_create`** — see
     section 6 below. `booking_create` is likewise an LLM bound to one
     tool, `create_booking`.
   - **`booking_status`** — also an LLM bound to one tool,
     `get_booking_status`, which looks up a previously-created booking's
     live status from the Express backend.
   - **`response`** — the single node that turns whatever is in state into
     the actual reply text sent back to the user; not an LLM call.
5. The final state is saved back into memory under the same session id.
6. `app/api/chat.py` returns `{ response, recommendations, booking }` to
   Express, which returns it unchanged to the frontend.

---

## 4. Agents / Nodes

| Node / Agent | File | What it actually does |
|---|---|---|
| Requirements | `app/agents/requirements_agent.py` | LLM chain, forced into the `Requirement` schema (`service`, `location`, `date`, `description`) |
| Planner | `app/agents/planner_agent.py` | Deterministic rules first (greetings, keywords, regex), LLM fallback (`PlannerDecision` schema) only if nothing matches |
| Search + recommend | `app/graph/nodes/search_agent_node.py` | **LLM tool-calling** — bound to `search_providers` + `recommend_providers`; decides whether/which to call. See section 5. |
| Booking selection/collection | `app/graph/nodes/booking_agent_node.py` | Plain Python, not an LLM call — detects `"Book N"` via regex, then incrementally fills date/description from the requirements extracted each turn |
| Booking confirmation | `app/graph/nodes/booking_confirmation_node.py` | Validates all required fields exist, reads the user's literal yes/no reply via regex |
| Booking creation | `app/graph/nodes/booking_create_node.py` | **LLM tool-calling** — bound to `create_booking`. See section 5. |
| Booking status | `app/graph/nodes/booking_status_node.py` | **LLM tool-calling** — bound to `get_booking_status`. See section 5. |
| Response | `app/graph/nodes/response_node.py` | Formats every user-facing message; not an LLM call |

Deliberately **not** converted to tool-calling: the planner's intent
classification (search vs. booking vs. status vs. chit-chat), the
provider-selection/slot-filling logic in `booking_agent_node.py`, and the
yes/no parsing in `booking_confirmation_node.py`. None of those call an
external system — they're local decisions about already-known
conversation state, where a regex is strictly more reliable than an LLM
call and there's nothing "agentic" to gain by routing them through one.
The tool-calling upgrade targets exactly the four actions that *do* touch
an external system: search, recommend, create, check status.

---

## 5. Agentic Tool-Calling

This is the actual "agent" in the AI service. Four real actions are
exposed as LangChain tools (`app/tools/factory.py`) and bound to the
LLM via `llm.bind_tools([...])`; a small shared loop
(`app/agents/tool_runner.py`) lets the model call one, see the result, and
decide whether to call another — a genuine, if intentionally narrow,
ReAct loop — instead of a Python `if/else` calling the same functions
directly.

| Tool | Called from | What it wraps |
|---|---|---|
| `search_providers(service, location)` | `search_agent_node.py` | `app/rag/provider_index.py::semantic_search()` (falls back to `app/services/provider_search_service.py` → `backend_client.search_providers()` if unavailable) — see section 6 |
| `recommend_providers()` | `search_agent_node.py` | `app/agents/recommendation_agent.py` (an LLM ranking chain — a tool that itself calls another LLM) |
| `create_booking()` | `booking_create_node.py` | `backend_client.create_booking()` |
| `get_booking_status()` | `booking_status_node.py` | `app/services/booking_status_service.py` |

Each node builds a fresh `context` dict, gets only the 1–2 tools relevant
to that step (least privilege — `booking_create_node` literally cannot
call `search_providers`, it isn't in the bound tool list), and runs
`run_tool_agent(session_id, system_prompt, human_prompt, tools)`. That
loop invokes the LLM, and for every tool call it requests, looks the
tool up by name, executes it, and feeds the result back as a
`ToolMessage` — repeating until the LLM stops requesting tools (capped
at 4 iterations). Verified live: given `service=Electrician,
location=Kandy`, the agent calls `search_providers`, sees "Found 1
provider(s)", and correctly calls `recommend_providers` next; given a
location with no matches, it correctly stops after `search_providers`
alone.

**Anti-hallucination design — why the tool signatures look the way they do:**
`search_providers` takes `service`/`location` as real LLM arguments
because those genuinely vary per search and come from the user's own
message, already extracted by `requirement_node` before the agent ever
runs. `recommend_providers`, `create_booking` and `get_booking_status`
take **no identity-bearing arguments from the LLM at all** —
`provider_id` and `booking_id` are read from `context`, populated from
state the LLM never sees as a free-text field (provider selection is
still the existing index-based `"Book N"` lookup in
`booking_agent_node.py`; the booking id is re-derived from this
session's own `booking_result`). This mirrors the pre-existing safe
pattern already in the recommendation logic, which never trusted an
LLM's provider name for anything functional and always re-resolved the
real record by index — the same principle now covers every tool that
touches a real record. `create_booking` additionally re-validates every
required field itself and refuses (without ever calling the backend) if
any is missing — defence in depth, verified by the evaluation harness's
`agent_calls_tool_but_tool_rejects_incomplete_booking` case.

Every tool call and its result is logged (`app.tools.factory`
logger) alongside the agent's own tool choice (`app.agents.tool_runner`
logger) — see section 14 for a real captured trace of this exact
sequence.

---

## 6. Retrieval-Augmented Search (RAG)

This is the "R" in RAG: `search_providers` retrieves the real providers
whose actual profiles are most *semantically* relevant to what the
customer described — not only the ones whose `category`/`district`
field happens to string-match exactly.

**Retrieval** (`app/rag/provider_index.py`) is fully separate from
**generation** (the existing `recommend_providers` tool / LLM ranking
chain, section 5) — retrieval decides *which real providers are in
play*; generation decides *how to order and explain them*.
`recommend_providers` didn't need a single line changed: it already
only ever reads from `context["providers"]` and always re-resolves the
real record by index, so it doesn't know or care whether that list came
from semantic retrieval or the old exact-match fallback.

### How it works

1. **Index build** (lazy, on first use, then auto-refreshed every 10
   minutes — `INDEX_TTL_SECONDS`): fetch every non-blocked provider via
   `backend_client.search_providers(service="", location="")` (the existing backend
   regex already treats empty strings as "match everything" — no new
   backend endpoint needed), build one text string per provider from
   fields that actually exist on the `User` model — name, `category`,
   `city`/`district`, `rating`, `reviews` (count), `description` — and
   embed all of them with [fastembed](https://github.com/qdrant/fastembed)'s
   `BAAI/bge-small-en-v1.5` model (384-dim, ONNX, no PyTorch/GPU, ~130MB
   one-time download). The resulting vectors are held as one NumPy array
   in memory.
2. **Query time**: `search_providers` builds a query from
   `"{service} in {location}. Customer request: {raw user message}"`,
   embeds it with the same model, and computes cosine similarity against
   every indexed provider — brute-force, since a provider catalogue of
   dozens-to-low-hundreds doesn't need an approximate/indexed vector
   database; the search itself is sub-millisecond once the model is
   loaded.
3. Results below `MIN_SIMILARITY` are dropped, and the top `k=5` of what
   remains are returned as real, unmodified provider dicts — the LLM
   never sees or produces the provider records themselves at any point
   in this path.

Verified live against WedaHub's real provider data — a query with **zero
literal keyword overlap** with any provider's description:

> *"my lights keep flickering and the fuse box smells burnt, I am in
> Matara"*

correctly retrieved and ranked real electricians (0.60–0.70 similarity)
by matching the *meaning* of their technical descriptions ("ground-fault
tracing", "GFCI/AFCI arc-fault protection", "fault-finding using
multimeters...") — text that shares no words with the query at all — and
correctly ranked a plumber in the exact right city *lower* than
electricians in nearby cities, because the retrieval is about relevance
to the request, not just location.

### Choosing the similarity threshold

`MIN_SIMILARITY = 0.55` isn't a guess — it's calibrated against two real
measurements on WedaHub's actual (small) provider catalogue:

| Query | Real match? | Top similarity |
|---|---|---|
| *"my lights keep flickering..."* | Yes (real electricians) | 0.64–0.70 |
| *"Wedding Photography"* (a category the catalogue has none of, paired with a made-up city so an exact city-name match can't inflate the score) | No | 0.50 |

0.55 sits cleanly between those two measurements. One honest limitation
surfaced while calibrating this: every provider document shares the
same templated phrases (`"Category: ..."`, `"Located in ..."`,
`"Rated N from M reviews"`), and a real city name repeated in both the
query and a provider's profile can inflate similarity regardless of
whether the *service* matches — e.g. `"Wedding Photography in Kandy"`
scores a real Kandy-based electrician at 0.62, well above the threshold,
purely on the city-name coincidence. This is a genuine, known limitation
of single-vector whole-profile embedding (not something split by field),
documented rather than hidden — see "Known Limitations" below for the
straightforward way to tighten this further.

### Fallback path

If `fastembed` can't load the model (not installed, or no network for
the first-time download) or the provider fetch fails, `semantic_search()`
returns `None`, and `search_providers` falls back to the exact/regex
`backend_client.search_providers()` path used before this feature existed — the tool
result string even says which path ran (`retrieval=semantic` vs.
`retrieval=keyword_fallback`), and it's logged either way. The chat flow
degrades; it never breaks.

### Keeping the index fresh

- **Automatic**: rebuilt lazily whenever it's more than `INDEX_TTL_SECONDS`
  (10 minutes) old — new/edited providers show up within that window
  with zero manual steps.
- **Manual**: `POST /rag/refresh` forces an immediate rebuild (e.g. right
  after a bulk data change); `GET /rag/status` reports whether the
  embedder loaded, how many providers are indexed, and how old the index
  is. Neither is bridged through Express or called by the frontend —
  they're operational endpoints, not part of the chat UX.

### Logging

```
RAG embedder loaded (BAAI/bge-small-en-v1.5) in 0.5s
RAG index built: 7 providers indexed in 0.19s
RAG retrieval query='Electrician in Matara. Customer request: my lights keep flickering and the fuse box smells burnt, I am in Matara' top_k=5 matches=[('Kapila Perera', 0.703), ('Supun Udara', 0.678), ('Piyal Vikum', 0.672), ('Prabath Kusum', 0.642), ('Kasun Fdo', 0.64)]
TOOL RESULT search_providers -> 5 provider(s) via semantic
```

---

## 7. Booking Flow

Once a provider is selected, keep that provider's service category throughout
the booking. Later descriptions only fill in the work details: door repair for
a selected Electrician stays an Electrician booking, including electrical doors.
The graph enforces this even if the extraction model proposes another category.
Before provider selection, a service change starts a new search. Semantic results
are filtered by provider category before limiting the result count.

The chat JSON/SSE `booking` field contains a saved booking only when that turn
successfully creates it. Draft selections and confirmation requests return
`booking: null`, so the frontend cannot show an early "Booking Created" card.

1. User replies `"Book 1"` (etc.) after a search → `booking_agent_node.py`
   maps the number to a recommended provider and seeds `state["booking"]`
   with `provider_id` / `provider_name` / `service` / `city`.
2. On following turns, the same node copies `date` / `description` out of
   whatever the requirements extractor just found in the latest message,
   and asks for whichever one is still missing.
3. Once provider + service + city + date + description are all present,
   `booking_confirmation_node.py` shows a summary and waits for an exact
   "yes"/"no" reply.
4. On "yes", `booking_create_node.py` runs the tool-calling agent
   described in section 5 above, which calls the `create_booking` tool →
   `backend_client.create_booking()` → `POST {BACKEND_URL}/api/bookings/ai`
   on the Express backend, which parses the natural-language date
   server-side and creates a real `Booking` document
   (`status: "pending"`, `source: "ai"`).
5. The Express response is reshaped into a flat dict and stored in
   `state["booking"]` / `state["booking_result"]`, which is what
   `response_node.py` formats into the final "✅ Booking Created
   Successfully!" message, and what's returned to the frontend as the
   `booking` field (rendered as a `ChatBookingCard`).
6. Asking **"booking status"** afterwards runs `booking_status_node.py`'s
   tool-calling agent, which calls `get_booking_status` →
   `GET /api/bookings/:id` and reports its live status.

**Login is required to book.** If there's no `customerId` when the planner
detects a `"Book N"` intent, the response is "🔒 Please login first to
create a booking."

---

## 8. Memory Handling

`app/memory/conversation_memory.py::ConversationMemory` is a plain
in-process Python dictionary (`defaultdict(dict)`), keyed by `session_id`
(which falls back to `customerId`, then `"guest"`).

- **What's stored (temporarily):** the entire conversation state for that
  session — extracted requirements, the in-progress booking, search
  results, recommendations, the last booking result — round-tripped on
  every turn (load → merge new message → run graph → save).
- **What's *not* stored permanently:** everything. There is no database or
  file backing this. Restarting the process clears all conversations for
  all users. It is not shared across multiple worker processes.
- **Clearing it:** `POST /chat/reset` (bridged from the frontend's "New
  Chat" button via `POST /api/ai/chat/reset` on Express) clears one
  session's entry.

`experiments/legacy/database.py` holds a working MongoDB client that is **not**
currently used for memory or anything else — see
[`experiments/legacy/README.md`](experiments/legacy/README.md).

---

## 9. API Endpoints

This service only exposes what's listed below — nothing else.

| Method | Path | Request | Response |
|---|---|---|---|
| GET | `/` | – | `{"message": "WedaHub AI Service Running"}` |
| POST | `/chat` | `{ message, customerId?, sessionId? }` | `{ response, recommendations, booking }` (one JSON blob) |
| POST | `/chat/stream` | same body as `/chat` | Server-Sent-Events stream — see section 13 |
| POST | `/chat/reset` | `{ customerId?, sessionId? }` | `{ message: "chat reset", sessionId }` |
| GET | `/rag/status` | – | `{ available, provider_count, built_at, age_seconds, model_name }` |
| POST | `/rag/refresh` | – | `{ ok, provider_count, built_at }` — forces an immediate index rebuild, see section 6 |

`/rag/*` is operational only — not bridged through Express, not called
by the frontend.

Bridged through the Express backend as:

| Express route | Proxies to |
|---|---|
| `POST /api/ai/chat` | this service's `POST /chat` |
| `POST /api/ai/chat/stream` | this service's `POST /chat/stream`, piped through without buffering |
| `POST /api/ai/chat/reset` | this service's `POST /chat/reset` |

There used to also be `POST /api/ai/booking`, `GET /api/ai/booking/:id`,
and `POST /api/ai/recommend` on the Express side, proxying to matching
routes on this service — those routes never existed here, and calling
them was never reachable from the actual chat UI (booking is created and
checked conversationally through `/chat` instead). They've been removed
from the frontend and Express rather than left as dead, broken endpoints.

---

## 10. Setup Instructions

**Prerequisites:** Python `>=3.10` (pinned via `.python-version`). Managed
with [`uv`](https://github.com/astral-sh/uv) (`pyproject.toml` + `uv.lock`).

```bash
cd ai-service
uv sync

uv run uvicorn main:app --reload --port 8000
```

For a new checkout, copy `.env.example` to `.env` and configure your Groq key
and backend URLs. Keep an existing `.env` when updating the project.

No new environment variable or API key is needed for semantic
retrieval — `fastembed` runs the embedding model fully locally. The
*first* call downloads the model (~130MB, one-time, cached under your
user profile); every call after that is fast and fully offline.

The Express backend expects this service at `http://localhost:8000` by
default (override with its own `AI_SERVICE_URL` env var). The frontend
talks to Express, never to this service directly — you need the Express
backend (for the `/api/ai/*` bridge and the `/api/bookings/*`,
`/api/providers/search` routes this service calls back into) and, for
local CORS to work, the frontend running at `http://localhost:5173` (the
only origin `main.py` currently allows).

---

## 11. Environment Variables

Set in `ai-service/.env`:

| Variable | Used by | Notes |
|---|---|---|
| `GROQ_API_KEY` | `app/core/llm.py` | Required — the Groq LLM API key |
| `MODEL_NAME` | `app/core/llm.py` | Defaults to `llama-3.1-8b-instant` if unset |
| `EXPRESS_API` | `app/clients/backend_client.py`, `app/rag/provider_index.py` (index build fetches providers through the same tool) | Base URL for provider search, e.g. `http://localhost:3000/api` |
| `BACKEND_URL` | `app/clients/backend_client.py` | Base URL for booking creation; defaults to `http://localhost:3000` if unset |
| `MONGO_URI` / `MONGODB_URI` | `experiments/legacy/database.py` (unused by the live app) | Either name is accepted |
| `DB_NAME` | `experiments/legacy/database.py` (unused by the live app) | — |
| `LOG_LEVEL` | `app/core/logging_config.py` | `INFO` by default; set to `DEBUG` to see full state/payload dumps |
| `LANGCHAIN_TRACING_V2` | Read directly by LangChain, not by this repo's code | Set to `true` to turn on LangSmith tracing — see section 14 |
| `LANGCHAIN_API_KEY` | Read directly by LangChain | Your LangSmith API key |
| `LANGCHAIN_PROJECT` | Read directly by LangChain | Defaults to `wedahub-ai-service` if unset |

Semantic retrieval (section 6) needs none of the above — no new key.

---

## 12. Logging

Every module logs through the standard `logging` module instead of
`print()` — `app/core/logging_config.py::configure_logging()` sets the
format and level once, called at the top of `main.py`.

- **INFO** (the default) — one line per meaningful step: a node ran, a
  decision was made, an HTTP request went out, a booking was created.
- **DEBUG** (`LOG_LEVEL=DEBUG`) — full state/payload dumps, for when you
  need to see everything a node received.
- **WARNING** — recoverable oddities (an unknown planner action, a booking
  status lookup that came back empty).
- **ERROR / EXCEPTION** — a request-level failure; exception logs include
  the full traceback automatically.

## 13. Streaming

`/chat/stream` replaces the old client-side "fake typing" — the frontend
used to get one complete JSON response and reveal it with hand-tuned
`setTimeout` delays per character. It now reads a real Server-Sent-Events
stream from the network as it arrives.

**Being precise about what this is:** `response_node.py` builds the final
reply with plain Python string formatting — it is not a live LLM
generation call, so there's no token-by-token stream to relay for the
reply text itself (any LLM calls inside `requirements`/`planner`/
`recommend` have already finished by the time this text exists). What
`/chat/stream` does is take that already-known text and send it over a
real HTTP stream in several small chunks with **no artificial delay**
between them — genuine network streaming of a known string, not
token-by-token generation. It's the closest real streaming this
architecture supports without inventing a new LLM-based response step.

Wire format (newline-delimited SSE frames):
```
data: {"type": "chunk", "text": "..."}\n\n
...
data: {"type": "done", "recommendations": [...], "booking": {...} | null}\n\n
```

Express (`aiController.chatStream`) pipes the upstream stream straight
through with no buffering. The frontend (`aiChatService.js::streamMessage`)
reads it with `fetch` + `response.body.getReader()` — not axios, whose
browser adapter buffers the whole response before resolving.

## 14. Tracing / Observability

Two layers, both optional-by-default and additive:

- **LangSmith** (for the actual LLM calls: requirements extraction,
  planner fallback, recommendation ranking, and the tool-calling agent's
  own `.bind_tools()` calls) — needs zero code. LangChain reads
  `LANGCHAIN_TRACING_V2` / `LANGCHAIN_API_KEY` / `LANGCHAIN_PROJECT`
  straight from the environment for every `ChatGroq` / `ChatPromptTemplate`
  / `.with_structured_output()` / `.bind_tools()` call already in this
  codebase. Set those three env vars and every LLM call, including which
  tools were offered and which one it picked, automatically appears in
  your LangSmith project — nothing else to wire up.
- **`app/core/tracing.py::trace_node`** — LangSmith only sees LangChain
  objects, so it can't see the plain-Python graph nodes (the planner's
  deterministic branches, booking slot-filling, the response formatter).
  `trace_node` is a decorator applied to every node registered in
  `app/graph/workflow.py` (`requirement_node`, `planner_node`,
  `search_agent_node`, `booking_agent_node`, `booking_confirmation_node`,
  `booking_create_node`, `booking_status_node`, `response_node`). It logs
  one line when a node starts and one when it finishes (or raises), with
  the session id, elapsed time, and the resulting planner action.

Combined with the tool-call logging in section 5, one real request
produces a trace like this (captured live, lightly trimmed):

```
TRACE start node=search_agent_node session=X
agent chose tool=search_providers args={'service': 'Electrician', 'location': 'Kandy'}
TOOL CALL search_providers(service='Electrician', location='Kandy')
TOOL RESULT search_providers -> 1 provider(s)
agent chose tool=recommend_providers args={}
TOOL CALL recommend_providers (providers_available=1)
TOOL RESULT recommend_providers -> ranked 1 of 1
agent stopped after 2 tool call(s), no further calls requested
TRACE end   node=search_agent_node session=X elapsed_ms=2377.1 next_action=search_services
```

That's the entire agentic decision — which tool, with what arguments, in
what order, and why it stopped — reconstructable from logs alone, with
or without LangSmith configured.

## Automated tests and manual checks

Run the automated suite from `ai-service/`:

```bash
uv run python -m unittest discover -s tests -v
```

These tests mock the LLM and Express backend. They exercise real graph routing,
booking confirmation/cancellation, tool isolation, backend request contracts,
conversation memory, and chat/SSE/reset endpoints. They never create a live booking.

Run deterministic evaluation cases without external services:

```bash
uv run python -m evals.run_eval --offline
```

Manual checks are explicit module commands, for example:

```bash
uv run python -m scripts.check_planner
uv run python -m scripts.check_llm
uv run python -m scripts.check_search
```

The LLM/backend checks require `.env` and the relevant external services. The
manual booking/chat checks may create real bookings when confirmed. Dormant
MongoDB and alternate booking checks live under `experiments/manual_checks/`.

## 15. Evaluation Harness

```bash
cd ai-service
uv run python -m evals.run_eval
```

Cases live in `evals/dataset.py`, results are printed by
`evals/run_eval.py`. Five kinds of coverage:

- **Planner decisions** (`PLANNER_CASES`) and **booking slot-filling**
  (`BOOKING_AGENT_CASES`) — deterministic Python logic, no LLM, no
  network. Checked with hard assertions; always run.
- **Requirement extraction** (`REQUIREMENT_CASES`) and **recommendation
  ranking** (`RECOMMENDATION_LIVE_CASE`) — real LLM calls. Checked with
  fuzzy substring scoring (a case passes at ≥75% of its expected fields
  matching, since LLM phrasing varies slightly run to run).
- **Provider search** (`SEARCH_LIVE_CASE`) — a real HTTP call to the
  Express backend.
- **The tool-calling agent nodes themselves** — `search_agent_node`,
  `booking_create_node` and `booking_status_node`, run end to end. The
  booking-creation case specifically verifies the agent calls
  `create_booking` but the tool *refuses* an incomplete booking before
  any HTTP call is made, so this case can never create a real booking no
  matter how many times the suite runs.
- **Semantic retrieval** (`PROVIDER_TEXT_CASE`, deterministic;
  `SEMANTIC_SEARCH_LIVE_CASE`, real embedding model + backend) — the
  live case specifically requires a *non-empty* result for a query with
  zero keyword overlap with the expected match's description, so an
  empty/unavailable result correctly fails the case instead of silently
  passing.

Anything that needs the LLM, the backend, or the embedding model and
can't reach it is reported as **SKIP**, not **FAIL** — the harness stays
runnable with no `GROQ_API_KEY` or backend running at all (you'll just
see the deterministic cases run). No case creates a real booking, so
running the suite never leaves side effects in the database.

Exit code is `1` if anything hard-`FAIL`s, `0` otherwise (skips don't
affect it) — usable as a CI gate.

---

## 16. Known Limitations

- Conversation memory is in-process only — no persistence, no expiry, not
  safe across multiple workers (see section 8).
- The `/chat/stream` endpoint streams an already-fully-computed string,
  not live LLM tokens — see section 13 for exactly what that means.
- The tool-calling agent nodes (section 5) are each bound to only 1–2
  tools and given a directive system prompt telling them what to do —
  this is real tool-calling machinery, but deliberately bounded for
  reliability rather than a fully open-ended agent. See section 5 for why.
- Semantic retrieval (section 6) embeds each provider's *entire* profile
  as one vector rather than separate fields — a real city name repeated
  in both the query and a provider's profile can inflate similarity
  regardless of whether the service category matches. Splitting the
  index into separate service/location/description vectors (and
  weighting them independently) would fix this; not done here to keep
  the index a single, simple array. The provider catalogue used for
  calibration is also small (single digits), so `MIN_SIMILARITY` may
  need re-tuning as real data grows — `GET /rag/status` plus the
  eval harness's `rag` cases are the fastest way to check.
- The in-memory vector index is per-process and rebuilt from scratch on
  restart (a few hundred milliseconds for the current catalogue size) —
  fine at this scale, would need an actual vector store if the provider
  catalogue grew into the tens of thousands.
- `trace_node` gives structured logs, not a queryable trace UI — for that,
  configure LangSmith (section 14).
- CORS in `main.py` only allows `http://localhost:5173`.
- A few alternate/earlier implementations of the booking flow exist but
  are intentionally unwired — see [`experiments/legacy/README.md`](experiments/legacy/README.md).
