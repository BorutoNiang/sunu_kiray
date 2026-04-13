"""
Génère des disponibilités pour tous les services de toutes les structures
sur les 30 prochains jours (lundi-samedi, 2 créneaux par jour).
Un médecin générique est affecté à chaque service selon la structure.
"""
import pymysql
import pymysql.cursors
import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv

# Charger .env depuis backend/ quel que soit l'endroit d'où on lance le script
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

load_dotenv()

db = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASS", ""),
    database=os.getenv("DB_NAME", "sunu_kiray"),
    cursorclass=pymysql.cursors.DictCursor
)

# Mapping médecin par structure (médecin principal de chaque structure)
# medecin_id -> structure_id
medecins_par_structure = {
    1: [1, 2],   # structure 1 : médecin 1 (Cardio) + médecin 2 (Générale)
    2: [5],      # structure 2 : médecin 5
    3: [],       # structure 3 : pas de médecin inscrit → on utilise médecin 2
    4: [3],      # structure 4 : médecin 3
    5: [4],      # structure 5 : médecin 4
    6: [],       # structure 6 : pas de médecin → on utilise médecin 3
}

# Médecin de secours par structure si pas de médecin dédié
medecin_secours = {3: 2, 6: 3}

# Récupérer tous les services actifs
with db.cursor() as cur:
    cur.execute("SELECT id, structure_id, nom FROM services WHERE est_actif=1")
    services = cur.fetchall()

# Récupérer les médecins avec leur spécialité
with db.cursor() as cur:
    cur.execute("SELECT id, structure_id, specialite FROM medecins")
    medecins = cur.fetchall()

# Index médecins par structure
med_by_struct = {}
for m in medecins:
    med_by_struct.setdefault(m["structure_id"], []).append(m)

today = date.today()
inserted = 0
skipped  = 0

for service in services:
    sid   = service["id"]
    strid = service["structure_id"]
    snom  = service["nom"]

    # Trouver le médecin le plus adapté pour ce service
    meds = med_by_struct.get(strid, [])
    if not meds:
        # Utiliser médecin de secours
        fallback_id = medecin_secours.get(strid)
        if not fallback_id:
            continue
        medecin_id = fallback_id
    else:
        # Préférer un médecin dont la spécialité correspond
        match = next((m for m in meds if m["specialite"].lower() in snom.lower()
                      or snom.lower() in m["specialite"].lower()), None)
        medecin_id = match["id"] if match else meds[0]["id"]

    # Générer les créneaux sur 30 jours (lundi à samedi)
    for delta in range(1, 31):
        d = today + timedelta(days=delta)
        if d.weekday() == 6:  # Dimanche → skip
            continue

        # Créneau matin
        with db.cursor() as cur:
            try:
                cur.execute(
                    "INSERT IGNORE INTO disponibilites "
                    "(medecin_id, structure_id, service_id, date_travail, heure_debut, heure_fin, nb_slots_max) "
                    "VALUES (%s, %s, %s, %s, '08:00:00', '12:00:00', 10)",
                    (medecin_id, strid, sid, d)
                )
                if cur.rowcount: inserted += 1
                else: skipped += 1
            except Exception as e:
                skipped += 1

        # Créneau après-midi (pas le samedi)
        if d.weekday() < 5:
            with db.cursor() as cur:
                try:
                    cur.execute(
                        "INSERT IGNORE INTO disponibilites "
                        "(medecin_id, structure_id, service_id, date_travail, heure_debut, heure_fin, nb_slots_max) "
                        "VALUES (%s, %s, %s, %s, '14:00:00', '18:00:00', 10)",
                        (medecin_id, strid, sid, d)
                    )
                    if cur.rowcount: inserted += 1
                    else: skipped += 1
                except Exception as e:
                    skipped += 1

db.commit()
db.close()

print(f"Créneaux insérés  : {inserted}")
print(f"Déjà existants    : {skipped}")
print(f"Total services    : {len(services)}")
print("Disponibilités générées pour tous les services sur 30 jours.")
