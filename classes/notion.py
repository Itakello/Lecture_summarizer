import os
from dataclasses import dataclass
from .recordings import Recording
from .chunk import Chunk
import requests

@dataclass
class NotionPage():
    recording: Recording
    DB_ID : str = "7e0e7afa117c42ff8f51a0cc9eaa531d"
    
    def __post_init__(self):
        self.NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
        self.headers = {'Authorization': f"Bearer {self.NOTION_API_KEY}", 
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
        return response.status_code
    
    def _create_chunk_payload(self, chunk:Chunk, chunk_idx:int) -> dict:
        blocks = []
        blocks.append(self._contruct_header_obj('heading_1',f"{chunk_idx}. {chunk.title}"))
        transcription = self._split_text_into_paragraphs(chunk.transcript)
        blocks.extend(self._construct_text_obj(transcription))
        blocks.append(self._contruct_header_obj('heading_2','Summary'))
        summary = self._split_text_into_paragraphs(chunk.summary)
        blocks.extend(self._construct_text_obj(summary))
        blocks.append(self._contruct_header_obj('heading_2','Main points'))
        blocks.extend(self._construct_list_obj(chunk.main_points))
        blocks.append(self._contruct_header_obj('heading_2','Follow ups'))
        blocks.extend(self._construct_list_obj(chunk.follow_up))
        """blocks.append(self._contruct_header_obj('heading_2','Stories'))
        blocks.extend(self._construct_list_obj(chunk.stories))
        blocks.append(self._contruct_header_obj('heading_2','Arguments'))
        blocks.extend(self._construct_list_obj(chunk.arguments))"""
        payload = {
            "children": blocks
        }
        return payload
    
    def _split_text_into_paragraphs(self, text:str, sentences_per_paragraph:int = 6) -> list:
        splitted = text.split(". ")
        paragraphs = []
        for i in range(0, len(splitted), sentences_per_paragraph):
            paragraphs.append(". ".join(splitted[i:i+sentences_per_paragraph]) + ".")
        return paragraphs
    
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
    
    def _construct_list_obj(self, list_items:list) -> dict:
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