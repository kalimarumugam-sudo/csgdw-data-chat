from __future__ import annotations

from os import getenv
from typing import Iterable, List, Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LlmClient:
    def __init__(self, model: str = "gpt-4") -> None:
        api_key = getenv("OPENAI_API_KEY")
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def stream(self, messages: List[Dict[str, str]]):
        return self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            stream=True,
        )


