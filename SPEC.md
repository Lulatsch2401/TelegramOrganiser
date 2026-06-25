# Telegram Packlisten-Bot — Build-Spec für Claude Code

> Bau dieses Projekt von Grund auf in diesem (leeren) Verzeichnis. Initialisiere Git,
> erstelle die Struktur, implementiere den Bot, schreibe Dockerfile + docker-compose
> für einen Raspberry Pi 5 (ARM64) und eine README mit dem Deployment-Flow.
> Am Ende: ein lauffähiges Repo, das ich auf dem Mac testen und per `git pull` auf dem Pi
> deployen kann. **Kein LLM, keine externe API** außer der Telegram Bot API.

## Ziel

Ein Telegram-Bot, der auf ein Stichwort (z. B. `schwimmen`) mit einer gespeicherten
Packliste antwortet, dargestellt als **antippbare Checkliste** (Inline-Keyboard, Tippen
hakt ab/an). Die Listen pflege ich selbst in einer **YAML-Datei** im Editor.

## Stack

- Python 3.12
- `python-telegram-bot` v21+ (async, **Long-Polling** — kein Webhook, kein offener Port)
- `PyYAML`
- `difflib` (stdlib) für leichtes Fuzzy-Matching
- Docker + docker-compose, lauffähig auf ARM64 (`python:3.12-slim`)

## Repo-Struktur

```
.
├── bot/
│   ├── __init__.py
│   ├── main.py          # Entry-Point, Polling-Loop, Handler-Registrierung
│   ├── lists.py         # YAML laden, Lookup, Fuzzy-Match, Reload
│   ├── keyboards.py     # Inline-Checklisten bauen + Toggle-Logik
│   └── config.py        # Env-Variablen einlesen + validieren
├── lists.yaml           # die Packlisten (von mir gepflegt)
├── tests/
│   └── test_lists.py    # Lookup + Fuzzy-Match testen (pytest, ohne Telegram)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore           # u. a. .env
└── README.md
```

## Verhalten

- **Bloßes Stichwort** (`schwimmen`, Groß/Klein egal, Leerzeichen trimmen)
  → passende Liste als Inline-Checkliste. Jede Zeile ein Button mit `▫️`/`✅`;
  Tippen toggelt den Haken (Message-Edit). Titel der Liste als erste Zeile.
- **`/listen`** (auch das Wort `listen`) → alle verfügbaren Stichwörter, alphabetisch.
- **Unbekanntes Wort** → freundlicher Hinweis + die nächste Fuzzy-Übereinstimmung
  (`difflib.get_close_matches`, cutoff ~0.6) als Vorschlag, plus Hinweis auf `/listen`.
- **`/reload`** → liest `lists.yaml` neu ein, ohne Container-Neustart (für „auf Pi gepullt,
  jetzt übernehmen"). Bestätigt, wie viele Listen geladen wurden.
- **`/start`** → kurze Begrüßung + verfügbare Stichwörter.

### Checklisten-Toggle (stateless halten)

Der Haken-Zustand soll **aus der Nachricht selbst** ablesbar sein (Emoji im Button-Text),
nicht aus einer DB. `callback_data` enthält Listen-Key + Item-Index; im Callback-Handler
das Keyboard neu aufbauen und nur das getippte Item umschalten, dann `edit_message_reply_markup`.
So braucht es keinen persistenten State und keine Datenbank.

## Sicherheit (wichtig)

**Allowlist als allererste Prüfung** in jedem Handler. Nur User-IDs aus der Env-Variable
`ALLOWED_USER_IDS` (kommagetrennt) dürfen den Bot nutzen; alle anderen bekommen eine kurze
Absage und werden ignoriert. Am saubersten über einen `filters.User(user_id=[...])`-Filter
plus ein Fallback-Handler für Fremde.

## Konfiguration

Alles über Env (kein Hardcoding):

- `BOT_TOKEN` — Telegram-Bot-Token von @BotFather
- `ALLOWED_USER_IDS` — z. B. `123456789` (oder mehrere, kommagetrennt)

`.env.example` mit diesen Keys committen, echte `.env` in `.gitignore`.

## lists.yaml — Beispiel zum Mitliefern

```yaml
schwimmen:
  title: "🏊 Schwimmen"
  aliases: [pool, baden, swim]
  items:
    - Badehose
    - Schwimmbrille
    - Handtuch
    - Badekappe
    - 1-Euro-Stück (Spind)
rennrad:
  title: "🚴 Rennrad"
  aliases: [rr, radfahren]
  items:
    - Helm
    - Trikot
    - Ersatzschlauch
    - Multitool
    - Pumpe
```

`aliases` sollen wie eigene Stichwörter funktionieren und ins Fuzzy-Matching einfließen.

## Docker / Deployment

- `Dockerfile`: schlankes `python:3.12-slim`, `requirements.txt` installieren, `CMD` startet
  `python -m bot.main`.
- `docker-compose.yml`:
  - `build: .`
  - `env_file: .env`
  - Volume `./lists.yaml:/app/lists.yaml` — damit ich die Liste ohne Rebuild ändern kann
    (Pull + `/reload`).
  - `restart: unless-stopped`
- Muss auf ARM64 (Pi 5) ohne Cross-Build-Tricks bauen.

## README — soll diesen Flow beschreiben

1. **Lokal (Mac):** `.env` aus `.env.example` anlegen, `pip install -r requirements.txt`,
   `python -m bot.main` zum Testen. `pytest` für die Lookup-Tests.
2. **Auf den Pi:** Repo klonen/`git pull`, `.env` einmalig anlegen,
   `docker compose up -d --build`.
3. **Liste ändern:** `lists.yaml` editieren → committen/pullen (oder direkt auf dem Pi
   editieren) → im Chat `/reload`. Kein Rebuild nötig.

## Zum Schluss

- Sinnvolle Logs (wer was angefragt hat, Reload-Ergebnis), aber **kein** Logging von Tokens.
- Erster Commit mit aussagekräftiger Message.
- Kurz in der README notieren, wie ich meine eigene Telegram-User-ID herausfinde
  (z. B. via @userinfobot).
