Understood. You want to try a **list of free OpenRouter models** sequentially, with a fallback model (`gpt-4o-mini`) if all free ones fail. No caching, no blacklisting – just simple sequential fallback.

Here's the modified `get_companion_identity` function:

```python
import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from functools import cache

load_dotenv()

# List of free models to try (in order of preference)
FREE_MODELS = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "openai/gpt-oss-120b:free",
    "nvidia/nemotron-3-super:free",
    "google/gemma-4-31b:free",
    "google/gemma-4-26b-a4b:free",
    "openai/gpt-oss-20b:free",
    "cohere/north-mini-code:free",
    "poolside/laguna-m.1:free",
    "nvidia/nemotron-3-nano-omni:free",
    "nvidia/nemotron-nano-12b-2-vl:free",
    "poolside/laguna-xs-2.1:free",
    "poolside/laguna-xs.2:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "nvidia/nemotron-nano-9b-v2:free"
]

FALLBACK_MODEL = "gpt-4o-mini"

@cache
def get_companion_identity(personality_path: Path) -> str:
    """
    Tries each model from FREE_MODELS (via OpenRouter) in order.
    If all free models fail, falls back to FALLBACK_MODEL.
    Returns extracted name or 'Faust' on total failure.
    """
    # 1. Read profile file (unchanged)
    try:
        if not isinstance(personality_path, Path):
            personality_path = Path(personality_path)
        if not personality_path.exists():
            print(f"⚠️  Warning: Profile not found at {personality_path}. Defaulting name to 'Faust'.")
            return "Faust"
        raw_profile = personality_path.read_text(encoding="utf-8").strip()
        if not raw_profile:
            print(f"⚠️  Warning: {personality_path} is empty. Defaulting name to 'Faust'.")
            return "Faust"
    except Exception as e:
        print(f"❌ Error reading file: {e}. Defaulting to 'Faust'.")
        return "Faust"

    # 2. Build the message payload (same for all models)
    system_instruction = (
        "You are a precise data extraction utility. Read the provided AI companion "
        "personality profile text.\n\n"
        "Identify the primary name or moniker the assistant goes by or is assigned. "
        "If no specific name is mentioned anywhere in the text, you must return 'Faust'.\n\n"
        "Output ONLY a valid JSON object matching this schema: {\"name\": \"extracted_name_here\"}."
    )
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Profile Text:\n{raw_profile}"}
    ]

    # 3. Try each free model, then fallback
    models_to_try = FREE_MODELS + [FALLBACK_MODEL]
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.0,
                timeout=30
            )
            raw_content = response.choices[0].message.content
            data = json.loads(raw_content)
            extracted_name = data.get("name", "Faust").strip()
            print(f"⚙️ Identity Extractor (model={model}): Resolved name -> [{extracted_name}]")
            return extracted_name
        except Exception as e:
            print(f"❌ Model {model} failed: {e}. Trying next...")
            continue

    # 4. If all failed
    print("All models failed. Defaulting to 'Faust'.")
    return "Faust"


# Example test
if __name__ == "__main__":
    default_path = Path(os.getenv("APP_PERSONALITY_PATH", "./data/personality.md"))
    print("--- Executing Local Extraction Test (Free Model Rotation) ---")
    companion_name = get_companion_identity(default_path)
    print(f"Resulting Companion Name: {companion_name}")
