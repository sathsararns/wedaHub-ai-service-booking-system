# Legacy / Experimental Code

These files are **not imported by anything in `main.py` / `app/graph/workflow.py`**.
They are kept (instead of deleted outright) because each represents a
complete, coherent alternative approach that could be revived later —
unlike plain dead duplicates, which were removed instead of moved here.

None of this code runs in the live service. If you're tracing the actual
request flow, start at `main.py` and `app/graph/workflow.py` — nothing here
is on that path.

## `booking_agent.py` + `booking_prompt.py` + `booking_request.py`

An **LLM-based** alternative to the currently-active booking field
extractor. The live workflow (`app/graph/nodes/booking_agent_node.py`) reuses the
general-purpose `requirements_agent` plus plain regex (`"Book N"`) instead.
This trio shows a different design: a dedicated prompt (`booking_prompt.py`)
and a dedicated Pydantic schema (`booking_request.py`, `BookingRequest`)
purpose-built for turning a booking-related message into structured fields
via `.with_structured_output()`. Worth revisiting if the current
regex+reused-extractor approach in `booking_agent_node.py` needs to get
smarter about parsing booking-specific phrasing.

## `booking_node.py`

A complete, self-contained booking-creation node — validates required
fields, calls `backend_client.create_booking(...)`, and stores the raw response
into `state["booking_result"]` as `{"message": ..., "booking": {...}}`
(the shape the Express `/api/bookings/ai` endpoint actually returns).

This is **not** the node wired into the graph — `app/graph/nodes/booking_create_node.py`
is, and it reshapes the result into a flat dict instead. The
`booking_status_tool.py` bug that was just fixed existed because
`booking_status_tool.py` was written expecting *this* file's nested shape,
while `booking_create_node.py` (the one actually running) produces the flat
one.

## `planner_prompt.py`

A full, detailed LLM prompt for the planner (JSON-only, with worked
examples for every action). The live planner (`app/agents/planner_agent.py`)
uses a shorter inline prompt and only falls back to the LLM after a series
of deterministic keyword/regex checks. This file is the "prompt-only"
version of that same idea, kept in case the deterministic-first approach
needs to be replaced with something closer to this.

## `database.py`

A working Motor (async MongoDB) client (`db = client[DB_NAME]`), pointed at
the same database the Node/Express backend uses. It is not imported
anywhere — the AI service currently never talks to MongoDB directly; every
read/write goes through the Express backend's REST API instead
(`app/clients/backend_client.py`, `app/clients/backend_client.py`,
`app/services/booking_status_service.py`). Kept because a future feature
(e.g. persisting conversation memory, or reading provider data directly for
a RAG-style search) would likely start from this file.
