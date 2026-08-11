#!/usr/bin/env python3
"""Revue annuelle des liens morts : retest, recherche de remplacement via l'API
Claude (web_search), application des corrections, préparation de la PR.

Lu par .gitea/workflows/liens-morts.yml. Ne modifie que le texte des URL, jamais
le texte des liens qui les portent (sauf si la nouvelle cible le rend trompeur,
ce que ce script ne juge pas — laissé au relecteur humain de la PR).
"""

import json
import os
import re
import sys

import anthropic
import requests

REPORT_PATH = "broken_links.json"
MODEL = "claude-haiku-4-5"
REQUEST_TIMEOUT = 15


def resolve_path(key: str) -> str | None:
    if os.path.exists(key):
        return key
    for marker in ("content/", "docs/"):
        idx = key.find(marker)
        if idx != -1:
            candidate = key[idx:]
            if os.path.exists(candidate):
                return candidate
    return None


def still_broken(url: str) -> bool:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; adoc-link-checker)"}
    try:
        r = requests.head(url, timeout=REQUEST_TIMEOUT, allow_redirects=True, headers=headers)
        if r.status_code < 400:
            return False
    except requests.RequestException:
        pass
    try:
        r = requests.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True, headers=headers, stream=True)
        return r.status_code >= 400
    except requests.RequestException:
        return True


def find_replacement(client: anthropic.Anthropic, url: str, file_path: str) -> tuple[str | None, str]:
    prompt = (
        f"L'URL suivante est morte (lien inaccessible) dans un site de documentation "
        f"AsciiDoc de culture générale : {url}\n"
        f"Elle est citée dans le fichier {file_path}.\n\n"
        "Cherche un remplacement fiable, dans cet ordre de préférence strict :\n"
        "1. Une version archivée de la même page sur la Wayback Machine "
        "(web.archive.org) — c'est le meilleur choix, il préserve l'intention "
        "originale du rédacteur.\n"
        "2. Si le site a réorganisé ses URL, l'adresse actuelle de la même page "
        "sur le même domaine.\n"
        "3. Sinon, une source équivalente faisant autorité sur le même sujet "
        "(site institutionnel, encyclopédie de référence).\n\n"
        "Réponds STRICTEMENT sous cette forme, sans aucun autre texte :\n"
        "REMPLACEMENT: <URL complète, ou NONE si tu n'as rien trouvé de fiable>\n"
        "NOTE: <une phrase expliquant ton choix, ou ce qui manque si NONE>"
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=[{"type": "web_search_20260209", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )
    text = "\n".join(b.text for b in response.content if b.type == "text")
    m_url = re.search(r"REMPLACEMENT:\s*(\S+)", text)
    m_note = re.search(r"NOTE:\s*(.+)", text)
    note = m_note.group(1).strip() if m_note else "(pas de note fournie)"
    if not m_url or m_url.group(1).strip().upper() == "NONE":
        return None, note
    return m_url.group(1).strip(), note


def main() -> int:
    if not os.path.exists(REPORT_PATH):
        print("Pas de rapport de liens morts.")
        return 0
    with open(REPORT_PATH, encoding="utf-8") as f:
        report = json.load(f)
    if not report:
        print("Aucun lien mort.")
        return 0

    client = anthropic.Anthropic()

    fixed = []  # (file, old_url, new_url, note)
    unresolved = []  # (file, url, note_or_reason)

    for raw_path, entries in report.items():
        path = resolve_path(raw_path)
        if path is None:
            for url, _reason in entries:
                unresolved.append((raw_path, url, "fichier introuvable dans le checkout"))
            continue

        with open(path, encoding="utf-8") as f:
            content = f.read()

        for url, _reason in entries:
            if not still_broken(url):
                print(f"faux positif, toujours vivant : {url}")
                continue

            new_url, note = find_replacement(client, url, path)
            if new_url is None:
                unresolved.append((path, url, note))
                continue

            if url not in content:
                unresolved.append((path, url, "URL introuvable dans le fichier (a peut-être déjà changé)"))
                continue

            content = content.replace(url, new_url)
            fixed.append((path, url, new_url, note))

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    if not fixed:
        print("Aucun remplacement fiable trouvé — pas de PR.")
        return 0

    with open("fixes_commit_message.txt", "w", encoding="utf-8") as f:
        f.write(f"🔗 fix(content): corrige {len(fixed)} lien(s) mort(s) (revue annuelle)\n")

    lines = ["## Liens corrigés\n"]
    for path, old, new, note in fixed:
        lines.append(f"- `{path}`\n  - {old}\n  - → {new}\n  - _{note}_\n")

    if unresolved:
        lines.append("\n## Liens morts sans remplacement trouvé\n")
        lines.append("Laissés inchangés — à chercher manuellement.\n")
        for path, url, note in unresolved:
            lines.append(f"- `{path}` : {url} — {note}\n")

    with open("fixes_summary.md", "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"{len(fixed)} lien(s) corrigé(s), {len(unresolved)} sans remplacement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
