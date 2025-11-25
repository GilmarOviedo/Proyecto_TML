# Fashion Finder 🔍👕

Sistema de búsqueda multimodal de prendas de vestir usando IA

**Proyecto Final - Tópicos Avanzados en Machine Learning**

---

## 📋 Descripción

Fashion Finder es un sistema de búsqueda inteligente que permite encontrar prendas de ropa mediante:
- **Búsqueda por texto**: Describe la prenda en español (ej: "vestido rojo elegante")
- **Búsqueda por imagen**: Sube una foto de una prenda similar

El sistema utiliza el modelo CLIP (ViT-L/14) para crear embeddings multimodales y FAISS con índice HNSW para búsquedas ultra-rápidas (O(log n)).

## 🚀 Características

- ✅ **Búsqueda multimodal**: Texto e imagen
- ✅ **Traducción inteligente**: Español → Inglés con diccionario de moda
- ✅ **Filtros avanzados**: Por género y categoría
- ✅ **Similarity scores**: Porcentaje de similitud con badges visuales
- ✅ **Búsqueda rápida**: FAISS HNSW optimizado (O(log n))
- ✅ **Interfaz moderna**: Diseño con tabs responsive
- ✅ **Métricas de performance**: Tiempo de búsqueda en ms

## 🛠️ Tecnologías

### Backend
- **FastAPI**: API REST moderna y rápida
- **OpenAI CLIP**: Modelo ViT-L/14 para embeddings (768 dimensiones)
- **FAISS**: Búsqueda vectorial con índice HNSW
- **MySQL**: Base de datos relacional
- **SQLAlchemy + Alembic**: ORM y migraciones
- **PyTorch**: Framework de deep learning
- **Transformers (Hugging Face)**: Implementación de CLIP

### Frontend
- **HTML5 + CSS3**: Interfaz moderna con tabs
- **JavaScript (Vanilla)**: Sin frameworks, código simple
- **Fetch API**: Comunicación con backend

### Infraestructura
- **Docker + Docker Compose**: Contenedorización
- **Nginx**: Servidor web para frontend

## 📦 Estructura del Proyecto

```
Proyecto_TML/
├── backend/
│   ├── app/
│   │   ├── main.py              # API FastAPI
│   │   ├── crud.py              # Lógica de búsqueda (CLIP + FAISS)
│   │   ├── models.py            # Modelos SQLAlchemy
│   │   ├── schemas.py           # Schemas Pydantic
│   │   ├── database.py          # Configuración DB
│   │   ├── config.py            # Variables de entorno
│   │   └── deps.py              # Dependencias
│   ├── migrations/              # Migraciones Alembic
│   ├── scripts/
│   │   └── build_hnsw_index.py  # Script para construir índice FAISS
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── index.html               # Página principal con tabs
│   ├── app.js                   # Lógica de búsqueda
│   ├── styles.css               # Estilos modernos
│   ├── Dockerfile
│   └── nginx.conf
├── data/
│   ├── images/
│   │   └── img_real_clean/      # 43,648 imágenes del dataset
│   └── embeddings/
│       ├── embeddings.csv       # 43,648 vectores de 768 dimensiones
│       ├── embeddings_data.sql  # Datos para MySQL
│       └── faiss_hnsw_index.bin # Índice FAISS optimizado (M=32, efSearch=100)
├── scripts/
│   ├── load_embeddings.py       # Carga embeddings a MySQL
│   └── build_hnsw_index.py      # Construye índice FAISS
├── docker-compose.yml
└── README.md
```

## 🔧 Instalación

### Requisitos previos
- Docker y Docker Compose instalados
- Al menos 4GB RAM disponible
- Puerto 3000, 8000 y 3307 libres

### Paso 1: Clonar el repositorio

```bash
git clone <url-del-repo>
cd Proyecto_TML
```

### Paso 2: Preparar datos

