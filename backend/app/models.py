from sqlalchemy import Column, Integer, String, Text, DateTime, func

from .database import Base


class ImageEmbedding(Base):
    __tablename__ = "image_embeddings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # Ruta relativa de la imagen, por ejemplo:
    # WOMEN/Denim/id_00002359/03_3_back.jpg
    image_path = Column(String(512), unique=True, index=True, nullable=False)
    # Embedding completo como string (lista de 768 floats).
    embedding = Column(Text, nullable=False)
    # Índice del vector dentro del archivo faiss_index.bin
    faiss_index = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

