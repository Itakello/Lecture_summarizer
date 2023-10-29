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