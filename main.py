import os
from pathlib import Path

import whisper
from dotenv import load_dotenv
from tqdm import tqdm

from classes.chatGPT import ChatGPTUtils
from classes.notion import NotionPage
from classes.utils import (
    get_chunks_from_transcription,
    get_paths,
    get_recording,
    move_to_folder,
)


def _validate_env() -> tuple[str, str]:
    """Validate required environment variables and return language and model."""
    language = os.environ.get("LANGUAGE")
    model = os.environ.get("OPENAI_MODEL")

    if language not in {"ENG", "ITA"}:
        raise EnvironmentError(
            "LANGUAGE must be set to 'ENG' or 'ITA' in your .env file."
        )
    if not model:
        raise EnvironmentError(
            "OPENAI_MODEL is not set in your .env file."
        )
    return language, model


def main() -> None:
    # Load .env if present
    load_dotenv()

    _, model = _validate_env()

    recordings_root = Path("recordings")
    if not recordings_root.exists():
        raise FileNotFoundError(
            "'recordings' folder not found. Create it and add your audio subfolders."
        )

    paths = get_paths(recordings_root)
    gpt_utils = ChatGPTUtils(model=model)
    model = whisper.load_model("medium")

    for path in tqdm(paths, desc="Processing recordings"):
        recording = get_recording(path)
        transcription = model.transcribe(str(recording.audio_path))["text"]
        chunks = get_chunks_from_transcription(
            str(transcription), max_tokens=2000
        )  # Also take into account the input prompt and the output
        notion_page = NotionPage(recording)

        for idx, chunk in tqdm(enumerate(chunks), desc="Processing chunks"):
            chunk_obj = gpt_utils.get_additional_info(
                chunk_str=chunk, language=recording.language
            )
            notion_page.update_page(chunk_obj, idx + 1)

        move_to_folder(recording.audio_path, "processed")


if __name__ == "__main__":
    main()
