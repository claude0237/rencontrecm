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
│   ├── config.py              # Configuration Flask (MySQL, Secret Key)
│   └── run.py                 # Commandes CLI & Lancement
└── frontend/
    ├── static/                # CSS/JS
    └── templates/
        ├── layouts/           # base.html (Tailwind + Alpine.js)
        ├── auth/              # login.html, register.html
        ├── main/              # index.html (Filtres asynchrones), profil.html
        └── admin/             # dashboard.html, utilisateurs.html, geographie.html, alertes.html
```

## Prérequis

- Python 3.11 ou 3.12
- MySQL 8.0+
- pip (gestionnaire de paquets Python)

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/claude0237/rencontrecm.git
cd rencontrecm
```

2. Créer un environnement virtuel :
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Installer les dépendances Python :
```bash
pip install -r requirements.txt
```

4. Configurer la base de données MySQL :
```bash
# Créer la base de données
mysql -u root -p
CREATE DATABASE rencontres_cm;
EXIT;
```

5. Configurer la connexion MySQL dans `backend/config.py` :
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://votre_user:votre_password@localhost/rencontres_cm'
```

6. Initialiser la base de données :
```bash
cd backend
python run.py init-db
```

Cela va :
- Créer les tables
- Ajouter les 10 régions du Cameroun comme villes principales
- Ajouter au moins 5 communes/arrondissements pour Douala et Yaoundé
- Créer un compte admin : admin@rencontres.cm / Cm2026!Admin

7. Exécuter les scripts de migration pour les fonctionnalités de sécurité :
```bash
mysql -u root -p rencontres_cm < backend/add_password_resets_table.sql
mysql -u root -p rencontres_cm < backend/add_security_fields.sql
```

Ces scripts ajoutent :
- La table `password_resets` pour la gestion des codes de réinitialisation
- Les champs de sécurité `wave_count`, `last_attempt_at` pour le suivi des tentatives
- Les champs `disabled_reason`, `disabled_at` pour le suivi des comptes désactivés

## Lancement

Lancer l'application en développement :
```bash
cd backend
python run.py
```

L'application sera accessible sur http://localhost:5000

## Déploiement en Production (VPS Linux)

### Prérequis serveur
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip mysql-server nginx
```

### Configuration MySQL
```bash
sudo mysql_secure_installation
sudo mysql -u root -p
CREATE DATABASE rencontres_cm;
CREATE USER 'rencontres_user'@'localhost' IDENTIFIED BY 'mot_de_passe_secure';
GRANT ALL PRIVILEGES ON rencontres_cm.* TO 'rencontres_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Déploiement de l'application
```bash
# Cloner le dépôt
git clone https://github.com/claude0237/rencontrecm.git
cd rencontrecm

# Créer l'environnement virtuel
python3.11 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
pip install gunicorn

# Configurer la base de données
nano backend/config.py  # Modifier SQLALCHEMY_DATABASE_URI

# Initialiser la base de données
cd backend
python run.py init-db
```

### Configuration Gunicorn + Nginx
```bash
# Créer un service systemd
sudo nano /etc/systemd/system/rencontrecm.service
```

Contenu du service :
```ini
[Unit]
Description=RencontresCM Gunicorn Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/rencontrecm
Environment="PATH=/path/to/rencontrecm/.venv/bin"
ExecStart=/path/to/rencontrecm/.venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 "run:create_app()"

[Install]
WantedBy=multi-user.target
```

```bash
# Démarrer le service
sudo systemctl start rencontrecm
sudo systemctl enable rencontrercm

