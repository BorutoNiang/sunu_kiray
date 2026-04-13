from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db
from security import get_current_user, require_role
from utils import fix_rows

router = APIRouter(tags=["Médecins"])

@router.get("")
def index(specialite: Optional[str]=None, structure_id: Optional[int]=None,
          disponible: Optional[str]=None, _=Depends(get_current_user)):
    db = get_db()
    try:
        where, params = ["u.est_actif=1"], []
        if specialite:  where.append("m.specialite LIKE %s"); params.append(f"%{specialite}%")
        if structure_id:where.append("m.structure_id=%s"); params.append(structure_id)
        if disponible=="1": where.append('m.disponibilite="disponible"')
        sql = f"""SELECT m.id,m.specialite,m.grade,m.disponibilite,m.peut_etre_redeploye,
                  CONCAT(u.prenom,' ',u.nom) AS nom_complet,u.telephone,u.email,
                  s.nom AS structure_nom,s.ville,s.region
                  FROM medecins m JOIN utilisateurs u ON m.utilisateur_id=u.id
                  JOIN structures_sante s ON m.structure_id=s.id
                  WHERE {' AND '.join(where)} ORDER BY m.disponibilite,u.nom"""
        with db.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return {"success": True, "message": "OK", "data": rows}
    finally:
        db.close()

@router.get("/redeployables")
def redeployables(user=Depends(require_role("administrateur"))):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM vue_medecins_redeployables")
            rows = cur.fetchall()
        return {"success": True, "message": "OK", "data": rows}
    finally:
        db.close()

@router.get("/{id}/planning")
def planning(id: int, date_debut: Optional[str]=None, date_fin: Optional[str]=None,
             current_user=Depends(get_current_user)):
    from datetime import date, timedelta
    if not date_debut: date_debut = str(date.today())
    if not date_fin:   date_fin   = str(date.today() + timedelta(days=7))
    if current_user.get("role") == "medecin" and current_user.get("medecin_id") != id:
        raise HTTPException(403, "Accès refusé.")
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT r.id,r.date_rdv,r.heure_rdv,r.statut,r.motif,
                       CONCAT(u.prenom,' ',u.nom) AS patient_nom,u.telephone AS patient_tel,
                       sv.nom AS service,st.nom AS structure
                FROM rendez_vous r
                JOIN utilisateurs u ON r.patient_id=u.id
                JOIN services sv ON r.service_id=sv.id
                JOIN structures_sante st ON sv.structure_id=st.id
                WHERE r.medecin_id=%s AND r.date_rdv BETWEEN %s AND %s
                  AND r.statut NOT IN ('annule_patient','annule_medecin')
                ORDER BY r.date_rdv,r.heure_rdv""", (id, date_debut, date_fin))
            rows = cur.fetchall()
        return {"success": True, "message": "OK", "data": fix_rows(rows)}
    finally:
        db.close()

class DispoBody(BaseModel):
    disponibilite: str

@router.put("/{id}/disponibilite")
def update_disponibilite(id: int, body: DispoBody, current_user=Depends(require_role("medecin","administrateur"))):
    allowed = ["disponible","en_consultation","en_mission","absent","conge"]
    if body.disponibilite not in allowed:
        raise HTTPException(422, "Valeur non autorisée.")
    if current_user.get("role") == "medecin" and current_user.get("medecin_id") != id:
        raise HTTPException(403, "Accès refusé.")
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("UPDATE medecins SET disponibilite=%s WHERE id=%s", (body.disponibilite, id))
        db.commit()
        return {"success": True, "message": "Disponibilité mise à jour.", "data": None}
    finally:
        db.close()

# ── HORAIRES HEBDOMADAIRES ────────────────────────────────

JOURS = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi']

@router.get("/{id}/horaires")
def get_horaires(id: int, current_user=Depends(get_current_user)):
    if current_user.get("role") == "medecin" and current_user.get("medecin_id") != id:
        raise HTTPException(403, "Accès refusé.")
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT h.id, h.jour_semaine, h.heure_debut, h.heure_fin, h.nb_slots, h.est_actif,
                       sv.id AS service_id, sv.nom AS service_nom,
                       s.id AS structure_id, s.nom AS structure_nom
                FROM horaires_medecins h
                JOIN services sv ON h.service_id = sv.id
                JOIN structures_sante s ON h.structure_id = s.id
                WHERE h.medecin_id = %s
                ORDER BY h.jour_semaine, h.heure_debut
            """, (id,))
            rows = cur.fetchall()
        for r in rows:
            r["jour_nom"] = JOURS[r["jour_semaine"]]
        return {"success": True, "message": "OK", "data": rows}
    finally:
        db.close()

class HoraireBody(BaseModel):
    jour_semaine: int   # 0=Lundi … 5=Samedi
    heure_debut:  str
    heure_fin:    str
    service_id:   int
    nb_slots:     Optional[int] = 10

@router.post("/{id}/horaires", status_code=201)
def add_horaire(id: int, body: HoraireBody, current_user=Depends(require_role("medecin","administrateur"))):
    if current_user.get("role") == "medecin" and current_user.get("medecin_id") != id:
        raise HTTPException(403, "Accès refusé.")
    if not (0 <= body.jour_semaine <= 5):
        raise HTTPException(422, "jour_semaine doit être entre 0 (Lundi) et 5 (Samedi).")
    db = get_db()
    try:
        # Récupérer la structure du médecin
        with db.cursor() as cur:
            cur.execute("SELECT structure_id FROM medecins WHERE id=%s", (id,))
            med = cur.fetchone()
            if not med: raise HTTPException(404, "Médecin introuvable.")
            cur.execute(
                "INSERT INTO horaires_medecins (medecin_id, structure_id, service_id, jour_semaine, heure_debut, heure_fin, nb_slots) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (id, med["structure_id"], body.service_id, body.jour_semaine,
                 body.heure_debut, body.heure_fin, body.nb_slots)
            )
            horaire_id = cur.lastrowid
        db.commit()
        # Générer immédiatement les créneaux pour les 30 prochains jours
        with db.cursor() as cur:
            cur.execute("CALL generer_disponibilites(30)")
        db.commit()
        return {"success": True, "message": "Horaire ajouté et créneaux générés.", "data": {"id": horaire_id}}
    except Exception as e:
        db.rollback()
        if "Duplicate" in str(e):
            raise HTTPException(409, "Un horaire existe déjà pour ce créneau.")
        raise HTTPException(500, str(e))
    finally:
        db.close()

@router.delete("/{id}/horaires/{horaire_id}")
def delete_horaire(id: int, horaire_id: int, current_user=Depends(require_role("medecin","administrateur"))):
    if current_user.get("role") == "medecin" and current_user.get("medecin_id") != id:
        raise HTTPException(403, "Accès refusé.")
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM horaires_medecins WHERE id=%s AND medecin_id=%s", (horaire_id, id))
            if cur.rowcount == 0:
                raise HTTPException(404, "Horaire introuvable.")
        db.commit()
        return {"success": True, "message": "Horaire supprimé.", "data": None}
    finally:
        db.close()
