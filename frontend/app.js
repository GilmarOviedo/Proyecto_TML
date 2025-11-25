const API_BASE = "http://localhost:8000";

// DOM Elements
const textForm = document.getElementById("text-search-form");
const imageForm = document.getElementById("image-search-form");
const textQuery = document.getElementById("text-query");
const imageFile = document.getElementById("image-file");
const uploadArea = document.getElementById("upload-area");
const previewContainer = document.getElementById("preview-container");
const previewImage = document.getElementById("preview-image");
const removeImageBtn = document.getElementById("remove-image");
const resultsContainer = document.getElementById("results");
const resultsSection = document.getElementById("results-section");
const resultsCount = document.getElementById("results-count");
const searchTime = document.getElementById("search-time");
const topKSelector = document.getElementById("top-k-selector");
const genderFilter = document.getElementById("gender-filter");
const categoryFilter = document.getElementById("category-filter");
const loading = document.getElementById("loading");
const noResults = document.getElementById("no-results");

// Tab functionality
const tabButtons = document.querySelectorAll(".tab-button");
const tabContents = document.querySelectorAll(".tab-content");

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const targetTab = button.getAttribute("data-tab");

    // Remove active class from all buttons and contents
    tabButtons.forEach((btn) => btn.classList.remove("active"));
    tabContents.forEach((content) => content.classList.remove("active"));

    // Add active class to clicked button and corresponding content
    button.classList.add("active");
    const targetContent = document.getElementById(`${targetTab}-tab`);
    if (targetContent) {
      targetContent.classList.add("active");
    }

    // Focus on the appropriate input when switching tabs
    if (targetTab === "text-search") {
      textQuery.focus();
    }
  });
});

// Suggestion tags
const suggestionTags = document.querySelectorAll(".tag");
suggestionTags.forEach((tag) => {
  tag.addEventListener("click", () => {
    const query = tag.getAttribute("data-query");
    textQuery.value = query;
    textForm.dispatchEvent(new Event("submit"));
  });
});

// File upload handlers
uploadArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadArea.classList.add("dragover");
});

uploadArea.addEventListener("dragleave", () => {
  uploadArea.classList.remove("dragover");
});

uploadArea.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadArea.classList.remove("dragover");
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    imageFile.files = files;
    showPreview(files[0]);
  }
});

imageFile.addEventListener("change", (e) => {
  if (e.target.files.length > 0) {
    showPreview(e.target.files[0]);
  }
});

removeImageBtn.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();
  clearImagePreview();
});

function showPreview(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImage.src = e.target.result;
    uploadArea.querySelector(".upload-content").style.display = "none";
    previewContainer.style.display = "block";
  };
  reader.readAsDataURL(file);
}

function clearImagePreview() {
  imageFile.value = "";
  previewImage.src = "";
  uploadArea.querySelector(".upload-content").style.display = "block";
  previewContainer.style.display = "none";
}

function showLoading() {
  loading.style.display = "block";
  resultsSection.style.display = "none";
  noResults.style.display = "none";
}

function hideLoading() {
  loading.style.display = "none";
}

function renderResults(items, searchTimeMs) {
  hideLoading();
  resultsContainer.innerHTML = "";

  if (!items || items.length === 0) {
    noResults.style.display = "block";
    resultsSection.style.display = "none";
    return;
  }

  noResults.style.display = "none";
  resultsSection.style.display = "block";
  resultsCount.textContent = `${items.length} ${items.length === 1 ? 'resultado' : 'resultados'}`;

  // Mostrar tiempo de búsqueda si está disponible
  if (searchTimeMs !== undefined && searchTimeMs !== null) {
    searchTime.textContent = `Tiempo de búsqueda: ${searchTimeMs} ms`;
  } else {
    searchTime.textContent = "";
  }

  items.forEach((item, index) => {
    const div = document.createElement("div");
    div.className = "result-item";
    div.style.animationDelay = `${index * 0.05}s`;

    const img = document.createElement("img");
    // Handle different possible image path formats
    const imagePath = item.url || item.file_path || item.path || "";
    // Add API_BASE to image URL since images are served from backend
    img.src = API_BASE + imagePath;
    img.alt = item.caption || item.image_id || `Resultado ${index + 1}`;
    img.onerror = () => {
      img.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect fill='%23f1f5f9' width='200' height='200'/%3E%3Ctext fill='%2394a3b8' font-family='sans-serif' font-size='14' x='50%25' y='50%25' text-anchor='middle' dominant-baseline='middle'%3EImagen no disponible%3C/text%3E%3C/svg%3E";
    };

    const caption = document.createElement("div");
    caption.className = "caption";
    const captionText = item.caption || item.image_id || item.filename || `Imagen ${index + 1}`;
    caption.textContent = captionText;

    // Add similarity score badge if available
    if (item.similarity !== undefined && item.similarity !== null) {
      const similarityBadge = document.createElement("div");
      similarityBadge.className = "similarity-badge";
      const percentage = (item.similarity * 100).toFixed(1);
      similarityBadge.textContent = `${percentage}%`;

      // Add color class based on similarity level
      if (item.similarity >= 0.8) {
        similarityBadge.classList.add("high");
      } else if (item.similarity >= 0.6) {
        similarityBadge.classList.add("medium");
      } else {
        similarityBadge.classList.add("low");
      }

      div.appendChild(similarityBadge);
    }

    div.appendChild(img);
    div.appendChild(caption);
    resultsContainer.appendChild(div);

    // Add click handler to view image in full size
    div.addEventListener("click", () => {
      window.open(API_BASE + imagePath, "_blank");
    });
  });
}

// Text search
textForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = textQuery.value.trim();

  if (!query) return;

  showLoading();

  try {
    const topK = parseInt(topKSelector.value);
    const gender = genderFilter.value || null;
    const category = categoryFilter.value || null;

    const res = await fetch(`${API_BASE}/search/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        top_k: topK,
        gender: gender,
        category: category
      }),
    });

    if (!res.ok) {
      throw new Error(`Error: ${res.status} ${res.statusText}`);
    }

    const data = await res.json();
    renderResults(data.results || data, data.search_time_ms);
  } catch (error) {
    console.error("Error en búsqueda por texto:", error);
    hideLoading();
    alert("Error al realizar la búsqueda. Por favor, verifica que el backend esté funcionando.");
  }
});

// Image search
imageForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (!imageFile.files || imageFile.files.length === 0) {
    alert("Por favor selecciona una imagen");
    return;
  }

  showLoading();

  try {
    const topK = parseInt(topKSelector.value);
    const gender = genderFilter.value || null;
    const category = categoryFilter.value || null;

    const formData = new FormData();
    formData.append("file", imageFile.files[0]);
    formData.append("top_k", topK);
    if (gender) formData.append("gender", gender);
    if (category) formData.append("category", category);

    const res = await fetch(`${API_BASE}/search/image`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      throw new Error(`Error: ${res.status} ${res.statusText}`);
    }

    const data = await res.json();
    renderResults(data.results || data, data.search_time_ms);
  } catch (error) {
    console.error("Error en búsqueda por imagen:", error);
    hideLoading();
    alert("Error al realizar la búsqueda. Por favor, verifica que el backend esté funcionando.");
  }
});

// Keyboard shortcuts
document.addEventListener("keydown", (e) => {
  // Focus text search with Ctrl+K or Cmd+K
  if ((e.ctrlKey || e.metaKey) && e.key === "k") {
    e.preventDefault();
    textQuery.focus();
  }
});

// Initial focus
textQuery.focus();
