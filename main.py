from pathlib import Path

import whisper
from tqdm import tqdm

from classes.chatGPT import ChatGPTUtils
from classes.notion import NotionPage
from classes.utils import (
    get_chunks_from_transcription,
    get_paths,
    get_recording,
    move_to_folder,
)


def main() -> None:
    paths = get_paths(Path("/mnt/c/Users/maxst/OneDrive/class_recordings"))
    gpt_utils = ChatGPTUtils(model="gpt-3.5-turbo")
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
