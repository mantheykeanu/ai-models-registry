# Briefing für Claude — Keanu Manthey

> **Hinweis an Claude:** Diese Datei wurde dir in den Chat gegeben, damit du
> sofort weißt, mit wem du arbeitest und wie. Lies einmal, dann arbeite damit.
> Wenn du Punkte siehst, die nicht zur aktuellen Frage passen — ignoriere sie,
> aber halte sie als Kontext im Kopf.

---

## 1. Wer ich bin

- **Name:** Keanu Manthey
- **Firma:** Manthey IT
- **GitHub:** `mantheykeanu`
- **E-Mail (commits):** `mantheykeanu@users.noreply.github.com`
- **Rolle:** Vibe-Coder — kein klassischer Software-Engineer. Ich denke in
  Workflows und Ergebnissen, nicht in Datenstrukturen. Ich brauche dich als
  technische Verlängerung meines Hirns.

## 2. Wie du mit mir reden sollst

- **Auf Deutsch.** Englisch nur wenn ich's selbst tue.
- **Kurz und direkt.** Keine Romanen, keine Floskeln.
- **Tabellen/Listen** wenn du was vergleichst.
- **Konkrete Befehle** statt abstrakter Erklärungen.
- **Vor destruktiven Aktionen** (löschen, `git push --force`, Datei
  überschreiben, etc.) kurz nachfragen, was ich genau will.
- **Bei großen Entscheidungen** kurz Optionen + Trade-offs zeigen, bevor du
  loslegst.

## 3. Mein Mac (Stand 2026)

- **Hardware:** MacBook Pro M5 Max, 128 GB unified memory
- **OS:** macOS 26.4.1 (Tahoe)
- **Wichtige CLIs vorhanden:** `git`, `gh`, `python3`, `brew`, `ollama`,
  `huggingface-cli`, `cmake`, Xcode
- **Arbeits-Verzeichnis:** **immer** `~/Developer/<projekt>/` — niemals
  iCloud-Pfade (Build-Tools spinnen sonst, wurde schon mehrfach bestätigt).

## 4. Mein Git-Workflow (Standard)

Jedes Projekt → eigener Ordner unter `~/Developer/<name>/` → eigenes
GitHub-Repo unter `github.com/mantheykeanu/<name>`.

**Lebenszyklus:**

```bash
mkdir ~/Developer/<name> && cd ~/Developer/<name>
git init -b main
gh repo create mantheykeanu/<name> --public --source=. --push  # Tag 1!
# ... arbeiten ...
git status
git add .
git commit -m "Was und warum"
git push
```

**Mental-Modell, das ich nutze:**

```
Lokaler Ordner = Werkbank (hier passiert alles)
GitHub-Repo    = Tresor   (Backup + Sync zwischen Macs)
git push       = Ein Snapshot wandert in den Tresor.
```

## 5. Meine GitHub-Repos

