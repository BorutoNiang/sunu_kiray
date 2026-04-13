# Sunu Kiray — Plateforme médicale sénégalaise

> "Notre Santé" en Wolof

Plateforme numérique de gestion des rendez-vous médicaux et de redéploiement
des ressources de santé au Sénégal.

**Projet PPP 2025-2026 | DIC 1 / DGI / ESP / UCAD**
**Encadrant : Dr Mangoné FALL**

---

## Structure du projet

```
sunu-kiray/
├── backend/             ← API REST Python (FastAPI)
├── frontend/            ← Interface web HTML/CSS/JS
├── sunu_kiray.sql       ← Base de données MySQL
├── start.bat            ← Démarrage rapide (Windows)
└── README.md
```

---

## Démarrage rapide

### 1. Base de données

Importer le fichier SQL dans MySQL :

```sql
-- Dans le terminal MySQL :
source sunu_kiray.sql
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
# Configurer backend/.env (voir backend/README.md)
python -m uvicorn main:app --reload --port 8001
```

Ou double-cliquer sur **`start.bat`** depuis la racine.

### 3. Frontend

Ouvrir `frontend/auth.html` avec **Live Server** dans VS Code.

---

## Comptes de test

> Mot de passe pour tous : `Sunu2025!`

| Rôle | Email |
|------|-------|
| Administrateur | `admin@plateforme-med.sn` |
| Médecin | `a.diallo@med.sn` |
| Patient | `m.sarr@gmail.com` |

---

## Documentation

- [Backend — API & installation](backend/README.md)
- [Frontend — Pages & utilisation](frontend/README.md)
- API interactive : [http://localhost:8001/docs](http://localhost:8001/docs)

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend | Python 3.13, FastAPI, uvicorn |
| Base de données | MySQL 8, pymysql |
| Authentification | JWT (python-jose), bcrypt |
| Frontend | HTML5, CSS3, JavaScript ES2022 |
| Serveur de dev | uvicorn (backend), Live Server (frontend) |
