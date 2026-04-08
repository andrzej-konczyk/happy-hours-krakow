from fastapi import FastAPI
from api.routes import health, venues, deals, preview

app = FastAPI(
    title="Happy Hours Kraków",
    description="API for discovering happy hour deals in Kraków bars",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(venues.router)
app.include_router(deals.router)
app.include_router(preview.router)