from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from database import get_db
from security import require_role

router = APIRouter(tags=["Alertes"])

@router.get("")
def index(priorite: Optional[str]=None, user=Depends(require_role("administrateur"))):
    db = get_db()
    try:
        where, params = ["a.est_traitee=0"], []
        if priorite: where.append("a.priorite=%s"); params.append(priorite)
        w = ' AND '.join(where)
        with db.cursor() as cur:
            cur.execute(f"""
                SELECT a.*,s.nom AS structure_nom,s.ville,sv.nom AS service_nom
                FROM alertes a
                JOIN structures_sante s ON a.structure_id=s.id
                LEFT JOIN services sv ON a.service_id=sv.id
                WHERE {w}
                ORDER BY FIELD(a.priorite,'critique','haute','moyenne','faible'),a.created_at DESC""", params)
            rows = cur.fetchall()
        return {"success": True, "message": "OK", "data": rows}
    finally:
        db.close()

class TraiterBody(BaseModel):
    action_effectuee: Optional[str] = ""

@router.put("/{id}/traiter")
def traiter(id: int, body: TraiterBody, user=Depends(require_role("administrateur"))):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "UPDATE alertes SET est_traitee=1,traitee_par=%s,traitee_le=NOW(),action_effectuee=%s WHERE id=%s",
                (user["sub"], body.action_effectuee, id))
        db.commit()
        return {"success": True, "message": "Alerte traitée.", "data": None}
    finally:
        db.close()