⚠️ **IMPORTANTE**: Los archivos de datos **NO están incluidos** en este repositorio (son muy grandes para GitHub).

#### Descargar Dataset e Embeddings

Necesitas descargar por separado:

1. **Imágenes del dataset** (6.7GB):
   - [Fashion Product Images Dataset - Kaggle](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset)
   - Colocar en: `data/images/img_real_clean/`

2. **Embeddings y índices FAISS** (~1.5GB):
   - Descargar desde: [Link compartido del equipo]
   - Colocar en: `data/embeddings/`

#### Estructura final de datos

```
data/
├── images/
│   └── img_real_clean/           # 43,648 imágenes del dataset
└── embeddings/
    ├── embeddings.csv            # Vectores CLIP (646 MB)
    ├── embeddings_data.sql       # Datos SQL (617 MB)
    ├── faiss_hnsw_index.bin      # Índice HNSW (139 MB)
    └── faiss_index.bin           # Índice Flat (128 MB)
```

### Paso 3: Levantar los servicios

```bash
# Construir las imágenes
docker-compose build

# Iniciar los servicios
docker-compose up -d
```

Los servicios estarán disponibles en:
- 🌐 **Frontend**: http://localhost:3000
- 🚀 **Backend API**: http://localhost:8000
- 📊 **MySQL**: localhost:3307

### Paso 4: Aplicar migraciones

```bash
docker-compose exec backend alembic upgrade head
```

### Paso 5: Cargar datos (si es necesario)

```bash
# Opción 1: Cargar desde SQL
docker-compose exec db mysql -uroot -ppassword image_search < data/embeddings/embeddings_data.sql

# Opción 2: Cargar desde CSV
python scripts/load_embeddings.py
```

## 📖 Uso

1. Abre http://localhost:3000 en tu navegador
2. Elige el tipo de búsqueda:
   - **Texto**: Escribe una descripción en español
   - **Imagen**: Arrastra o selecciona una imagen
3. Configura filtros opcionales:
   - Cantidad de resultados (10, 20, 50)
   - Género (Hombre, Mujer, Todos)
   - Categoría (Camisetas, Pantalones, Vestidos, etc.)
4. Haz clic en "Buscar"
5. Visualiza resultados con porcentajes de similitud

## 🔬 Arquitectura Técnica

### Pipeline de Búsqueda por Texto

```
Texto en español
  ↓
Traducción (ES → EN) con diccionario de moda
  ↓
CLIP Text Encoder (ViT-L/14)
  ↓
Vector de 768 dimensiones normalizado
  ↓
FAISS HNSW Search (O(log n))
  ↓
Top-K resultados + Similarity Score
  ↓
Filtros SQL (género, categoría)
  ↓
JSON Response
```

### Pipeline de Búsqueda por Imagen

```
Imagen subida (JPG/PNG)
  ↓
Preprocesamiento (resize, normalize)
  ↓
CLIP Image Encoder (ViT-L/14)
  ↓
Vector de 768 dimensiones normalizado
  ↓
FAISS HNSW Search (O(log n))
  ↓
Top-K resultados + Similarity Score
  ↓
Filtros SQL (género, categoría)
  ↓
JSON Response
```

### Índice FAISS HNSW

El sistema utiliza un índice HNSW (Hierarchical Navigable Small World) optimizado:

- **Tipo**: `IndexHNSWFlat` con Inner Product
- **Dimensiones**: 768 (CLIP ViT-L/14)
- **M**: 32 conexiones por nodo (balance precisión/memoria)
- **efConstruction**: 200 (calidad de construcción)
- **efSearch**: 100 (calidad de búsqueda)
- **Complejidad**: O(log n) vs O(n) de búsqueda lineal
- **Performance**: ~10-50x más rápido que IndexFlat

## 📊 Dataset

