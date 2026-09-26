# Site 2aFormation

Site statique publié sur GitHub Pages à l'adresse https://2aformation.com.

## Modifier le contenu

**Le plus simple : l'interface d'administration.** Connectez-vous sur https://app.pagescms.org avec le compte GitHub, ouvrez ce dépôt, puis modifiez les formations, les chiffres, les tarifs ou l'équipe dans les formulaires. Enregistrez : le site se met à jour tout seul en une à deux minutes.

**Directement sur GitHub :** tous les textes sont dans le dossier `_source/contenu/`.

| Pour changer… | Fichier |
|---|---|
| Chiffres clés, tarifs des formations, coordonnées, équipe | `_source/contenu/site.yml` |
| Diplômes VAE, formules et tarifs VAE | `_source/contenu/vae.yml` |
| Une formation | `_source/contenu/formations/<nom-de-la-formation>.yml` |
| Ajouter une formation | copier un fichier de `_source/contenu/formations/`, le renommer et le modifier |
| Retirer une formation sans la supprimer | ajouter la ligne `publie: false` dans son fichier |
| Mentions légales, confidentialité | `_source/contenu/pages/` |

## Fonctionnement technique

- Les sources du site sont dans `_source/`. Les pages publiées, à la racine du dépôt, sont **générées automatiquement** : ne les modifiez pas à la main, elles seraient écrasées.
- `_source/build.py` assemble les pages à partir de `_source/contenu/` et des gabarits de `gabarits/`.
- À chaque modification sur la branche `main`, GitHub Actions (`.github/workflows/publier.yml`) reconstruit les pages, les enregistre à la racine du dépôt, et GitHub Pages les met en ligne.
- Styles : `_source/static/assets/css/site.css`. Images : `_source/static/assets/img/`.
- Tester en local : `pip install jinja2 pyyaml markdown` puis `python3 build.py` ; le site est généré dans `_site/`.

En cas d'erreur, l'onglet **Actions** du dépôt affiche le message. Le site en ligne reste alors dans sa version précédente.
