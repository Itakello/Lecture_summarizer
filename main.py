
import whisper
from classes.chatGPT import ChatGPTUtils
from classes.notion import NotionPage
from tqdm import tqdm
from classes.utils import *

def main():
    recordings = get_recordings(recordings_folder_path="/mnt/c/Users/maxst/OneDrive/class_recordings")
    gpt_utils = ChatGPTUtils()
    model = whisper.load_model("large")
    
    for recording in tqdm(recordings, desc="Processing recordings"):
        transcription = model.transcribe(recording.audio_path)['text']
        
        chunks = get_chunks_from_transcription(transcription.split(". "), max_words=1000) # Also take into account the input prompt and the output
        notion_page = NotionPage(recording)
        
        for idx, chunk in tqdm(enumerate(chunks), desc="Processing chunks"):
            chunk_obj = gpt_utils.get_additional_info(transcription=chunk, language=recording.language)
            notion_page.update_page(chunk_obj, idx + 1)
            
        move_to_folder(recording.audio_path, 'processed')
    
if __name__ == "__main__":
    main()