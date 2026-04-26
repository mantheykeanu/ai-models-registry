#!/usr/bin/env bash
#
# new-ai-project.sh — startet ein neues KI-Projekt mit sauberem Setup.
#
# Was es macht:
#   1. Erstellt ~/Developer/<projekt-name>/
#   2. git init + Templates: CLAUDE.md, README.md, .gitignore
#   3. Initial Commit
#   4. (Standard) GitHub-Repo anlegen + pushen
#
# Aufruf:
#   ~/Developer/ai-models-registry/new-ai-project.sh <projekt-name>
#   ~/Developer/ai-models-registry/new-ai-project.sh <projekt-name> --private
#   ~/Developer/ai-models-registry/new-ai-project.sh <projekt-name> --no-github

set -euo pipefail

# ---- Args parsen ----------------------------------------------------------

PROJECT_NAME=""
VISIBILITY="--public"
CREATE_GITHUB=true

for arg in "$@"; do
  case "$arg" in
    --private)    VISIBILITY="--private" ;;
    --public)     VISIBILITY="--public" ;;
    --no-github)  CREATE_GITHUB=false ;;
    -h|--help)
      sed -n '3,15p' "$0"
      exit 0
      ;;
    --*)
      echo "Unbekannte Option: $arg" >&2
      exit 1
      ;;
    *)
      if [[ -z "$PROJECT_NAME" ]]; then
        PROJECT_NAME="$arg"
      else
        echo "Mehrere Projektnamen angegeben — nur einer erlaubt." >&2
        exit 1
      fi
      ;;
  esac
done

if [[ -z "$PROJECT_NAME" ]]; then
  echo "Fehler: Projektname fehlt." >&2
  echo "Aufruf: $(basename "$0") <projekt-name> [--private] [--no-github]" >&2
  exit 1
fi

if ! [[ "$PROJECT_NAME" =~ ^[a-z0-9][a-z0-9_-]*$ ]]; then
  echo "Fehler: Projektname '$PROJECT_NAME' ungültig." >&2
  echo "Erlaubt: kleine Buchstaben, Zahlen, Bindestrich, Unterstrich (Start: Buchstabe/Zahl)." >&2
  exit 1
fi

# ---- Prerequisites prüfen -------------------------------------------------

command -v git >/dev/null 2>&1 || { echo "git fehlt." >&2; exit 1; }
if $CREATE_GITHUB; then
  command -v gh >/dev/null 2>&1 || { echo "gh fehlt. Installiere mit: brew install gh" >&2; exit 1; }
  gh auth status >/dev/null 2>&1 || { echo "Nicht bei GitHub angemeldet. Lauf: gh auth login" >&2; exit 1; }
fi

# ---- Pfade ----------------------------------------------------------------

DEV_DIR="$HOME/Developer"
PROJECT_DIR="$DEV_DIR/$PROJECT_NAME"

mkdir -p "$DEV_DIR"

if [[ -e "$PROJECT_DIR" ]]; then
  echo "Fehler: $PROJECT_DIR existiert bereits." >&2
  exit 1
fi

GH_USER=$(gh api user --jq .login 2>/dev/null || echo "DEIN-USER")
TODAY=$(date +%Y-%m-%d)

# ---- Projekt anlegen ------------------------------------------------------

echo "→ Erstelle $PROJECT_DIR"
mkdir "$PROJECT_DIR"
cd "$PROJECT_DIR"

git init -b main >/dev/null

# ---- Templates schreiben --------------------------------------------------

cat > CLAUDE.md <<EOF
# Claude Code Briefing — $PROJECT_NAME

Diese Datei wird von Claude Code automatisch geladen, sobald jemand diesen
Ordner öffnet. Sie hält den Kontext fest, damit du (Claude) sofort weißt,
worum es geht und wie der User arbeitet.

---

## Rolle für Claude

