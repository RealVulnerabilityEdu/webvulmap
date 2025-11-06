# CS 2023: CWE to Knowledge Area Mapping Programs

These programs use LangChain + Ollama (LLM) to automatically map
Knowledge Areas (KAs) from the 2023 ACM/IEEE Computer Science Curriculum
to Common Weakness Enumerations (CWEs) using zero-shot, few-shot
and RAG prompt engineering approaches.

They take a JSON file describing a Knowledge Area, query an Ollama model
(e.g., mistral), and output a structured mapping of relevant CWEs in JSON format.

## Features

- **Zero-shot, few-shot and RAG reasoning** via Ollama LLM models

- **LangChain integration** for structured prompting

- **Automatic CWE extraction and formatting**

- **Incremental output updates** (avoids duplicates)

- **Mock mode** for offline testing (no LLM calls)

## Input

These programs expect a JSON file as input. The file will
be a structured KA to be read in by the programs and used in the
query to the LLM.

## Usage

```python
python
<full path to the mapping program (e.g., cs2023_zero_shot.py)>
<full path to the KA JSON file (e.g., SE_v2.json)>
<full path to the output file (e.g., output.json)>
```

**NOTE** The output file will be created if it does not already exist

**NOTE** Add `--mock` to the end of this command for a mock mode test run

**Example run:**

python .../cs2023_zero_shot.py .../SE_v2.json .../cs2023_zero_shot_output.json

**With mock mode:**

python .../cs2023_zero_shot.py .../SE_v2.json .../cs2023_zero_shot_output.json --mock

## Sample Output

```json
{
    "Software Engineering": [
        {
            "cwe": "190",
            "name": "Improper Input Validation",
            "reason": "Software Engineering, particularly in its design
             and development phases, often involves handling user inputs. Proper
             input validation ensures that these inputs are safe, which helps
             prevent security vulnerabilities and errors in the software."
        }
    ]
}
```

## How It Works

1. **Load Input:** Reads the Knowledge Area name from the JSON file.

1. **Primary Query:** Sends a zero-shot, few-shot or RAG prompt to
   Ollama asking for the most relevant CWE.

1. **Fallback Query:** If the primary query fails or returns no CWE,
   it asks for 3–5 relevant CWEs.

1. **Parse & Structure:** Extracts CWE IDs, names, and reasoning from the LLM response.

1. **Save Output:** Updates (or creates) an output JSON file with structured mappings.
