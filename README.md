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

---

## Notion Integration Setup

1. Go to **Settings & Members → Integrations → Develop your own integration** and click **+ New integration**.
2. Save the generated **Internal Integration Token** → this is your `NOTION_API_KEY`.
3. Open the database you want to use, click **Share**, add your integration and give it *edit* permissions.
4. Copy the database’s URL and extract the 32-char ID (the part after the last slash, before the `?`). Use that as `NOTION_DB_ID`.

---

## Pipeline Overview

1. **Discovery** – `utils.get_paths()` scans `recordings/` for audio files.
2. **Transcription** – Whisper (`medium` model by default) converts audio to text.
3. **Chunking** – Long transcriptions are split into ~2k-token chunks.
4. **Enrichment** – `ChatGPTUtils` calls OpenAI with language-specific prompts to obtain title, summary, main points, follow-ups.
5. **Publishing** – `NotionPage` builds / updates a page in your target DB for each chunk.
6. **Archiving** – Processed audio is moved into a `processed/` sub-folder alongside the original file.

---

*Sections below describe the original GPU / WSL2 setup and are kept for reference.*

---

# Lecture Summarizer Environment Setup Guide

This guide outlines the steps required to set up the environment for running the Lecture Summarizer project on a system with an NVIDIA GPU, using Windows Subsystem for Linux (WSL2), and Conda.

## Table of Contents
1. [CUDA Toolkit Installation](#cuda-toolkit-installation)
2. [Environment Variables Configuration](#environment-variables-configuration)
3. [Conda Environment Creation](#conda-environment-creation)
4. [Verifying Installation](#verifying-installation)
5. [Troubleshooting](#troubleshooting)

## CUDA Toolkit Installation

1. Follow the NVIDIA guide for [installing CUDA on WSL2](https://docs.nvidia.com/cuda/wsl-user-guide/index.html).

## Environment Variables Configuration

1. Temporarily add the CUDA Toolkit's bin directory to the PATH for the current session:
    ```bash
    export PATH=/usr/local/cuda/bin:$PATH
    ```
2. Permanently add the CUDA Toolkit's bin directory to the PATH for all future sessions:
    ```bash
    echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
    source ~/.bashrc
    ```

3. Temporarily set the `LD_LIBRARY_PATH` environment variable to let torch and use the GPU:
    ```bash
    export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
    ```

4. Permanently set the `LD_LIBRARY_PATH` environment variable to let torch and use the GPU:
    ```bash
    echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
    source ~/.bashrc
    ```

## Conda Environment Creation

1. Create a new Conda environment specifying the desired Python version (e.g., 3.11.5):
    ```bash
    conda create -n lecture_summarizer python=3.11.5
    conda activate lecture_summarizer
    ```

2. After the CUDA Toolkit installation, install the necessary libraries within the Conda environment:
    ```bash
    pip install -r requirements.txt
    ```

## Verifying Installation

1. Verify the CUDA Toolkit installation:
    ```bash
    nvcc --version
    ```

## Troubleshooting

1. **libcuda.so Error**: If you encounter a `libcuda.so: cannot open shared object file: No such file or directory` error:
    - Locate `libcuda.so`:
        ```bash
        sudo find /usr -name libcuda.so
        ```
    - Update `LD_LIBRARY_PATH`:
        ```bash
        export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH
        ```
    - Make the change permanent:
        ```bash
        echo 'export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
        source ~/.bashrc
        ```

2. **libcuda.so Accessibility**: Verify that `libcuda.so` is accessible:
    ```bash
    ldconfig -p | grep libcuda.so
    ```

# Setting Up API Keys

## Notion API Key

1. Obtain your Notion API key from your [Notion account](https://www.notion.so/my-integrations) settings under the Integrations section.
2. Temporarily set the `NOTION_API_KEY` environment variable for the current session:
    ```bash
    export NOTION_API_KEY=your_notion_api_key_here
    ```
3. Permanently set the `NOTION_API_KEY` environment variable for all future sessions:
    ```bash
    echo 'export NOTION_API_KEY=your_notion_api_key_here' >> ~/.bashrc
    source ~/.bashrc
    ```

## OpenAI API Key

1. Obtain your OpenAI API key from your [OpenAI account](https://platform.openai.com/account/api-keys) settings.
2. Temporarily set the `OPENAI_API_KEY` environment variable for the current session:
    ```bash
    export OPENAI_API_KEY=your_openai_api_key_here
    ```
3. Permanently set the `OPENAI_API_KEY` environment variable for all future sessions:
    ```bash
    echo 'export OPENAI_API_KEY=your_openai_api_key_here' >> ~/.bashrc
    source ~/.bashrc
    ```

Now your environment is fully set up to run the Lecture Summarizer program.

---

This addition to your guide provides a clear and straightforward method for setting up the necessary API keys for your program.