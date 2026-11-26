# S3 — MCP Client (LangGraph, Ollama)

LangGraph agent that connects to the MCP server from `[s3]-[mcp-server]` via
`langchain-mcp-adapters` (stdio transport). Wraps all six MCP tools as LangChain tools.

Shows the full end-to-end: Ollama model → LangGraph loop → MCP stdio → synthetic tool execution.


## Step Diagram

```mermaid
flowchart LR
    A([P1 Alert]) --> B[LangGraph Agent]
    B --> C[langchain-mcp-adapters]
    C --> D[MCP stdio transport]
    D --> E[MCP Server
s3-mcp-server]
    E --> F[6 tools]
    F --> G([Root-cause report])

    style A fill:#666666,stroke:#fff,color:#fff
    style B fill:#4a7ab5,stroke:#fff,color:#fff
    style C fill:#2e8b6e,stroke:#fff,color:#fff
    style D fill:#2e8b6e,stroke:#fff,color:#fff
    style E fill:#4a7ab5,stroke:#fff,color:#fff
    style F fill:#2e8b6e,stroke:#fff,color:#fff
    style G fill:#666666,stroke:#fff,color:#fff
```

> LangGraph agent wraps the MCP server tools via langchain-mcp-adapters over stdio transport.

## Status

`TODO` — implement `agent.py` (requires s3-mcp-server running)
