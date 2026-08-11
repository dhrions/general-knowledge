#!/usr/bin/env python3
"""Construit le corps JSON de la requête de création de PR Gitea.

Usage: build_pr_payload.py <titre> <branche> <fichier_body>
"""

import json
import sys

title, branch, body_path = sys.argv[1], sys.argv[2], sys.argv[3]
with open(body_path, encoding="utf-8") as f:
    body = f.read()

print(json.dumps({"title": title, "body": body, "head": branch, "base": "main"}))
