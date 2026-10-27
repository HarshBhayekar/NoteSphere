/**
 * NoteSphere - My Uploads Script
 * Allows students to monitor the moderation status of their submissions.
 */

document.addEventListener("DOMContentLoaded", async () => {
  const tableBody = document.getElementById("my-uploads-tbody");
  const emptyState = document.getElementById("my-uploads-empty");

  // Display loading indicator while auth and notes are being retrieved
  if (tableBody) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align: center; padding: 48px; color: var(--color-muted);">
          <div class="spinner" style="margin-bottom: 12px;"></div>
          <div style="font-weight: 500;">Loading your uploads...</div>
        </td>
      </tr>
    `;
  }

  // Check auth - waits until Firebase has determined whether the user is logged in
  const token = await getCurrentToken();
  if (!token) {
    if (tableBody) tableBody.innerHTML = "";
    showToast("Please log in to view your submissions.", "warning");
    setTimeout(() => { window.location.href = "/login.html"; }, 1500);
    return;
  }

  try {
    const res = await api.getMyNotes();
    const notes = res.data || [];
    renderUserNotes(notes);
  } catch (err) {
    console.error("Error fetching user notes:", err);
    if (tableBody) tableBody.innerHTML = "";
    showToast("Failed to load your submissions.", "error");
  }

  function renderUserNotes(notes) {
    if (!notes || notes.length === 0) {
      if (tableBody) tableBody.innerHTML = "";
      if (emptyState) emptyState.style.display = "flex";
      return;
    }

    if (emptyState) emptyState.style.display = "none";
    if (tableBody) {
      tableBody.innerHTML = notes.map((note) => `
        <tr>
          <td>
            <div style="font-weight: 600; color: var(--color-heading);">${escapeHtml(note.title)}</div>
            <div style="font-size: 0.8125rem; color: var(--color-muted);">${formatFileSize(note.fileSizeBytes)} · Semester ${note.semester}</div>
          </td>
          <td>${escapeHtml(note.subjectName)}</td>
          <td>${formatDate(note.createdAt)}</td>
          <td>
            <span class="status-pill approved">Published</span>
          </td>
          <td>${note.downloadCount || 0}</td>
          <td>
            <div style="display:flex; gap:8px;">
              <a href="/note-details.html?id=${note.id}" class="btn btn-secondary btn-sm">View</a>
              <button onclick="deleteMyNote('${note.id}', '${escapeHtml(note.title)}')" class="btn btn-danger btn-sm">Delete</button>
            </div>
          </td>
        </tr>
      `).join("");
    }
  }

  window.deleteMyNote = async function(noteId, title) {
    if (!confirm(`Are you sure you want to delete "${title}"? This cannot be undone.`)) {
      return;
    }
    try {
      await api.deleteNote(noteId);
      showToast("Note deleted successfully.", "success");
      // Reload list
      const res = await api.getMyNotes();
      renderUserNotes(res.data || []);
    } catch (err) {
      showToast(err.message || "Failed to delete note.", "error");
    }
  };
});
