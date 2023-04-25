from dataclasses import dataclass
from enum import Enum

class Language(Enum):
    ENGLISH = "en"
    ITALIAN = "ita"

class Owner(Enum):
    ITAKELLO = "itakello"
    BIRI = "biri"

@dataclass
class Recording():
    audio_path: str
    name: str
    language: Language
    owner: Owner
    duration: int
    subject: str
    
    def get_short_subject(self) -> str:
        if len(self.subject) < 30:
            return self.subject
        else:
            return ''.join([word[0].upper() for word in self.subject.split(' ')])
    
    def get_owner_surname(self) -> str:
        match self.owner:
            case Owner.ITAKELLO:
                return '🦃 Itakello'
            case Owner.BIRI:
                return '🐢 Biri'
            case _:
                raise ValueError(f'Unknown owner: {self.owner}')