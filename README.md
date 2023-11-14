# Export de Stylo en Python

## Installation

Pré-requis : Python3.

Installer et activer un environnement virtuel :

    $ python3 -m venv venv
    $ source venv/bin/activate

Installer les dépendances :

    $ make install

Vous avez aussi besoin d’avoir un Pandoc-API qui tourne quelque part :

https://gitlab.huma-num.fr/ecrinum/stylo/pandoc-api


## Environnement

Créer un fichier d’environnement :

    $ touch .env

Y mettre l’adresse de la Pandoc-API propre à l’environnement, ça peut être :

    SE_PANDOC_API_BASE_URL="http://127.0.0.1:8000/latest/"

Y mettre aussi le token GraqhQL de l’instance Stylo vers laquelle vous pointez :

    SE_GRAPHQL_TOKEN="eyJhbGciO...YPlED4WM"

D’autres variables sont définies dans le fichier `app/config.py`, voir ci-dessous.
Vous pouvez les écraser dans votre fichier `.env`.


## Configuration

Voir le fichier `styloexport/config.py`

### SE_PANDOC_API_BASE_URL

Valeur par défaut : `http://127.0.0.1:8000/latest/`

### SE_PANDOC_API_TIMEOUT

Valeur par défaut : `None` (désactivé)

Temps (en secondes) d’attente de la génération du PDF côté Pandoc-API.

### SE_STYLO_API_TIMEOUT

Valeur par défaut : `None` (désactivé)

Temps (en secondes) d’attente de la requête GRAPHQL côté Stylo.

### SE_ALLOWED_INSTANCE_BASE_URLS

Valeur par défaut : `"https://stylo.huma-num.fr https://stylo-dev.huma-num.fr"`

Liste des URLs d’instances à séparer par des espaces ` ` à partir desquelles l’export est autorisé.

### SE_DOWNLOAD_DIR

Valeur par défaut : `(Path() / "styloexport" / "downloads").resolve()`

Chemin vers lequel sont récupérées les archives et images téléchargées.

### SE_STYLES_DIR

Valeur par défaut : `(Path() / "styloexport" / "styles").resolve()`

Chemin vers lequel sont récupérées les styles téléchargées depuis Zotero.

### SE_STYLES_FIELDS

Valeur par défaut : `humanities`

Liste (séparateur virgule `,`) des catégories de styles Zotero conservées dans notre sous-liste.

### SE_SUPPORTED_IMAGES_EXTENSIONS

Valeur par défaut : `[".png", ".jpg", ".jpeg", ".gif"]`

Liste des extensions autorisées/reconnues pour les images.

### SE_IMAGES_TIMEOUT

Valeur par défaut : `60` (1 minute)

Temps (en secondes) d’attente pour le téléchargement des images des articles.

### SE_GRAPHQL_TOKEN

Valeur par défaut : `""`

JSON token privé qui doit être défini pour accéder aux articles via l’API graphql.

### SE_EDITIONS

Valeur par défaut :

```
SE_EDITIONS = {
    "generique": {
        "name": "Générique",
        "exports": [
            ("originals", "fichiers originaux (md, yaml et bib)"),
            ("html", "conversion HTML"),
            ("tex", "conversion LaTeX"),
            ("pdf", "conversion PDF"),
            ("odt", "conversion ODT (OpenOffice)"),
            ("docx", "conversion DOCX (Word)"),
            ("icml", "conversion ICML (Impress)"),
            ("xml-tei", "conversion XML-TEI"),
            ("xml-erudit", "conversion XML Erudit"),
            ("xml-tei-metopes", "conversion XML-TEI Commons (Métopes)"),
        ],
    },
    "sens-public": {
        "name": "Sens-Public",
        "exports": {
            "all": {
                "name": "Tous les exports",
                "formats": [
                    "originals",
                    "html",
                    "tex",
                    "pdf",
                    "xml-tei",
                    "xml-erudit",
                ],
            }
        },
        "images_path": "media",
    },
}
```

Définition des éditions disponibles et de leurs particularités.
Les clefs `name` sont rendues visibles dans l’interface.


## Lancement

Lancer le serveur local :

    $ make run

Aller sur http://127.0.0.1:5000/


## Développement

Installer les dépendances :

    $ make dev


### Lancer les tests

Lancer la commande :

    $ make test

Optionnellement, la commande `ptw` permet de rafraîchir le lancement des
tests à chaque modification du code (ou des tests).


## Mise à jour des styles bibliographiques

On utilise les styles bibliographiques depuis 
[le site de Zotero](https://www.zotero.org/styles?fields=humanities&dependent=0),
ils sont téléchargés en fonction des domaines définis dans `SE_STYLES_FIELDS` :

    $ make styles

⚠️ Ne pas commiter le fichier `styles/styles-zotero.json` qui est relativement gros !

Pour une mise à jour des styles, il faut commencer par supprimer le contenu du dossier `styles` puis lancer la commande générale `make styles`.

Lors d’un ajout de type de `templates`, il faut ensuite lancer la commande `FLASK_APP=styloexport flask styles custom` afin que les feuilles de style soient copiées dans le dossier principal des `styles`.

### Contribuer

Il faut s’assurer préallablement :

1. Que les tests passent : `make test`
2. Que le code coverage reste à plus de 90% dans le résultat ci-dessus
3. Que le code soit propre : `make lint`


### Ajouter une dépendance au projet

1. Ajouter le nom de la dépendance dans `pyproject.toml`
2. Lancer `make deps`
3. Installer les nouvelles dépendances : `make dev`


## Déploiement

Un exemple avec gunicorn :

    $ pip install gunicorn
    $ make production
