# Runtime Adapters

## Goal

Preserve the useful parts of backend-bound search workflows without preserving any hard dependency on a specific API vendor, crawler service, or hosted search backend.

Keep the method. Replace the backend.
Use `hellosearch` as a pure skill layered on top of host-native search capability.

## Core layers

Split the system into three layers:

1. Skill layer
   - Decide when to search
   - Plan search rounds
   - Enforce evidence discipline
   - Shape the final answer

2. Runtime layer
   - Discover available capabilities in the current environment
   - Route each operation to the best available backend
   - Normalize outputs into one internal shape

3. Backend adapter layer
   - Implement concrete `search`, `fetch`, and optional `map`
   - Wrap host-native tools only

## Adapter contract

Use a common internal contract even if the host APIs differ:

- `search(query, options) -> { content, sources, raw }`
- `fetch(url, options) -> { content, metadata, raw }`
- `map(url, options) -> { urls, metadata, raw }`
- `capabilities() -> { search, fetch, map, citations, recency }`

Normalize source items to:

- `title`
- `url`
- `snippet`
- `provider`
- `published_at`
- `retrieved_at`

## Routing order

Choose backends in this order:

1. Host-native live web tools
2. Host-native page open or fetch tools

Do not require extra backend setup just to make the skill usable.

## What to keep from earlier search workflows

- Query framing and multi-round planning
- Source extraction and normalization
- Date awareness and exact-time answering
- Response parsing discipline
- Optional site-mapping before deep page fetches
- Search-first, fetch-second, verify-third workflow

## What to remove from backend-bound implementations

- Mandatory vendor-specific API URLs and API keys
- Mandatory provider-specific client construction
- Assumption that one `chat/completions` endpoint implies real web access
- Assumption that a dedicated crawler or search SaaS always exists
- Assumption that the skill should ship with extra transport or backend layers

## Minimum viable implementation

Build the first usable runtime with:

1. A host capability detector
2. A native-search adapter
3. A native-fetch adapter
4. A normalized source model
5. A citation-block parser for mixed answer text
6. A graceful "no live web available" path
