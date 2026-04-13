from fastapi import APIRouter, Depends
from database import get_db
from security import require_role

router = APIRouter(tags=["Dashboard"])

@router.get("")
def stats(user=Depends(require_role("administrateur"))):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM structures_sante WHERE statut='actif'")
            structures_actives = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM medecins")
            total_medecins = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM medecins WHERE disponibilite='disponible'")
            medecins_disponibles = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM rendez_vous WHERE date_rdv=CURDATE()")
            rdv_aujourd_hui = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM alertes WHERE est_traitee=0")
            alertes_actives = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM utilisateurs WHERE role='patient'")
            total_patients = cur.fetchone()["n"]
            cur.execute("SELECT * FROM vue_charge_structures ORDER BY taux_charge_pct DESC")
            charge_structures = cur.fetchall()
            cur.execute("""
                SELECT DATE_FORMAT(date_rdv,'%a') AS jour, COUNT(*) AS total
                FROM rendez_vous
                WHERE date_rdv BETWEEN DATE_SUB(CURDATE(),INTERVAL 6 DAY) AND CURDATE()
                GROUP BY date_rdv ORDER BY date_rdv""")
            rdv_semaine = cur.fetchall()
        return {"success": True, "message": "OK", "data": {
            "structures_actives": structures_actives,
            "total_medecins": total_medecins,
            "medecins_disponibles": medecins_disponibles,
            "rdv_aujourd_hui": rdv_aujourd_hui,
            "alertes_actives": alertes_actives,
            "total_patients": total_patients,
            "charge_structures": charge_structures,
            "rdv_semaine": rdv_semaine,
        }}
    finally:
        db.close()
