# Sunu Kiray — Plateforme médicale sénégalaise

> "Notre Santé" en Wolof

Plateforme numérique de gestion des rendez-vous médicaux et de redéploiement des ressources de santé au Sénégal.

**Projet PPP 2025-2026 | DIC 1 / DGI / ESP / UCAD — Encadrant : Dr Mangoné FALL**

---

## Structure du projet

```
sunu_kiray/
├── backend/
│   ├── routers/              ← Endpoints API
│   │   ├── auth.py           ← Authentification (login, register, profil)
│   │   ├── structures.py     ← Structures de santé
│   │   ├── medecins.py       ← Médecins, planning, horaires
│   │   ├── rendez_vous.py    ← RDV, créneaux, annulation
│   │   ├── alertes.py        ← Alertes de surcharge
│   │   ├── redeplois.py      ← Missions temporaires
│   │   ├── dashboard.py      ← Statistiques admin
│   │   └── admin.py          ← Génération créneaux, stats dispo
│   ├── scripts/              ← Utilitaires (à exécuter une seule fois)
│   │   ├── seed_data.sql     ← Données initiales (charges, alertes)
│   │   ├── horaires.sql      ← Horaires hebdomadaires + procédure SQL
│   │   ├── add_medecins.sql  ← Médecins pour Pikine et Touba
│   │   ├── generate_disponibilites.py  ← Génère les créneaux sur 30j
│   │   └── reset_passwords.py          ← Réinitialise les mots de passe de test
│   ├── main.py               ← Point d'entrée FastAPI
│   ├── database.py           ← Connexion MySQL (pymysql)
│   ├── security.py           ← JWT + bcrypt
│   ├── utils.py              ← Helpers (conversion timedelta, etc.)
│   ├── requirements.txt      ← Dépendances Python
│   ├── .env.example          ← Modèle de configuration
│   └── README.md             ← Documentation API complète
├── frontend/
│   ├── api.js                ← Couche API centralisée (fetch + JWT)
│   ├── auth.html             ← Connexion / Inscription
│   ├── dashboard.html        ← Espace administrateur
│   ├── medecin.html          ← Espace médecin
│   ├── patient.html          ← Espace patient
│   ├── index.html            ← Page d'accueil publique
│   └── README.md             ← Guide d'utilisation frontend
├── database/
│   └── sunu_kiray.sql        ← Schéma complet + données de test
├── start.bat                 ← Démarrage rapide (Windows)
└── README.md
```

---

## Installation

### 1. Base de données

```bash
# Dans le terminal MySQL :
source database/sunu_kiray.sql

# Puis les données initiales :
source backend/scripts/seed_data.sql
source backend/scripts/horaires.sql
source backend/scripts/add_medecins.sql
```

### 2. Backend

```bash
# Copier et configurer l'environnement
cp backend/.env.example backend/.env
# Éditer backend/.env : DB_HOST, DB_USER, DB_PASS, JWT_SECRET

# Installer les dépendances
pip install -r backend/requirements.txt

# Générer les créneaux de disponibilité
cd backend && python scripts/generate_disponibilites.py

# Démarrer le serveur
python -m uvicorn main:app --reload --port 8001
```

Ou depuis la racine : double-cliquer sur **`start.bat`**

### 3. Frontend

Ouvrir dans le navigateur :
```
http://localhost:8001/app/auth.html
```

---

## Comptes de test

> Mot de passe pour tous : `Sunu2025!`

| Rôle | Email | Accès |
|------|-------|-------|
| Administrateur | `admin@plateforme-med.sn` | Dashboard complet |
| Médecin (Cardiologue) | `a.diallo@med.sn` | Planning, missions, stats |
| Médecin (Généraliste) | `f.ndiaye@med.sn` | Planning, missions, stats |
| Patient | `m.sarr@gmail.com` | Prise de RDV, mes RDV |
| Patient | `c.thiam@gmail.com` | Prise de RDV, mes RDV |

---

## Fonctionnalités

| Espace | Fonctionnalité |
|--------|---------------|
| Patient | Prise de RDV en ligne, calendrier des créneaux, annulation, historique |
| Médecin | Planning hebdomadaire dynamique, gestion des consultations, missions de redéploiement, horaires récurrents |
| Admin | Dashboard temps réel, gestion des alertes, redéploiements, rapports, génération automatique des créneaux |

---

## Documentation

- [Backend — Routes API & installation](backend/README.md)
- [Frontend — Pages & guide d'utilisation](frontend/README.md)
- API interactive (Swagger) : [http://localhost:8001/docs](http://localhost:8001/docs)

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend | Python 3.13, FastAPI, uvicorn |
| Base de données | MySQL 8, pymysql |
| Authentification | JWT (python-jose), bcrypt |
| Frontend | HTML5, CSS3, JavaScript ES2022 (vanilla) |
| Serveur de dev | uvicorn avec `--reload` |
