#!/usr/bin/env python3
"""
AI Models Doctor — gleicht registry.yaml mit dem echten Festplatten-Stand ab.

Aufruf:
    python3 doctor.py

Liest registry.yaml im selben Ordner. Scannt:
  - Ollama (via `ollama list`)
  - VoiceInk Whisper-Modelle (Dateien in WhisperModels/)
  - Hugging Face Cache
  - Custom-Pfade aus storage.custom

Gibt aus:
  - Storage-Übersicht (wo wie viel)
  - ✅ Aktiv: deklariert + vorhanden
  - ⚠️  Orphans: vorhanden, aber von keinem Projekt deklariert (Lösch-Kandidaten)
  - ❌ Missing: deklariert, aber nicht da (Re-Download nötig)
  - 💡 Aufräum-Befehle (copy-paste-bereit)
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Fehler: PyYAML fehlt. Installiere mit:  pip3 install pyyaml", file=sys.stderr)
    sys.exit(1)


REGISTRY_PATH = Path(__file__).parent / "registry.yaml"


def expand(p: str) -> Path:
    return Path(os.path.expanduser(p))


def human_size(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def dir_size(path: Path) -> int:
    if not path.exists():
        return 0
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += (Path(root) / f).stat().st_size
            except (OSError, FileNotFoundError):
                pass
    return total


def list_ollama_models() -> list[dict]:
    """Returns [{name, id, size_str}] from `ollama list`."""
    try:
        out = subprocess.check_output(["ollama", "list"], text=True, stderr=subprocess.DEVNULL)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    models = []
    for line in out.strip().split("\n")[1:]:  # skip header
        parts = re.split(r"\s{2,}", line.strip())
        if len(parts) >= 3:
            models.append({"name": parts[0], "id": parts[1], "size": parts[2]})
    return models


def scan_whisper_dir(path: Path) -> list[dict]:
    """Find .bin files in Whisper-Models dir."""
    if not path.exists():
        return []
    files = []
    for f in path.iterdir():
        if f.is_file():
            files.append({"name": f.name, "path": str(f), "size_bytes": f.stat().st_size})
    return files


def main():
    if not REGISTRY_PATH.exists():
        print(f"Fehler: {REGISTRY_PATH} nicht gefunden.", file=sys.stderr)
        sys.exit(1)

    with open(REGISTRY_PATH) as f:
        reg = yaml.safe_load(f)

    storage = reg.get("storage", {})
    projects = reg.get("projects", {}) or {}
    acknowledged = {o["name"] for o in (reg.get("known_orphans_acknowledged") or [])}

    # Sammle alle deklarierten Modelle (Name + Framework)
    declared = []  # [(framework, name, project)]
    for proj_name, proj in projects.items():
        if not proj.get("active", True):
            continue
        for m in proj.get("models", []):
            declared.append((m["framework"], m["name"], proj_name, m))

    declared_ollama = {name for fw, name, _, _ in declared if fw == "ollama"}
    declared_whisper = {name for fw, name, _, _ in declared if fw == "whisper.cpp"}

    print("=" * 70)
    print("  AI Models Doctor")
    print("=" * 70)

    # --- Storage-Übersicht ---
    print("\n📊 Storage-Übersicht\n")
    storage_paths = {
        "Ollama": expand(storage.get("ollama", "~/.ollama/models")),
        "HuggingFace-Cache": expand(storage.get("huggingface_cache", "~/.cache/huggingface/hub")),
        "VoiceInk-Whisper": expand(storage.get("voiceink_whisper", "")),
    }
    for name, path in storage_paths.items():
        size = dir_size(path)
        marker = "" if path.exists() else "  (existiert nicht)"
        print(f"  {name:20s} {human_size(size):>10s}   {path}{marker}")
    for label, p in (storage.get("custom") or {}).items():
        path = expand(p)
        size = dir_size(path)
        marker = "" if path.exists() else "  (existiert nicht)"
        print(f"  custom/{label:13s} {human_size(size):>10s}   {path}{marker}")

    total_storage = sum(dir_size(p) for p in storage_paths.values()) + sum(
        dir_size(expand(p)) for p in (storage.get("custom") or {}).values()
    )
    print(f"  {'─' * 50}")
    print(f"  {'Gesamt':20s} {human_size(total_storage):>10s}")

    # --- Ist-Stand sammeln ---
    ollama_present = list_ollama_models()
    whisper_path = expand(storage.get("voiceink_whisper", ""))
    whisper_files = scan_whisper_dir(whisper_path) if storage.get("voiceink_whisper") else []

    # --- Aktiv genutzt (deklariert + vorhanden) ---
    print("\n✅ Aktiv genutzt (deklariert + vorhanden)\n")
    found_active = False
    ollama_present_names = {m["name"] for m in ollama_present}
    whisper_present_names = {f["name"] for f in whisper_files}

    for fw, name, project, meta in declared:
        if fw == "ollama" and name in ollama_present_names:
            size = next((m["size"] for m in ollama_present if m["name"] == name), "?")
            print(f"  [ollama]  {name:30s} {size:>10s}   → {project}")
            found_active = True
        elif fw == "whisper.cpp" and name in whisper_present_names:
            size = next(
                (human_size(f["size_bytes"]) for f in whisper_files if f["name"] == name), "?"
            )
            print(f"  [whisper] {name:50s} {size:>10s}   → {project}")
            found_active = True
    if not found_active:
        print("  (nichts aktiv)")

    # --- Orphans (vorhanden, aber nicht deklariert) ---
    print("\n⚠️  Orphans (auf Platte, von keinem Projekt deklariert)\n")
    orphans = []  # (framework, name, size_str, cleanup_cmd)
    cleanup_cmds = []

    for m in ollama_present:
        if m["name"] not in declared_ollama and m["name"] not in acknowledged:
            orphans.append(("ollama", m["name"], m["size"], f"ollama rm {m['name']}"))

    for f in whisper_files:
        if f["name"] not in declared_whisper and f["name"] not in acknowledged:
            orphans.append(
                ("whisper", f["name"], human_size(f["size_bytes"]), f"rm '{f['path']}'")
            )

    for label, p in (storage.get("custom") or {}).items():
        path = expand(p)
        if path.exists():
            using_project = None
            for proj_name, proj in projects.items():
                if not proj.get("active", True):
                    continue
                for m in proj.get("models", []):
                    if m.get("path", "").startswith(str(path)):
                        using_project = proj_name
                        break
            if not using_project and f"custom/{label}" not in acknowledged:
                size = dir_size(path)
                orphans.append(
                    ("custom", f"~/{path.relative_to(Path.home())}/", human_size(size), f"rm -rf '{path}'")
                )

    if not orphans:
        print("  (keine Orphans — sauber!)")
    else:
        for fw, name, size, cmd in orphans:
            print(f"  [{fw:7s}] {name:50s} {size:>10s}")
            cleanup_cmds.append(cmd)

    # --- Missing (deklariert, aber nicht gefunden) ---
    print("\n❌ Missing (deklariert, aber nicht gefunden)\n")
    missing = []
    for fw, name, project, meta in declared:
        if fw == "ollama" and name not in ollama_present_names:
            missing.append((fw, name, project))
        elif fw == "whisper.cpp":
            declared_path = meta.get("path")
            if declared_path and not expand(declared_path).exists():
                missing.append((fw, name, project))
    if not missing:
        print("  (alles da)")
    else:
        for fw, name, project in missing:
            print(f"  [{fw}] {name}   → von {project} gebraucht")

    # --- Aufräum-Befehle ---
    if cleanup_cmds:
        print("\n💡 Cleanup-Befehle (kopieren + ausführen, wenn sicher)\n")
        for cmd in cleanup_cmds:
            print(f"  {cmd}")
        print()

    print("=" * 70)


if __name__ == "__main__":
    main()
