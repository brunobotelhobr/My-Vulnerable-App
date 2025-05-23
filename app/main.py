from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.database.database import engine, Base
from app.routes import auth, cart

# Create FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, tags=["authentication"])
app.include_router(cart.router, tags=["cart"])

# Root route redirect
@app.get("/")
async def root():
    """Redirect root to index.html."""
    return RedirectResponse(url="/index.html")

# Create database tables
Base.metadata.create_all(bind=engine)

# Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static") 