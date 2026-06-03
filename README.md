# RencontresCM

Application de rencontre camerounaise avec architecture modulaire et découplée.

## Architecture

```
/
├── backend/
│   ├── app/
│   │   ├── __init__.py        # Factory & Extensions (CORS, SQLAlchemy)
│   │   ├── models.py          # Modèles SQLAlchemy
│   │   ├── routes/
│   │   │   ├── auth.py        # API Login/Register (Session-based)
│   │   │   ├── members.py     # API Profils, Villes et Communes
│   │   │   └── admin.py       # API de gestion (AlerteGlobale, Modération)
│   │   └── utils/             # Décorateur @admin_required
│   ├── config.py              # Configuration Flask (SQLite, Secret Key)
│   └── run.py                 # Commandes CLI & Lancement
└── frontend/
    ├── static/                # CSS/JS
    └── templates/
        ├── layouts/           # base.html (Tailwind + Alpine.js)
        ├── auth/              # login.html, register.html
        └── main/              # index.html (Filtres asynchrones), profil.html
```

## Installation

1. Installer les dépendances Python :
```bash
pip install -r requirements.txt
```

2. Initialiser la base de données :
```bash
cd backend
python run.py init-db
```

Cela va :
- Créer les tables
- Ajouter les 10 régions du Cameroun comme villes principales
- Ajouter au moins 5 communes/arrondissements pour Douala et Yaoundé
- Créer un compte admin : admin@rencontres.cm / Cm2026!Admin

## Lancement

Lancer l'application :
```bash
cd backend
python run.py
```

L'application sera accessible sur http://localhost:5000

## Fonctionnalités

### Backend (API REST)

- **Authentification** : Login/Register avec sessions
- **Profils** : CRUD pour les profils utilisateurs
- **Régions et Communes** : API pour les villes et quartiers
- **Admin** : Gestion des alertes globales et modération

### Frontend

- **Design Luxury** : Couleurs Rose (#e8536a), Crème (#fdf6f0), Charcoal (#1c1c2e)
- **Tailwind CSS** : Styling moderne
- **Alpine.js** : Interactivité côté client
- **Filtres asynchrones** : Filtrage des profils sans rechargement
- **Communes dynamiques** : Mise à jour automatique des communes selon la ville sélectionnée

## Compte Admin

- Email : admin@rencontres.cm
- Mot de passe : Cm2026!Admin

## Technologies

- Backend : Flask, SQLAlchemy, Flask-CORS
- Frontend : Tailwind CSS, Alpine.js
- Base de données : SQLite
