document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-upload');
    const fileNameEl = document.querySelector('.file-name');
    const fileSizeIndicator = document.getElementById('file-size-indicator');
    const fileSizeText = document.getElementById('file-size-text');
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
        return (bytes / Math.pow(1024, i)).toFixed(i ? 2 : 0) + ' ' + sizes[i];
    }

    // file input -> update UI
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const f = e.target.files[0];
            if (!f) {
                if (fileNameEl) fileNameEl.textContent = '';
                if (fileSizeIndicator) fileSizeIndicator.style.display = 'none';
                return;
            }
            if (fileNameEl) fileNameEl.textContent = `${f.name} selected`;
            if (fileSizeText) fileSizeText.textContent = `File size: ${humanFileSize(f.size)}`;
            if (fileSizeIndicator) fileSizeIndicator.style.display = 'flex';
        });
    }

    // when form submits show loading indicator quickly (server will handle actual work)
    if (form) {
        form.addEventListener('submit', () => {
            if (convertBtn) {
                convertBtn.disabled = true;
                convertBtn.style.opacity = '0.85';
            }
            if (loadingIndicator) loadingIndicator.style.display = 'block';
        });
    }

    // open filename modal to download with custom name
    if (downloadBtn) {
        downloadBtn.addEventListener('click', (e) => {
            const audio = downloadBtn.dataset.audio;
            if (!audio) return;
            if (filenameModal) filenameModal.style.display = 'flex';
            customFilenameInput && (customFilenameInput.value = '');
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
            // keep modal open until browser navigates (safer UX)
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
});

