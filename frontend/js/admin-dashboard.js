/**
 * NoteSphere - Admin Dashboard & Moderation Workspace
 */

let activeNoteToReject = null;
let activeNoteToDelete = null;

document.addEventListener("DOMContentLoaded", async () => {
  const statTotal = document.getElementById("stat-total");
  const statPending = document.getElementById("stat-pending");
  const statApproved = document.getElementById("stat-approved");
  const statDownloads = document.getElementById("stat-downloads");
  const queueTbody = document.getElementById("moderation-tbody");
  const statusFilterTabs = document.querySelectorAll(".filter-tab-btn");

  let currentFilter = "pending";

  // Check Admin Authorization
  await verifyAdminAccess();

  // Load Initial Dashboard Data
  await loadStats();
  await loadQueue(currentFilter);

  // Tab Filtering
  statusFilterTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      statusFilterTabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      currentFilter = tab.dataset.status;
      loadQueue(currentFilter);
    });
  });

  async function verifyAdminAccess() {
    const token = await getCurrentToken();
    if (!token) {
      showToast("Access denied. Please log in as an administrator.", "error");
      setTimeout(() => { window.location.href = "/login.html"; }, 1500);
      return;
    }
  }

  async function loadStats() {
    try {
      const res = await api.getAdminStats();
      const stats = res.data;
      if (statTotal) statTotal.textContent = stats.totalNotes;
      if (statPending) statPending.textContent = stats.pendingNotes;
      if (statApproved) statApproved.textContent = stats.approvedNotes;
      if (statDownloads) statDownloads.textContent = stats.totalDownloads;
    } catch (e) {
      console.error("Error loading admin stats:", e);
    }
  }

  async function loadQueue(status) {
    if (!queueTbody) return;
    queueTbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:30px;">Loading submissions...</td></tr>`;

    try {
      const res = await api.getAdminNotes(status);
      const notes = res.data || [];
      renderQueue(notes);
    } catch (e) {
      console.error("Error loading moderation queue:", e);
      queueTbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--color-error); padding:30px;">Failed to load moderation queue.</td></tr>`;
    }
  }

  function renderQueue(notes) {
    if (!notes || notes.length === 0) {
      queueTbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:30px; color:var(--color-muted);">No submissions found for status "${currentFilter}".</td></tr>`;
      return;
    }

    queueTbody.innerHTML = notes.map((note) => `
      <tr>
        <td>
          <div style="font-weight: 600; color: var(--color-heading);">${escapeHtml(note.title)}</div>
          <div style="font-size: 0.8125rem; color: var(--color-muted);">${formatFileSize(note.fileSizeBytes)}</div>
        </td>
        <td>${escapeHtml(note.subjectName)} (Sem ${note.semester})</td>
        <td>${escapeHtml(note.uploaderName || note.uploadedBy || "Student")}</td>
        <td>${formatDate(note.createdAt)}</td>
        <td><span class="status-pill ${note.status}">${note.status}</span></td>
        <td>
          <div class="table-actions">
            <a href="/note-details.html?id=${note.id}" class="btn btn-secondary btn-sm" target="_blank">Preview</a>
            ${note.status !== 'approved' ? `
              <button onclick="approveNote('${note.id}')" class="btn btn-primary btn-sm" style="background:var(--color-success);">Approve</button>
            ` : ''}
            ${note.status !== 'rejected' ? `
              <button onclick="openRejectDialog('${note.id}', '${escapeHtml(note.title)}')" class="btn btn-secondary btn-sm" style="color:var(--color-warning);">Reject</button>
            ` : ''}
            <button onclick="openDeleteDialog('${note.id}', '${escapeHtml(note.title)}')" class="btn btn-danger btn-sm">Delete</button>
          </div>
        </td>
      </tr>
    `).join("");
  }

  // Global moderation action handlers
  window.approveNote = async function (noteId) {
    try {
      await api.moderateNote(noteId, "approved");
      showToast("Note approved and published!", "success");
      loadStats();
      loadQueue(currentFilter);
    } catch (err) {
      showToast(err.message || "Failed to approve note.", "error");
    }
  };

  window.openRejectDialog = function (noteId, noteTitle) {
    activeNoteToReject = noteId;
    const titleEl = document.getElementById("reject-note-title");
    if (titleEl) titleEl.textContent = noteTitle;
    openModal("reject-modal");
  };

  window.confirmRejection = async function () {
    const reasonInput = document.getElementById("rejection-reason-input");
    const reason = reasonInput ? reasonInput.value.trim() : "";
    if (!reason) {
      showToast("Please provide a rejection reason.", "error");
      return;
    }

    try {
      await api.moderateNote(activeNoteToReject, "rejected", reason);
      showToast("Submission marked as rejected.", "success");
      closeModal("reject-modal");
      if (reasonInput) reasonInput.value = "";
      loadStats();
      loadQueue(currentFilter);
    } catch (err) {
      showToast(err.message || "Failed to reject note.", "error");
    }
  };

  window.openDeleteDialog = function (noteId, noteTitle) {
    activeNoteToDelete = noteId;
    const titleEl = document.getElementById("delete-note-title");
    if (titleEl) titleEl.textContent = noteTitle;
    openModal("delete-modal");
  };

  window.confirmDeletion = async function () {
    try {
      await api.deleteNote(activeNoteToDelete);
      showToast("Note and Cloudinary asset permanently deleted.", "success");
      closeModal("delete-modal");
      loadStats();
      loadQueue(currentFilter);
    } catch (err) {
      showToast(err.message || "Failed to delete note.", "error");
    }
  };
});
