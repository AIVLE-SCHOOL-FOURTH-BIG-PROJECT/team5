document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file-upload');
    if (fileInput) {
        fileInput.addEventListener('change', function(event) {
            if (this.files && this.files[0]) {
                previewFile(this.files[0]);
                updateAnalyzeButton();
            }
        });
    }

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
        const styleOptions = document.querySelector('input[name="style"]:checked');
        const analyzeButton = document.getElementById('analyze-button');
        if (fileInput && analyzeButton) {
            analyzeButton.disabled = !(fileInput.files.length && styleOptions);
        }
    }

    document.querySelectorAll('input[name="style"]').forEach(function(radio) {
        radio.addEventListener('change', updateAnalyzeButton);
    });
    
    // Update the button state when the file is selected
    document.getElementById('file-upload').addEventListener('change', function() {
        if (this.files && this.files[0]) {
            previewFile(this.files[0]);
        }
        updateAnalyzeButton();
    });

   

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
    const analyzeButton2 = document.getElementById('analyze-button');
    if (analyzeButton2) {
        analyzeButton2.addEventListener('click', function() {
            var fileInput2 = document.getElementById('file-upload');
            if (fileInput2 && fileInput2.files.length > 0) {
                var formData2 = new FormData(document.getElementById('image-upload-form'));

                fetch('/path-to-image_change_handler', {
                    method: 'POST',
                    credentials: 'include',
                    body: formData2
                })
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        throw new Error('Network response was not ok.');
                    }
                })
                .then(data => {
                    // 분석 결과에 따라 다음 페이지로 이동 또는 메시지 표시
                    if(data.result === 'success') {
                        window.location.href = '/airemodeling_result';
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
