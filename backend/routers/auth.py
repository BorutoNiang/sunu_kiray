from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from database import get_db
from security import hash_password, verify_password, create_token, get_current_user
import secrets

router = APIRouter(tags=["Auth"])

class RegisterBody(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    telephone: str
    mot_de_passe: str
    role: str
    date_naissance: Optional[str] = None
    sexe: Optional[str] = None
    ville: Optional[str] = None
    specialite: Optional[str] = None
    numero_ordre: Optional[str] = None
    structure_id: Optional[int] = None
    grade: Optional[str] = "generaliste"

class LoginBody(BaseModel):
    email: EmailStr
    mot_de_passe: str

class ForgotBody(BaseModel):
    email: EmailStr

class ResetBody(BaseModel):
    token: str
    nouveau_mot_de_passe: str

@router.post("/register", status_code=201)
def register(body: RegisterBody):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM utilisateurs WHERE email = %s", (body.email.lower(),))
            if cur.fetchone():
                raise HTTPException(409, "Cet email est déjà utilisé.")
            cur.execute("SELECT id FROM utilisateurs WHERE telephone = %s", (body.telephone,))
            if cur.fetchone():
                raise HTTPException(409, "Ce téléphone est déjà utilisé.")

            hashed = hash_password(body.mot_de_passe)
            cur.execute(
                "INSERT INTO utilisateurs (nom,prenom,email,telephone,mot_de_passe,role,date_naissance,sexe,ville) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (body.nom, body.prenom, body.email.lower(), body.telephone,
                 hashed, body.role, body.date_naissance, body.sexe, body.ville)
            )
            user_id = cur.lastrowid

            if body.role == "medecin":
                if not body.specialite or not body.numero_ordre or not body.structure_id:
                    raise HTTPException(422, "specialite, numero_ordre et structure_id requis pour un médecin.")
                cur.execute("SELECT id FROM medecins WHERE numero_ordre = %s", (body.numero_ordre,))
                if cur.fetchone():
                    raise HTTPException(409, "Ce numéro d'ordre est déjà enregistré.")
                cur.execute(
                    "INSERT INTO medecins (utilisateur_id,structure_id,specialite,numero_ordre,grade) VALUES (%s,%s,%s,%s,%s)",
                    (user_id, body.structure_id, body.specialite, body.numero_ordre, body.grade)
                )
        db.commit()
        token = create_token({"sub": str(user_id), "role": body.role, "nom": body.nom, "prenom": body.prenom})
        return {"success": True, "message": "Compte créé.", "data": {
            "token": token,
            "user": {"id": user_id, "nom": body.nom, "prenom": body.prenom, "email": body.email, "role": body.role}
        }}
    finally:
        db.close()

@router.post("/login")
def login(body: LoginBody):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT u.*, m.id AS medecin_id, m.structure_id, m.specialite "
                "FROM utilisateurs u LEFT JOIN medecins m ON m.utilisateur_id = u.id "
                "WHERE u.email = %s", (body.email.lower(),)
            )
            user = cur.fetchone()
        if not user or not verify_password(body.mot_de_passe, user["mot_de_passe"]):
            raise HTTPException(401, "Email ou mot de passe incorrect.")
        if not user["est_actif"]:
            raise HTTPException(403, "Compte désactivé.")
        with db.cursor() as cur:
            cur.execute("UPDATE utilisateurs SET derniere_connexion = NOW() WHERE id = %s", (user["id"],))
        db.commit()
        payload = {"sub": str(user["id"]), "role": user["role"], "nom": user["nom"], "prenom": user["prenom"], "email": user["email"]}
        if user["role"] == "medecin":
            payload["medecin_id"]   = user["medecin_id"]
            payload["structure_id"] = user["structure_id"]
        token = create_token(payload)
        user.pop("mot_de_passe", None)
        user.pop("token_reset", None)
        user.pop("token_expire_le", None)
        return {"success": True, "message": "Connexion réussie.", "data": {"token": token, "user": user}}
    finally:
        db.close()

@router.post("/forgot-password")
def forgot_password(body: ForgotBody):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM utilisateurs WHERE email = %s AND est_actif = 1", (body.email.lower(),))
            user = cur.fetchone()
            if user:
                token = secrets.token_hex(32)
                cur.execute(
                    "UPDATE utilisateurs SET token_reset = %s, token_expire_le = DATE_ADD(NOW(), INTERVAL 1 HOUR) WHERE id = %s",
                    (token, user["id"])
                )
        db.commit()
        return {"success": True, "message": "Si cet email existe, un lien a été envoyé.", "data": None}
    finally:
        db.close()

@router.post("/reset-password")
def reset_password(body: ResetBody):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM utilisateurs WHERE token_reset = %s AND token_expire_le > NOW()", (body.token,))
            user = cur.fetchone()
            if not user:
                raise HTTPException(400, "Token invalide ou expiré.")
            cur.execute(
                "UPDATE utilisateurs SET mot_de_passe = %s, token_reset = NULL, token_expire_le = NULL WHERE id = %s",
                (hash_password(body.nouveau_mot_de_passe), user["id"])
            )
        db.commit()
        return {"success": True, "message": "Mot de passe réinitialisé.", "data": None}
    finally:
        db.close()

@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT u.id,u.nom,u.prenom,u.email,u.telephone,u.role,u.ville,u.date_naissance,u.sexe, "
                "m.id AS medecin_id, m.specialite, m.grade, m.disponibilite, s.nom AS structure_nom "
                "FROM utilisateurs u "
                "LEFT JOIN medecins m ON m.utilisateur_id = u.id "
                "LEFT JOIN structures_sante s ON s.id = m.structure_id "
                "WHERE u.id = %s", (current_user["sub"],)
            )
            user = cur.fetchone()
        if not user:
            raise HTTPException(404, "Utilisateur introuvable.")
        return {"success": True, "message": "OK", "data": user}
    finally:
        db.close()

from pydantic import BaseModel as _BaseModel

class UpdateProfileBody(_BaseModel):
    nom:            Optional[str] = None
    prenom:         Optional[str] = None
    telephone:      Optional[str] = None
    ville:          Optional[str] = None
    date_naissance: Optional[str] = None
    sexe:           Optional[str] = None

@router.put("/me")
def update_me(body: UpdateProfileBody, current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        fields, params = [], []
        if body.nom            is not None: fields.append("nom=%s");            params.append(body.nom)
        if body.prenom         is not None: fields.append("prenom=%s");         params.append(body.prenom)
        if body.telephone      is not None: fields.append("telephone=%s");      params.append(body.telephone)
        if body.ville          is not None: fields.append("ville=%s");          params.append(body.ville)
        if body.date_naissance is not None: fields.append("date_naissance=%s"); params.append(body.date_naissance or None)
        if body.sexe           is not None: fields.append("sexe=%s");           params.append(body.sexe or None)
        if not fields:
            raise HTTPException(400, "Aucun champ à mettre à jour.")
        params.append(current_user["sub"])
        with db.cursor() as cur:
            cur.execute(f"UPDATE utilisateurs SET {', '.join(fields)} WHERE id=%s", params)
        db.commit()
        return {"success": True, "message": "Profil mis à jour.", "data": None}
    finally:
        db.close()
