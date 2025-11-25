import json
import os
from pathlib import Path

import deepl
import faiss
import numpy as np
from fastapi import UploadFile
from PIL import Image
from sqlalchemy.orm import Session
from transformers import CLIPModel, CLIPProcessor

from . import models, schemas
from .config import settings

# Cargar modelo CLIP ViT-L/14 (768 dimensiones) - mismo modelo usado para generar embeddings
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")

# Inicializar cliente DeepL para traducción
translator = deepl.Translator(settings.deepl_api_key)

# Diccionario de términos de moda español-inglés (basado en categorías del dataset)
FASHION_TERMS = {
    # Tops - Parte superior
    "polo": "polo shirt",
    "polos": "polo shirts",
    "camiseta": "t-shirt",
    "camisetas": "t-shirts",
    "playera": "t-shirt",
    "playeras": "t-shirts",
    "blusa": "blouse",
    "blusas": "blouses",
    "camisa": "shirt",
    "camisas": "shirts",
    "top": "top",
    "tops": "tops",
    "tank": "tank top",
    "musculosa": "tank top",
    "tirantes": "tank top",

    # Sweaters y abrigos
    "suéter": "sweater",
    "suéteres": "sweaters",
    "sweater": "sweater",
    "cárdigan": "cardigan",
    "cardigán": "cardigan",
    "cardigan": "cardigan",
    "cardiganes": "cardigans",
    "sudadera": "hoodie sweatshirt",
    "sudaderas": "hoodies sweatshirts",
    "hoodie": "hoodie",
    "chamarra": "jacket",
    "chaqueta": "jacket",
    "chaquetas": "jackets",
    "abrigo": "coat",
    "abrigos": "coats",
    "chaleco": "vest",
    "chalecos": "vests",

    # Bottoms - Parte inferior
    "pantalón": "pants",
    "pantalones": "pants",
    "short": "shorts",
    "shorts": "shorts",
    "bermuda": "bermuda shorts",
    "bermudas": "bermuda shorts",
    "leggings": "leggings",
    "mallas": "leggings",
    "jeans": "jeans denim",
    "mezclilla": "denim",
    "vaqueros": "jeans denim",
    "denim": "denim",

    # Dresses y vestidos
    "vestido": "dress",
    "vestidos": "dresses",
    "falda": "skirt",
    "faldas": "skirts",
    "enterizo": "romper jumpsuit",
    "enterizos": "rompers jumpsuits",
    "mameluco": "romper jumpsuit",
    "mamelucos": "rompers jumpsuits",
    "overol": "jumpsuit",
    "overoles": "jumpsuits",

    # Trajes
    "traje": "suit",
    "trajes": "suits",
    "saco": "blazer suit jacket",
    "sacos": "blazers suit jackets",

    # Colores
    "rojo": "red",
    "azul": "blue",
    "negro": "black",
    "blanco": "white",
    "gris": "gray",
    "verde": "green",
    "amarillo": "yellow",
    "rosa": "pink",
    "morado": "purple",
    "café": "brown",
    "beige": "beige",
    "naranja": "orange",
}

# Cargar índice FAISS HNSW (O(log n) search)
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "/data/embeddings/faiss_hnsw_index.bin")
faiss_index = None
if Path(FAISS_INDEX_PATH).exists():
    faiss_index = faiss.read_index(FAISS_INDEX_PATH)
    print(f"[+] Índice FAISS HNSW cargado: {FAISS_INDEX_PATH} ({faiss_index.ntotal} vectores)")


