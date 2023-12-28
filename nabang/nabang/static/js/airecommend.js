function previewFile(file) {
    const preview = document.getElementById('preview-image');
    const uploadInstructions = document.getElementById('upload-instructions');
    const changeInstructions = document.getElementById('change-instructions');
    const reader = new FileReader();

    reader.onloadend = function () {
        preview.src = reader.result;
        preview.style.display = 'block';
        uploadInstructions.style.display = 'none';
        changeInstructions.style.display = 'block';
    }

    if (file) {
        reader.readAsDataURL(file);
    } else {
        preview.src = "";
        preview.style.display = 'none';
        uploadInstructions.style.display = 'block';
        changeInstructions.style.display = 'none';
    }
}

function updateAnalyzeButton() {
    const fileInput = document.getElementById('file-upload');
    const analyzeButton = document.getElementById('analyze-button');
    analyzeButton.disabled = !fileInput.files.length;
}

document.getElementById('file-upload').addEventListener('change', function(event) {
    if (this.files && this.files[0]) {
        previewFile(this.files[0]);
        updateAnalyzeButton();
    }
});

document.getElementById('drag-drop-area').addEventListener('dragover', function(event) {
    event.preventDefault();
    event.stopPropagation();
    this.classList.add('drag-over');
}, false);

document.getElementById('drag-drop-area').addEventListener('dragleave', function(event) {
    event.preventDefault();
    event.stopPropagation();
    this.classList.remove('drag-over');
}, false);

document.getElementById('drag-drop-area').addEventListener('drop', function(event) {
    event.preventDefault();
    event.stopPropagation();
    this.classList.remove('drag-over');

    const file = event.dataTransfer.files[0];
    document.getElementById('file-upload').files = event.dataTransfer.files;
    previewFile(file);
    updateAnalyzeButton();
}, false);

document.getElementById('analyze-button').addEventListener('click', function() {
    var fileInput = document.getElementById('file-upload');
    if (fileInput.files.length > 0) {
        var formData = new FormData(document.getElementById('image-upload-form'));

        fetch('/path-to-image-upload-handler', {
            method: 'POST',
            credentials: 'include',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Network response was not ok.');
            }
        })
        .then(data => {
            console.log(data);
            if(data.result === 'success') {
                window.location.href = '/airecommend_result';
            } else {
                alert('업로드에 실패했습니다.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('업로드 중 오류가 발생했습니다.');
        });
    }
});