"""
Script para cargar embeddings desde CSV a MySQL
"""
import pandas as pd
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Conexión a la base de datos
DATABASE_URL = "mysql+pymysql://root:password@localhost:3307/image_search"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def load_embeddings_from_csv():
    """Carga embeddings desde CSV a la base de datos"""
    print("[*] Leyendo archivo CSV...")
    df = pd.read_csv("data/embeddings/embeddings.csv")

    print(f"[+] Leidos {len(df)} registros del CSV")
    print(f"[i] Columnas: {df.columns.tolist()}")

    session = Session()

    try:
        # Limpiar tabla existente
        print("[*] Limpiando tabla image_embeddings...")
        session.execute(text("DELETE FROM image_embeddings"))
        session.commit()

        # Insertar embeddings en lotes
        batch_size = 100
        total = len(df)

        for i in range(0, total, batch_size):
            batch = df.iloc[i:i+batch_size]

            for _, row in batch.iterrows():
                # El embedding ya está en formato JSON string
                embedding_json = row['embedding']

                # Insertar en la base de datos
                session.execute(
                    text("""
                    INSERT INTO image_embeddings (image_path, embedding)
                    VALUES (:image_path, :embedding)
                    """),
                    {
                        "image_path": row['path'],  # La columna se llama 'path' en el CSV
                        "embedding": embedding_json
                    }
                )

            session.commit()
            print(f"[+] Insertados {min(i+batch_size, total)}/{total} registros...")

        print(f"[+] Completado! Se cargaron {total} embeddings a la base de datos")

    except Exception as e:
        print(f"[-] Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    load_embeddings_from_csv()
