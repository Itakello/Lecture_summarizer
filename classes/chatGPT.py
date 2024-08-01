import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

from openai import OpenAI

from .chunk import Chunk
from .recordings import Language


@dataclass
class ChatGPTUtils:
    model: str
    client: OpenAI = field(
        default=OpenAI(api_key=os.environ.get("OPENAI_API_KEY")), init=False
    )
    prompts_path: Path = field(default=Path("prompts"), init=False)

    def call_openai_api(self, content: str, prompt: str, retries: int = 0) -> dict:
        MAX_RETRIES = 5
        if retries > MAX_RETRIES:
            raise Exception("Reached maximum number of retries.")
        try:
            retries += 1
            response = self._invoke_prompt(content, prompt)
            parsed_res = json.loads(response)
        except json.decoder.JSONDecodeError as je:
            print(je)
            time.sleep(10)
            je_content, je_propmpt = self._create_content_and_prompt_json_error(
                response, je
            )
            response = self._invoke_prompt(je_content, je_propmpt)
            parsed_res = json.loads(response)
        except Exception as e:
            print(e)
            time.sleep(10)
            parsed_res = self.call_openai_api(content, prompt, retries)
        return parsed_res

    def get_additional_info(self, chunk_str: str, language: Language) -> Chunk:
        content, prompt = self._create_content_and_prompt(chunk_str, language)
        parsed_res = self.call_openai_api(content, prompt)
        chunk = self._create_chunk(chunk_str, parsed_res)
        return chunk

    def _create_chunk(self, transcription: str, parsed_res: dict) -> Chunk:
        return Chunk(
            parsed_res["title"],
            transcription,
            parsed_res["summary"],
            parsed_res["main_points"],
            parsed_res["follow_up"],
        )

    def _invoke_prompt(self, content: str, prompt: str, max_retries=3, delay=10) -> str:
        for retry in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": content},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                )

                return str(response.choices[0].message.content)
            except Exception:
                if retry < max_retries - 1:  # It's not the final retry
                    time.sleep(delay)
                    continue
                else:
                    raise ConnectionError

    def _create_content_and_prompt(
        self, transcription: str, language: Language
    ) -> tuple[str, str]:
        if language == Language.ENGLISH:
            prompt_filename = "prompt_english.txt"
            content_filename = "content_english.txt"
        elif language == Language.ITALIAN:
            prompt_filename = "prompt_italian.txt"
            content_filename = "content_italian.txt"
        else:
            raise ValueError("Unsupported language")

        prompt = self.read_prompt_from_file(prompt_filename).format(
            transcription=transcription
        )
        content = self.read_prompt_from_file(content_filename)
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
