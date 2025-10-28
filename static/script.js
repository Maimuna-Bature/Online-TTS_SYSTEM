document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-upload');
    const fileNameEl = document.querySelector('.file-upload-box .file-name');
    const fileUploadBox = document.querySelector('.file-upload-box');
    const fileSizeIndicator = document.getElementById('file-size-indicator');
    const fileSizeText = document.getElementById('file-size-text');
    const standaloneVoicesLabel = document.getElementById('standalone-voices-label');
    const form = document.querySelector('.tts-form');
    const loadingIndicator = document.getElementById('loading-indicator');
    const convertBtn = document.querySelector('.convert-btn');
    const downloadBtn = document.getElementById('custom-download-btn');
    const filenameModal = document.getElementById('filename-modal');
    const confirmDownloadBtn = document.getElementById('confirm-download-btn');
    const cancelDownloadBtn = document.getElementById('cancel-download-btn');
    const customFilenameInput = document.getElementById('custom-filename-input');

    function humanFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        // **UPDATED: Include the "File size: " prefix for full consistency**
        return `File size: ${(bytes / Math.pow(1024, i)).toFixed(i ? 2 : 0)} ${sizes[i]}`;
    }

    // file input -> update UI
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const f = e.target.files[0];
            
            // 1. Reset state
            fileUploadBox && fileUploadBox.classList.remove('file-selected');
            fileSizeIndicator && (fileSizeIndicator.style.display = 'none');
            fileNameEl && (fileNameEl.textContent = '');
            standaloneVoicesLabel && (standaloneVoicesLabel.style.display = 'block'); 

            if (!f) {
                return;
            }

            // 2. Update file upload box
            if (fileUploadBox) {
                fileUploadBox.classList.add('file-selected');
            }
            if (fileNameEl) {
                fileNameEl.textContent = `${f.name} selected`;
            }

            // 3. Update file size indicator
            if (fileSizeText) fileSizeText.textContent = humanFileSize(f.size);
            if (fileSizeIndicator) fileSizeIndicator.style.display = 'flex';
            standaloneVoicesLabel && (standaloneVoicesLabel.style.display = 'none'); 
        });
    }

    // when form submits show loading indicator quickly (server will handle actual work)
    if (form) {
        form.addEventListener('submit', () => {
            if (convertBtn) {
                convertBtn.textContent = 'Loading...';
                convertBtn.classList.remove('convert-btn');
                convertBtn.classList.add('loading-btn');
                convertBtn.disabled = true; 
                convertBtn.style.opacity = '1'; 
            }
            if (loadingIndicator) loadingIndicator.style.display = 'flex';
        });
    }

    // open filename modal to download with custom name
    if (downloadBtn) {
        downloadBtn.addEventListener('click', (e) => {
            const audio = downloadBtn.dataset.audio;
            if (!audio) return;
            if (filenameModal) filenameModal.style.display = 'flex';
            
            let defaultName = audio.replace('.mp3', '').split('/').pop();
            defaultName = defaultName.split('?')[0]; 
            
            customFilenameInput && (customFilenameInput.value = defaultName);
            confirmDownloadBtn && (confirmDownloadBtn.dataset.audio = audio);
        });
    }

    // confirm download (redirect to download endpoint with custom name)
    if (confirmDownloadBtn) {
        confirmDownloadBtn.addEventListener('click', () => {
            const audio = confirmDownloadBtn.dataset.audio;
            const name = (customFilenameInput && customFilenameInput.value.trim()) || '';
            let url = `/download/${encodeURIComponent(audio)}`;
            if (name) url += `?name=${encodeURIComponent(name)}`;
            window.location.href = url;
            
            if (filenameModal) filenameModal.style.display = 'none';
        });
    }

    // cancel modal
    if (cancelDownloadBtn) {
        cancelDownloadBtn.addEventListener('click', () => {
            if (filenameModal) filenameModal.style.display = 'none';
        });
    }

    // close modal on ESC
    document.addEventListener('keydown', (ev) => {
        if (ev.key === 'Escape' && filenameModal && filenameModal.style.display === 'flex') {
            filenameModal.style.display = 'none';
        }
    });

    // Initial state check for the voices label on page load
    if (fileInput && fileInput.files.length > 0) {
        standaloneVoicesLabel && (standaloneVoicesLabel.style.display = 'none');
    } else {
        standaloneVoicesLabel && (standaloneVoicesLabel.style.display = 'block');
    }
});