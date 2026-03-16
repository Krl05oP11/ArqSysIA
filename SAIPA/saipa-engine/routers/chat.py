"""
Chat router — Fase 1: RAG pipeline with LangChain + ChromaDB + Ollama.
"""
import logging

from fastapi import APIRouter, Depends
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel

from config import get_settings
from rag.retriever import retrieve
from routers.health import _verify_token

log = logging.getLogger("saipa_engine.routers.chat")

router = APIRouter()

SYSTEM_PROMPT = (
    "Eres SAIPA, un asistente pedagógico inteligente diseñado para ayudar a estudiantes "
    "universitarios. Responde siempre en español de manera clara, amable y educativa. "
    "Tu rol es el de un tutor que guía al estudiante hacia la comprensión, no simplemente "
    "le da las respuestas. Si tienes información del curso en el contexto a continuación, "
    "úsala para fundamentar tus respuestas.\n\n"
    "{context}"
)


class ChatRequest(BaseModel):
    course_id: int
    user_id: int
    message: str
    session_id: int | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: int | None = None
    sources: list[str] = []


@router.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(
    req: ChatRequest,
    token: None = Depends(_verify_token),
) -> ChatResponse:
    """
    Receives a student message and returns the assistant's reply.
    Uses RAG: ChromaDB retrieval + Ollama LLM.
    """
    settings = get_settings()

    # 1. Retrieve relevant chunks from ChromaDB
    docs = retrieve(req.message, req.course_id, top_k=5)
    sources = list({d["source"] for d in docs})

    if docs:
        context_text = "Contexto del curso:\n" + "\n---\n".join(
            f"[{d['source']}]: {d['content']}" for d in docs
        )
    else:
        context_text = ""

    # 2. Build prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ])

    # 3. Call Ollama
    llm = ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=0.3,
        request_timeout=float(settings.ollama_timeout),
    )

    chain = prompt | llm
    response = await chain.ainvoke({
        "context": context_text,
        "question": req.message,
    })

    reply = response.content if hasattr(response, "content") else str(response)
    log.info(
        "Chat course=%d sources=%d reply_len=%d",
        req.course_id, len(docs), len(reply),
    )

    return ChatResponse(reply=reply, session_id=req.session_id, sources=sources)
