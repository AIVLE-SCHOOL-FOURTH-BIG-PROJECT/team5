document.addEventListener('DOMContentLoaded', function() {
    // 파일 미리보기 기능
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

    // 분석 버튼 상태 업데이트 기능
    function updateAnalyzeButton() {
        const fileInput = document.getElementById('file-upload');
        const analyzeButton = document.getElementById('analyze-button');
        if (fileInput && analyzeButton) {
            analyzeButton.disabled = !fileInput.files.length;
        }
    }

    // 파일이 변경될 때마다 호출되는 이벤트 리스너
    const fileInput = document.getElementById('file-upload');
    if (fileInput) {
        fileInput.addEventListener('change', function(event) {
            if (this.files && this.files[0]) {
                previewFile(this.files[0]);
                updateAnalyzeButton();
            }
        });
    }

    // 드래그 앤 드롭 이벤트 리스너들
    const dragDropArea = document.getElementById('drag-drop-area');
    if (dragDropArea) {
        dragDropArea.addEventListener('dragover', function(event) {
            event.preventDefault();
            event.stopPropagation();
            this.classList.add('drag-over');
        }, false);

        dragDropArea.addEventListener('dragleave', function(event) {
            event.preventDefault();
            event.stopPropagation();
            this.classList.remove('drag-over');
        }, false);

        dragDropArea.addEventListener('drop', function(event) {
            event.preventDefault();
            event.stopPropagation();
            this.classList.remove('drag-over');

            const file = event.dataTransfer.files[0];
            if (fileInput && file) {
                fileInput.files = event.dataTransfer.files;
                previewFile(file);
                updateAnalyzeButton();
            }
        }, false);
    }

    // 이미지 분석 시작 버튼 이벤트 리스너
    const analyzeButton = document.getElementById('analyze-button');
    if (analyzeButton) {
        analyzeButton.addEventListener('click', function() {
            var fileInput = document.getElementById('file-upload');
            if (fileInput && fileInput.files.length > 0) {
                var formData = new FormData(document.getElementById('image-upload-form'));

                // 이 부분에 서버의 업로드 처리 URL을 정확하게 지정해야 합니다.
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
    }
});