- **Fuente**: Fashion Product Images Dataset
- **Total imágenes**: 43,648
- **Categorías**: 15+ (Camisetas, Pantalones, Vestidos, Chaquetas, etc.)
- **Géneros**: Hombre y Mujer
- **Embeddings**: Vectores de 768 dimensiones pre-computados con CLIP ViT-L/14

## 🧪 Scripts Disponibles

### Construir índice FAISS HNSW

```bash
python scripts/build_hnsw_index.py
```

Genera `data/embeddings/faiss_hnsw_index.bin` optimizado para búsqueda rápida.

### Cargar embeddings a MySQL

```bash
python scripts/load_embeddings.py
```

Lee `embeddings.csv` y carga los vectores en la base de datos.

## 📝 API Endpoints

### `GET /`
Healthcheck del API

### `POST /search/text`
Búsqueda por texto

**Body**:
```json
{
  "query": "vestido rojo elegante",
  "top_k": 10,
  "gender": "WOMEN",
  "category": "Dresses"
}
```

**Response**:
```json
{
  "results": [
    {
      "image_id": "12345",
      "file_path": "WOMEN/Dresses/id_00001234/01_1_front.jpg",
      "url": "/images/WOMEN/Dresses/id_00001234/01_1_front.jpg",
      "similarity": 0.92
    }
  ],
  "search_time_ms": 5436.99
}
```

### `POST /search/image`
Búsqueda por imagen

**Form Data**:
- `file`: Archivo de imagen (multipart/form-data)
- `top_k`: Número de resultados (default: 10)
- `gender`: Filtro opcional
- `category`: Filtro opcional

## 🎨 Features de UI

- **Tabs modernos**: Separación clara entre búsqueda por texto e imagen
- **Drag & drop**: Subir imágenes arrastrando
- **Similarity badges**: Verde (>80%), Amarillo (60-80%), Rojo (<60%)
- **Search time**: Tiempo de búsqueda en milisegundos
- **Responsive**: Adaptable a móviles y tablets
- **Sugerencias**: Tags rápidos con búsquedas comunes
- **Keyboard shortcuts**: Ctrl+K para enfocar búsqueda

## ⚡ Performance

- **Tiempo de búsqueda**: ~5-6 segundos (incluye traducción + CLIP + FAISS + SQL)
- **Índice FAISS**: O(log n) con 43,648 vectores
- **Memoria**: ~135MB para índice HNSW
- **Embeddings**: Pre-computados (sin re-encoding en cada búsqueda)

## 🔐 Configuración

### Variables de entorno (backend)

```env
DATABASE_URL=mysql+pymysql://root:password@db:3306/image_search
```

### Docker Compose

- **MySQL**: Puerto 3307 (externo) → 3306 (interno)
- **Backend**: Puerto 8000
- **Frontend**: Puerto 3000 (Nginx)

## 📦 Dependencias principales

```
torch==2.1.0
transformers==4.35.0
faiss-cpu==1.7.4
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pymysql==1.1.0
pillow==10.1.0
numpy==1.24.3
pandas==2.1.3
```

## 🚧 Limitaciones conocidas

- **Traducción**: Diccionario limitado a términos comunes de moda
- **Dataset**: Solo prendas individuales, sin outfits completos
- **Similarity scores**: Algunos resultados muestran 100% (vectores muy similares o idénticos)
- **Performance**: Primera búsqueda más lenta (carga de modelo CLIP)

## 🔮 Mejoras futuras

- [ ] Caché de embeddings frecuentes
- [ ] Búsqueda combinada (texto + imagen)
- [ ] Reranking con modelo adicional
- [ ] Soporte para más idiomas
- [ ] Filtros por color dominante
- [ ] Historial de búsquedas
- [ ] Sistema de recomendaciones

## 👥 Autores

Proyecto Final - Tópicos Avanzados en Machine Learning

## 📄 Licencia

Proyecto académico - Universidad

---

⭐ **Fashion Finder** - Búsqueda inteligente de moda con IA
