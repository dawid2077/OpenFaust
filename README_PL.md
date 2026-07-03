# 🐶 OpenFaust (v2)

 [In English 🇬🇧](README.md) | Po Polsku

---
Asynchroniczny, sterowany zdarzeniami (event-driven), wieloprocesowy framework asystenta AI stworzony dla platformy Discord. OpenFaust nie tylko biernie odpowiada na wiadomości — aktywnie monitoruje dynamikę konwersacji, autonomicznie decyduje, kiedy się zaangażować, i samoczynnie budzi się, aby przełamać długą ciszę za pomocą niestandardowego silnika routingu.

Rozwijany na **NixOS**, napisany w **Pythonie** i bezproblemowo wdrażany za pomocą **Dockera**.

---

<img src="assets/mephi_small.png" alt="Projects mascot named mephi" width="350">

## 🗺️ Architektura Systemu

Ekosystem składa się z odizolowanych modułów oddzielających główne zdarzenia Discorda, orkiestrację LLM oraz procesy działające w tle:

<img src="assets/Faust.drawio.png" alt="OpenFaust Architecture Diagram" width="750">

---

## ✨ Główne Funkcje

*   **🧠 Router Semantyczny Kairos:** Używa szybkiego, deterministycznego modelu (`gpt-4o-mini`) jako „kontrolera ruchu”, aby ocenić, czy wiadomość użytkownika wymaga odpowiedzi na podstawie czasu, bezpośrednich oznaczeń lub ciągłości konwersacji, zanim przekaże ją do cięższego modelu.
*   **💓 Odizolowana Pętla Heartbeat:** Proces w tle (`multiprocessing.Process`), całkowicie oddzielony od wątku Discorda, który co 30 minut ocenia ciszę na czacie i może autonomicznie wywołać interakcję.
*   **📂 Trwała Pamięć Lokalna:** Zasilana przez zoptymalizowaną bazę danych SQLite, która śledzi czystą, ustrukturyzowaną historię użytkowników oraz kontekst metadanych.
*   **🎭 Dynamiczny Silnik Persony:** Całkowicie niezależny od osobowości. Wystarczy wrzucić dowolny profil w formacie Markdown do katalogu danych, a framework automatycznie wyodrębni tożsamość i dopasuje logikę routingu.

---

## 🚀 Szybki Start

### 1. Utwórz Aplikację Discord
Zanim uruchomisz OpenFausta, potrzebujesz tokena bota Discord. Utwórz go tutaj:

