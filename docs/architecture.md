# FinPilot AI — System Architecture & Design Specification

## 1. Executive Summary & Product Vision
**FinPilot AI** is a production-grade personal financial intelligence copilot built for technical interview demonstration in high-impact AI Engineer / Forward Deployed Engineer (FDE) roles. Rather than presenting generic LLM wrappers or synthetic mockups, FinPilot AI combines **deterministic financial calculations**, **domain-constrained tool calling**, **hybrid semantic & lexical document RAG**, and **multi-factor statistical/machine-learning anomaly detection** over verified relational financial ledgers.

---

## 2. Architecture Diagram

```mermaid
flowchart TD
    subgraph Client["Frontend Layer (Next.js 16 + React 19)"]
        UI["Tailwind CSS + Recharts UI"]
        State["Client State & Token Storage"]
        Views["Dashboard | AI Copilot | Ledger | Budgets | Document Center | Telemetry"]
    end

    subgraph Gateway["API & Security Boundary (FastAPI)"]
        Auth["JWT Authentication & RBAC"]
        RateLimit["Rate Limiting & CORS Middleware"]
        TelemetryMid["Live Telemetry & Latency Tracker"]
        Router["Deterministic Request Router & Safety Filter"]
    end

    subgraph Orchestration["AI & Tool Calling Layer"]
        Orchestrator["AI Orchestrator (Bound Step Loop)"]
        ToolRegistry["Typed Tool Registry (10 Tools)"]
        LLM["Model Provider Abstraction\n(Gemini / OpenAI / Deterministic Engine)"]
    end

    subgraph Engines["Core Financial Engines"]
        Math["Deterministic Financial Math\n(Decimal Reducing Balance EMI & DTI)"]
        Anomaly["Transaction Anomaly Detector\n(Isolation Forest + Category IQR)"]
        RAG["Hybrid RAG Engine\n(384-d Vector Cosine + Lexical Overlap)"]
    end

    subgraph Storage["Persistent Relational Storage"]
        DB[(PostgreSQL 16 / SQLite)]
        Tables["Users | Transactions | Categories | Budgets | Goals"]
        DocStore["Documents | Chunks (Embeddings)"]
        AuditLog["Audit Events | Operational Metrics | Eval Runs"]
    end

    UI -->|Bearer JWT HTTP Requests| Gateway
    Gateway --> Router
    Router -->|Safe Intent Dispatch| Orchestrator
    Router -->|Adversarial / Speculation| Gateway
    Orchestrator --> ToolRegistry
    ToolRegistry --> Math
    ToolRegistry --> Anomaly
    ToolRegistry --> RAG
    ToolRegistry --> Storage
    Math & Anomaly & RAG --> Storage
    Orchestrator --> LLM
    LLM --> UI
    Gateway --> TelemetryMid --> AuditLog
```

---

## 3. Component Interactions & Request Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Client
    participant API as FastAPI Gateway
    participant Sec as Security & Router
    participant Orch as AI Orchestrator
    participant Tool as Tool Registry
    participant Engine as Math & Anomaly & RAG
    participant DB as Relational Database
    participant LLM as Model Provider

    User->>API: POST /api/v1/chat (Prompt + Bearer Token)
    API->>Sec: Validate JWT & User Active Status
    Sec->>Sec: Inspect prompt for Prompt Injection & UNSUPPORTED advice
    alt Adversarial or Speculative Detected
        Sec-->>User: Refusal & Compliance Notice (Audit Logged)
    else Valid Intent
        Sec->>Orch: Dispatch (Intent, Sanitized Query, User ID)
        Orch->>Tool: Select and Execute Authorized Tool(s)
        Tool->>DB: Parameterized Query (Enforcing User Tenant ID)
        DB-->>Tool: Raw Verified Records
        Tool->>Engine: Run Deterministic Math / Anomaly / Hybrid Vector Scoring
        Engine-->>Tool: Verified Computation Result
        Tool-->>Orch: Tool Result Payload & Execution Latency
        Orch->>LLM: Synthesize Grounded Natural Language (Prompt + Tool Data)
        LLM-->>Orch: Grounded Explanation with Citations
        Orch->>DB: Persist User Message, Assistant Message, & Tool Provenance
        Orch-->>API: ChatResponse (Content, Tool Calls, Citations, Latency)
        API-->>User: Rendered Response with Markdown, Citations & Provenance
    end
```

---

## 4. End-to-End RAG Pipeline Architecture

1. **Ingestion & Validation**:
   - Files are validated against an allowed extension whitelist (`.pdf`, `.txt`, `.csv`) and a 10MB size cap.
   - Text is parsed using `pypdf` for PDFs, `csv.reader` for tabular ledgers, and UTF-8 stream normalization for TXT documents.
2. **Chunking & Page Preserving**:
   - Sliding window chunker (500 words chunk size, 100 words overlap).
   - Preserves source document metadata: `document_id`, `user_id`, `chunk_index`, and `page_number`.
3. **Embeddings & Vector Indexing**:
   - Normalized 384-dimensional dense vectors generated with sub-word character-3-gram and content-word hashing.
   - Fully supports Google Gemini `text-embedding-004` and OpenAI embeddings when API keys are configured.
4. **Hybrid Retrieval**:
   - Semantic Cosine Similarity ($0.5$ weight) + Normalized Lexical Term Match ($0.5$ weight).
   - Stopword filtering strips query conversational boilerplate.
   - Similarity threshold of `0.25` ensures relevant passages score `0.45 - 0.70+` while ungrounded/out-of-domain queries score `<0.22`, guaranteeing honest abstention rather than hallucination.
5. **Strict Tenant Isolation**:
   - Every database query explicitly filters `DocumentChunk.user_id == current_user.id` on the server before calculating similarity.

---

## 5. Technical Decision Records (TDR)

### TDR-001: Decimal Arithmetic vs Floating Point for Money
- **Decision**: All financial amounts in calculations use Python's `decimal.Decimal` with explicit `ROUND_HALF_UP` rounding.
- **Rationale**: Standard IEEE 754 floating-point arithmetic introduces cumulative representation errors (e.g. `0.1 + 0.2 != 0.3`) unacceptable in fintech ledgers and loan schedules.

### TDR-002: Dual-Mode Database Strategy (SQLite Dev / PostgreSQL pgvector Prod)
- **Decision**: SQLAlchemy ORM with universal JSON embedding storage in development and pgvector compatibility in production Docker Compose.
- **Rationale**: Allows 100% friction-free local execution without requiring a Docker daemon to be running, while fully supporting cloud PostgreSQL with pgvector for production deployments.

### TDR-003: Deterministic Request Routing Before Model Invocation
- **Decision**: Classify intent using regex patterns and deterministic heuristics before calling expensive LLMs.
- **Rationale**: Avoids unnecessary LLM token costs and multi-second latency for routine arithmetic, while instantly cutting off prompt injection attacks before they reach the model.
