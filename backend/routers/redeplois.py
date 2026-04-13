from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db
from security import require_role

router = APIRouter(tags=["Redéploiements"])

class StoreBody(BaseModel):
    medecin_id: int
    structure_origine_id: int
    structure_destination_id: int
    date_debut: str
    date_fin: str
    motif: str
    alerte_id: Optional[int] = None
    service_destination_id: Optional[int] = None

@router.post("", status_code=201)
def store(body: StoreBody, user=Depends(require_role("administrateur"))):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO redeplois (medecin_id,alerte_id,structure_origine_id,structure_destination_id,"
                "service_destination_id,date_debut,date_fin,motif,propose_par) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (body.medecin_id, body.alerte_id, body.structure_origine_id, body.structure_destination_id,
                 body.service_destination_id, body.date_debut, body.date_fin, body.motif, user["sub"]))
            rdp_id = cur.lastrowid
            cur.execute("SELECT utilisateur_id FROM medecins WHERE id=%s", (body.medecin_id,))
            m = cur.fetchone()
            if m:
                cur.execute(
                    "INSERT INTO notifications (utilisateur_id,type_notif,canal,titre,message) "
                    "VALUES (%s,'proposition_redeploiement','inapp','Nouvelle mission proposée',%s)",
                    (m["utilisateur_id"], f"Mission proposée du {body.date_debut} au {body.date_fin}."))
        db.commit()
        return {"success": True, "message": "Redéploiement proposé.", "data": {"id": rdp_id}}
    finally:
        db.close()

class RepondreBody(BaseModel):
    statut: str
    note_medecin: Optional[str] = ""

@router.put("/{id}/repondre")
def repondre(id: int, body: RepondreBody, user=Depends(require_role("medecin"))):
    if body.statut not in ("accepte","refuse"):
        raise HTTPException(422, "Statut invalide.")
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM redeplois WHERE id=%s", (id,))
            rdp = cur.fetchone()
            if not rdp: raise HTTPException(404, "Redéploiement introuvable.")
            cur.execute("SELECT id FROM medecins WHERE id=%s AND utilisateur_id=%s", (rdp["medecin_id"], user["sub"]))
            if not cur.fetchone(): raise HTTPException(403, "Accès refusé.")
            cur.execute("UPDATE redeplois SET statut=%s,note_medecin=%s WHERE id=%s", (body.statut, body.note_medecin, id))
            if body.statut == "accepte":
                cur.execute("UPDATE medecins SET disponibilite='en_mission' WHERE id=%s", (rdp["medecin_id"],))
        db.commit()
        return {"success": True, "message": "Réponse enregistrée.", "data": None}
    except HTTPException:
        db.rollback(); raise
    finally:
        db.close()

@router.get("")
def index(user=Depends(require_role("administrateur"))):
    """Liste tous les redéploiements."""
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT r.id, r.statut, r.date_debut, r.date_fin, r.motif, r.note_medecin,
                       CONCAT(u.prenom,' ',u.nom) AS medecin_nom, m.specialite,
                       so.nom AS structure_origine, sd.nom AS structure_destination,
                       r.created_at
                FROM redeplois r
                JOIN medecins m ON r.medecin_id = m.id
                JOIN utilisateurs u ON m.utilisateur_id = u.id
                JOIN structures_sante so ON r.structure_origine_id = so.id
                JOIN structures_sante sd ON r.structure_destination_id = sd.id
                ORDER BY r.created_at DESC
                LIMIT 50
            """)
            rows = cur.fetchall()
        import datetime
        for r in rows:
            for k in ('date_debut','date_fin','created_at'):
                if isinstance(r.get(k), (datetime.date, datetime.datetime)):
                    r[k] = str(r[k])
        return {"success": True, "message": "OK", "data": rows}
    finally:
        db.close()
