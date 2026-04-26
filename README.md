# AI Models Registry

**Zweck:** Eine zentrale Übersicht über alle KI-Modelle auf dem Mac.
Welches Modell liegt wo, welches Projekt braucht es, was kann weg.

So sehe ich auf einen Blick:
- ✅ Was ist aktiv genutzt
- ⚠️ Was ist „Orphan" (auf Platte, aber niemand braucht's mehr)
- ❌ Was fehlt (deklariert, aber nicht da)

## Schnellstart

```bash
cd ~/Developer/ai-models-registry
python3 doctor.py
```

Output erklärt sich selbst — am Ende stehen copy-paste-bereite Cleanup-Befehle.

## Wenn ich ein neues Modell lade

1. **Ganz normal über sein Framework laden** (`ollama pull …`, `huggingface-cli download …`, etc.)
2. **In `registry.yaml` eintragen** — unter dem Projekt, das es braucht
3. **`python3 doctor.py`** zum Verify

## Wenn ich ein Projekt nicht mehr brauche

1. Block in `registry.yaml` rauslöschen (oder `active: false` setzen)
2. `python3 doctor.py` zeigt die zugehörigen Modelle als Orphans + die Lösch-Befehle
3. Befehle ausführen → Platte ist frei

## Git-Workflow (nach jeder Änderung)

```bash
git status                                # was hat sich geändert?
git add .
git commit -m "Was und warum"
git push                                  # in die Cloud (GitHub)
```

Brauchst du mehr Git-Hilfe oder eine andere Frage zu dem Setup?
→ Öffne diesen Ordner in Claude Code, die [CLAUDE.md](CLAUDE.md) macht den Rest.

## Auf einem neuen Mac aufsetzen

```bash
gh repo clone mantheykeanu/ai-models-registry ~/Developer/ai-models-registry
cd ~/Developer/ai-models-registry
python3 doctor.py
```

## Neues KI-Projekt starten

Statt händisch `mkdir`, `git init`, `gh repo create` etc. — einfach:

```bash
~/Developer/ai-models-registry/new-ai-project.sh mein-projekt
```

Das Script erstellt `~/Developer/mein-projekt/` mit `CLAUDE.md`, `README.md`,
`.gitignore`, macht den ersten Commit und legt direkt ein GitHub-Repo an
(default public, mit `--private` private, mit `--no-github` ohne).

## Dateien hier drin

| Datei | Zweck |
|---|---|
| `registry.yaml` | Single Source of Truth: alle Projekte + ihre Modelle |
| `doctor.py` | Scannt Mac, vergleicht gegen `registry.yaml`, gibt Report aus |
| `new-ai-project.sh` | Startet neues KI-Projekt mit sauberem Setup |
| `CLAUDE.md` | Briefing für Claude Code — beantwortet Fragen, navigiert das System |
| `README.md` | Diese Datei |
