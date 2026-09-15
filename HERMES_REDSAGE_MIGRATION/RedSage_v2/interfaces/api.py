"""Minimal FastAPI server exposing KB search and source listing.

Run from the project root:
    uvicorn interfaces.api:app --host 127.0.0.1 --port 8000
or: python -m interfaces.api
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from core.kb_engine import KBEngine

app = FastAPI(
    title="RedSage v2",
    version="2.0.0",
    description="Decoupled RedSage knowledge base API",
)
engine = KBEngine()


class AskRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=25)


class CitationResponse(BaseModel):
    chunk_id: str
    title: str
    source: str
    url: str
    text: str
    score: float


class AskResponse(BaseModel):
    query: str
    answer: str
    citations: list[CitationResponse]


@app.get("/api/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "embedding_provider": engine.embedder.provider_name,
        "active_collection": engine.collection_name,
    }


@app.post("/api/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        citations = engine.search(request.query, top_k=request.top_k)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"KB search failed: {error}") from error
    return AskResponse(
        query=request.query,
        answer=engine.grounded_answer(request.query, citations),
        citations=[
            CitationResponse(
                chunk_id=citation.chunk_id,
                title=citation.title,
                source=citation.source,
                url=citation.url,
                text=citation.text,
                score=round(citation.score, 4),
            )
            for citation in citations
        ],
    )


@app.get("/api/kb/sources")
def kb_sources() -> list[dict[str, object]]:
    return engine.list_sources()


@app.get("/api/kb/stats")
def kb_stats() -> list[dict[str, object]]:
    return engine.collection_stats()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
