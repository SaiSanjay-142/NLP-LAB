const API_BASE_URL = 'http://127.0.0.1:8000';

// DOM Elements
const uploadForm = document.getElementById('upload-form');
const fileInput = document.getElementById('file-upload');
const uploadBtn = document.getElementById('upload-btn');
const uploadMessage = document.getElementById('upload-message');
const fileLabel = document.querySelector('.file-label');

const searchForm = document.getElementById('search-form');
const searchInput = document.getElementById('search-input');
const resultsContainer = document.getElementById('results-container');
const noResults = document.getElementById('no-results');

const docCountEl = document.getElementById('doc-count');
const vocabSizeEl = document.getElementById('vocab-size');

// Initial Setup
document.addEventListener('DOMContentLoaded', () => {
  fetchStats();
});

// Update label when file is selected
fileInput.addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    fileLabel.innerHTML = `<i class="fa-solid fa-file-check"></i> ${e.target.files[0].name}`;
  } else {
    fileLabel.innerHTML = `<i class="fa-solid fa-file-arrow-up"></i> Choose a .txt or .pdf file`;
  }
});

// Handle Upload
uploadForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const file = fileInput.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  uploadBtn.disabled = true;
  uploadBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Uploading...';
  
  try {
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();

    if (response.ok) {
      showMessage(data.message, 'success');
      fileInput.value = ''; // Reset
      fileLabel.innerHTML = `<i class="fa-solid fa-file-arrow-up"></i> Choose a .txt or .pdf file`;
      fetchStats(); // Update stats
    } else {
      showMessage(data.detail || 'Upload failed', 'error');
    }
  } catch (error) {
    showMessage('Connection error. Is the backend running?', 'error');
  } finally {
    uploadBtn.disabled = false;
    uploadBtn.innerHTML = `<span>Upload & Index</span> <i class="fa-solid fa-arrow-right"></i>`;
  }
});

// Handle Search
searchForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const query = searchInput.value.trim();
  if (!query) return;

  resultsContainer.innerHTML = '<div class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><p>Searching...</p></div>';
  noResults.classList.add('hidden');

  try {
    const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`);
    const results = await response.json();

    renderResults(results, query);
  } catch (error) {
    resultsContainer.innerHTML = '';
    showMessage('Search failed. Backend error.', 'error');
  }
});

function renderResults(results, query) {
  resultsContainer.innerHTML = '';

  if (!results || results.length === 0) {
    noResults.classList.remove('hidden');
    return;
  }

  // Split query into terms to highlight
  const terms = query.toLowerCase().split(/\s+/).filter(t => t.length > 0);

  results.forEach((result, index) => {
    // Basic highlight logic
    let highlightedSnippet = result.snippet;
    terms.forEach(term => {
      // Regex to wrap term in highlight span, ignoring case
      const regex = new RegExp(`(${term})`, 'gi');
      highlightedSnippet = highlightedSnippet.replace(regex, '<span class="highlight">$1</span>');
    });

    const icon = result.filename.endsWith('.pdf') ? 'fa-file-pdf' : 'fa-file-lines';

    const card = document.createElement('div');
    card.className = 'result-card';
    card.style.animationDelay = `${index * 0.1}s`;
    card.innerHTML = `
      <div class="result-header">
        <div class="result-filename"><i class="fa-solid ${icon}"></i> ${result.filename}</div>
        <div class="result-score">Score: ${result.score.toFixed(4)}</div>
      </div>
      <div class="result-snippet">${highlightedSnippet}</div>
    `;
    resultsContainer.appendChild(card);
  });
}

function showMessage(msg, type) {
  uploadMessage.textContent = msg;
  uploadMessage.className = `message ${type}`;
  uploadMessage.classList.remove('hidden');
  setTimeout(() => {
    uploadMessage.classList.add('hidden');
  }, 5000);
}

async function fetchStats() {
  try {
    const response = await fetch(`${API_BASE_URL}/stats`);
    const data = await response.json();
    docCountEl.textContent = data.document_count;
    vocabSizeEl.textContent = data.vocabulary_size;
  } catch (error) {
    console.error('Failed to fetch stats', error);
  }
}
