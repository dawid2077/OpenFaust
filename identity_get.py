import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from functools import cache

# Load .env file FIRST
load_dotenv()

# Now read the API key
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("⚠️  OPENROUTER_API_KEY not found in .env file. Check your configuration.")

# List of free models
FREE_MODELS = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "openai/gpt-oss-120b:free",
    # ... (rest of your list) ...
    "nvidia/nemotron-nano-9b-v2:free"
]

FALLBACK_MODEL = "gpt-4o-mini"

@cache
def get_companion_identity(personality_path: Path) -> str:
    # Global API key check
    if not API_KEY:
        print("❌ OPENROUTER_API_KEY not set. Cannot proceed.")
        return "Faust"

    # 1. Read profile file
    try:
        if not isinstance(personality_path, Path):
            personality_path = Path(personality_path)
        if not personality_path.exists():
            print(f"⚠️  Profile not found at {personality_path}. Defaulting to 'Faust'.")
            return "Faust"
        raw_profile = personality_path.read_text(encoding="utf-8").strip()
        if not raw_profile:
            print(f"⚠️  {personality_path} is empty. Defaulting to 'Faust'.")
            return "Faust"
    except Exception as e:
        print(f"❌ Error reading file: {e}. Defaulting to 'Faust'.")
        return "Faust"

    # 2. Build messages
    system_instruction = (
        "You are a precise data extraction utility. ..."  # your instruction unchanged
    )
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Profile Text:\n{raw_profile}"}
    ]

    # 3. Create client ONCE using the global API key
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY
    )

    models_to_try = FREE_MODELS + [FALLBACK_MODEL]
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

    print("All models failed. Defaulting to 'Faust'.")
    return "Faust"

# Example test
if __name__ == "__main__":
    default_path = Path(os.getenv("APP_PERSONALITY_PATH", "./data/personality.md"))
    print("--- Executing Local Extraction Test (Free Model Rotation) ---")
    companion_name = get_companion_identity(default_path)
    print(f"Resulting Companion Name: {companion_name}")
