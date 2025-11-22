import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI(title="SneakPeek API", description="E-commerce Shoes Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def seed_on_startup():
    try:
        if db is None:
            return
        count = db["shoeproduct"].count_documents({})
        if count == 0:
            samples = [
                {
                    "title": "AirFlex Pro Triple White",
                    "slug": "airflex-pro-triple-white",
                    "brand": "SneakPeek",
                    "description": "A lightweight performance sneaker with breathable mesh and responsive cushioning for all-day comfort.",
                    "price": 149.0,
                    "rating": 4.7,
                    "images": [
                        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=1400&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1542291025-59c29d6d7c43?q=80&w=1400&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1542291022-7d5c4f47b1f4?q=80&w=1400&auto=format&fit=crop"
                    ],
                    "colors": [
                        {"name": "Triple White", "hex": "#ffffff"},
                        {"name": "Ice", "hex": "#e6f0ff"}
                    ],
                    "sizes": [7,7.5,8,8.5,9,9.5,10,10.5,11,12],
                    "stock": {"9": 12, "10": 8, "11": 4},
                    "tags": ["running","lightweight","white"]
                },
                {
                    "title": "Runner X Shadow",
                    "slug": "runner-x-shadow",
                    "brand": "AeroLab",
                    "description": "Engineered knit upper with carbon plate midsole for explosive energy return.",
                    "price": 189.0,
                    "rating": 4.8,
                    "images": [
                        "https://images.unsplash.com/photo-1543508282-6319a3e2621f?q=80&w=1400&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1542291024-54f8c2b590bd?q=80&w=1400&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1519741497674-611481863552?q=80&w=1400&auto=format&fit=crop"
                    ],
                    "colors": [
                        {"name": "Shadow", "hex": "#111827"},
                        {"name": "Volt", "hex": "#a7f3d0"}
                    ],
                    "sizes": [7,8,9,10,11,12,13],
                    "stock": {"9": 6, "10": 3},
                    "tags": ["race","carbon","black"]
                },
                {
                    "title": "Court Classic 2.0",
                    "slug": "court-classic-2",
                    "brand": "RetroWorks",
                    "description": "Premium leather upper with vintage tooling for an everyday court-inspired look.",
                    "price": 129.0,
                    "rating": 4.6,
                    "images": [
                        "https://images.unsplash.com/photo-1542291024-94bcdc71f39d?q=80&w=1400&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1520256862855-398228c41684?q=80&w=1400&auto=format&fit=crop",
                        "https://images.unsplash.com/photo-1519741497674-611481863552?q=80&w=1400&auto=format&fit=crop"
                    ],
                    "colors": [
                        {"name": "Sail", "hex": "#f5f5f4"},
                        {"name": "Gum", "hex": "#d97706"}
                    ],
                    "sizes": [6,7,8,9,10,11],
                    "stock": {"8": 10, "9": 2},
                    "tags": ["leather","casual","retro"]
                }
            ]
            for s in samples:
                create_document("shoeproduct", s)
    except Exception:
        # Avoid crashing on startup if db unavailable
        pass

@app.get("/")
def read_root():
    return {"message": "SneakPeek backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# ---------- Shoes endpoints ----------
class ShoeSeed(BaseModel):
    title: str
    slug: str
    brand: str
    description: str
    price: float
    rating: float
    images: List[str]
    colors: List[dict]
    sizes: List[float]
    stock: dict
    tags: List[str]

@app.post("/seed/shoes")
def seed_shoes(payload: List[ShoeSeed]):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    inserted_ids = []
    for item in payload:
        inserted_id = create_document("shoeproduct", item)
        inserted_ids.append(inserted_id)
    return {"inserted": len(inserted_ids), "ids": inserted_ids}

@app.get("/products")
def list_products(limit: int = 20):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("shoeproduct", {}, limit)
    for d in docs:
        if "_id" in d and isinstance(d["_id"], ObjectId):
            d["_id"] = str(d["_id"])
    return {"items": docs}

@app.get("/products/{slug}")
def get_product(slug: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("shoeproduct", {"slug": slug}, 1)
    if not docs:
        raise HTTPException(status_code=404, detail="Product not found")
    doc = docs[0]
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
