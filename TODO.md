# TODO

Backlog technique de **general-knowledge** — tâches actionnables, à mon usage et à celui de Claude.

> Voir la charte du parc `conventions-suivi-taches.adoc` : ce fichier est le backlog technique
> (*comment* faire). Pas de `ROADMAP.md` dans ce dépôt pour l'instant, donc aucun renvoi de jalon ici.

## Documentation Antora (docs/)

- [ ] `docs/modules/nav.adoc` est vide alors qu'`antora.yml` le référence comme seule nav (docs/antora.yml:6) → le menu de doc ne contient rien au build ; y ajouter au moins l'entrée `index.adoc`
- [ ] Déplacer/renommer le nav vers l'emplacement canonique `docs/modules/ROOT/nav.adoc`
- [ ] Supprimer le scaffold Antora mort `docs/modules/comprehensive-module/` (attachments/examples/images/pages/partials — README.adoc placeholders jamais peuplés, non référencé dans `antora.yml`)
- [ ] Réécrire `docs/modules/ROOT/pages/index.adoc` : le texte actuel est un scaffold non adapté, il pointe vers un dossier `main/` qui n'existe pas dans ce dépôt (le contenu réel vit dans `content/`)
- [ ] Créer `.repo-meta.json` à la racine (le repo est déjà répertorié dans `repos-meta/REPOS_INDEX.md:137`)

## README

- [ ] Corriger le lien `content/build/antora/index.html` → `content/build/culture-generale/antora/index.html` (composant Antora nommé `culture-generale`, cf. content/antora.yml:1)
- [ ] Corriger le lien `docs/build/antora/index.html` → `docs/build/ma-documentation/index.html` (composant Antora nommé `ma-documentation`, cf. docs/antora.yml:1)
- [ ] Ajouter une description courte en citation (`>`) sous l'en-tête du README
- [ ] Préfixer la section TL;DR de l'émoji réservé `⚡` (`== ⚡ TL;DR`)

## CI/CD

- [ ] Clarifier la répartition des workflows entre `.gitea/workflows/docs.yml` (déploiement nginx interne) et `.github/workflows/publish.yml` (GitHub Pages) : double publication voulue, ou l'un des deux devrait être retiré ?
- [ ] Pas de workflow de scan de secrets (`secrets-scan.yml`) sur ce dépôt

## Commits

- [ ] Faire suivre les commits futurs le format `<emoji> <type>(<scope>): <description>` de bout en bout (des écarts subsistent sur des commits récents, ex. `22e7cb3`, `3a25a8d`) — pas de réécriture rétroactive de l'historique
