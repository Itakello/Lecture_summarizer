import re

def _split_text_into_paragraphs(self, text: str, max_chars: int = 1800) -> list:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        paragraphs = []
        current_paragraph = ""
        for sentence in sentences:
            if len(current_paragraph) + len(sentence) <= max_chars:
                current_paragraph += sentence
            else:
                
                paragraphs.extend(self._split_string(current_paragraph.strip()))
        
        if current_paragraph != "":
            paragraphs.extend(self._split_string(current_paragraph.strip()))
        
        return paragraphs
    
