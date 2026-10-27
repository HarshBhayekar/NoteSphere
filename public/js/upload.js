/**
 * NoteSphere - Note Upload Workflow
 * Handles drag-and-drop PDF selection, validation, and submission
 */

document.addEventListener("DOMContentLoaded", async () => {
  const uploadForm = document.getElementById("upload-form");
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");
  const fileSelectedBox = document.getElementById("file-selected-box");
  const fileNameDisplay = document.getElementById("file-selected-name");
  const fileSizeDisplay = document.getElementById("file-selected-size");
  const removeFileBtn = document.getElementById("remove-file-btn");
  const semesterSelect = document.getElementById("semester-select");
  const subjectSelect = document.getElementById("subject-select");
  const submitBtn = document.getElementById("submit-upload-btn");
  const uploadAlert = document.getElementById("upload-alert");

  let selectedFile = null;

  // Initialize subjects dropdown
  await loadSubjects();

  if (semesterSelect) {
    semesterSelect.addEventListener("change", () => loadSubjects(semesterSelect.value));
  }

  async function loadSubjects(semester = "") {
    if (!subjectSelect) return;
    try {
      const res = await api.getSubjects(semester);
      const subjects = res.data || [];
      subjectSelect.innerHTML = '<option value="">Select a Subject...</option>';
      subjects.forEach((sub) => {
        const opt = document.createElement("option");
        opt.value = sub.id || sub.name;
        opt.dataset.name = sub.name;
        opt.textContent = `${sub.name} (Sem ${sub.semester})`;
        subjectSelect.appendChild(opt);
      });
    } catch (e) {
      console.error("Error loading subjects:", e);
    }
  }

  // Dropzone drag & drop events
  if (dropzone && fileInput) {
    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", () => {
      dropzone.classList.remove("dragover");
    });

    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFileSelection(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener("change", () => {
      if (fileInput.files && fileInput.files.length > 0) {
        handleFileSelection(fileInput.files[0]);
      }
    });
  }

  function handleFileSelection(file) {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      showToast("Only PDF files are supported.", "error");
      return;
    }

    const maxBytes = 10 * 1024 * 1024; // 10 MB
    if (file.size > maxBytes) {
      showToast("File size exceeds 10 MB limit.", "error");
      return;
    }

    selectedFile = file;
    fileNameDisplay.textContent = file.name;
    fileSizeDisplay.textContent = formatFileSize(file.size);
    dropzone.style.display = "none";
    fileSelectedBox.classList.add("active");
  }

  if (removeFileBtn) {
    removeFileBtn.addEventListener("click", () => {
      selectedFile = null;
      if (fileInput) fileInput.value = "";
      fileSelectedBox.classList.remove("active");
      dropzone.style.display = "block";
    });
  }

  // Form submission
  if (uploadForm) {
    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const user = await getCurrentToken();
      if (!user) {
        showToast("Please log in to upload notes.", "warning");
        setTimeout(() => { window.location.href = "/login.html"; }, 1500);
        return;
      }

      if (!selectedFile) {
        showToast("Please select a PDF document to upload.", "error");
        return;
      }

      const title = document.getElementById("title-input").value.trim();
      const semester = semesterSelect.value;
      const selectedOption = subjectSelect.options[subjectSelect.selectedIndex];
      const subjectId = subjectSelect.value;
      const subjectName = selectedOption ? (selectedOption.dataset.name || selectedOption.text) : "";
      const description = document.getElementById("description-input").value.trim();
      const tags = document.getElementById("tags-input").value.trim();

      if (!title || !semester || !subjectId) {
        showToast("Please complete all required fields.", "error");
        return;
      }

      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("title", title);
      formData.append("semester", semester);
      formData.append("subjectId", subjectId);
      formData.append("subjectName", subjectName);
      formData.append("description", description);
      formData.append("tags", tags);

      submitBtn.disabled = true;
      submitBtn.textContent = "Uploading to Cloud...";

      try {
        const response = await api.uploadNote(formData);
        showToast("Notes published successfully!", "success");

        if (uploadAlert) {
          uploadAlert.style.display = "block";
          uploadAlert.className = "auth-alert success";
          uploadAlert.innerHTML = `
            <strong>Published!</strong> Your notes are now live and accessible to all students.
            <div style="margin-top: 12px; display: flex; gap: 10px;">
              <a href="/browse.html" class="btn btn-primary btn-sm">Browse Notes</a>
              <a href="/my-uploads.html" class="btn btn-secondary btn-sm">View in My Uploads</a>
            </div>
          `;
        }

        uploadForm.reset();
        removeFileBtn.click();
      } catch (err) {
        console.error("Upload error:", err);
        showToast(err.message || "Failed to upload notes.", "error");
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Publish Notes";
      }
    });
  }
});
