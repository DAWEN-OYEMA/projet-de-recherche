# 🏫 Gestion Scolaire

Application web complète de gestion scolaire développée avec **Python 3.12**, **Streamlit** et **MySQL**.

## Fonctionnalités

| Module | Description |
|--------|-------------|
| 📊 **Tableau de bord** | KPI, graphiques statistiques, recettes et impayés |
| 👨‍🎓 **Élèves** | CRUD, import/export Excel, fiche PDF imprimable |
| 👨‍🏫 **Enseignants** | Gestion, matières, salaires |
| 🏛️ **Classes** | Création, titulaire, effectifs |
| 📚 **Cours** | Emploi du temps, matières, horaires |
| 💰 **Paiements** | Frais scolaires, encaissements, reçus PDF |
| 📝 **Notes** | Saisie, moyennes, classement, bulletins |
| 📑 **Rapports** | Export PDF et Excel |

### Rôles utilisateur

- **Administrateur** — accès complet
- **Enseignant** — élèves, classes, cours, notes
- **Caissier** — élèves, paiements, rapports

## Prérequis

- Python 3.12+
- MySQL (WampServer en local)
- pip

## Installation (développement local)

### 1. Cloner le projet

```bash
cd GestionEcole
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer la base de données

Copiez `.env.example` vers `.env` et modifiez les paramètres :

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=gestion_ecole
```

> **WampServer** : démarrez WampServer, laissez `DB_PASSWORD` vide si root n'a pas de mot de passe.

### 5. Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`.

### Compte par défaut

| Utilisateur | Mot de passe | Rôle |
|-------------|--------------|------|
| `admin` | `admin123` | Administrateur |

> Les tables MySQL et le compte admin sont créés automatiquement au premier lancement.

## Structure du projet

```
GestionEcole/
├── app.py              # Point d'entrée Streamlit
├── config.py           # Configuration (.env)
├── database.py         # SQLAlchemy + init DB
├── requirements.txt
├── .env                # Variables d'environnement (local)
├── .env.example
├── models/             # Modèles SQLAlchemy
│   ├── user.py
│   ├── eleve.py
│   ├── enseignant.py
│   ├── matiere.py
│   ├── classe.py
│   ├── cours.py
│   ├── frais.py
│   ├── paiement.py
│   └── note.py
├── pages/              # Modules de l'interface
│   ├── dashboard.py
│   ├── eleves.py
│   ├── enseignants.py
│   ├── classes.py
│   ├── cours.py
│   ├── paiements.py
│   ├── notes.py
│   └── rapports.py
├── utils/              # Auth, UI, export, helpers
├── assets/photos/      # Photos des élèves
└── exports/            # Fichiers PDF/Excel générés
```

## Déploiement sur Streamlit Community Cloud

### 1. Pousser le code sur GitHub

Assurez-vous que le dépôt contient `app.py` et `requirements.txt` à la racine de `GestionEcole/`.

### 2. Créer l'application sur Streamlit Cloud

1. Allez sur [share.streamlit.io](https://share.streamlit.io)
2. Connectez votre dépôt GitHub
3. Définissez le chemin du fichier principal : `GestionEcole/app.py`

### 3. Configurer les secrets (base de données distante)

Dans **Settings → Secrets**, ajoutez les variables d'environnement :

```toml
DB_HOST = "votre-host-mysql.com"
DB_PORT = "3306"
DB_USER = "votre_utilisateur"
DB_PASSWORD = "votre_mot_de_passe"
DB_NAME = "gestion_ecole"
APP_TITLE = "Gestion Scolaire"
SCHOOL_NAME = "École Primaire Excellence"
```

> Streamlit Cloud injecte ces secrets comme variables d'environnement. Le fichier `config.py` les lit via `python-dotenv` et `os.getenv()`.

### 4. Base de données distante

Utilisez un hébergeur MySQL compatible (PlanetScale, Railway, Aiven, etc.) et mettez à jour les secrets — **aucune modification de code n'est nécessaire**.

## Technologies

- **Streamlit** — interface web
- **MySQL** — base de données
- **SQLAlchemy** — ORM et relations
- **Pandas** — manipulation de données
- **Plotly** — graphiques interactifs
- **bcrypt** — chiffrement des mots de passe
- **ReportLab** — génération PDF
- **openpyxl** — import/export Excel

## Licence

Projet éducatif — libre d'utilisation et de modification.
