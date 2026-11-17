# S3 — MCP Client (LangGraph, Ollama)

LangGraph agent that connects to the MCP server from `[s3]-[mcp-server]` via
`langchain-mcp-adapters` (stdio transport). Wraps all six MCP tools as LangChain tools.

Shows the full end-to-end: Ollama model → LangGraph loop → MCP stdio → synthetic tool execution.

## Status

`TODO` — implement `agent.py` (requires s3-mcp-server running)