# Configurer Nginx
sudo nano /etc/nginx/sites-available/rencontrecm
```

Configuration Nginx :
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/rencontrecm/frontend/static;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/rencontrecm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Fonctionnalités

### Backend (API REST)

- **Authentification** : Login/Register avec sessions, gestion de la dernière connexion
- **Réinitialisation de mot de passe** : 
  - Code à 6 chiffres envoyé par email/SMS
  - Expiration après 15 minutes
  - Maximum 3 tentatives par code
  - Cooldown de 30 minutes après 3 tentatives échouées
  - Désactivation automatique après 3 vagues de tentatives échouées
- **Profils** : CRUD complet, photos multiples, photo principale, compteur de visites
- **Géolocalisation** : Calcul de distance entre utilisateurs, tracking de position
- **Régions et Communes** : API pour les villes et quartiers du Cameroun
- **Profils recommandés** : Algorithme basé sur le genre, les visites et la distance
- **Pagination** : Support de pagination pour les listes de profils
- **Admin** :
  - Tableau de bord avec statistiques (utilisateurs totaux, actifs/inactifs)
  - Gestion des utilisateurs (promotion admin, désactivation)
  - Configuration géographique (CRUD régions/quartiers)
  - Gestion des alertes globales (bannière défilante)
  - Gestion des comptes désactivés (réactivation, affichage des raisons)
  - **Gestion des publicités** : Validation, rejet avec raison, suspension, suppression
  - **Gestion des packs publicitaires** : CRUD complet pour les packs d'annonces
  - **Statistiques détaillées** : Appels, visites de profils, clics WhatsApp
  - **Notifications admin** : Alertes pour nouvelles publicités et paiements
  - **Persistance de l'état** : Menu admin et pagination sauvegardés après rafraîchissement
  - **Validation des paiements** : Validation/rejet des paiements manuels et Mobile Money

### Système de Paiement

#### Méthodes de Paiement Actuelles

Le système implémente actuellement trois méthodes de paiement pour les publicités:

1. **Mobile Money (Orange Money / MTN Mobile Money)**
   - L'utilisateur entre le numéro qui a effectué le paiement
   - Le statut passe à `en_attente_paiement_manuel`
   - Une notification admin est créée avec le numéro de paiement
   - L'admin valide en comparant avec les reçus reçus
   - **Note**: Actuellement manuel, prévu pour intégration API automatique

2. **Paiement Manuel (Admin)**
   - L'utilisateur demande un paiement manuel
   - Optionnellement entre une référence de paiement
   - Le statut passe à `en_attente_paiement_manuel`
   - Une notification admin est créée
   - L'admin valide après vérification du dépôt

3. **Carte Bancaire**
   - Placeholder pour intégration future avec passerelle de paiement
   - Actuellement non implémenté

#### Processus de Validation Admin

Le flux de validation des paiements suit ce processus:

1. **Soumission du paiement**
   - L'utilisateur sélectionne une méthode de paiement
   - Les données sont envoyées à `/api/v1/ads/pub/<id>/payer`
   - Le statut de la publicité passe à `en_attente_paiement_manuel`
   - Une notification admin est créée dans `admin_notifications`

2. **Notification Admin**
   - Type: `paiement_manuel`
   - Contient: titre, message avec détails (numéro/référence, montant, utilisateur)
   - Accessible depuis le tableau de bord admin

3. **Validation par l'admin**
   - L'admin consulte les paiements en attente
   - Compare les informations avec les reçus bancaires/Mobile Money
   - Valide ou rejette le paiement avec raison

4. **Activation de la publicité**
   - Si validé: statut passe à `validee`, dates de validité définies
   - Si rejeté: statut passe à `rejetee`, raison enregistrée
   - Historique de validation enregistré dans `ad_validation_history`

#### Intégration Future d'API de Paiement Automatique

Pour une future intégration avec les API de paiement automatique (Orange Money, MTN, etc.), voici la logique à suivre:

**Architecture proposée:**

1. **Configuration des API de paiement**
   - Ajouter les clés API dans `backend/config.py` ou variables d'environnement
   - Créer un service de paiement (`backend/app/services/payment_service.py`)
   - Implémenter les méthodes pour chaque opérateur (Orange, MTN)

2. **Modification du flux Mobile Money**
   - Remplacer la saisie manuelle du numéro par une redirection vers l'API de paiement
   - L'utilisateur est redirigé vers la page de paiement de l'opérateur
   - Après paiement, l'opérateur redirige vers un webhook/callback

3. **Webhook de notification de paiement**
   - Créer un endpoint `/api/v1/payments/webhook/<operator>`
   - Recevoir les notifications de succès/échec de l'opérateur
   - Vérifier la signature de la notification pour la sécurité
   - Mettre à jour automatiquement le statut de la publicité

4. **Modifications du modèle**
   - Ajouter des champs pour suivre les transactions:
     ```python
     # Dans Advertisement
     transaction_id = db.Column(db.String(100))  # ID de transaction API
     payment_status = db.Column(db.String(50))   # pending, success, failed
     payment_response = db.Column(db.Text)       # Réponse JSON de l'API
     ```

5. **Exemple d'implémentation**

   ```python
   # backend/app/services/payment_service.py
   class PaymentService:
       def initiate_mobile_money_payment(self, ad, phone_number, operator):
           """Initie un paiement Mobile Money via API"""
           if operator == 'orange':
               return self._initiate_orange_payment(ad, phone_number)
           elif operator == 'mtn':
               return self._initiate_mtn_payment(ad, phone_number)
       
       def _initiate_orange_payment(self, ad, phone_number):
           """Intégration avec Orange Money API"""
           # Appel à l'API Orange Money
           # Retourne l'URL de paiement et transaction_id
           pass
       
       def verify_payment(self, transaction_id):
           """Vérifie le statut d'une transaction"""
           # Appel à l'API pour vérifier le statut
           pass
   ```

6. **Endpoint de callback**
   ```python
   @ads_bp.route('/payments/callback/orange', methods=['POST'])
   def orange_payment_callback():
       """Callback Orange Money après paiement"""
       data = request.get_json()
       # Vérifier la signature
       # Mettre à jour le statut de la publicité
       # Envoyer confirmation à l'utilisateur
       pass
   ```

**Points clés pour l'intégration:**
- Sécuriser les webhooks avec des signatures
- Gérer les timeouts et les échecs de paiement
- Logger toutes les transactions pour audit
- Implémenter des mécanismes de retry pour les paiements en attente
- Tester en mode sandbox avant production

**Fichiers à modifier:**
- `backend/app/routes/ads.py` - Modifier `pay_for_advertisement()`
- `backend/app/services/payment_service.py` - Nouveau fichier
- `backend/app/models.py` - Ajouter champs de transaction
- `frontend/templates/main/mes_pubs.html` - Modifier l'UI pour redirection API

### Frontend

- **Design Luxury** : Couleurs Rose (#e8536a), Crème (#fdf6f0), Charcoal (#1c1c2e)
- **Tailwind CSS** : Styling moderne et responsive
- **Alpine.js** : Interactivité côté client
- **Filtres asynchrones** : Filtrage des profils sans rechargement
- **Communes dynamiques** : Mise à jour automatique des communes selon la ville sélectionnée
- **Pagination** : Navigation par pages sur l'accueil et les profils similaires
- **Persistance de pagination** : La page courante est sauvegardée après rafraîchissement
- **Profils cliquables** : Navigation directe en cliquant sur les cartes
- **Alertes défilantes** : Bannière d'alertes avec animation marquee
- **Responsive mobile** : Menu hamburger, layout adapté
- **Section Publicités** : Affichage des publicités avec défilement automatique lent
- **Détails des publicités** : Page de détail avec boutons d'appel et WhatsApp
- **Scrollbars optimisés** : Hauteur 70vh sur les pages admin pour afficher plus de contenu

### Fonctionnalités Utilisateur

- Inscription avec photo
- Édition de profil (informations, photos, photo principale)
- Géolocalisation automatique
- Affichage de distance entre utilisateurs
- Compteur de visites de profil
- Statut en ligne
- Recherche par ville, genre, âge, commune
- **Création de publicités** : Upload d'image, sélection de pack, validation par admin
- **Affichage des publicités** : Bandeau défilant avec publicités validées
- **Contact via publicités** : Boutons d'appel et WhatsApp sur les détails des publicités

## Compte Admin

- Email : admin@rencontres.cm
- Mot de passe : Cm2026!Admin

## Technologies

- **Backend** : Flask 3.0.0, SQLAlchemy 3.1.1, Flask-CORS 4.0.0
- **Frontend** : Tailwind CSS, Alpine.js 3.x
- **Base de données** : MySQL 8.0+ (pymysql 1.1.0)
- **Déploiement** : Gunicorn, Nginx

## Structure de la base de données

### Tables principales
- **utilisateur** : Profils utilisateurs avec photos, géolocalisation, statistiques
- **region** : Régions du Cameroun
- **quartier** : Communes/arrondissements
- **alerte_globale** : Alertes pour la bannière
- **password_resets** : Codes de réinitialisation de mot de passe
- **advertisement** : Publicités avec image, statut, pack, historique de validation
- **ad_pack** : Packs publicitaires (prix, durée, nombre de publicités)
- **ad_validation_history** : Historique des validations de publicités

### Colonnes utilisateur
- Informations de base (nom, email, mot de passe, âge, genre)
- Localisation (region_id, quartier_id, latitude, longitude)
- Photos (photos JSON, photo_principale)
- Statistiques (nombre_visites, derniere_connexion, en_ligne)
- Contact (contact_whatsapp, contact_direct)
- Admin (est_admin, actif)
- Sécurité (disabled_reason, disabled_at)

## Sécurité

- Sessions HTTPOnly et SameSite=Lax
- Hachage des mots de passe
- Protection CSRF
- Validation des entrées
- Gestion des rôles admin
- **Sécurité du reset de mot de passe** :
  - Code à 6 chiffres avec expiration de 15 minutes
  - Maximum 3 tentatives par code
  - Cooldown de 30 minutes après 3 tentatives échouées
  - Désactivation automatique après 3 vagues de tentatives échouées
  - Suivi des vagues de tentatives dans la base de données

## Licence

Ce projet est propriétaire. Tous droits réservés.
