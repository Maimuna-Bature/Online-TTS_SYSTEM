document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file');
    const fileNameSpan = document.getElementById('file-name');
    const textArea = document.getElementById('text'); //gets the texterea element
    const form = document.querySelector('form'); //gets the form element
    const submitBtn = form.querySelector('button[type="submit"]');
    const uploadText = document.getElementById('upload-text');

    // Show selected file name
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) {
            fileNameSpan.textContent = fileInput.files[0].name;
            textArea.value = ''; // Clear the textarea when a new file is selected
        } else {
            fileNameSpan.textContent = "No file chosen";
        }
    });

    //Clear file selection if user types into texterea
    textArea.addEventListener('input', function() {
        if (textArea.value.trim() !== '') {
            fileInput.value = ''; // Clear the file input
            fileNameSpan.textContent = "No file chosen"; // Update the file name display
        }
    });

    //Submit loading feedback
    form.addEventListener('submit', function() {
        const isTextEntered = textArea.value.trim() !== '';
        const isFileSelected = fileInput.files.length > 0;

        if (isTextEntered || isFileSelected) {
            submitBtn.classList.add('loading');
            submitBtn.textContent = 'Loading...';
            submitBtn.disabled = true; // Disable the button to prevent multiple submissions
        }
    });

    if (fileInput && uploadText) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                uploadText.innerHTML = `<b>${this.files[0].name}</b> selected`;
            } else {
                uploadText.innerHTML = `Upload <b>.txt</b> or <b>.docx</b> file<br><small>(Click to upload)</small>`;
            }
        });
    }

    const customDownloadBtn = document.getElementById('custom-download-btn');
    const filenameModal = document.getElementById('filename-modal');
    const confirmDownloadBtn = document.getElementById('confirm-download-btn');
    const cancelDownloadBtn = document.getElementById('cancel-download-btn');
    const customFilenameInput = document.getElementById('custom-filename-input');

    if (customDownloadBtn) {
        customDownloadBtn.addEventListener('click', function() {
            filenameModal.style.display = 'flex';
            customFilenameInput.value = '';
            customFilenameInput.focus();
        });
    }
    if (cancelDownloadBtn) {
        cancelDownloadBtn.addEventListener('click', function() {
            filenameModal.style.display = 'none';
        });
    }
    if (confirmDownloadBtn) {
        confirmDownloadBtn.addEventListener('click', function() {
            const filename = customFilenameInput.value.trim() || 'speech';
            const audioFilename = customDownloadBtn.getAttribute('data-audio');
            window.location.href = `/download/${audioFilename}?name=${encodeURIComponent(filename)}`;
            filenameModal.style.display = 'none';
        });
    }
});

