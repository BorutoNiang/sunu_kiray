from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db
from security import get_current_user, require_role

router = APIRouter(tags=["Structures"])

@router.get("")
def index(region: Optional[str] = None, type: Optional[str] = None, _=Depends(get_current_user)):
    db = get_db()
    try:
        where, params = ['s.statut = "actif"'], []
        if region: where.append("s.region = %s"); params.append(region)
        if type:   where.append("s.type_structure = %s"); params.append(type)
        sql = f"""
            SELECT s.*,
              ROUND((s.charge_actuelle/s.capacite_journaliere)*100,1) AS taux_charge_pct,
              CASE WHEN (s.charge_actuelle/s.capacite_journaliere)>=0.90 THEN 'critique'
                   WHEN (s.charge_actuelle/s.capacite_journaliere)>=0.75 THEN 'haute'
                   WHEN (s.charge_actuelle/s.capacite_journaliere)>=0.50 THEN 'moyenne'
                   ELSE 'normale' END AS niveau_charge,
              (SELECT COUNT(*) FROM medecins m WHERE m.structure_id=s.id AND m.disponibilite='disponible') AS medecins_disponibles,
              (SELECT COUNT(*) FROM medecins m WHERE m.structure_id=s.id) AS total_medecins
            FROM structures_sante s WHERE {' AND '.join(where)} ORDER BY s.charge_actuelle DESC"""
        with db.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return {"success": True, "message": "OK", "data": rows}
    finally:
        db.close()

@router.get("/{id}")
def show(id: int, _=Depends(get_current_user)):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM structures_sante WHERE id = %s", (id,))
            s = cur.fetchone()
            if not s: raise HTTPException(404, "Structure introuvable.")
            cur.execute("SELECT * FROM services WHERE structure_id = %s AND est_actif = 1", (id,))
            s["services"] = cur.fetchall()
            cur.execute(
                "SELECT m.id,m.specialite,m.grade,m.disponibilite,CONCAT(u.prenom,' ',u.nom) AS nom_complet "
                "FROM medecins m JOIN utilisateurs u ON m.utilisateur_id=u.id WHERE m.structure_id=%s", (id,))
            s["medecins"] = cur.fetchall()
        return {"success": True, "message": "OK", "data": s}
    finally:
        db.close()

@router.get("/{id}/alertes")
def alertes(id: int, user=Depends(require_role("administrateur"))):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM alertes WHERE structure_id=%s AND est_traitee=0 ORDER BY priorite DESC", (id,))
            rows = cur.fetchall()
        return {"success": True, "message": "OK", "data": rows}
    finally:
        db.close()

class ChargeBody(BaseModel):
    charge_actuelle: int

@router.put("/{id}/charge")
def update_charge(id: int, body: ChargeBody, user=Depends(require_role("administrateur","medecin"))):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("UPDATE structures_sante SET charge_actuelle=%s WHERE id=%s", (body.charge_actuelle, id))
            cur.execute("CALL verifier_charge_structure(%s)", (id,))
        db.commit()
        return {"success": True, "message": "Charge mise à jour.", "data": None}
    finally:
        db.close()