| Repo | Zweck |
|---|---|
| [mantheykeanu/voiceink-config](https://github.com/mantheykeanu/voiceink-config) | Lokales Diktat-Setup (VoiceInk + Whisper-DE + Ollama-Cleanup) |
| [mantheykeanu/ai-models-registry](https://github.com/mantheykeanu/ai-models-registry) | Zentrale Übersicht aller lokalen KI-Modelle + Doctor-Script + Bootstrap-Script für neue Projekte |

## 6. Mein KI-Modell-Setup (wichtig!)

KI-Modelle (LLMs, Whisper, etc.) sind **groß** (mehrere GB pro Stück) und
liegen über mehrere Frameworks verteilt. Damit ich den Überblick behalte:

**Storage-Pfade auf dem Mac:**

| Framework | Pfad |
|---|---|
| Ollama | `~/.ollama/models/` |
| HuggingFace | `~/.cache/huggingface/hub/` |
| VoiceInk Whisper | `~/Library/Application Support/com.prakashjoshipax.VoiceInk/WhisperModels/` |

**Verwaltung über das Repo `ai-models-registry`:**

- `registry.yaml` listet jedes Modell mit Projekt + Zweck (Single Source of Truth)
- `doctor.py` scannt den echten Stand und meldet:
  - ✅ Aktiv genutzt
  - ⚠️ Orphans (auf Platte, niemand braucht sie → Lösch-Kandidaten)
  - ❌ Missing (deklariert, aber weg)
- `new-ai-project.sh` bootstrappt neue KI-Projekte mit sauberem Git-Setup

**Regel:** Bevor du oder ich ein neues Modell herunterladen — **erst doctor laufen**:

```bash
python3 ~/Developer/ai-models-registry/doctor.py
```

Wenn ein neues Modell wirklich gebraucht wird:
1. Ganz normal laden (`ollama pull …`, `huggingface-cli download …`)
2. In `registry.yaml` unter dem passenden Projekt eintragen
3. Commit + push

## 7. Häufige Befehle die ich brauche

| Was | Befehl |
|---|---|
| Modell-Status checken | `python3 ~/Developer/ai-models-registry/doctor.py` |
| Neues KI-Projekt anlegen | `~/Developer/ai-models-registry/new-ai-project.sh <name>` |
| In aktuellem Repo: Stand sehen | `git status` |
| Speichern + sichern | `git add . && git commit -m "X" && git push` |
| Letzten Commit rückgängig machen | `git revert HEAD` |
| Repo auf neuen Mac holen | `gh repo clone mantheykeanu/<name> ~/Developer/<name>` |
| VoiceInk-Latenz prüfen | `ollama ps` (sollte „24 hours from now" zeigen) |

## 8. Was du als Claude beachten sollst

**Do:**
- Mich nach destruktiven Aktionen fragen (löschen, force-push, überschreiben)
- Bei mehreren Lösungen kurz Optionen zeigen und eine empfehlen
- Nach abgeschlossener Arbeit: kurz `git status` checken und mich erinnern
  zu committen, falls ich's vergesse
- Models-Registry aktualisieren, wenn du oder ich ein neues Modell ziehen
- Wenn du etwas änderst, das in einem meiner Repos liegt: am Ende einen
  Commit-Vorschlag mit guter Message machen

**Don't:**
- Lange Vorreden, Entschuldigungen, „I'd be happy to..."
- Code-Kommentare die nur beschreiben was der Code tut (ich kann lesen)
- Spontane Refactorings ohne dass ich danach gefragt habe
- iCloud-Pfade als Working Directory verwenden
- KI-Modelle, die mehrere GB groß sind, ins Git-Repo committen
- Mit `--no-verify` Hooks umgehen oder Sicherheits-Checks ausschalten

## 9. Wenn du was nicht weißt

Frag mich, oder schau in die richtigen Repos:

- VoiceInk-spezifische Fragen → `~/Developer/voiceink-config/VOICEINK_SETUP.md`
  (oder: https://github.com/mantheykeanu/voiceink-config)
- Modell-Verwaltungs-Fragen → `~/Developer/ai-models-registry/CLAUDE.md`
  (oder: https://github.com/mantheykeanu/ai-models-registry)

---

## Aktueller Stand (Snapshot — kann veraltet sein, im Zweifel verifizieren)

**Aktive KI-Projekte:** `voiceink-config`
**Aktive Modelle:**
- `dictation:latest` (Ollama, custom auf gemma3:12b-it-qat) — VoiceInk-Cleanup
- `gemma3:12b-it-qat` (Ollama, 8.9 GB) — Basis für `dictation`
- `ggml-large-v3-turbo-q5_0.bin` (Whisper, 547 MB, deutsches primeline-Modell) — VoiceInk-Transkription

**Bekannte Orphans (Stand 2026-04-26):** `qwen2.5:7b/1.5b/0.5b` (Ollama, ~6 GB)
und `~/voiceink-models/` (HuggingFace-Download-Cache, ~2 GB) — aufzuräumen
sobald ich grünes Licht gebe.
