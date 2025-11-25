from pydantic import BaseModel


class ImageEmbeddingBase(BaseModel):
    image_path: str
    embedding: str
    faiss_index: int | None = None


class ImageEmbeddingCreate(ImageEmbeddingBase):
    pass


class ImageEmbedding(ImageEmbeddingBase):
    id: int

    class Config:
        from_attributes = True


class TextSearchRequest(BaseModel):
    query: str
    top_k: int = 10
    gender: str | None = None  # MEN, WOMEN o None para todos
    category: str | None = None  # Denim, Polo, etc. o None para todas


class ImageResult(BaseModel):
    image_id: str
    file_path: str
    url: str
    similarity: float | None = None


class SearchResponse(BaseModel):
    results: list[ImageResult]
    search_time_ms: float | None = None  # Tiempo de búsqueda en milisegundos
