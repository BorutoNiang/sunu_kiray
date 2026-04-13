// ============================================================
//  SUNU KIRAY — Couche API frontend
//  Centralise tous les appels fetch vers le backend Python (FastAPI)
//  API : http://localhost:8001
// ============================================================

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8001'
  : '';
const TOKEN_KEY = 'sunu_kiray_token';
const USER_KEY  = 'sunu_kiray_user';

// ── Helpers ──────────────────────────────────────────────

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function getUser() {
  try { return JSON.parse(localStorage.getItem(USER_KEY)); } catch { return null; }
}

function saveSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function isLoggedIn() {
  return !!getToken();
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = 'Bearer ' + token;

  const res = await fetch(API_BASE + path, { ...options, headers });
  const json = await res.json();

  if (!json.success) {
    const err = new Error(json.message || 'Erreur API');
    err.status = res.status;
    err.errors = json.errors;
    throw err;
  }
  return json.data;
}

// ── AUTH ─────────────────────────────────────────────────

const Auth = {
  async login(email, mot_de_passe) {
    const data = await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, mot_de_passe }),
    });
    saveSession(data.token, data.user);
    return data;
  },

  async register(payload) {
    const data = await apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    saveSession(data.token, data.user);
    return data;
  },

  async me() {
    return apiFetch('/auth/me');
  },

  async forgotPassword(email) {
    return apiFetch('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  async updateMe(payload) {
    return apiFetch('/auth/me', {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },

  logout() {
    clearSession();
    window.location.href = 'auth.html';
  },
};

// ── STRUCTURES ───────────────────────────────────────────

const Structures = {
  list(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return apiFetch('/structures' + (qs ? '?' + qs : ''));
  },
  get(id) { return apiFetch('/structures/' + id); },
  alertes(id) { return apiFetch('/structures/' + id + '/alertes'); },
};

// ── MÉDECINS ─────────────────────────────────────────────

const Medecins = {
  list(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return apiFetch('/medecins' + (qs ? '?' + qs : ''));
  },
  redeployables() { return apiFetch('/medecins/redeployables'); },
  planning(id, params = {}) {
    const qs = new URLSearchParams(params).toString();
    return apiFetch('/medecins/' + id + '/planning' + (qs ? '?' + qs : ''));
  },
  updateDisponibilite(id, disponibilite) {
    return apiFetch('/medecins/' + id + '/disponibilite', {
      method: 'PUT',
      body: JSON.stringify({ disponibilite }),
    });
  },
  getHoraires(id) {
    return apiFetch('/medecins/' + id + '/horaires');
  },
  addHoraire(id, payload) {
    return apiFetch('/medecins/' + id + '/horaires', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  deleteHoraire(id, horaireId) {
    return apiFetch('/medecins/' + id + '/horaires/' + horaireId, { method: 'DELETE' });
  },
};

// ── RENDEZ-VOUS ──────────────────────────────────────────

const RendezVous = {
  list(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return apiFetch('/rendez-vous' + (qs ? '?' + qs : ''));
  },
  get(id) { return apiFetch('/rendez-vous/' + id); },
  disponibilites(structure_id, service_id, date) {
    return apiFetch(`/rendez-vous/disponibilites?structure_id=${structure_id}&service_id=${service_id}&date=${date}`);
  },
  create(disponibilite_id, motif = '') {
    return apiFetch('/rendez-vous', {
      method: 'POST',
      body: JSON.stringify({ disponibilite_id, motif }),
    });
  },
  cancel(id) {
    return apiFetch('/rendez-vous/' + id + '/annuler', { method: 'PUT' });
  },
  updateStatus(id, statut, notes_medecin = '') {
    return apiFetch('/rendez-vous/' + id + '/statut', {
      method: 'PUT',
      body: JSON.stringify({ statut, notes_medecin }),
    });
  },
};

// ── ALERTES ──────────────────────────────────────────────

const Alertes = {
  list(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return apiFetch('/alertes' + (qs ? '?' + qs : ''));
  },
  traiter(id, action_effectuee = '') {
    return apiFetch('/alertes/' + id + '/traiter', {
      method: 'PUT',
      body: JSON.stringify({ action_effectuee }),
    });
  },
};

// ── REDÉPLOIEMENTS ───────────────────────────────────────

const Redeplois = {
  list() {
    return apiFetch('/redeplois');
  },
  proposer(payload) {
    return apiFetch('/redeplois', { method: 'POST', body: JSON.stringify(payload) });
  },
  repondre(id, statut, note_medecin = '') {
    return apiFetch('/redeplois/' + id + '/repondre', {
      method: 'PUT',
      body: JSON.stringify({ statut, note_medecin }),
    });
  },
};

// ── DASHBOARD ────────────────────────────────────────────

const Dashboard = {
  stats() { return apiFetch('/dashboard'); },
};

// ── ADMINISTRATION ────────────────────────────────────────

const Admin = {
  genererCreneaux(nb_jours = 30) {
    return apiFetch('/admin/generer-creneaux', {
      method: 'POST',
      body: JSON.stringify({ nb_jours }),
    });
  },
  horaires(medecin_id = null) {
    const qs = medecin_id ? `?medecin_id=${medecin_id}` : '';
    return apiFetch('/admin/horaires' + qs);
  },
  statsDisponibilites() {
    return apiFetch('/admin/stats-disponibilites');
  },
};

// ── Guard de navigation ───────────────────────────────────
// Appeler en haut de chaque page protégée :
// requireLogin();            → redirige si non connecté
// requireLogin('admin');     → redirige si pas le bon rôle

function requireLogin(role = null) {
  if (!isLoggedIn()) {
    window.location.href = 'auth.html';
    return;
  }
  if (role) {
    const user = getUser();
    if (!user || user.role !== role) {
      window.location.href = 'auth.html';
    }
  }
}

// ── Utilitaire heure ─────────────────────────────────────
// MySQL retourne parfois les TIME comme timedelta (secondes) ou string
function formatHeure(h) {
  if (!h && h !== 0) return '—';
  if (typeof h === 'number') {
    const hh = Math.floor(h / 3600).toString().padStart(2, '0');
    const mm = Math.floor((h % 3600) / 60).toString().padStart(2, '0');
    return `${hh}:${mm}`;
  }
  return String(h).slice(0, 5);
}
