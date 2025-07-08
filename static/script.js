document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file');
    const fileNameSpan = document.getElementById('file-name');
    const textArea = document.getElementById('text'); //gets the texterea element
    const form = document.querySelector('form'); //gets the form element
    const submitBtn = form.querySelector('button[type="submit"]');

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

    document.getElementById('file').addEventListener('change', function(e) {
        const uploadText = document.getElementById('upload-text');
        if (this.files && this.files.length > 0) {
            uploadText.innerHTML = `<b>${this.files[0].name}</b> selected`;
        } else {
            uploadText.innerHTML = `Upload <b>.txt</b> or <b>.docx</b> file<br><small>(Click or drag to upload)</small>`;
        }
    });
});

