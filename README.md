# Lecture Summarizer

A lightweight pipeline that transcribes lecture audio, summarizes it with OpenAI, and publishes nicely-formatted pages to Notion.

## Quick Start

1. **Clone & install**
   ```bash
   git clone https://github.com/your-org/lecture_summarizer.git
   cd lecture_summarizer
   pip install -r requirements.txt
   ```
2. **Configure**
   ```bash
   cp .env.example .env   # then edit .env with your keys
   ```
3. **Prepare recordings**  
   Create a `recordings/` folder at repo root. Inside, add sub-folders named `<subject>_<owner>` (e.g. `Physics_itakello`). Drop your `.mp3`/`.m4a` files there.
4. **Run**
   ```bash
   python main.py
   ```

---

## Configuration (`.env`)

| Variable          | Description                                        |
|-------------------|----------------------------------------------------|
| `NOTION_API_KEY`  | Secret from your Notion integration                |
| `NOTION_DB_ID`    | Target database ID (32-char UUID w/o dashes)       |
| `OPENAI_API_KEY`  | Your OpenAI key                                    |
| `LANGUAGE`        | `ENG` or `ITA` – language of the recordings        |
| `OPENAI_MODEL`    | Model to use (`gpt-4o-mini`, `gpt-4o`, etc.)       |

The app validates `LANGUAGE` and `OPENAI_MODEL` at startup and will abort with a clear error if anything is missing.

## Notion Integration Setup

1. Go to **Settings & Members → Integrations → Develop your own integration** and click **+ New integration**.
2. Save the generated **Internal Integration Token** → this is your `NOTION_API_KEY`.
3. Open the database you want to use, click **Share**, add your integration and give it *edit* permissions.
4. Copy the database’s URL and extract the 32-char ID (the part after the last slash, before the `?`). Use that as `NOTION_DB_ID`.

---

## How the Pipeline Works

Below is a high-level walk-through of what happens when you run `python main.py`:

1. **Discovery** – `utils.get_paths()` scans the `recordings/` directory for audio files and groups them by subject/owner.
2. **Transcribe (Whisper)** – The recording is fed into OpenAI’s Whisper model (medium by default) which returns raw text.
3. **Chunking** – The transcription is split into ~2k-token segments (taking prompt & response tokens into account) via `utils.get_chunks_from_transcription()` so each chunk comfortably fits within the context window.
4. **Enrichment with OpenAI** – For every chunk, `ChatGPTUtils` crafts a language-specific prompt and calls the Chat Completions API to obtain a JSON payload with:
   * `title`
   * `summary`
   * `main_points`
   * `follow_up` questions
5. **Publish to Notion** – A `NotionPage` instance converts the structured data into rich blocks and upserts them into your target database page (creating it on first run, updating it on subsequent runs).
6. **Archive** – After a successful run the source audio file is moved to a `processed/` sub-folder next to the original for safe keeping.