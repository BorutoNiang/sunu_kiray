# Sunu Kiray — Frontend

Interface web statique en **HTML / CSS / JavaScript** pur, sans framework.

---

## Prérequis

- Le backend doit tourner sur `http://localhost:8001`
- Un navigateur moderne (Chrome, Edge, Firefox)
- Extension **Live Server** dans VS Code (recommandé)

---

## Lancement

### Option 1 — Live Server (recommandé)

1. Ouvrir le dossier du projet dans VS Code
2. Clic droit sur `frontend/auth.html`
3. Cliquer **"Open with Live Server"**
4. Le navigateur s'ouvre sur `http://127.0.0.1:5500/frontend/auth.html`

### Option 2 — Navigateur direct

Glisser-déposer `frontend/auth.html` dans le navigateur.

> Si les appels API échouent avec cette méthode, utiliser Live Server.

---

## Structure

```
frontend/
├── api.js           ← Couche API centralisée (tous les appels fetch)
├── auth.html        ← Page de connexion / inscription
├── dashboard.html   ← Tableau de bord administrateur
├── medecin.html     ← Espace médecin (planning, missions, stats)
├── patient.html     ← Espace patient (prise de RDV, mes RDV)
└── index.html       ← Page d'accueil publique
```

---

## Fichier api.js

Toute la communication avec le backend passe par `api.js`.
Il expose des objets globaux utilisables dans toutes les pages :

```javascript
// Authentification
Auth.login(email, mot_de_passe)
Auth.register(payload)
Auth.me()
Auth.logout()

// Structures de santé
Structures.list({ region: 'Dakar' })
Structures.get(id)
Structures.alertes(id)

// Médecins
Medecins.list({ disponible: '1' })
Medecins.planning(id, { date_debut, date_fin })
Medecins.updateDisponibilite(id, 'disponible')

// Rendez-vous
RendezVous.list()
RendezVous.disponibilites(structure_id, service_id, date)
RendezVous.create(disponibilite_id, motif)
RendezVous.cancel(id)
RendezVous.updateStatus(id, statut)

// Alertes
Alertes.list({ priorite: 'critique' })
Alertes.traiter(id, action_effectuee)

// Redéploiements
Redeplois.proposer(payload)
Redeplois.repondre(id, statut)

// Dashboard
Dashboard.stats()
```

### Guard de navigation

Chaque page protégée appelle `requireLogin()` en haut du script :

```javascript
requireLogin('administrateur')  // dashboard.html
requireLogin('medecin')         // medecin.html
requireLogin('patient')         // patient.html
```

Si l'utilisateur n'est pas connecté ou n'a pas le bon rôle,
il est automatiquement redirigé vers `auth.html`.

---

## Pages

### auth.html
- Connexion avec email + mot de passe
- Inscription en 3 étapes (rôle, identité, confirmation)
- Redirection automatique selon le rôle après connexion

### dashboard.html
- Réservé aux administrateurs
- KPIs en temps réel (structures, médecins, RDV, alertes)
- Graphique d'activité sur 7 jours
- Gestion des alertes et redéploiements

### medecin.html
- Réservé aux médecins
- Planning hebdomadaire interactif
- Gestion des missions de redéploiement
- Statistiques personnelles
- Toggle disponibilité en temps réel

### patient.html
- Réservé aux patients
- Wizard de prise de RDV en 4 étapes
- Calendrier dynamique avec créneaux disponibles
- Liste des rendez-vous avec annulation

### index.html
- Page publique de présentation
- Liens vers auth.html

---

## Comptes de test

> Mot de passe pour tous : `Sunu2025!`

| Rôle | Email | Page de redirection |
|------|-------|---------------------|
| Administrateur | `admin@plateforme-med.sn` | `dashboard.html` |
| Médecin | `a.diallo@med.sn` | `medecin.html` |
| Patient | `m.sarr@gmail.com` | `patient.html` |

---

## Configuration

L'URL de l'API est définie en haut de `api.js` :

```javascript
const API_BASE = 'http://localhost:8001';
```

Changer cette valeur si le backend tourne sur un autre port ou domaine.

---

*Sunu Kiray — "Notre Santé" en Wolof*
*DIC 1 / DGI / ESP / UCAD — Encadrant : Dr Mangoné FALL*