1. Wejdź na [Discord Developer Portal](https://discord.com/developers/applications)
2. Kliknij **New Application**, nadaj nazwę i utwórz.
3. Przejdź do zakładki **Bot** po lewej stronie.
4. Kliknij **Reset Token** (lub **Copy**, jeśli już istnieje) — to jest twój `DISCORD_TOKEN`. **Trzymaj go w tajemnicy.**
5. W sekcji **Privileged Gateway Intents** włącz:
   - ✅ **MESSAGE CONTENT INTENT** (wymagane do odczytu treści wiadomości)
   - ✅ **SERVER MEMBERS INTENT** (zalecane)
6. Zapisz zmiany.
7. Przejdź do zakładki **OAuth2 → URL Generator**.
8. W sekcji **Scopes** zaznacz `bot`.
9. W sekcji **Bot Permissions** zaznacz:
   - `Send Messages`
   - `Read Message History`
   - `Read Messages/View Channels`
   - `Mention Everyone` (opcjonalne, do funkcji automatycznego wybudzania)
10. Skopiuj wygenerowany URL, otwórz go w przeglądarce i zaproś bota na swój serwer.

### 2. Konfiguracja Środowiska
Utwórz plik `.env` w katalogu głównym:

```env
DISCORD_TOKEN=twoj_token_bota_discord
OPENROUTER_API_KEY=twoj_klucz_api_openrouter
APP_DATA_PATH=/app/data
APP_PERSONALITY_PATH=/app/data/personality.md
```

### 3. Konfiguracja (`data/config.conf`)
OpenFaust czyta ustawienia uruchomieniowe z pliku `data/config.conf`. Skopiuj `data/config.conf.example` do `data/config.conf` i dostosuj według potrzeb:

```bash
cp data/config.conf.example data/config.conf
```

Ustawienia domyślne:

```
DAILY_LIMIT_MAX=2
DAYS_AFTER_LIMIT_RESETS=1
MESSAGES_BY_USER_LIMIT=40
HEARTBEAT_TIME_SECONDS=15
CONTEXT_LIMIT=5000
```

| Ustawienie | Domyślnie | Opis |
|------------|-----------|------|
| `DAILY_LIMIT_MAX` | `2` | Maksymalna liczba wiadomości użytkownika przed limitem |
| `DAYS_AFTER_LIMIT_RESETS` | `1` | Dni do resetu limitu |
| `MESSAGES_BY_USER_LIMIT` | `40` | Maksymalna liczba @wzmianek na użytkownika dziennie |
| `HEARTBEAT_TIME_SECONDS` | `15` | Interwał (sekundy) między sprawdzeniami pętli heartbeat |
| `CONTEXT_LIMIT` | `5000` | Maksymalna liczba ostatnich wiadomości pobieranych z SQLite dla kontekstu |

### 4. Konfiguracja Docker Compose
Utwórz plik `docker-compose.yml` w katalogu głównym:

```yaml
services:
  openfaust:
    build: .
    container_name: openfaust
    restart: unless-stopped
    env_file:
      - .env  
    volumes:
      - ./data:/app/data
```

### 5. Uruchomienie Frameworku
Uruchom skonteneryzowaną aplikację w trybie odizolowanym (detached mode):

```bash
docker compose up -d
```

---

## 🎭 Dynamiczna Personalizacja Osobowości

Aby dynamicznie zmienić profil zachowania bota:

1. Zatrzymaj bieżący kontener wdrożeniowy:
   ```bash
   docker compose stop
   ```
2. Otwórz i zmodyfikuj plik `./data/personality.md` (lub ścieżkę do własnego pliku, jeśli została zmieniona), aby zaprojektować nowe reguły promptu osobowości.
3. Uruchom framework ponownie:
   ```bash
   docker compose up -d
   ```

---

## 🛠️ Moje Wybory Projektowe

### 🐍 Python
> Zdecydowałem się na użycie Pythona, ponieważ mam w nim największe doświadczenie i lubię z niego korzystać. Posiada on również świetne biblioteki do obsługi Discorda oraz API modeli.

### 🧠 Router Kairos & Heartbeat
> Dodałem Kairosa, aby OpenFaust brzmiał bardziej ludzko, pozwalając mu na autonomiczną interakcję z użytkownikami, jednocześnie obniżając koszty API.

### 🗄️ SQLite & Kontekst
> Wybrałem SQLite, ponieważ działa w oparciu o jeden plik i dobrze radzi sobie z formatem JSON. Potrzebowałem bazy danych do trwałego przechowywania danych i zarządzania kontekstem, ponieważ kontenery Dockera są domyślnie bezstanowe (stateless).

### 🐋 Wieloprocesowa Konteneryzacja (Docker)
> Zdecydowałem się na Dockera, ponieważ cenię sobie jego prostotę działania (plug-and-play), a ponadto zapewnia on solidne bezpieczeństwo, izolację i bezproblemowe zarządzanie.

### 🌐 Hosting & Wdrożenie (OCI & NixOS)
> Projekt rozwijałem na NixOS i mój serwer również działa pod kontrolą NixOS, ponieważ uwielbiam ten system operacyjny i uważam, że jest wysoce niedoceniany zarówno do programowania, jak i jako dystrybucja serwerowa. Obydwie usługi hostuję na OCI (Oracle Cloud Infrastructure), ponieważ oferuje ono bardzo hojną darmową strefę (free tier), a samą platformę znałem już wcześniej dzięki mojemu certyfikatowi.

---

## LICENCJA

*   **Ten projekt jest licencjonowany na warunkach licencji GNU Affero General Public License v3.0 - szczegóły znajdziesz w pliku [LICENSE](LICENSE).** 
*   **Copyright (c) 2026 dawid2077**
