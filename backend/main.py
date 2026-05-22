from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from logger import get_logger
import os

load_dotenv()
log = get_logger("main")

from routers import auth, structures, medecins, rendez_vous, alertes, redeplois, dashboard, admin

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Sunu Kiray API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
            affected = cur.rowcount
        db.commit()
        db.close()
        if affected:
            log.info(f"Startup : {affected} RDV passés marqués absents.")
    except Exception as e:
        log.error(f"Startup cleanup error: {e}")

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
