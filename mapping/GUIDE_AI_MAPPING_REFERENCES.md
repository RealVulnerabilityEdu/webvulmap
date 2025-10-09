# AI Mapping Guide

## Templates

### Zero-shot: considering input is "2023_ka.json"

1. "What cwe is most relevant to the computer science topic {2023_ka.json}?"
1. "Which potential cwes can be relevant to the topic {2023_ka.json}?" (Give
   multiple relevant potential cwes if a single strong one is not found.)
1. "Which cwe represents a vulnerability that can occur in risky software
   related to {2023_ka.json}?"

## Evaluating Generative AI Libraries

### LangChain

1. What it is
   - A framework, written in **Python and JavaScript**, for developing
     applications powered by large language models (LLMs).
   - **Open source** and widely used in the LLM ecosystem.

1. Capability
   - Enables chaining of LLMs, prompts, tools, and memory for complex tasks.
   - Supports integrations with APIs, databases, and external tools.
   - Provides modules for agents, **retrieval-augmented generation (RAG)**, and
     conversational memory.

1. Debugging
   - Suitable for local development and terminal-based debugging.
   - Allows for building chains in modular pieces, which helps isolate bugs.

1. Suitability for mapping
   - A **strong fit**, especially for building modular, LLM-powered pipelines
     for curriculum-to-CWE mapping.
   - Reusable and parameterized templates help with reasoning and traceability.

1. Documentation/tutorials
   - [Extensive official documentation](https://python.langchain.com/docs/).
   - Quickstart guides, tutorials, and example projects.
   - Community forums and Discord for **support**.

1. Development and user base
   - Over 70k GitHub stars (as of 2024).
   - Thousands of contributors and a large, active user community, so it is
     frequently updated.

1. Affordability
   - **Free** and open source for core features and a good starting point with
     free templates.
   - Some integrations may require **paid API keys** (e.g., OpenAI, Anthropic).

### CrewAI

1. What it is
   - A framework for building multi-agent AI systems in **Python**.
   - **Open source**, allowing inspection, local execution, modification, and
     sharing.

1. Capability
   - Being open source and in Python means it can be run locally.
   - Allows for **tracing** to observe LLM behavior before responses are
     generated.

1. Debugging
   - No native debugging dashboard; however, debug logging is available via
     environment variables.
   - Setting `DEBUG=true` generates logs including agent thoughts, tool
     invocations, and task transitions.

1. Suitability for mapping
   - Suitable if **structured well**.
   - Requires careful setup and may face challenges due to ambiguity, data
     inconsistency, and limitations of LLM reasoning.

1. Documentation/tutorials
   - Guides for quickstarts, installation, agents, flows, and prompt
     customization.
   - Examples and community forums for **questions and support**.

1. Development and user base
   - Over 100k certified developers.
   - About 2k active contributors.

1. Affordability
   - Open source core is **free** for small-scale development and prototypes.
   - **Paid plans** are available for production, large-scale development, and
     enterprise features.

## Running Scripts Locally (LangChain + Ollama)

Prerequisite: [Python 3.8+](https://www.python.org/downloads/) installed

1. Install [Git Bash](https://gitforwindows.org/).  
   **Note:** Use the `git` command for Linux/Unix.

1. Download [Ollama](https://ollama.com/download).

1. Clone the repository locally with the command:

   ```bash
   git clone https://github.com/cunymasslab/webvulmap

   ```

1. Run these pip install commands:

   ```bash
   pip install -U langchain langchain-community
   pip install -U langchain-ollama

   ```

1. At the top of your Python script, add these imports:

   ```bash
   from langchain_community.llms import Ollama
   from langchain_ollama import OllamaLLM

   ```

1. On Git Bash, run command:

   `ollama pull mistral`

   **Note:** you can replace `mistral` with any model name.

1. Navigate to project directory:

   `cd webvulmap`

1. Run python script with command:

   `python 'zero_shot.py'`

   **Note:** `'zero_shot.py'` can be replaced with the file you want to run.

## References

### Prompt Engineering

1. [Prompt engineering guide](https://www.promptingguide.ai/techniques)
1. [ChatGPT's guide](https://help.openai.com/en/articles/10032626-prompt-engineering-best-practices-for-chatgpt)
1. [Google Cloud's guide](https://cloud.google.com/discover/what-is-prompt-engineering#types-of-prompts)
1. [Library for prompt engineering](https://learnprompting.org/docs/introduction?srsltid=AfmBOoq3xmOfnAfRulNQtD7i8BWqbBJc_syAWK00Tobf8BChpTfJ1F9J)

### For designing templates

1. [Langchain-AI repository](https://github.com/langchain-ai/langchain/blob/master/docs/docs/concepts/prompt_templates.mdx)
1. [Crewai-customizing prompts](https://docs.crewai.com/en/guides/advanced/customizing-prompts)

### CWE

1. [CWEs](https://cwe.mitre.org/) (we will define a scope of cwes for the 2023 curriculum)

### Running code locally

1. [Python download](https://www.python.org/downloads/)
1. [Git Bash download](https://gitforwindows.org/)
1. [Ollama download](https://ollama.com/download)
