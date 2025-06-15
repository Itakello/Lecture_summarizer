import re
import shutil
from pathlib import Path

import tiktoken
from pydub import AudioSegment

from .recordings import Language, Owner, Recording


def get_folder_meta(path: str) -> tuple[Language, Owner]:
    chunks = path.split("_")
    assert len(chunks) == 2
    owner = chunks[0].lower()
    language = chunks[1].lower()
    return Language(language), Owner(owner)


# return the list of audio paths in each recording subfolder of each personal folder
def get_paths(recordings_folder_path: Path) -> list[Path]:
    paths = list()
    for folder in recordings_folder_path.iterdir():
        for subfolder in folder.iterdir():
            for file in subfolder.iterdir():
                if file.suffix == ".mp3" or file.suffix == ".m4a":
                    paths.append(file)
    return paths


def get_recording(file_path: Path) -> Recording:
    audio = AudioSegment.from_file(file_path)
    duration = int(len(audio) / 1000)
    subject_folder = file_path.parent.name
    language, owner = get_folder_meta(file_path.parent.parent.name)
    return Recording(
        file_path, file_path.stem, language, owner, duration, subject_folder
    )


def get_chunks_from_transcription(transcription: str, max_tokens: int) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", transcription)
    encoding = tiktoken.get_encoding("cl100k_base")
    chunks = []
    current_chunk = ""
    current_chunk_tokens = 0
    for sentence in sentences:
        num_tokens = len(encoding.encode(sentence))
        if current_chunk_tokens + num_tokens <= max_tokens:
            current_chunk += f" {sentence}"
            current_chunk_tokens += num_tokens
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
            current_chunk_tokens = num_tokens
    if current_chunk != "":
        chunks.append(current_chunk)
    return chunks


def move_to_folder(audio_path: Path, folder: str) -> None:
    processed_folder = audio_path.parent / folder
    processed_folder.mkdir(exist_ok=True, parents=True)
    shutil.move(audio_path, processed_folder)
