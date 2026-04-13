from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from database import get_db
from security import get_current_user, require_role
import random
import string
from datetime import date as date_type

router = APIRouter(tags=["Rendez-vous"])

def gen_code() -> str:
    return ''.join(random.choices(string.digits, k=6))

@router.get("")
def index(page: int = 1, per_page: int = 20, statut: Optional[str] = None,
          date_rdv: Optional[str] = None, structure_id: Optional[int] = None,
          current_user=Depends(get_current_user)):
    db = get_db()
    try:
        per_page = min(per_page, 50)
        offset   = (page - 1) * per_page
        where, params = ["1=1"], []
        if current_user["role"] == "patient":
            where.append("r.patient_id=%s"); params.append(current_user["sub"])
        elif current_user["role"] == "medecin":
            where.append("r.medecin_id=%s"); params.append(current_user.get("medecin_id"))
        if statut:      where.append("r.statut=%s");          params.append(statut)
        if date_rdv:    where.append("r.date_rdv=%s");        params.append(date_rdv)
        if structure_id:where.append("st.id=%s");             params.append(structure_id)
        w = ' AND '.join(where)
        with db.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS total FROM rendez_vous r JOIN medecins md ON r.medecin_id=md.id JOIN services sv ON r.service_id=sv.id JOIN structures_sante st ON sv.structure_id=st.id WHERE {w}", params)
            total = cur.fetchone()["total"]
            cur.execute(f"""
                SELECT r.id, r.date_rdv, r.heure_rdv, r.statut, r.motif, r.code_confirmation,
                       CONCAT(up.prenom,' ',up.nom) AS patient_nom, up.telephone AS patient_tel,
                       CONCAT(um.prenom,' ',um.nom) AS medecin_nom, md.specialite,
                       sv.nom AS service, st.nom AS structure, st.ville
                FROM rendez_vous r
                JOIN utilisateurs up ON r.patient_id=up.id
                JOIN medecins md ON r.medecin_id=md.id
                JOIN utilisateurs um ON md.utilisateur_id=um.id
                JOIN services sv ON r.service_id=sv.id
                JOIN structures_sante st ON sv.structure_id=st.id
                WHERE {w} ORDER BY r.date_rdv, r.heure_rdv
                LIMIT %s OFFSET %s""", params + [per_page, offset])
            rdvs = cur.fetchall()
        # Convertir timedelta en string HH:MM:SS
        import datetime
        for r in rdvs:
            if isinstance(r.get("heure_rdv"), datetime.timedelta):
                total_sec = int(r["heure_rdv"].total_seconds())
                r["heure_rdv"] = f"{total_sec//3600:02d}:{(total_sec%3600)//60:02d}:00"
            if isinstance(r.get("date_rdv"), datetime.date):
                r["date_rdv"] = str(r["date_rdv"])
        last_page = max(1, -(-total // per_page))
        return {"success": True, "message": "OK", "data": {
            "rdvs": rdvs,
            "pagination": {"total": total, "per_page": per_page, "current_page": page, "last_page": last_page}
        }}
    finally:
        db.close()

@router.get("/disponibilites")
def disponibilites(structure_id: int = Query(...), service_id: int = Query(...),
                   date: Optional[str] = None, _=Depends(get_current_user)):
    query_date = date or str(date_type.today())
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT d.id, d.date_travail, d.heure_debut, d.heure_fin,
                       d.nb_slots_max, d.nb_slots_pris,
                       (d.nb_slots_max - d.nb_slots_pris) AS slots_restants,
                       CONCAT(u.prenom,' ',u.nom) AS medecin_nom, m.specialite
                FROM disponibilites d
                JOIN medecins m ON d.medecin_id=m.id
                JOIN utilisateurs u ON m.utilisateur_id=u.id
                WHERE d.structure_id=%s AND d.service_id=%s AND d.date_travail=%s
                  AND d.est_actif=1 AND d.nb_slots_pris < d.nb_slots_max
                ORDER BY d.heure_debut""", (structure_id, service_id, query_date))
            rows = cur.fetchall()
        import datetime
        for r in rows:
            for k in ('heure_debut', 'heure_fin'):
                if isinstance(r.get(k), datetime.timedelta):
                    s = int(r[k].total_seconds())
                    r[k] = f"{s//3600:02d}:{(s%3600)//60:02d}:00"
            if isinstance(r.get('date_travail'), datetime.date):
                r['date_travail'] = str(r['date_travail'])
        return {"success": True, "message": "OK", "data": rows}
    finally:
        db.close()

class RdvBody(BaseModel):
    disponibilite_id: int
    motif: Optional[str] = ""

@router.post("", status_code=201)
def store(body: RdvBody, current_user=Depends(require_role("patient"))):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT d.*, s.id AS service_id FROM disponibilites d "
                "JOIN services s ON d.service_id=s.id "
                "WHERE d.id=%s AND d.est_actif=1 AND d.date_travail>=CURDATE() FOR UPDATE",
                (body.disponibilite_id,))
            dispo = cur.fetchone()
            if not dispo:
                raise HTTPException(404, "Créneau introuvable ou indisponible.")
            if dispo["nb_slots_pris"] >= dispo["nb_slots_max"]:
                raise HTTPException(409, "Ce créneau est complet.")
            cur.execute(
                "SELECT r.id FROM rendez_vous r JOIN services sv ON r.service_id=sv.id "
                "WHERE r.patient_id=%s AND r.date_rdv=%s AND sv.structure_id=%s "
                "AND r.statut NOT IN ('annule_patient','annule_medecin','absent')",
                (current_user["sub"], dispo["date_travail"], dispo["structure_id"]))
            if cur.fetchone():
                raise HTTPException(409, "Vous avez déjà un RDV dans cette structure ce jour-là.")
            code = gen_code()
            cur.execute(
                "INSERT INTO rendez_vous "
                "(patient_id, medecin_id, service_id, disponibilite_id, date_rdv, heure_rdv, motif, code_confirmation, statut) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'confirme')",
                (current_user["sub"], dispo["medecin_id"], dispo["service_id"],
                 dispo["id"], dispo["date_travail"], dispo["heure_debut"], body.motif or "", code))
            rdv_id = cur.lastrowid
            cur.execute("UPDATE disponibilites SET nb_slots_pris=nb_slots_pris+1 WHERE id=%s", (dispo["id"],))
            cur.execute(
                "INSERT INTO notifications (utilisateur_id, rendez_vous_id, type_notif, canal, titre, message) "
                "VALUES (%s,%s,'confirmation_rdv','sms','Rendez-vous confirmé',%s)",
                (current_user["sub"], rdv_id,
                 f"Votre RDV du {dispo['date_travail']} est confirmé. Code : {code}"))
        db.commit()
        return {"success": True, "message": "Rendez-vous créé.", "data": {
            "rdv_id": rdv_id,
            "code_confirmation": code,
            "date_rdv": str(dispo["date_travail"]),
            "heure_rdv": str(dispo["heure_debut"])
        }}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Erreur serveur : {str(e)}")
    finally:
        db.close()

@router.get("/{id}")
def show(id: int, current_user=Depends(get_current_user)):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT r.*, CONCAT(up.prenom,' ',up.nom) AS patient_nom,
                       CONCAT(um.prenom,' ',um.nom) AS medecin_nom, md.specialite,
                       sv.nom AS service, st.nom AS structure, st.ville, st.adresse
                FROM rendez_vous r
                JOIN utilisateurs up ON r.patient_id=up.id
                JOIN medecins md ON r.medecin_id=md.id
                JOIN utilisateurs um ON md.utilisateur_id=um.id
                JOIN services sv ON r.service_id=sv.id
                JOIN structures_sante st ON sv.structure_id=st.id
                WHERE r.id=%s""", (id,))
            rdv = cur.fetchone()
        if not rdv:
            raise HTTPException(404, "RDV introuvable.")
        if current_user["role"] == "patient" and rdv["patient_id"] != current_user["sub"]:
            raise HTTPException(403, "Accès refusé.")
        if current_user["role"] == "medecin" and rdv["medecin_id"] != current_user.get("medecin_id"):
            raise HTTPException(403, "Accès refusé.")
        return {"success": True, "message": "OK", "data": rdv}
    finally:
        db.close()

@router.put("/{id}/annuler")
def cancel(id: int, current_user=Depends(get_current_user)):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM rendez_vous WHERE id=%s", (id,))
            rdv = cur.fetchone()
            if not rdv:
                raise HTTPException(404, "RDV introuvable.")
            if current_user["role"] == "patient" and rdv["patient_id"] != current_user["sub"]:
                raise HTTPException(403, "Accès refusé.")
            if rdv["statut"] in ("termine", "annule_patient", "annule_medecin"):
                raise HTTPException(400, "Ce RDV ne peut plus être annulé.")
            nouveau = "annule_patient" if current_user["role"] == "patient" else "annule_medecin"
            cur.execute("UPDATE rendez_vous SET statut=%s WHERE id=%s", (nouveau, id))
            cur.execute(
                "UPDATE disponibilites SET nb_slots_pris=GREATEST(0, nb_slots_pris-1) WHERE id=%s",
                (rdv["disponibilite_id"],))
        db.commit()
        return {"success": True, "message": "RDV annulé.", "data": None}
    except HTTPException:
        db.rollback()
        raise
    finally:
        db.close()

class StatutBody(BaseModel):
    statut: str
    notes_medecin: Optional[str] = ""

@router.put("/{id}/statut")
def update_status(id: int, body: StatutBody, current_user=Depends(require_role("medecin", "administrateur"))):
    allowed = ["confirme", "en_cours", "termine", "absent"]
    if body.statut not in allowed:
        raise HTTPException(422, f"Statut invalide. Valeurs acceptées : {', '.join(allowed)}")
    db = get_db()
    try:
        with db.cursor() as cur:
            if body.statut == "termine" and body.notes_medecin:
                cur.execute(
                    "UPDATE rendez_vous SET statut=%s, notes_medecin=%s WHERE id=%s",
                    (body.statut, body.notes_medecin, id))
            else:
                cur.execute("UPDATE rendez_vous SET statut=%s WHERE id=%s", (body.statut, id))
        db.commit()
        return {"success": True, "message": "Statut mis à jour.", "data": None}
    finally:
        db.close()


def gen_code() -> str:
    return ''.join(random.choices(string.digits, k=6))

@router.get("")
def index(page: int=1, per_page: int=20, statut: Optional[str]=None,
          date_rdv: Optional[str]=None, current_user=Depends(get_current_user)):
    db = get_db()
    try:
        per_page = min(per_page, 50)
        offset   = (page-1)*per_page
        where, params = ["1=1"], []
        if current_user["role"] == "patient":
            where.append("r.patient_id=%s"); params.append(current_user["sub"])
        elif current_user["role"] == "medecin":
            where.append("r.medecin_id=%s"); params.append(current_user.get("medecin_id"))
        if statut:   where.append("r.statut=%s"); params.append(statut)
        if date_rdv: where.append("r.date_rdv=%s"); params.append(date_rdv)
        w = ' AND '.join(where)
        with db.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS total FROM rendez_vous r WHERE {w}", params)
            total = cur.fetchone()["total"]
            cur.execute(f"""
                SELECT r.id,r.date_rdv,r.heure_rdv,r.statut,r.motif,r.code_confirmation,
                       CONCAT(up.prenom,' ',up.nom) AS patient_nom,up.telephone AS patient_tel,
                       CONCAT(um.prenom,' ',um.nom) AS medecin_nom,md.specialite,
                       sv.nom AS service,st.nom AS structure,st.ville
                FROM rendez_vous r
                JOIN utilisateurs up ON r.patient_id=up.id
                JOIN medecins md ON r.medecin_id=md.id
                JOIN utilisateurs um ON md.utilisateur_id=um.id
                JOIN services sv ON r.service_id=sv.id
                JOIN structures_sante st ON sv.structure_id=st.id
                WHERE {w} ORDER BY r.date_rdv,r.heure_rdv
                LIMIT %s OFFSET %s""", params+[per_page, offset])
            rdvs = cur.fetchall()
        last_page = max(1, -(-total//per_page))
        return {"success": True, "message": "OK", "data": {
            "rdvs": rdvs,
            "pagination": {"total":total,"per_page":per_page,"current_page":page,"last_page":last_page}
        }}
    finally:
        db.close()

@router.get("/disponibilites")
def disponibilites(structure_id: int=Query(...), service_id: int=Query(...),
                   date: Optional[str]=None, _=Depends(get_current_user)):
    if not date: date = str(date.today())
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT d.id,d.date_travail,d.heure_debut,d.heure_fin,
                       d.nb_slots_max,d.nb_slots_pris,
                       (d.nb_slots_max-d.nb_slots_pris) AS slots_restants,
                       CONCAT(u.prenom,' ',u.nom) AS medecin_nom,m.specialite
                FROM disponibilites d
                JOIN medecins m ON d.medecin_id=m.id
                JOIN utilisateurs u ON m.utilisateur_id=u.id
                WHERE d.structure_id=%s AND d.service_id=%s AND d.date_travail=%s
                  AND d.est_actif=1 AND d.nb_slots_pris<d.nb_slots_max
                ORDER BY d.heure_debut""", (structure_id, service_id, date))
            rows = cur.fetchall()
        return {"success": True, "message": "OK", "data": rows}
    finally:
        db.close()

class RdvBody(BaseModel):
    disponibilite_id: int
    motif: Optional[str] = ""

@router.post("", status_code=201)
def store(body: RdvBody, current_user=Depends(require_role("patient"))):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT d.*,s.id AS service_id FROM disponibilites d "
                "JOIN services s ON d.service_id=s.id "
                "WHERE d.id=%s AND d.est_actif=1 AND d.date_travail>=CURDATE() FOR UPDATE",
                (body.disponibilite_id,))
            dispo = cur.fetchone()
            if not dispo: raise HTTPException(404, "Créneau introuvable.")
            if dispo["nb_slots_pris"] >= dispo["nb_slots_max"]:
                raise HTTPException(409, "Ce créneau est complet.")
            cur.execute(
                "SELECT r.id FROM rendez_vous r JOIN services sv ON r.service_id=sv.id "
                "WHERE r.patient_id=%s AND r.date_rdv=%s AND sv.structure_id=%s "
                "AND r.statut NOT IN ('annule_patient','annule_medecin','absent')",
                (current_user["sub"], dispo["date_travail"], dispo["structure_id"]))
            if cur.fetchone(): raise HTTPException(409, "Vous avez déjà un RDV dans cette structure ce jour-là.")
            code = gen_code()
            cur.execute(
                "INSERT INTO rendez_vous (patient_id,medecin_id,service_id,disponibilite_id,date_rdv,heure_rdv,motif,code_confirmation) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (current_user["sub"], dispo["medecin_id"], dispo["service_id"],
                 dispo["id"], dispo["date_travail"], dispo["heure_debut"], body.motif or "", code))
            rdv_id = cur.lastrowid
            cur.execute("UPDATE disponibilites SET nb_slots_pris=nb_slots_pris+1 WHERE id=%s", (dispo["id"],))
            cur.execute(
                "INSERT INTO notifications (utilisateur_id,rendez_vous_id,type_notif,canal,titre,message) "
                "VALUES (%s,%s,'confirmation_rdv','sms','Rendez-vous confirmé',%s)",
                (current_user["sub"], rdv_id, f"Votre RDV du {dispo['date_travail']} est confirmé. Code : {code}"))
        db.commit()
        return {"success": True, "message": "Rendez-vous créé.", "data": {
            "rdv_id": rdv_id, "code_confirmation": code,
            "date_rdv": str(dispo["date_travail"]), "heure_rdv": str(dispo["heure_debut"])
        }}
    except HTTPException:
        db.rollback(); raise
    except Exception as e:
        db.rollback(); raise HTTPException(500, str(e))
    finally:
        db.close()

@router.get("/{id}")
def show(id: int, current_user=Depends(get_current_user)):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT r.*,CONCAT(up.prenom,' ',up.nom) AS patient_nom,
                       CONCAT(um.prenom,' ',um.nom) AS medecin_nom,md.specialite,
                       sv.nom AS service,st.nom AS structure,st.ville,st.adresse
                FROM rendez_vous r
                JOIN utilisateurs up ON r.patient_id=up.id
                JOIN medecins md ON r.medecin_id=md.id
                JOIN utilisateurs um ON md.utilisateur_id=um.id
                JOIN services sv ON r.service_id=sv.id
                JOIN structures_sante st ON sv.structure_id=st.id
                WHERE r.id=%s""", (id,))
            rdv = cur.fetchone()
        if not rdv: raise HTTPException(404, "RDV introuvable.")
        if current_user["role"]=="patient"  and rdv["patient_id"]!=current_user["sub"]: raise HTTPException(403,"Accès refusé.")
        if current_user["role"]=="medecin"  and rdv["medecin_id"]!=current_user.get("medecin_id"): raise HTTPException(403,"Accès refusé.")
        return {"success": True, "message": "OK", "data": rdv}
    finally:
        db.close()

@router.put("/{id}/annuler")
def cancel(id: int, current_user=Depends(get_current_user)):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM rendez_vous WHERE id=%s", (id,))
            rdv = cur.fetchone()
            if not rdv: raise HTTPException(404, "RDV introuvable.")
            if current_user["role"]=="patient" and rdv["patient_id"]!=current_user["sub"]: raise HTTPException(403,"Accès refusé.")
            if rdv["statut"] in ("termine","annule_patient","annule_medecin"): raise HTTPException(400,"Ne peut plus être annulé.")
            nouveau = "annule_patient" if current_user["role"]=="patient" else "annule_medecin"
            cur.execute("UPDATE rendez_vous SET statut=%s WHERE id=%s", (nouveau, id))
            cur.execute("UPDATE disponibilites SET nb_slots_pris=GREATEST(0,nb_slots_pris-1) WHERE id=%s", (rdv["disponibilite_id"],))
        db.commit()
        return {"success": True, "message": "RDV annulé.", "data": None}
    except HTTPException:
        db.rollback(); raise
    finally:
        db.close()

class StatutBody(BaseModel):
    statut: str
    notes_medecin: Optional[str] = ""

@router.put("/{id}/statut")
def update_status(id: int, body: StatutBody, current_user=Depends(require_role("medecin","administrateur"))):
    allowed = ["confirme","en_cours","termine","absent"]
    if body.statut not in allowed: raise HTTPException(422, "Statut invalide.")
    db = get_db()
    try:
        with db.cursor() as cur:
            if body.statut == "termine" and body.notes_medecin:
                cur.execute("UPDATE rendez_vous SET statut=%s,notes_medecin=%s WHERE id=%s", (body.statut, body.notes_medecin, id))
            else:
                cur.execute("UPDATE rendez_vous SET statut=%s WHERE id=%s", (body.statut, id))
        db.commit()
        return {"success": True, "message": "Statut mis à jour.", "data": None}
    finally:
        db.close()
