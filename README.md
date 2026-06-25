# Telegram Packlisten-Bot

Ein Telegram-Bot, der auf Stichwörter mit antippbaren Checklisten antwortet.  
Listen werden in `lists.yaml` gepflegt — kein Rebuild nötig, einfach `/reload`.

## Features

- Stichwort eingeben → Checkliste als Inline-Keyboard erscheint
- Jeden Punkt antippen → hakt ab (✅) oder wieder ab (▫️), kein Backend nötig
- Fuzzy-Matching für Tippfehler
- Alias-Support (z. B. `pool` findet `schwimmen`)
- `/reload` lädt die YAML live neu, ohne Container-Neustart
- Allowlist: nur konfigurierte User-IDs können den Bot nutzen

## Eigene Telegram-User-ID herausfinden

Schreibe im Telegram-Chat dem Bot [@userinfobot](https://t.me/userinfobot) — er antwortet sofort mit deiner numerischen User-ID.

---

## Lokaler Start (Mac)

```bash
cd TelegramOrganiser

# Abhängigkeiten installieren
pip install -r requirements.txt

# .env anlegen
cp .env.example .env
# BOT_TOKEN und ALLOWED_USER_IDS in .env eintragen

# Bot starten
python -m bot.main
```

### Tests ausführen

```bash
pytest
```

---

## Deployment auf dem Raspberry Pi 5

### Einmalig einrichten

```bash
# Repo klonen
git clone <repo-url>
cd TelegramOrganiser

# .env anlegen (einmalig, nicht committen!)
cp .env.example .env
nano .env   # BOT_TOKEN und ALLOWED_USER_IDS eintragen

# Bot starten
docker compose up -d --build
```

### Update einspielen

```bash
git pull
docker compose up -d --build
```

---

## Liste ändern (ohne Rebuild)

1. `lists.yaml` editieren (lokal oder direkt auf dem Pi)
2. Änderungen committen und auf den Pi pullen — **oder** direkt auf dem Pi bearbeiten
3. Im Telegram-Chat `/reload` eingeben

Der Bot lädt die Liste sofort neu. Kein `docker compose restart` nötig.

---

## Konfiguration

| Variable           | Beschreibung                                      |
|--------------------|---------------------------------------------------|
| `BOT_TOKEN`        | Token von [@BotFather](https://t.me/BotFather)    |
| `ALLOWED_USER_IDS` | Kommagetrennte Telegram-User-IDs, z. B. `123,456` |

---

## Bot-Befehle

| Eingabe          | Aktion                                          |
|------------------|-------------------------------------------------|
| `schwimmen`      | Checkliste für Schwimmen anzeigen               |
| `pool`, `swim`   | Alias → gleiche Liste                           |
| `/listen`        | Alle verfügbaren Stichwörter auflisten          |
| `listen`         | Wie `/listen` (auch als Freitext)               |
| `/reload`        | `lists.yaml` neu laden                          |
| `/start`         | Begrüßung + Übersicht                           |

---

## lists.yaml — Format

```yaml
schlüssel:
  title: "🏊 Anzeige-Titel"
  aliases: [alias1, alias2]   # optional, funktionieren wie eigene Stichwörter
  items:
    - Item 1
    - Item 2
```
