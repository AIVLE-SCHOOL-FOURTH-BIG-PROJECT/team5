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
        const analyzeButton = document.getElementById('analyze-button');
        if (fileInput && analyzeButton) {
            analyzeButton.disabled = !fileInput.files.length;
        }
    }


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
                uploadAndAnalyzeImage(fileInput.files[0]);
            }
        });
    }

    function uploadAndAnalyzeImage(file) {
        var formData = new FormData();
        formData.append('file', file);

        fetch('/path-to-image-upload-handler', {
            method: 'POST',
            credentials: 'include',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.result === 'success') {
                // 이미지 분석 결과를 받아서 원형 그래프에 표시
                drawColorChart(data.colorAnalysis);
            } else {
                alert('업로드에 실패했습니다.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('업로드 중 오류가 발생했습니다.');
        });
    }
    if (window.location.pathname.endsWith('/airecommend_result')) {
        fetchColorDataAndDrawChart();
    }

    function fetchColorDataAndDrawChart() {
        fetch('/get-color-data') // 서버에서 색상 데이터를 가져오는 API 경로
            .then(response => response.json())
            .then(colorData => {
                drawColorChart(colorData);
            })
            .catch(error => console.error('Error fetching color data:', error));
    }

    function drawColorChart(colorData) {
        const ctx = document.getElementById('colorChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: colorData.map(item => item.percentage),
                    backgroundColor: colorData.map(item => `rgb(${item.rgb.join(',')})`),
                }],
                labels: colorData.map(item => `${item.label} (${item.percentage}%)`),
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: '색상 분석 결과'
                }
            }
        });
    }
});