User ist **Keanu (Manthey IT)**, Vibe-Coder — kein Software-Engineer.
Halte Antworten:
- **Auf Deutsch**
- **Kurz und direkt**, mit konkreten Befehlen statt abstrakten Erklärungen
- **Mit Tabellen/Listen** wenn du was vergleichst
- **Vor destruktiven Aktionen** (löschen, push --force) immer kurz nachfragen

## Worum geht's in diesem Projekt

> _TODO Keanu: kurz beschreiben, was dieses Projekt tut und warum es existiert._

## KI-Modelle, die hier gebraucht werden

Bevor du irgendein Modell herunterlädst — **erst prüfen ob's schon da ist**:

\`\`\`bash
python3 ~/Developer/ai-models-registry/doctor.py
\`\`\`

Wenn ein neues Modell wirklich nötig ist:
1. Lade es ganz normal (\`ollama pull …\`, \`huggingface-cli download …\`)
2. Trage es in \`~/Developer/ai-models-registry/registry.yaml\` ein
   (unter \`projects.$PROJECT_NAME.models\` — Block ggf. neu anlegen)
3. Commit + push die Registry-Änderung

## Git-Workflow (für jeden Stand der Arbeit)

\`\`\`bash
git status
git add .
git commit -m "Was und warum"
git push
\`\`\`

## Verbundene Repos

| Zweck | GitHub |
|---|---|
| Dieses Projekt | https://github.com/$GH_USER/$PROJECT_NAME |
| AI Models Registry | https://github.com/$GH_USER/ai-models-registry |
EOF

cat > README.md <<EOF
# $PROJECT_NAME

> _Kurze Beschreibung was dieses Projekt macht._

## Setup

\`\`\`bash
gh repo clone $GH_USER/$PROJECT_NAME ~/Developer/$PROJECT_NAME
cd ~/Developer/$PROJECT_NAME
\`\`\`

## Modelle

Dieses Projekt nutzt KI-Modelle, die zentral in
[ai-models-registry](https://github.com/$GH_USER/ai-models-registry) verwaltet werden.

Status checken:
\`\`\`bash
python3 ~/Developer/ai-models-registry/doctor.py
\`\`\`

## Erstellt am
$TODAY
EOF

cat > .gitignore <<'EOF'
# macOS
.DS_Store

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/
.env

# Claude Code
.claude/

# AI-Modelle (gehören NICHT ins Repo — über ai-models-registry verwaltet)
*.bin
*.gguf
*.safetensors
*.pt
*.pth
*.onnx
modelle/
models/

# Build-Output / Caches
dist/
build/
*.log
EOF

# ---- Initial Commit -------------------------------------------------------

git add CLAUDE.md README.md .gitignore
git commit -m "Initial: $PROJECT_NAME via new-ai-project.sh" >/dev/null

echo "→ Initial Commit angelegt"

# ---- GitHub-Repo (optional) -----------------------------------------------

if $CREATE_GITHUB; then
  echo "→ Lege GitHub-Repo an ($VISIBILITY)..."
  gh repo create "$GH_USER/$PROJECT_NAME" $VISIBILITY \
    --source=. --remote=origin \
    --description "$PROJECT_NAME — neues KI-Projekt" \
    >/dev/null
  # Workaround für gelegentliches GitHub-Backend-Race
  sleep 2
  git push -u origin main >/dev/null 2>&1 || git push -u origin main
  echo "→ Gepusht zu https://github.com/$GH_USER/$PROJECT_NAME"
fi

# ---- Done -----------------------------------------------------------------

echo
echo "✅ Projekt '$PROJECT_NAME' fertig eingerichtet."
echo
echo "   Lokal:   $PROJECT_DIR"
if $CREATE_GITHUB; then
  echo "   GitHub:  https://github.com/$GH_USER/$PROJECT_NAME"
fi
echo
echo "   Nächste Schritte:"
echo "     cd $PROJECT_DIR"
echo "     # Claude Code in diesem Ordner öffnen — die CLAUDE.md lädt automatisch"
echo "     # CLAUDE.md und README.md mit Projekt-Beschreibung füllen"
echo
