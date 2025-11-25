from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import ImageEmbedding


def get_csv_path() -> Path:
    """Devuelve la ruta al CSV de embeddings.

    Por defecto usa /data/embeddings/embeddings.csv dentro del contenedor.
    """
    env_path = os.getenv("EMBEDDINGS_CSV", "/data/embeddings/embeddings.csv")
    return Path(env_path)


def load_embeddings(csv_path: Path | str | None = None, batch_size: int = 1000) -> None:
    """Carga embeddings desde un CSV a la tabla image_embeddings.

    El CSV debe tener columnas:
      - path: ruta relativa de la imagen (ej. WOMEN/Denim/...)
      - embedding: string con la lista de floats.
    """
    if csv_path is None:
        csv_path = get_csv_path()
    csv_path = Path(csv_path)

    if not csv_path.is_file():
        raise FileNotFoundError(f"No se encontró el archivo CSV: {csv_path}")

    print(f"📄 Leyendo embeddings desde: {csv_path}")
    df = pd.read_csv(csv_path)

    required_cols = {"path", "embedding"}
    if not required_cols.issubset(set(df.columns)):
        raise ValueError(f"El CSV debe contener las columnas: {required_cols}. Columnas encontradas: {df.columns}")

    session: Session
    with SessionLocal() as session:
        total = len(df)
        print(f"🔢 Registros a procesar: {total}")

        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            chunk = df.iloc[start:end]

            print(f"➡️  Insertando filas {start} - {end - 1}")
            for idx, row in chunk.iterrows():
                image_path = str(row["path"])
                embedding_str = str(row["embedding"])

                # Evitar duplicados por image_path
                exists = (
                    session.query(ImageEmbedding)
                    .filter(ImageEmbedding.image_path == image_path)
                    .first()
                )
                if exists:
                    continue

                item = ImageEmbedding(
                    image_path=image_path,
                    embedding=embedding_str,
                    # Índice FAISS = posición en el CSV.
                    faiss_index=int(idx),
                )
                session.add(item)

            session.commit()
            print(f"✅ Commit hasta fila {end - 1}")

    print("🎉 Carga de embeddings completada.")


if __name__ == "__main__":
    load_embeddings()

