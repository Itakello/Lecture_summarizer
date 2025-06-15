import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openai import OpenAI

import config

from .chunk import Chunk
from .recordings import Language


@dataclass
class ChatGPTUtils:
    model: str
    client: OpenAI = field(default=OpenAI(api_key=config.OPENAI_API_KEY), init=False)
    prompts_path: Path = field(default=Path("prompts"), init=False)

    # ------------------------------------------------------------------
    #  Constants & helpers
    # ------------------------------------------------------------------
    SCHEMA: dict[str, Any] = field(
        default_factory=lambda: {
            "title": {"type": "string"},
            "summary": {"type": "string"},
            "main_points": {
                "type": "array",
                "items": {"type": "string"},
            },
            "follow_up": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        init=False,
        repr=False,
    )

    temperature: float = field(default=config.TEMPERATURE, init=False)

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------

    def _get_structured_response(
        self,
        sys_prompt: str | None,
        user_prompt: str | None,
        use_web_search: bool = False,
    ) -> dict[str, Any]:
        """Wrapper around OpenAI Responses API returning structured JSON."""
        from openai.types.beta.responses import (
            ResponseTextConfigParam,
        )  # type: ignore

        # Build messages list
        messages = []
        if sys_prompt:
            messages.append({"role": "system", "content": sys_prompt})
        if user_prompt:
            messages.append({"role": "user", "content": user_prompt})
        if not messages:
            raise ValueError(
                "At least one of sys_prompt or user_prompt must be provided"
            )

        text_config: ResponseTextConfigParam = {
            "format": {
                "type": "json_schema",
                "name": "structured_response",
                "strict": True,
                "schema": self.SCHEMA,
            }
        }

        response = self.client.responses.create(
            input=messages,
            model=self.model,
            text=text_config,
            temperature=self.temperature,
        )

        if response.error:
            raise ValueError(f"API Error: {response.error.message}")

        return json.loads(response.output_text) if response.output_text else {}

    def get_additional_info(self, chunk_str: str, language: Language) -> Chunk:
        content, prompt = self._create_content_and_prompt(chunk_str, language)
        parsed_res = self._get_structured_response(content, prompt)
        return self._create_chunk(chunk_str, parsed_res)

    def _create_chunk(self, transcription: str, parsed_res: dict) -> Chunk:
        return Chunk(
            parsed_res["title"],
            transcription,
            parsed_res["summary"],
            parsed_res["main_points"],
            parsed_res["follow_up"],
        )

    def _create_content_and_prompt(
        self, transcription: str, language: Language
    ) -> tuple[str, str]:
        # Read single English prompt file which contains placeholders.
        prompt_template = self.read_prompt_from_file("prompt_english.txt")
        content = self.read_prompt_from_file("content_english.txt")

        prompt = prompt_template.format(
            transcription=transcription, output_language=config.output_language()
        )
        return content, prompt

    def _create_content_and_prompt_json_error(
        self, json_content: str, error: str
    ) -> tuple[str, str]:
        prompt_filename = "prompt_json_error.txt"
        content_filename = "content_english.txt"

        prompt = self.read_prompt_from_file(prompt_filename).format(
            error=error, json=json_content
        )
        content = self.read_prompt_from_file(content_filename)
        return content, prompt

    def read_prompt_from_file(self, filename: str) -> str:
        file_path = self.prompts_path / filename
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
