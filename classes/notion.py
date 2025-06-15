import os
from dataclasses import dataclass, field
from .recordings import Recording
from .chunk import Chunk
import requests
import re
from typing import Dict, Tuple

@dataclass
class NotionPage():
    recording: Recording
    DB_ID : str = field(init=False)
    
    # Define the expected database schema once so it can be reused by the
    # verification & fix helpers.
    REQUIRED_PROPERTIES: Dict[str, str] = field(default_factory=lambda: {
        "Title": "title",
        "Duration (seconds)": "number",
        "Subject": "select",
        "Who": "select",
    }, init=False, repr=False)

    def __post_init__(self):
        # Load database ID and API key from environment
        self.DB_ID = os.environ.get("NOTION_DB_ID")
        notion_api_key = os.environ.get("NOTION_API_KEY")

        if not notion_api_key:
            raise EnvironmentError(
                "NOTION_API_KEY is not set. Please configure it in your .env file."
            )
        if not self.DB_ID:
            raise EnvironmentError(
                "NOTION_DB_ID is not set. Please configure it in your .env file."
            )

        self.headers = {
            "Authorization": f"Bearer {notion_api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
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

    # ------------------------------------------------------------------
    #  New methods: DB schema verification & automatic fixing
    # ------------------------------------------------------------------
    def verify_db_schema(self) -> Tuple[bool, Dict[str, str]]:
        """Check that the Notion database contains all required properties.

        Returns
        -------
        Tuple[bool, Dict[str, str]]
            * bool – True if the schema is correct, False otherwise.
            * dict – Mapping of property names to an error message (missing or wrong type).
        """
        url = f"https://api.notion.com/v1/databases/{self.DB_ID}"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch Notion DB schema: {resp.status_code} - {resp.text}")

        db_props = resp.json().get("properties", {})
        errors: Dict[str, str] = {}
        for name, expected_type in self.REQUIRED_PROPERTIES.items():
            if name not in db_props:
                errors[name] = "missing"
            else:
                actual_type = db_props[name].get("type")
                if actual_type != expected_type:
                    errors[name] = f"wrong type (expected '{expected_type}', got '{actual_type}')"
        return (len(errors) == 0, errors)

    def fix_db_schema(self) -> None:
        """Add or update database properties to match REQUIRED_PROPERTIES.

        If `verify_db_schema` reports issues, this method will PATCH the
        database, adding missing columns or updating incorrect ones to the
        correct type.
        """
        is_ok, errors = self.verify_db_schema()
        if is_ok:
            return  # Nothing to fix

        update_payload: Dict[str, Dict] = {"properties": {}}
        for name in errors.keys():
            correct_type = self.REQUIRED_PROPERTIES[name]
            update_payload["properties"][name] = self._build_property_definition(correct_type)

        url = f"https://api.notion.com/v1/databases/{self.DB_ID}"
        resp = requests.patch(url, json=update_payload, headers=self.headers)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to update Notion DB schema: {resp.status_code} - {resp.text}")

    # ---------------------  helpers  ----------------------------------
    def _build_property_definition(self, prop_type: str) -> Dict:
        """Return a Notion property definition JSON fragment for the given type."""
        if prop_type == "title":
            return {"title": {}}
        if prop_type == "number":
            return {"number": {"format": "number"}}
        if prop_type == "select":
            return {"select": {}}
        raise ValueError(f"Unsupported property type: {prop_type}")