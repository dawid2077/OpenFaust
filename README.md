# 🐶 OpenFaust (v2)

 English | [Po Polsku 🇵🇱](README_PL.md)

---
An asynchronous, event-driven, multi-processed AI companion framework built for Discord. OpenFaust doesn't just passively reply to messages—it actively monitors conversation momentum, autonomously decides when to engage, and wakes itself up to break long silences using a custom routing engine.

Developed on **NixOS**, written in **Python**, and deployed seamlessly via **Docker**.

---

<img src="assets/mephi_small.png" alt="Projects mascot named mephi" width="350">

## 🗺️ System Architecture

The ecosystem is built out of isolated modules separating core Discord events, LLM orchestration, and background processes:

<img src="assets/Faust.drawio.png" alt="OpenFaust Architecture Diagram" width="750">

---

## ✨ Key Features
*   **🎭 Dynamic Persona Engine:** Fully personality-agnostic. Drop any markdown profile into the data directory, and the framework automatically re-extracts the identity and re-aligns the routing logic.
*   **🧠 Kairos Semantic Router:** Uses a fast, deterministic model (`gpt-4o-mini`) as a traffic cop to evaluate whether a user's message warrants a response based on timing, direct tags, or conversational continuity before passing it to a heavier model.
*   **💓 Decoupled Heartbeat Loop:** A background `multiprocessing.Process` completely separate from the Discord thread that evaluates chat silences every 30 minutes and can autonomously trigger interactions.
*   **📂 Persistent Local Memory:** Powered by an optimized SQLite database factory tracking clean, structured user histories and metadata context.

---

## 🚀 Quick Start

### 1. Create a Discord Application
Before running OpenFaust, you need a Discord bot token. Create one here:

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application**, give it a name, and create it.
3. Go to the **Bot** tab on the left sidebar.
4. Click **Reset Token** (or **Copy** if one already exists) — this is your `DISCORD_TOKEN`. **Keep it secret.**
5. Under **Privileged Gateway Intents**, enable:
   - ✅ **MESSAGE CONTENT INTENT** (required for reading message content)
   - ✅ **SERVER MEMBERS INTENT** (recommended)
6. Save changes.
7. Go to the **OAuth2 → URL Generator** tab.
8. Under **Scopes**, check `bot`.
9. Under **Bot Permissions**, check:
   - `Send Messages`
   - `Read Message History`
   - `Read Messages/View Channels`
   - `Mention Everyone` (optional, for auto-wake functionality)
10. Copy the generated URL, open it in a browser, and invite the bot to your server.

### 2. Environment Configuration
Create a `.env` file in the root directory:

```env
DISCORD_TOKEN=your_discord_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
APP_DATA_PATH=/app/data
APP_PERSONALITY_PATH=/app/data/personality.md
```

### 3. Configuration (`data/config.txt`)
OpenFaust reads its runtime settings from `data/config.txt`. Copy `data/config.txt.example` to `data/config.txt` and adjust as needed:

```bash
cp data/config.txt.example data/config.txt
```

Default settings:

```
DAILY_LIMIT_MAX=2
DAYS_AFTER_LIMIT_RESETS=1
MESSAGES_BY_USER_LIMIT=40
HEARTBEAT_TIME_SECONDS=15
CONTEXT_LIMIT=5000
```

| Setting | Default | Description |
|---------|---------|-------------|
| `DAILY_LIMIT_MAX` | `2` | Max number of messages a user can send before hitting the rate limit |
| `DAYS_AFTER_LIMIT_RESETS` | `1` | Days until the rate limit resets |
| `MESSAGES_BY_USER_LIMIT` | `40` | Max direct @mentions per user per day |
| `HEARTBEAT_TIME_SECONDS` | `15` | Interval (seconds) between heartbeat loop checks |
| `CONTEXT_LIMIT` | `5000` | Max number of recent messages pulled from SQLite for context |

### 4. Docker Compose Configuration
Create a `docker-compose.yml` file in the root directory:

```yaml
services:
  openfaust:
    image: ghcr.io/dawid2077/openfaust:v2.0.0
    container_name: openfaust
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
```

### 5. Run the Framework
Launch the containerized application in detached mode:

```bash
docker compose up -d
```

---

## 🎭 Dynamic Personality Customization

To swap your bot's behavior profile dynamically:

1. Stop the current deployment container:
   ```bash
   docker compose stop
   ```
2. Open and modify the `./data/personality.md` file (or your custom file path if you changed it) to design your new custom personality prompt rules.
3. Bring the framework back online:
   ```bash
   docker compose up -d
   ```

---

## 🛠️ My Design Choices 

### 🐍 Python
> I decided to use Python because I have the most experience with it and enjoy using it. It also features excellent libraries for both Discord and model APIs.

### 🧠 The Kairos Router & Heartbeat
> I added Kairos to make OpenFaust feel more human by allowing it to interact with users autonomously, while also keeping API costs down.

### 🗄️ SQLite & Context
> I chose SQLite because it operates from a single file and handles JSON well. I needed a database for persistent storage and context management since Docker containers are stateless by default.

### 🐋 Multi-Process Containerization (Docker)
> I decided to go with Docker because I value its plug-and-play capability, and it provides robust security, isolation, and seamless management.

### 🌐 Hosting & Deployment (OCI & NixOS)
> I developed this project on NixOS, and my server runs on NixOS because I love the operating system and believe it is highly underrated for development and especially as a server distribution. I personally host it on OCI (Oracle Cloud Infrastructure) because it offers a very generous free tier, and I was already familiar with the platform through my certification.

---

## LICENSE

*   **This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.** 
*   **Copyright (c) 2026 dawid2077** 