def create_image_embedding(db: Session, data: schemas.ImageEmbeddingCreate) -> models.ImageEmbedding:
    db_item = models.ImageEmbedding(**data.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_image_embedding_by_path(db: Session, image_path: str) -> models.ImageEmbedding | None:
    return (
        db.query(models.ImageEmbedding)
        .filter(models.ImageEmbedding.image_path == image_path)
        .first()
    )


def get_all_embeddings(db: Session) -> list[models.ImageEmbedding]:
    """Obtiene todos los embeddings de la base de datos."""
    return db.query(models.ImageEmbedding).all()


def extract_gender_and_category(image_path: str) -> tuple[str | None, str | None]:
    """Extrae género y categoría de la ruta de imagen.

    Formato esperado: WOMEN/Denim/id_00002359/03_3_back.jpg
    Retorna: (gender, category)
    """
    try:
        parts = image_path.split("/")
        if len(parts) >= 2:
            gender = parts[0].upper()  # MEN o WOMEN
            category = parts[1]  # Denim, Polo, Vestidos, etc.
            return (gender, category)
        return (None, None)
    except Exception:
        return (None, None)


def search_by_text(
    db: Session,
    query: str,
    top_k: int = 10,
    gender: str | None = None,
    category: str | None = None,
) -> list[schemas.ImageResult]:
    """Busca imágenes similares usando una consulta de texto.

    Args:
        db: Sesión de base de datos
        query: Consulta de texto
        top_k: Número de resultados a retornar
        gender: Filtro por género (MEN, WOMEN) opcional
        category: Filtro por categoría opcional
    """

    # Traducir texto de español a inglés para mejor rendimiento con CLIP
    query_lower = query.lower().strip()

    # MEJORA: Traducir palabra por palabra primero
    words = query_lower.split()
    translated_words = []
    words_translated = False

    for word in words:
        if word in FASHION_TERMS:
            translated_words.append(FASHION_TERMS[word])
            words_translated = True
        else:
            translated_words.append(word)

    # Si alguna palabra fue traducida del diccionario, usar eso
    if words_translated:
        query_en = " ".join(translated_words)
        print(f"🌐 Traducción (diccionario): '{query}' → '{query_en}'")
    # Si query completo está en diccionario
    elif query_lower in FASHION_TERMS:
        query_en = FASHION_TERMS[query_lower]
        print(f"🌐 Traducción (diccionario): '{query}' → '{query_en}'")
    else:
        # Si no, usar DeepL con contexto de moda
        try:
            # Agregar contexto de "ropa" para mejores traducciones
            context_query = f"{query} ropa moda"
            result = translator.translate_text(context_query, source_lang="ES", target_lang="EN-US")
            # Limpiar el resultado removiendo "clothing fashion" que DeepL agregó
            query_en = result.text.replace(" clothing fashion", "").replace(" clothes fashion", "").strip()
            print(f"🌐 Traducción (DeepL): '{query}' → '{query_en}'")
        except Exception as e:
            print(f"⚠️  Error en traducción, usando texto original: {e}")
            query_en = query

    # Generar embedding del texto usando CLIP
    inputs = processor(text=[query_en], return_tensors="pt", padding=True)
    text_features = model.get_text_features(**inputs)
    text_embedding = text_features.detach().numpy()[0]
    text_embedding = text_embedding / np.linalg.norm(text_embedding)  # Normalizar

    # Si tenemos índice FAISS, usarlo
    if faiss_index is not None:
        # Búsqueda en FAISS - obtener más resultados para compensar filtrado
        search_k = top_k * 3 if (gender or category) else top_k
        distances, indices = faiss_index.search(np.array([text_embedding], dtype=np.float32), search_k)

        # MEJORA: Solo cargar los embeddings específicos que FAISS retornó
        results = []
        for i, idx in enumerate(indices[0]):
            # Cargar solo el embedding en la posición idx (offset + first)
            img_emb = db.query(models.ImageEmbedding).offset(int(idx)).first()

            if img_emb:
                # Aplicar filtros de género y categoría
                img_gender, img_category = extract_gender_and_category(img_emb.image_path)

                # Filtrar por género si se especificó
                if gender and img_gender != gender.upper():
                    continue

                # Filtrar por categoría si se especificó
                if category and img_category != category:
                    continue

                # Construir URL de la imagen
                image_url = f"/images/{img_emb.image_path}"

                # IndexHNSWFlat usa Inner Product, que retorna similitudes directamente
                # Valores más altos = más similares (no necesita invertir)
                similarity = max(0.0, min(1.0, float(distances[0][i])))

                results.append(schemas.ImageResult(
                    image_id=str(img_emb.id),
                    file_path=img_emb.image_path,
                    url=image_url,
                    similarity=similarity
                ))

                # Dejar de buscar si ya tenemos suficientes resultados
                if len(results) >= top_k:
                    break

        return results

    # Fallback: búsqueda manual (más lento)
    all_embeddings = get_all_embeddings(db)
    similarities = []

    for img_emb in all_embeddings:
        # Parsear embedding guardado
        try:
            embedding_vector = np.array(json.loads(img_emb.embedding), dtype=np.float32)
            embedding_vector = embedding_vector / np.linalg.norm(embedding_vector)

            # Calcular similaridad coseno
            similarity = np.dot(text_embedding, embedding_vector)
            similarities.append((img_emb, float(similarity)))
        except Exception as e:
            print(f"Error procesando embedding para {img_emb.image_path}: {e}")
            continue

    # Ordenar por similaridad descendente
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Tomar top K resultados
    results = []
    for img_emb, similarity in similarities[:top_k]:
        image_url = f"/images/{img_emb.image_path}"
        results.append(schemas.ImageResult(
            image_id=str(img_emb.id),
            file_path=img_emb.image_path,
            url=image_url,
            similarity=similarity
        ))

    return results


def search_by_image(
    db: Session,
    file: UploadFile,
    top_k: int = 10,
    gender: str | None = None,
    category: str | None = None,
) -> list[schemas.ImageResult]:
    """Busca imágenes similares usando una imagen de consulta.

    Args:
        db: Sesión de base de datos
        file: Archivo de imagen
        top_k: Número de resultados a retornar
        gender: Filtro por género (MEN, WOMEN) opcional
        category: Filtro por categoría opcional
    """

    # Leer y procesar la imagen
    image = Image.open(file.file).convert("RGB")

    # Generar embedding de la imagen usando CLIP
    inputs = processor(images=image, return_tensors="pt")
    image_features = model.get_image_features(**inputs)
    image_embedding = image_features.detach().numpy()[0]
    image_embedding = image_embedding / np.linalg.norm(image_embedding)  # Normalizar

    # Si tenemos índice FAISS, usarlo
    if faiss_index is not None:
        # Búsqueda en FAISS - obtener más resultados para compensar filtrado
        search_k = top_k * 3 if (gender or category) else top_k
        distances, indices = faiss_index.search(np.array([image_embedding], dtype=np.float32), search_k)

        # MEJORA: Solo cargar los embeddings específicos que FAISS retornó
        results = []
        for i, idx in enumerate(indices[0]):
            # Cargar solo el embedding en la posición idx (offset + first)
            img_emb = db.query(models.ImageEmbedding).offset(int(idx)).first()

            if img_emb:
                # Aplicar filtros de género y categoría
                img_gender, img_category = extract_gender_and_category(img_emb.image_path)

                # Filtrar por género si se especificó
                if gender and img_gender != gender.upper():
                    continue

                # Filtrar por categoría si se especificó
                if category and img_category != category:
                    continue

                # Construir URL de la imagen
                image_url = f"/images/{img_emb.image_path}"

                # IndexHNSWFlat usa Inner Product, que retorna similitudes directamente
                # Valores más altos = más similares (no necesita invertir)
                similarity = max(0.0, min(1.0, float(distances[0][i])))

                results.append(schemas.ImageResult(
                    image_id=str(img_emb.id),
                    file_path=img_emb.image_path,
                    url=image_url,
                    similarity=similarity
                ))

                # Dejar de buscar si ya tenemos suficientes resultados
                if len(results) >= top_k:
                    break

        return results

    # Fallback: búsqueda manual
    all_embeddings = get_all_embeddings(db)
    similarities = []

    for img_emb in all_embeddings:
        try:
            embedding_vector = np.array(json.loads(img_emb.embedding), dtype=np.float32)
            embedding_vector = embedding_vector / np.linalg.norm(embedding_vector)

            similarity = np.dot(image_embedding, embedding_vector)
            similarities.append((img_emb, float(similarity)))
        except Exception as e:
            print(f"Error procesando embedding para {img_emb.image_path}: {e}")
            continue

    similarities.sort(key=lambda x: x[1], reverse=True)

    results = []
    for img_emb, similarity in similarities[:top_k]:
        image_url = f"/images/{img_emb.image_path}"
        results.append(schemas.ImageResult(
            image_id=str(img_emb.id),
            file_path=img_emb.image_path,
            url=image_url,
            similarity=similarity
        ))

    return results
