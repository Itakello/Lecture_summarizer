from dataclasses import dataclass

@dataclass
class Chunk():
    title : str
    transcript : str
    summary: str
    main_points: list[str]
    follow_up: list[str]
    
    def split_text_into_paragraphs(text:str, sentences_per_paragraph:int = 6) -> list:
        splitted = text.split(". ")
        paragraphs = []
        for i in range(0, len(splitted), sentences_per_paragraph):
            paragraphs.append(". ".join(splitted[i:i+sentences_per_paragraph]) + ".")
        return paragraphs
     