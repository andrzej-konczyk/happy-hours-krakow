from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from api.routes import admin, health, venues, deals, preview

app = FastAPI(
    title="Happy Hours Kraków",
    description="API for discovering happy hour deals in Kraków bars",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(venues.router)
app.include_router(deals.router)
app.include_router(preview.router)
app.include_router(admin.router)


@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse(url="/deals/preview")