/**
 * NoteSphere - Browse Notes Catalog Script
 * Handles real-time search, multi-facet filtering, and rendering of approved notes.
 */

document.addEventListener("DOMContentLoaded", async () => {
  const searchInput = document.getElementById("search-input");
  const semesterFilter = document.getElementById("semester-filter");
  const subjectFilter = document.getElementById("subject-filter");
  const sortFilter = document.getElementById("sort-filter");
  const clearFiltersBtn = document.getElementById("clear-filters-btn");
  const notesGrid = document.getElementById("notes-grid");
  const emptyState = document.getElementById("empty-state");

  // Read URL parameters if arrived from Home shortcuts
  const urlParams = new URLSearchParams(window.location.search);
  const initialSemester = urlParams.get("semester");
  const initialSearch = urlParams.get("search");

  if (initialSemester && semesterFilter) {
    semesterFilter.value = initialSemester;
  }
  if (initialSearch && searchInput) {
    searchInput.value = initialSearch;
  }

  // Populate Subjects dropdown
  await loadSubjectsDropdown(initialSemester);

  // Load Notes
  await fetchAndRenderNotes();

  // Event Listeners
  if (searchInput) {
    searchInput.addEventListener("input", debounce(() => fetchAndRenderNotes(), 300));
  }
  if (semesterFilter) {
    semesterFilter.addEventListener("change", async () => {
      await loadSubjectsDropdown(semesterFilter.value);
      fetchAndRenderNotes();
    });
  }
  if (subjectFilter) {
    subjectFilter.addEventListener("change", () => fetchAndRenderNotes());
  }
  if (sortFilter) {
    sortFilter.addEventListener("change", () => fetchAndRenderNotes());
  }
  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener("click", () => {
      if (searchInput) searchInput.value = "";
      if (semesterFilter) semesterFilter.value = "";
      if (subjectFilter) subjectFilter.value = "";
      if (sortFilter) sortFilter.value = "newest";
      loadSubjectsDropdown();
      fetchAndRenderNotes();
    });
  }

  async function loadSubjectsDropdown(semester = "") {
    if (!subjectFilter) return;
    try {
      const res = await api.getSubjects(semester);
      const subjects = res.data || [];
      const currentVal = subjectFilter.value;
      subjectFilter.innerHTML = '<option value="">All Subjects</option>';
      subjects.forEach((sub) => {
        const opt = document.createElement("option");
        opt.value = sub.id || sub.name;
        opt.textContent = `${sub.name} (Sem ${sub.semester})`;
        if (opt.value === currentVal) opt.selected = true;
        subjectFilter.appendChild(opt);
      });
    } catch (err) {
      console.error("Error loading subjects dropdown:", err);
    }
  }

  async function fetchAndRenderNotes() {
    if (!notesGrid) return;
    showLoadingSkeletons();

    const params = {};
    if (searchInput && searchInput.value.trim()) params.search = searchInput.value.trim();
    if (semesterFilter && semesterFilter.value) params.semester = semesterFilter.value;
    if (subjectFilter && subjectFilter.value) params.subject = subjectFilter.value;
    if (sortFilter && sortFilter.value) params.sort = sortFilter.value;

    try {
      const res = await api.getNotes(params);
      const notes = res.data || [];
      renderNotes(notes);
    } catch (err) {
      console.error("Error fetching notes:", err);
      notesGrid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--color-error);">
          Failed to load study notes. Please check your connection and try again.
        </div>
      `;
    }
  }

  function showLoadingSkeletons() {
    if (emptyState) emptyState.style.display = "none";
    notesGrid.innerHTML = Array(6).fill(0).map(() => `
      <div class="skeleton-card">
        <div class="skeleton-line" style="width: 30%; height: 20px;"></div>
        <div class="skeleton-line" style="width: 80%; height: 24px; margin-top: 14px;"></div>
        <div class="skeleton-line" style="width: 50%; height: 16px;"></div>
        <div class="skeleton-line" style="width: 100%; height: 36px; margin-top: 24px;"></div>
      </div>
    `).join("");
  }

  function renderNotes(notes) {
    if (!notes || notes.length === 0) {
      notesGrid.innerHTML = "";
      if (emptyState) emptyState.style.display = "flex";
      return;
    }

    if (emptyState) emptyState.style.display = "none";
    notesGrid.innerHTML = notes.map((note) => `
      <div class="note-card">
        <div class="note-card-header">
          <div class="note-icon">PDF</div>
          <span class="sem-badge">Semester ${note.semester}</span>
        </div>
        <h3 class="note-card-title">${escapeHtml(note.title)}</h3>
        <p class="note-card-subject">${escapeHtml(note.subjectName)}</p>
        
        <div style="margin-top: 12px; margin-bottom: 16px; display: flex; gap: 8px;">
          <a href="/note-details.html?id=${note.id}" class="btn btn-secondary btn-sm" style="flex:1;">View Details</a>
          <a href="/api/notes/${note.id}/download" class="btn btn-primary btn-sm" target="_blank" style="flex:1;">
            Download
          </a>
        </div>

        <div class="note-card-footer">
          <span class="note-meta-item">
            ${formatFileSize(note.fileSizeBytes)}
          </span>
          <span class="note-meta-item">
            ${note.downloadCount || 0} downloads
          </span>
          <span class="note-meta-item">
            ${formatDate(note.createdAt)}
          </span>
        </div>
      </div>
    `).join("");
  }
});
