from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Language(Enum):
    ENGLISH = "en"
    ITALIAN = "it"


@dataclass
class Recording:
    audio_path: Path
    name: str
    language: Language
    owner: str
    duration: int
    subject: str

    def get_short_subject(self) -> str:
        if len(self.subject) < 30:
            return self.subject
        else:
            return "".join([word[0].upper() for word in self.subject.split(" ")])
