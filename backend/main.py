from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

load_dotenv()

from routers import auth, structures, medecins, rendez_vous, alertes, redeplois, dashboard, admin

app = FastAPI(title="Sunu Kiray API", version="1.0.0")

@app.on_event("startup")
def startup():
    """Nettoyage automatique au démarrage : marquer absents les RDV passés non honorés."""
    try:
        from database import get_db
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "UPDATE rendez_vous SET statut='absent' "
                "WHERE statut='confirme' AND date_rdv < CURDATE()"
            )
        db.commit()
        db.close()
    except Exception:
        pass

# CORS
origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,        prefix="/auth")
app.include_router(structures.router,  prefix="/structures")
app.include_router(medecins.router,    prefix="/medecins")
app.include_router(rendez_vous.router, prefix="/rendez-vous")
app.include_router(alertes.router,     prefix="/alertes")
app.include_router(redeplois.router,   prefix="/redeplois")
app.include_router(dashboard.router,   prefix="/dashboard")
app.include_router(admin.router,       prefix="/admin")

@app.get("/")
def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "../frontend/index.html"))

# Servir le frontend statique sur /app
app.mount("/app", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../frontend"), html=True), name="frontend")
