from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db
from security import require_role

router = APIRouter(tags=["Administration"])

class GenererCreneauxBody(BaseModel):
    nb_jours: Optional[int] = 30

@router.post("/generer-creneaux")
def generer_creneaux(body: GenererCreneauxBody, user=Depends(require_role("administrateur"))):
    """
    Génère automatiquement les créneaux de disponibilité pour tous les médecins
    sur les N prochains jours, en se basant sur leurs horaires hebdomadaires.
    """
    nb = max(1, min(body.nb_jours, 90))  # entre 1 et 90 jours
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("CALL generer_disponibilites(%s)", (nb,))
            result = cur.fetchone()
        db.commit()
        return {
            "success": True,
            "message": f"Créneaux générés pour les {nb} prochains jours.",
            "data": {"creneaux_generes": result.get("creneaux_generes", 0) if result else 0}
        }
    finally:
        db.close()

@router.get("/horaires")
def liste_horaires(medecin_id: Optional[int] = None, user=Depends(require_role("administrateur"))):
    """Liste les horaires hebdomadaires configurés."""
    db = get_db()
    try:
        jours = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi']
        where = "WHERE h.est_actif = 1"
        params = []
        if medecin_id:
            where += " AND h.medecin_id = %s"
            params.append(medecin_id)
        with db.cursor() as cur:
            cur.execute(f"""
                SELECT h.id, h.jour_semaine, h.heure_debut, h.heure_fin, h.nb_slots,
                       CONCAT(u.prenom,' ',u.nom) AS medecin_nom,
                       s.nom AS structure_nom, sv.nom AS service_nom
                FROM horaires_medecins h
                JOIN medecins m ON h.medecin_id = m.id
                JOIN utilisateurs u ON m.utilisateur_id = u.id
                JOIN structures_sante s ON h.structure_id = s.id
                JOIN services sv ON h.service_id = sv.id
                {where}
                ORDER BY h.medecin_id, h.jour_semaine, h.heure_debut
            """, params)
            rows = cur.fetchall()
        # Ajouter le nom du jour
        for r in rows:
            r["jour_nom"] = jours[r["jour_semaine"]]
        return {"success": True, "message": "OK", "data": rows}
    finally:
        db.close()

@router.get("/stats-disponibilites")
def stats_disponibilites(user=Depends(require_role("administrateur"))):
    """Statistiques des créneaux disponibles par structure."""
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT s.nom AS structure, s.ville,
                       COUNT(d.id) AS total_creneaux,
                       SUM(d.nb_slots_max - d.nb_slots_pris) AS slots_libres,
                       SUM(d.nb_slots_pris) AS slots_pris,
                       MIN(d.date_travail) AS prochain_creneau,
                       MAX(d.date_travail) AS dernier_creneau
                FROM structures_sante s
                LEFT JOIN services sv ON sv.structure_id = s.id
                LEFT JOIN disponibilites d ON d.service_id = sv.id
                    AND d.date_travail >= CURDATE()
                    AND d.est_actif = 1
                GROUP BY s.id
                ORDER BY s.id
            """)
            rows = cur.fetchall()
        return {"success": True, "message": "OK", "data": rows}
    finally:
        db.close()
