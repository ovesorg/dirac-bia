# ADR: Dirac-BIA Migration From Simple RAG to Scalable BI Agent Stack

Source note incorporated on 2026-05-04 from `docs/notes/initial-stack-proposals.md`.

## Status

Proposed

## Context

OVES currently operates a simple RAG chatbot with:

- Document-based retrieval
- Single LLM interaction
- Limited integration with business systems
- Minimal session memory and governance

This setup is useful but insufficient for:

- Multi-source intelligence (Odoo, Teams, IoT, Social)
- Scalable architecture
- Structured business decision support
- Workflow automation

The proposed modular stack includes:

- Source gateways (Teams, Odoo, Social, etc.)
- LLM gateway (model-agnostic)
- Redis (session + state)
- Webhooks (event-driven updates)
- Scraping (targeted ingestion)
- Vector DB (semantic search)
- Social media dialog integration

## Decision

Adopt a modular, agent-oriented architecture called `Dirac-BIA`, with the following principles.

### Separate Concerns

| Layer | Responsibility |
| --- | --- |
| Source Gateways | Controlled access to external systems |
| Vector DB | Semantic document retrieval |
| LLM Gateway | Model abstraction and routing |
| Redis | Session and short-term state only |
| Business Systems | Remain source of truth (Odoo, ABS, IoT) |
| Orchestration | Event and workflow handling (webhooks, n8n) |

### RAG Is One Component

RAG remains in scope for:

- Documentation
- Knowledge retrieval

Dirac-BIA expands beyond RAG to include:

- Live data queries
- KPI evaluation
- Structured outputs such as alerts and actions

### LLM Gateway

All model access goes through a unified API:

- Enables switching between models
- Supports task-based routing
- Avoids vendor lock-in

### Redis Usage

Redis is proposed for:

- Session memory
- Temporary conversation context
- Caching
- Event state

Redis is not proposed for:

- Long-term knowledge
- Business records
- Audit logs

### Event-Driven Updates

Updates should be event-driven:

- Content updates trigger re-indexing
- System events trigger workflows
- Social messages trigger dialogs

Queues and workflows should be used to avoid direct processing.

### Controlled Scraping

Scraping is allowed for:

- Known, trusted, targeted sources

Scraping is not a primary ingestion method.

### Multi-Channel Interaction

Dirac-BIA is expected to support:

- Internal users (Teams)
- External users (web, social media)

All interactions go through the same core agent logic.

## Simplified Target Architecture

```text
Users (Teams / Web / Social)
        |
    Dirac-BIA API
        |
    Agent Layer
   /    |    \
RAG   DTO APIs   Tools
Docs  Odoo/ABS   Scraping / Queries
        |
   LLM Gateway
        |
 Vector DB + Redis
        |
 Webhooks / n8n
```

## Placeholder Follow-Up Detail

Placeholder: detailed contracts for source gateways, DTO APIs, workflow orchestration, and social channel integrations are not specified in the source note.
