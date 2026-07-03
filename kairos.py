import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables once
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Default model list (free models + fallback)
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

# Cache file for model blacklisting
CACHE_FILE = "data/model_blacklist_cache.json"
FAIL_THRESHOLD = 5
BLACKLIST_DURATION = 48 * 3600  # 48 hours in seconds

# ---------- Cache helpers ----------
def load_cache():
    """Load the blacklist cache from disk."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}

def save_cache(cache):
    """Write the blacklist cache to disk."""
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def is_model_blacklisted(model, cache):
    """Check if a model is currently blacklisted."""
    entry = cache.get(model)
    if not entry:
        return False
    blacklisted_until = entry.get("blacklisted_until", 0)
    if blacklisted_until > time.time():
        return True
    # Blacklist period expired, remove entry
    if model in cache:
        del cache[model]
    return False

def record_failure(model, cache):
    """Increment failure count; blacklist if threshold reached."""
    now = time.time()
    entry = cache.get(model, {"fail_count": 0, "last_failure": 0})
    entry["fail_count"] = entry.get("fail_count", 0) + 1
    entry["last_failure"] = now

    if entry["fail_count"] >= FAIL_THRESHOLD:
        entry["blacklisted_until"] = now + BLACKLIST_DURATION
        entry["fail_count"] = 0  # reset counter
        print(f"⚠️ Blacklisted {model} for 48 hours (5 consecutive failures).")
    else:
        entry["blacklisted_until"] = 0  # ensure not blacklisted yet

    cache[model] = entry
    save_cache(cache)

def record_success(model, cache):
    """Reset failure count on successful call."""
    if model in cache:
        entry = cache[model]
        entry["fail_count"] = 0
        entry["blacklisted_until"] = 0
        save_cache(cache)
# -----------------------------------

def decide(new_message, context, CHARACTER_PROFILE):
    print(new_message)

    system_instructions = (
        f"You are Kairos, an intelligent, event-driven routing engine and context-gatekeeper for an AI companion.\n\n"
        f"### TARGET CHARACTER PROFILE:\n"
        f"{CHARACTER_PROFILE}\n\n"
        f"### SYSTEM OBJECTIVE:\n"
        f"Analyze the entire conversation history provided in the messages array and evaluate the VERY LAST message. "
        f"Determine the identity, name, and pronouns of the companion using the provided TARGET CHARACTER PROFILE. "
        f"Your sole job is to decide if the companion should respond to this last message based on conversational momentum and context.\n\n"
        f"### CONVERSATIONAL MOMENTUM RULES:\n"
        f"1. DIRECT REPLY EXPECTATION: Check the timestamp metadata in the chat history (e.g., 'Last message sent X minutes ago'). "
        f"If the companion spoke very recently (0 to 2 minutes ago), and a user immediately sends a new message without tagging "
        f"or naming another explicit person, assume they are speaking directly back to the companion.\n"
        f"2. OPEN QUESTIONS: If the companion's last message ended in a question or explicitly demanded user input, "
        f"and a user provides a rapid response within that short time window, treat this as a continuous conversation.\n\n"
        f"### ROUTING CLASSIFICATION (CHOOSE ONE):\n"
        f"- Output {{\"action\": \"1\"}} (SILENT): The message is generic background chatter, or users are clearly talking to each other.\n"
        f"- Output {{\"action\": \"2\"}} (REACT): The message is a casual greeting to the room ('hi everyone') or short, non-urgent presence chatter.\n"
        f"- Output {{\"action\": \"3\"}} (ENGAGE): The message explicitly mentions the companion's name, directly asks the companion a question, "
        f"or represents an immediate, rapid answer to a question the companion just asked.\n\n"
        f"### CRITICAL COMPLIANCE:\n"
        f"If the message matches a CONVERSATIONAL MOMENTUM RULE or explicitly references the companion's name, you MUST return \"3\".\n"
        f"Output ONLY a valid JSON object matching this schema: {{\"action\": \"1\" | \"2\" | \"3\"}}."
    )

    # Prepare messages list
    api_messages = [{"role": "system", "content": system_instructions}]
    if isinstance(context, list):
        for msg in context:
            api_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
    api_messages.append({"role": "user", "content": new_message})

    # Load cache
    cache = load_cache()

    # Build list of models to try (skip blacklisted free models)
    models_to_try = []
    for model in FREE_MODELS:
        if is_model_blacklisted(model, cache):
            print(f"⏭️ Skipping blacklisted model: {model}")
            continue
        models_to_try.append(model)
    # Ensure fallback is always tried (even if blacklisted – optional, but we allow it)
    models_to_try.append(FALLBACK_MODEL)

    last_error = None

    for model in models_to_try:
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY
            )
            response = client.chat.completions.create(
                model=model,
                messages=api_messages,
                response_format={"type": "json_object"},
                temperature=0.0,
                timeout=30
            )
            raw_content = response.choices[0].message.content
            data = json.loads(raw_content)
            action = data.get("action", "1")

            # Record success for this model
            record_success(model, cache)
            print("Used Model: ",model)
            return action

        except Exception as e:
            last_error = e
            print(f"❌ Model {model} failed: {e}")
            record_failure(model, cache)  # increment counter and possibly blacklist
            time.sleep(0.5)  # brief pause before next attempt

    # All models failed
    print(f"All models failed. Last error: {last_error}")
    return "1"
