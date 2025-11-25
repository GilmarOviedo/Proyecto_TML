import time

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import schemas, crud
from .deps import DBSessionDep


app = FastAPI(title="Image Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir imágenes estáticas
app.mount("/images", StaticFiles(directory="/data/images/img_real_clean"), name="images")


@app.get("/")
async def root():
    return {"message": "Image Search API running"}


@app.post("/images/", response_model=schemas.ImageEmbedding)
async def create_image(payload: schemas.ImageEmbeddingCreate, db=DBSessionDep):
    return crud.create_image_embedding(db, payload)


@app.post("/search/text", response_model=schemas.SearchResponse)
async def search_by_text(request: schemas.TextSearchRequest, db=DBSessionDep):
    start_time = time.time()
    results = crud.search_by_text(
        db,
        request.query,
        top_k=request.top_k,
        gender=request.gender,
        category=request.category,
    )
    search_time_ms = (time.time() - start_time) * 1000  # Convertir a milisegundos
    return {"results": results, "search_time_ms": round(search_time_ms, 2)}


@app.post("/search/image", response_model=schemas.SearchResponse)
async def search_by_image(
    file: UploadFile = File(...),
    top_k: int = Form(10),
    gender: str | None = Form(None),
    category: str | None = Form(None),
    db=DBSessionDep,
):
    start_time = time.time()
    results = crud.search_by_image(
        db, file, top_k=top_k, gender=gender, category=category
    )
    search_time_ms = (time.time() - start_time) * 1000
    return {"results": results, "search_time_ms": round(search_time_ms, 2)}

