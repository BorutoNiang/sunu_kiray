# Sunu Kiray — Backend API

API REST construite avec **FastAPI** (Python 3.13) et **MySQL**.

---

## Prérequis

- Python 3.10+
- MySQL 8+
- pip

---

## Installation

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configurer l'environnement
# Copier .env.example en .env et remplir les valeurs
cp .env.example .env

# 3. Importer la base de données
# Dans MySQL :
# source /chemin/vers/sunu_kiray.sql

# 4. Démarrer le serveur
python -m uvicorn main:app --reload --port 8001
```

Ou depuis la racine du projet, double-cliquer sur `start.bat`.

---

## Structure

```
backend/
├── main.py              ← Point d'entrée FastAPI, CORS, routers
├── database.py          ← Connexion MySQL (pymysql)
├── security.py          ← JWT, bcrypt, guards d'authentification
├── requirements.txt     ← Dépendances Python
├── .env                 ← Variables d'environnement (ne pas committer)
├── .env.example         ← Modèle de configuration
└── routers/
    ├── auth.py          ← Inscription, connexion, profil
    ├── structures.py    ← Structures de santé
    ├── medecins.py      ← Médecins, planning, disponibilité
    ├── rendez_vous.py   ← RDV, créneaux, annulation
    ├── alertes.py       ← Alertes de surcharge
    ├── redeplois.py     ← Missions temporaires
    └── dashboard.py     ← Statistiques admin
```

---

## Variables d'environnement

| Variable | Description | Exemple |
|----------|-------------|---------|
| `DB_HOST` | Hôte MySQL | `localhost` |
| `DB_PORT` | Port MySQL | `3306` |
| `DB_NAME` | Nom de la base | `sunu_kiray` |
| `DB_USER` | Utilisateur MySQL | `root` |
| `DB_PASS` | Mot de passe MySQL | `monmotdepasse` |
| `JWT_SECRET` | Clé secrète JWT (min. 32 chars) | `changez_moi_en_prod` |
| `JWT_EXPIRE` | Durée du token en secondes | `86400` (24h) |
| `APP_ENV` | Environnement | `development` ou `production` |
| `CORS_ALLOWED_ORIGINS` | Origines autorisées (séparées par virgule) | `http://localhost:5500` |

---

## Routes API

### Authentification

| Méthode | Route | Accès | Description |
|---------|-------|-------|-------------|
| POST | `/auth/register` | Public | Créer un compte |
| POST | `/auth/login` | Public | Se connecter |
| POST | `/auth/forgot-password` | Public | Mot de passe oublié |
| POST | `/auth/reset-password` | Public | Réinitialiser le mot de passe |
| GET  | `/auth/me` | Connecté | Profil de l'utilisateur connecté |

### Structures de santé

| Méthode | Route | Accès | Description |
|---------|-------|-------|-------------|
| GET  | `/structures` | Connecté | Liste avec charge temps réel |
| GET  | `/structures?region=Dakar` | Connecté | Filtrer par région |
| GET  | `/structures/{id}` | Connecté | Détail + services + médecins |
| PUT  | `/structures/{id}/charge` | Admin/Médecin | Mettre à jour la charge |
| GET  | `/structures/{id}/alertes` | Admin | Alertes de la structure |

### Médecins

| Méthode | Route | Accès | Description |
|---------|-------|-------|-------------|
| GET  | `/medecins` | Connecté | Liste des médecins |
| GET  | `/medecins?disponible=1` | Connecté | Médecins disponibles |
| GET  | `/medecins/redeployables` | Admin | Médecins disponibles pour mission |
| GET  | `/medecins/{id}/planning` | Médecin/Admin | Planning hebdomadaire |
| PUT  | `/medecins/{id}/disponibilite` | Médecin/Admin | Changer la disponibilité |

### Rendez-vous

| Méthode | Route | Accès | Description |
|---------|-------|-------|-------------|
| GET  | `/rendez-vous` | Connecté | Mes RDV (filtré par rôle) |
| POST | `/rendez-vous` | Patient | Créer un RDV |
| GET  | `/rendez-vous/disponibilites?structure_id=1&service_id=2&date=2026-04-15` | Connecté | Créneaux disponibles |
| GET  | `/rendez-vous/{id}` | Connecté | Détail d'un RDV |
| PUT  | `/rendez-vous/{id}/annuler` | Patient/Admin | Annuler un RDV |
| PUT  | `/rendez-vous/{id}/statut` | Médecin/Admin | Changer le statut |

### Alertes

| Méthode | Route | Accès | Description |
|---------|-------|-------|-------------|
| GET  | `/alertes` | Admin | Toutes les alertes actives |
| GET  | `/alertes?priorite=critique` | Admin | Filtrer par priorité |
| PUT  | `/alertes/{id}/traiter` | Admin | Marquer comme traitée |

### Redéploiements

| Méthode | Route | Accès | Description |
|---------|-------|-------|-------------|
| POST | `/redeplois` | Admin | Proposer un redéploiement |
| PUT  | `/redeplois/{id}/repondre` | Médecin | Accepter ou refuser |

### Dashboard

| Méthode | Route | Accès | Description |
|---------|-------|-------|-------------|
| GET  | `/dashboard` | Admin | Statistiques globales |

---

## Authentification

Toutes les routes protégées nécessitent un header :

```
Authorization: Bearer <token_jwt>
```

Le token est obtenu via `/auth/login` ou `/auth/register`.

---

## Format des réponses

### Succès
```json
{
  "success": true,
  "message": "Connexion réussie.",
  "data": { ... }
}
```

### Erreur
```json
{
  "detail": "Email ou mot de passe incorrect."
}
```

---

## Comptes de test

> Mot de passe pour tous : `Sunu2025!`

| Rôle | Email |
|------|-------|
| Administrateur | `admin@plateforme-med.sn` |
| Médecin (Cardiologue) | `a.diallo@med.sn` |
| Médecin (Généraliste) | `f.ndiaye@med.sn` |
| Patient | `m.sarr@gmail.com` |
| Patient | `c.thiam@gmail.com` |

---

## Documentation interactive

Une fois le serveur démarré, accéder à :

- Swagger UI : [http://localhost:8001/docs](http://localhost:8001/docs)
- ReDoc : [http://localhost:8001/redoc](http://localhost:8001/redoc)

---

*Sunu Kiray — "Notre Santé" en Wolof*
*DIC 1 / DGI / ESP / UCAD — Encadrant : Dr Mangoné FALL*
