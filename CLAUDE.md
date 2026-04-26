# Claude Code Briefing — AI Models Registry

Diese Datei wird von Claude Code automatisch geladen, sobald jemand diesen Ordner
öffnet. Sie enthält den vollständigen Kontext, damit Claude alle Fragen des Users
beantworten kann, ohne dass er Sachen wiederholen muss.

---

## Rolle für Claude

Du bist hier, weil der User (Keanu, Manthey IT) Hilfe bei seinem **lokalen
KI-Modell-Bestand** braucht. Er ist **Vibe-Coder** — kein Software-Engineer.
Halte Antworten:

- **Auf Deutsch** (sofern er nicht ausdrücklich Englisch will)
- **Kurz und direkt** — keine Roman-Antworten
- **Mit Tabellen oder Listen** wenn du was vergleichst
- **Mit konkreten Befehlen** statt abstrakten Erklärungen
- **Vor destruktiven Aktionen** (löschen, überschreiben, push --force)
  immer kurz nachfragen, was er will

## Was dieses Repo macht

Eine zentrale Inventur aller KI-Modelle auf seinem Mac.

**Problem:** KI-Modelle (LLMs für Ollama, Whisper-Modelle, HuggingFace-Downloads)
sind groß (mehrere GB pro Stück) und liegen über mehrere Frameworks/Pfade verteilt.
Ohne Registry verliert man den Überblick, hat doppelte Downloads, und weiß nicht
mehr, ob ein Modell noch von irgendwem gebraucht wird.

**Lösung in diesem Repo:**
- `registry.yaml` — Hand-gepflegte Wahrheits-Quelle: welches Projekt nutzt welches Modell, wofür.
- `doctor.py` — Scannt die echten Storage-Pfade (Ollama, Whisper, HF-Cache, eigene
  Pfade) und vergleicht mit `registry.yaml`. Output:
  - ✅ Aktiv: deklariert + vorhanden
  - ⚠️  Orphans: vorhanden, aber von niemandem deklariert → Lösch-Kandidaten
  - ❌ Missing: deklariert, aber nicht vorhanden → Re-Download nötig
  - 💡 Copy-paste-Befehle zum Aufräumen

## Storage-Pfade auf diesem Mac

| Framework | Standard-Pfad | Override-Mechanismus |
|---|---|---|
| Ollama | `~/.ollama/models/` | env `OLLAMA_MODELS=...` |
| HuggingFace (`huggingface-cli`, transformers, MLX) | `~/.cache/huggingface/hub/` | env `HF_HOME=...` |
| VoiceInk Whisper-Modelle | `~/Library/Application Support/com.prakashjoshipax.VoiceInk/WhisperModels/` | hartcodiert in App |
| huggingface-cli mit `--local-dir` | wo angegeben (z.B. `~/voiceink-models/`) | per Aufruf |

**Migration zu zentralem Pool** (z.B. `/Users/Shared/AI-Models/`) ist möglich,
aber **noch nicht passiert**. Falls der User danach fragt: erkläre die env-Vars
oben, warne dass laufende Modelle vor dem Umzug ge-`ollama rm`'t bzw. neu gepullt
werden müssen, und biete an, eine `setup-shared-storage.sh` zu schreiben.

## Verbundene Projekte (aktueller Stand)

Siehe `registry.yaml`. Aktuell deklariert:

- **voiceink** — Repo: https://github.com/mantheykeanu/voiceink-config
  - Lokal: `~/Developer/voiceink-config/`
  - Modelle: `gemma3:12b-it-qat`, `dictation:latest`, `ggml-large-v3-turbo-q5_0.bin` (+ generic-backup)

Wenn er ein neues KI-Projekt anfängt, soll er entweder:
- Einen neuen Block unter `projects:` in `registry.yaml` anlegen, **oder**
- Einen `models.yaml`-Block in das jeweilige Projekt-Repo legen und hier
  referenzieren (Multi-Repo-Variante — falls er es zukünftig will, biete an
  den Doctor entsprechend zu erweitern)

## Häufige User-Fragen + Antworten

### "Welche Modelle hab ich gerade auf dem Mac?"

```bash
cd ~/Developer/ai-models-registry && python3 doctor.py
```

### "Was kann ich gefahrlos löschen?"

→ Doctor laufen lassen. Alles unter „⚠️ Orphans" ist sicher löschbar. Die
copy-paste-Befehle stehen direkt drunter.

### "Ich hab ein neues Modell geladen — wie trage ich's ein?"

`registry.yaml` öffnen, neuen Eintrag unter dem passenden Projekt anlegen:

```yaml
- name: <ollama-name oder dateiname>
  framework: ollama  # oder whisper.cpp, huggingface, mlx
  purpose: "Wofür brauche ich das"
  required: true
```

Dann: `python3 doctor.py` → muss unter ✅ erscheinen, nicht mehr unter ⚠️.

### "Wie pushe ich Änderungen?"

```bash
cd ~/Developer/ai-models-registry
git status
git add .
git commit -m "Was geändert wurde"
git push
```

### "Wie kriege ich das Repo auf einen neuen Mac?"

```bash
gh repo clone mantheykeanu/ai-models-registry ~/Developer/ai-models-registry
```

Voraussetzung: `gh auth login` ist einmal gelaufen.

### "Wie starte ich ein neues KI-Projekt?"

```bash
~/Developer/ai-models-registry/new-ai-project.sh <projekt-name>
```

Default: legt `~/Developer/<projekt-name>/` an, schreibt CLAUDE.md / README.md /
.gitignore-Templates rein, macht Initial Commit, erstellt **public** GitHub-Repo
und pusht. Flags: `--private`, `--no-github`.

Die generierte CLAUDE.md verweist automatisch auf diese Registry — neue Projekte
sind also sofort an die zentrale Modell-Verwaltung angeschlossen.

### "Wie ändere ich Storage-Pfade?"

In `registry.yaml` unter `storage:` einfach den Pfad anpassen. Der Doctor liest
ihn beim nächsten Lauf neu.

## Konventionen

- **Kein Code in der Registry-YAML** — sie ist Daten, kein Programm.
- **Keine Modell-Dateien committen** — nur die Metadaten. Modelle sind über
  `ollama pull` / `huggingface-cli download` reproduzierbar.
- **Bei Code-Änderungen am `doctor.py`**: kurz die Hauptfälle gegen den
  realen Mac-Stand verifizieren, bevor du committest.

## Was hier *nicht* hingehört

- Fragen zur VoiceInk-Konfiguration selbst → die werden vom Repo
  `voiceink-config` (`~/Developer/voiceink-config/`) beantwortet, das eine
  eigene `VOICEINK_SETUP.md` hat.
- Allgemeine Mac-Setup-Fragen (Brew, Xcode, etc.) → außerhalb des Scopes.

## Verbundene Repos

| Zweck | GitHub |
|---|---|
| Diese Registry | https://github.com/mantheykeanu/ai-models-registry |
| VoiceInk-Konfig | https://github.com/mantheykeanu/voiceink-config |
