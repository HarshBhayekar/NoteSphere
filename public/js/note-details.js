/**
 * NoteSphere - Note Details View Script
 */

document.addEventListener("DOMContentLoaded", async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const noteId = urlParams.get("id");

  const titleEl = document.getElementById("note-title");
  const subjectEl = document.getElementById("note-subject");
  const semesterEl = document.getElementById("note-semester");
  const descEl = document.getElementById("note-description");
  const dateEl = document.getElementById("note-date");
  const uploaderEl = document.getElementById("note-uploader");
  const sizeEl = document.getElementById("note-size");
  const downloadsEl = document.getElementById("note-downloads");
  const downloadBtn = document.getElementById("download-btn");
  const tagsContainer = document.getElementById("note-tags");
  const statusContainer = document.getElementById("note-status-container");

  if (!noteId) {
    showToast("Invalid note reference.", "error");
    setTimeout(() => { window.location.href = "/browse.html"; }, 1500);
    return;
  }

  try {
    const res = await api.getNoteById(noteId);
    const note = res.data;

    if (titleEl) titleEl.textContent = note.title;
    if (subjectEl) subjectEl.textContent = note.subjectName;
    if (semesterEl) semesterEl.textContent = `Semester ${note.semester}`;
    if (descEl) descEl.textContent = note.description || "No description provided.";
    if (dateEl) dateEl.textContent = formatDate(note.createdAt);
    if (uploaderEl) uploaderEl.textContent = note.uploaderName || "Anonymous Student";
    if (sizeEl) sizeEl.textContent = formatFileSize(note.fileSizeBytes);
    if (downloadsEl) downloadsEl.textContent = `${note.downloadCount || 0} downloads`;

    // Download action
    if (downloadBtn) {
      downloadBtn.href = `/api/notes/${note.id}/download`;
      downloadBtn.addEventListener("click", () => {
        // Increment UI download count
        if (downloadsEl) {
          const currentCount = parseInt(note.downloadCount || 0, 10) + 1;
          downloadsEl.textContent = `${currentCount} downloads`;
        }
      });
    }



    // Tags
    if (tagsContainer && note.tags && note.tags.length > 0) {
      tagsContainer.innerHTML = note.tags.map((t) => `
        <span class="status-pill" style="background:#F1F5F9; color:#475569; font-weight:500;">#${escapeHtml(t)}</span>
      `).join("");
    }
  } catch (err) {
    console.error("Error loading note details:", err);
    showToast(err.message || "Failed to load note details.", "error");
    if (titleEl) titleEl.textContent = "Note Not Found";
  }
});
