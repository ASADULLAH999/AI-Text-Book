"""
LLM Service
Wraps OpenAI chat completions for RAG response generation.
"""

from typing import AsyncIterator, List, Dict, Any, Optional
import logging
from openai import AsyncOpenAI
from services.prompts.tone_modifiers import apply_tone_to_system_prompt, DEFAULT_TONE

logger = logging.getLogger(__name__)

# System prompts per mode
_BOOK_ONLY_SYSTEM_PROMPT = """You are a helpful textbook assistant. Your ONLY knowledge source is the textbook passages provided in the context below.

Rules you MUST follow:
1. Answer using ONLY information from the provided context passages.
2. Do not add any information from your own training knowledge.
3. Quote or closely paraphrase the source text to ensure accuracy.
4. If the context does not contain enough information to answer, say so clearly.
5. Keep your answer focused and directly responsive to the question.
6. Do not invent facts, statistics, or claims not present in the context."""

_SELECTED_TEXT_SYSTEM_PROMPT = """You are a helpful textbook assistant. Your ONLY knowledge source is the selected text passage provided below.

Rules you MUST follow:
1. Answer using ONLY the selected text passage — do not draw on other knowledge.
2. Quote or closely paraphrase the passage to ensure accuracy.
3. If the passage does not contain enough information, say so clearly.
4. Keep your answer focused on what the user highlighted."""

_GENERAL_KNOWLEDGE_SYSTEM_PROMPT = """You are a knowledgeable educational assistant. You may use your general knowledge to answer student questions.

When relevant textbook passages are provided, use them as helpful context, but do not restrict your answer to those passages only.
Always be accurate, pedagogically helpful, and clearly explain concepts."""

_CONTEXT_TEMPLATE = """## Textbook Context

{passages}

## Question
{query}

## Answer"""


def _build_context_passages(chunks: List[Dict[str, Any]]) -> str:
    """Format retrieved chunks into numbered context passages."""
    passages = []
    for i, chunk in enumerate(chunks, 1):
        text = chunk.get("text", "").strip()
        chapter = chunk.get("metadata", {}).get("chapter", chunk.get("chapter", ""))
        section = chunk.get("metadata", {}).get("section", chunk.get("section", ""))
        source = f"[{chapter}" + (f" — {section}" if section else "") + "]"
        passages.append(f"[{i}] {source}\n{text}")
    return "\n\n".join(passages)


class LLMService:
    """Generates answers using OpenAI chat completions with RAG context."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        max_tokens: int = 1024,
        temperature: float = 0.2,
    ):
        self._client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        logger.info(f"Initialized LLMService (model={model})")

    def _build_system_prompt(self, mode: str, tone: Optional[str]) -> str:
        if mode == "selected_text":
            base = _SELECTED_TEXT_SYSTEM_PROMPT
        elif mode == "general_knowledge":
            base = _GENERAL_KNOWLEDGE_SYSTEM_PROMPT
        else:
            base = _BOOK_ONLY_SYSTEM_PROMPT

        effective_tone = tone or DEFAULT_TONE.value
        return apply_tone_to_system_prompt(base, effective_tone)

    async def generate(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        mode: str = "book_only",
        tone: Optional[str] = None,
    ) -> str:
        """
        Generate a grounded answer from retrieved chunks.

        Returns the full response text.
        """
        system_prompt = self._build_system_prompt(mode, tone)
        passages = _build_context_passages(chunks)
        user_message = _CONTEXT_TEMPLATE.format(passages=passages, query=query)

        logger.debug(f"Calling OpenAI {self.model} for query: {query[:80]}...")
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        answer = response.choices[0].message.content or ""
        logger.info(f"LLM response generated ({len(answer)} chars)")
        return answer

    async def generate_stream(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        mode: str = "book_only",
        tone: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Stream response tokens as they are generated.

        Yields text delta strings.
        """
        system_prompt = self._build_system_prompt(mode, tone)
        passages = _build_context_passages(chunks)
        user_message = _CONTEXT_TEMPLATE.format(passages=passages, query=query)

        logger.debug(f"Streaming OpenAI {self.model} for query: {query[:80]}...")
        stream = await self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield delta


# Singleton
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create the singleton LLMService, loading config lazily."""
    global _llm_service
    if _llm_service is None:
        from config import get_settings
        s = get_settings()
        _llm_service = LLMService(
            api_key=s.openai.api_key,
            model=s.openai.chat_model,
        )
    return _llm_service
