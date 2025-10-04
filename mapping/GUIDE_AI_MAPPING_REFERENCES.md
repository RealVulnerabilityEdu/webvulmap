# AI Mapping Guide

## Templates

### Zero-shot: considering input is "2023_ka.json"

1. "What cwe is most relevant to the computer science topic {2023_ka.json}?"
1. "Which potential cwes can be relevant to the topic {2023_ka.json}?" (give
   multiple relevant potential cwes if a single strong one is not found)
1. "Which cwe represents a vulnerability that can occur in risky software
   related to {2023_ka.json}?"

## Evaluating Generative AI Libraries

### LangChain

1. What it is
   - a framework, written in **Python and JavaScript**, for developing
     applications powered by large language models (LLMs)
   - **open source** and widely used in the LLM ecosystem

1. Capability
   - enables chaining of LLMs, prompts, tools, and memory for complex tasks and
     supports integrations with APIs, databases, and external tools
   - provides modules for agents, **retrieval-augmented generation (RAG)**, and
     conversational memory

1. Debugging
   - great for local dev and terminal-based debugging
   - allows for building of chains in modular pieces which helps isolate bugs

1. Suitability for mapping
   - **strong fit**, especially for building modular, LLM-powered pipelines for
     curriculum-to-CWE mapping
   - reusable and parameterized templates help with reasoning and traceability

1. Documentation/tutorials
   - [extensive official documentation](https://python.langchain.com/docs/)
   - quickstart guides, tutorials, and example projects
   - community forums and Discord for **support**

1. Development and user base
   - over 70k GitHub stars (as of 2024).
   - thousands of contributors and a large, active user community so it is
     frequently updated

1. Affordability
   - **free** and open source for core features and good starting point with
     free templates
   - some integrations may require **paid API keys** (e.g., OpenAI, Anthropic)

### CrewAI

1. What it is
   - a framework for building multi-agent AI systems in **Python**
   - **open source** so you can see how it works, inspect it, run it yourself,
     modify it, share it, etc.

1. Capability
   - open source and in python means you can **run it locally**
   - allows for **tracing** so you can see the behavior of the LLMs before they
     respond

1. Debugging
   - no native debugging dashboard, however has debug logging with environmental
     variables
   - set "DEBUG = true" to generate logs including agent thoughts, tool
     invocations, and task transitions

1. Suitability for mapping
   - suitable if **structured well**
   - requires careful setup and may face challenges due to ambiguity, data
     inconsistency, and limitations of LLM reasoning

1. Documentation/tutorials
   - guides for quickstarts, installation, agents, flows, prompt customization
   - examples and community forums for **questions and concerns**

1. Development and user base
   - over 100k certified developers
   - about 2k active contributors

1. Affordability
   - open source core for small scale development and prototypes are **free**
   - **paid plans** available for production, large scale development, and
     enterprise features

## Running Scripts Locally (LangChain + Ollama)
Prerequisite: Python 3.8+ installed (https://www.python.org/downloads/)
1) Install Git Bash at https://gitforwindows.org/ **Note** use 'git' command for LINUX/UNIX
2) Download Ollama at https://ollama.com/download
3) Clone repository locally with command 'git clone https://github.com/cunymasslab/webvulmap'
4) pip install commands:

   pip install -U langchain langchain-community

   pip install -U langchain-ollama
5) At the top of your Python script, add these imports:

   from langchain_community.llms import Ollama

   from langchain_ollama import OllamaLLM
7) On Git Bash, run command 'ollama pull mistral' **Note** you can replace 'mistral' with any model name
8) Navigate to project directory, ex) cd webvulmap
9) Run python script with command: python 'zero_shot.py'

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
2. [Git Bash download](https://gitforwindows.org/)
3. [Ollama download](https://ollama.com/download)
