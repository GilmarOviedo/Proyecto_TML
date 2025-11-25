"""
Script para construir un índice FAISS HNSW optimizado (O(log n))
"""
import json
import numpy as np
import faiss
import pandas as pd
from pathlib import Path

def build_hnsw_index():
    """Construye un índice HNSW para búsqueda rápida O(log n)"""

    print("[*] Leyendo embeddings del CSV...")
    df = pd.read_csv("data/embeddings/embeddings.csv")

    print(f"[+] Leidos {len(df)} vectores")

    # Convertir embeddings a numpy array
    print("[*] Procesando embeddings...")
    embeddings = []
    for _, row in df.iterrows():
        # Parsear el embedding JSON
        emb = json.loads(row['embedding'])
        embeddings.append(emb)

    embeddings = np.array(embeddings, dtype=np.float32)
    print(f"[+] Shape de embeddings: {embeddings.shape}")

    # Normalizar vectores (importante para IndexHNSWFlat)
    print("[*] Normalizando vectores...")
    faiss.normalize_L2(embeddings)

    # Parámetros del índice HNSW
    dimension = embeddings.shape[1]  # 768 para ViT-L/14

    # M: número de conexiones por nodo (16-64 es óptimo)
    # Más alto = más preciso pero más memoria
    M = 32

    print(f"[*] Construyendo índice HNSW (d={dimension}, M={M})...")

    # Crear índice HNSW
    # IndexHNSWFlat usa producto interno (Inner Product) que es equivalente
    # a similitud coseno cuando los vectores están normalizados
    index = faiss.IndexHNSWFlat(dimension, M)

    # Parámetro ef_construction: calidad durante construcción
    # Más alto = mejor calidad pero más lento construir (100-200 es bueno)
    index.hnsw.efConstruction = 200

    # Agregar vectores al índice
    print("[*] Agregando vectores al índice...")
    index.add(embeddings)

    print(f"[+] Índice construido con {index.ntotal} vectores")

    # Configurar parámetro de búsqueda
    # ef_search: calidad durante búsqueda (50-200)
    # Más alto = más preciso pero más lento
    index.hnsw.efSearch = 100

    # Guardar índice
    output_path = "data/embeddings/faiss_hnsw_index.bin"
    print(f"[*] Guardando índice en {output_path}...")
    faiss.write_index(index, output_path)

    print("[+] Índice HNSW construido exitosamente!")
    print(f"[i] Archivo: {output_path}")
    print(f"[i] Tamaño: {Path(output_path).stat().st_size / (1024*1024):.2f} MB")

    # Hacer una búsqueda de prueba
    print("\n[*] Prueba de búsqueda...")
    test_vector = embeddings[0:1]
    distances, indices = index.search(test_vector, 5)
    print(f"[+] Top 5 vecinos más cercanos: {indices[0]}")
    print(f"[+] Distancias: {distances[0]}")

    print("\n[+] HNSW es ~10-50x más rápido que IndexFlat!")
    print("[i] Complejidad: O(log n) vs O(n)")

if __name__ == "__main__":
    build_hnsw_index()
