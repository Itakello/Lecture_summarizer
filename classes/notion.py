import os
from dataclasses import dataclass
from .recordings import Recording
from .chunk import Chunk
import requests
import re

@dataclass
class NotionPage():
    recording: Recording
    DB_ID : str = "7e0e7afa117c42ff8f51a0cc9eaa531d"
    
    def __post_init__(self):
        self.headers = {'Authorization': f"Bearer {os.environ.get('NOTION_API_KEY')}", 
            'Content-Type': 'application/json', 
            'Notion-Version': '2022-06-28'}
        self.page_id = self._create_page("https://api.notion.com/v1/pages")
        self.url_update = f"https://api.notion.com/v1/blocks/{self.page_id}/children"
    
    def _create_page(self, url:str) -> None:
        payload = self._create_initial_payload()
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()['id']
    
    def _create_initial_payload(self) -> dict:
        payload = {
            "parent": {
                "type": "database_id",
                "database_id": self.DB_ID
                },
            "properties":  {
                "Title": {
                    "title": [
                    {
                        "type": "text",
                        "text": {
                        "content": self.recording.name
                        }
                    }
                    ]
                },
                "Duration (seconds)": {
                    "number": self.recording.duration
                },
                "Subject":{
                    "select": {
                    "name": self.recording.get_short_subject()
                    }
                },
                "Who":{
                    "select": {
                    "name": self.recording.get_owner_surname()
                    }
                },
            },
            "icon": {
                "type": "emoji",
                "emoji": "🤖"
            },
            "children": [
                {
                "table_of_contents": {
                    "color": "blue"
                }
                }
            ]
        }
        return payload
    
    def update_page(self, chunk:Chunk, chunk_idx:int) -> None:
        payload = self._create_chunk_payload(chunk, chunk_idx)
        response = requests.patch(self.url_update, json=payload, headers=self.headers)
        if response.status_code != 200:
            return
    
    def _create_chunk_payload(self, chunk:Chunk, chunk_idx:int) -> dict:
        blocks = []
        blocks.append(self._contruct_header_obj('heading_1',f"{chunk_idx}. {chunk.title}"))
        transcription_paragraphs = self._split_text_into_paragraphs(chunk.transcript)
        blocks.extend(self._construct_text_obj(transcription_paragraphs))
        blocks.append(self._contruct_header_obj('heading_2','Summary'))
        summary_paragraphs = self._split_text_into_paragraphs(chunk.summary)
        blocks.extend(self._construct_text_obj(summary_paragraphs))
        blocks.append(self._contruct_header_obj('heading_2','Main points'))
        blocks.extend(self._construct_list_obj(chunk.main_points))
        blocks.append(self._contruct_header_obj('heading_2','Follow ups'))
        blocks.extend(self._construct_list_obj(chunk.follow_up))
        payload = {
            "children": blocks
        }
        return payload
    
    def _split_text_into_paragraphs(self, text:str) -> list[str]:
        # Split the text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # Split any sentence longer than 600 characters into smaller parts
        for i, sentence in enumerate(sentences):
            if len(sentence) > 600:
                parts = re.split(r'(?<=[,])\s+', sentence) # First attempt to split by commas
                if len(' '.join(parts)) > 600:  # If it's still too long, split on capital letters
                    parts = re.split(r'(?<=[a-z])\s+(?=[A-Z])', sentence)
                if len(' '.join(parts)) > 600:  # If it's still too long, split on spaces
                    parts = sentence.split(' ')
                    
                sentences[i:i+1] = parts
                
        chunks = []
        chunk = sentences[0]
        for sentence in sentences[1:]:
            if len(chunk) + len(sentence) + 1 > 600:  # +1 for the space between sentences
                chunks.append(chunk)
                chunk = sentence
            else:
                chunk += ' ' + sentence
        chunks.append(chunk)  # Don't forget the last chunk
        
        return chunks
    
    def _construct_text_obj(self, paragraphs:list) -> list:
        full_text = []
        for paragraph in paragraphs:
            obj = {
                "paragraph": {
                    "rich_text":[{
                        "text": {
                            "content": paragraph
                        }
                    }]
                }
            } 
            full_text.append(obj)
        return full_text
    
    def _contruct_header_obj(self, header_type:str, header:str) -> dict:
        return {
            header_type: {
                "rich_text": [
                {
                    "text": {
                        "content": header
                    }
                }
                ]
            }
        }
    
    def _construct_list_obj(self, list_items:list) -> list:
        full_list = []
        for item in list_items:
            obj = {
                "numbered_list_item": {
                    "rich_text": [{
                        "text": {
                            "content": item
                        }
                    }]
                }
            }
            full_list.append(obj)
        return full_list