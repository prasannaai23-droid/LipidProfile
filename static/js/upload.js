let selectedFile = null;
let cameraStream = null;

// ==================== Method Selection ====================
document.addEventListener('DOMContentLoaded', function() {
    initializeMethodCards();
    initializeDragDrop();
    initializeFileInput();
    initializeCameraControls();
    initializeManualForm();
});

function initializeMethodCards() {
    const methodCards = document.querySelectorAll('.method-card');
    
    methodCards.forEach(card => {
        card.addEventListener('click', () => {
            // Remove active from all cards
            methodCards.forEach(c => c.classList.remove('active'));
            // Add active to clicked card
            card.classList.add('active');
            
            const method = card.getAttribute('data-method');
            switchUploadMethod(method);
        });
    });
}

function switchUploadMethod(method) {
    // Hide all upload areas
    document.getElementById('fileUploadArea').classList.add('hidden');
    document.getElementById('cameraArea').classList.add('hidden');
    document.getElementById('manualArea').classList.add('hidden');
    
    // Show selected area
    if (method === 'file') {
        document.getElementById('fileUploadArea').classList.remove('hidden');
    } else if (method === 'camera') {
        document.getElementById('cameraArea').classList.remove('hidden');
    } else if (method === 'manual') {
        document.getElementById('manualArea').classList.remove('hidden');
    }
}

// ==================== File Upload ====================
function initializeDragDrop() {
    const dropZone = document.getElementById('dropZone');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-over');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-over');
        });
    });
    
    dropZone.addEventListener('drop', handleDrop);
    dropZone.addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });
}

function initializeFileInput() {
    const fileInput = document.getElementById('fileInput');
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFiles(files) {
    if (files.length > 0) {
        const file = files[0];
        
        // Validate file type
        const validTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
        if (!validTypes.includes(file.type)) {
            alert('Please upload a PDF, JPG, or PNG file');
            return;
        }
        
        // Validate file size (10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('File size must be less than 10MB');
            return;
        }
        
        selectedFile = file;
        displayFilePreview(file);
    }
}

function displayFilePreview(file) {
    document.getElementById('dropZone').classList.add('hidden');
    document.getElementById('filePreview').classList.remove('hidden');
    
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    
    // Show image preview if it's an image
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewImg = document.getElementById('previewImage');
            previewImg.src = e.target.result;
            previewImg.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function removeFile() {
    selectedFile = null;
    document.getElementById('filePreview').classList.add('hidden');
    document.getElementById('dropZone').classList.remove('hidden');
    document.getElementById('fileInput').value = '';
    document.getElementById('previewImage').classList.add('hidden');
}

function uploadFile() {
    if (!selectedFile) {
        alert('Please select a file first');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    showProcessing();
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideProcessing();
        if (data.success) {
            displayResults(data);
        } else {
            alert('Error processing file: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        hideProcessing();
        alert('Upload failed: ' + error.message);
    });
}

// ==================== Camera Functions ====================
function initializeCameraControls() {
    document.getElementById('startCamera').addEventListener('click', startCamera);
    document.getElementById('capturePhoto').addEventListener('click', capturePhoto);
    document.getElementById('retakePhoto').addEventListener('click', retakePhoto);
}

async function startCamera() {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: 'environment' } 
        });
        
        const video = document.getElementById('cameraVideo');
        video.srcObject = cameraStream;
        
        document.getElementById('startCamera').classList.add('hidden');
        document.getElementById('capturePhoto').classList.remove('hidden');
    } catch (error) {
        alert('Cannot access camera: ' + error.message);
    }
}

function capturePhoto() {
    const video = document.getElementById('cameraVideo');
    const canvas = document.getElementById('cameraCanvas');
    const context = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    
    // Stop camera stream
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
    }
    
    video.style.display = 'none';
    canvas.style.display = 'block';
    
    document.getElementById('capturePhoto').classList.add('hidden');
    document.getElementById('retakePhoto').classList.remove('hidden');
    
    // Convert canvas to blob and upload
    canvas.toBlob(blob => {
        selectedFile = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' });
        uploadFile();
    }, 'image/jpeg');
}

function retakePhoto() {
    const video = document.getElementById('cameraVideo');
    const canvas = document.getElementById('cameraCanvas');
    
    video.style.display = 'block';
    canvas.style.display = 'none';
    
    document.getElementById('retakePhoto').classList.add('hidden');
    document.getElementById('startCamera').classList.remove('hidden');
}

// ==================== Manual Entry ====================
function initializeManualForm() {
    document.getElementById('manualForm').addEventListener('submit', handleManualSubmit);
}

function handleManualSubmit(e) {
    e.preventDefault();
    
    const data = {
        total_cholesterol: parseFloat(document.getElementById('manualTC').value),
        ldl: parseFloat(document.getElementById('manualLDL').value),
        hdl: parseFloat(document.getElementById('manualHDL').value),
        triglycerides: parseFloat(document.getElementById('manualTG').value)
    };
    
    // Validate inputs
    if (!data.total_cholesterol || !data.ldl || !data.hdl || !data.triglycerides) {
        alert('Please fill in all fields');
        return;
    }
    
    showProcessing();
    
    fetch('/api/manual-entry', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        hideProcessing();
        if (result.success) {
            displayResults(result);
        } else {
            alert('Error: ' + (result.error || 'Unknown error'));
        }
    })
    .catch(error => {
        hideProcessing();
        alert('Submission failed: ' + error.message);
    });
}

// ==================== Processing Overlay ====================
function showProcessing() {
    document.getElementById('processingOverlay').classList.remove('hidden');
    
    const statuses = [
        'Analyzing document...',
        'Extracting text with OCR...',
        'Identifying lipid values...',
        'Running ML prediction...',
        'Generating recommendations...'
    ];
    
    let index = 0;
    const interval = setInterval(() => {
        if (index < statuses.length) {
            document.getElementById('processingStatus').textContent = statuses[index];
            index++;
        } else {
            clearInterval(interval);
        }
    }, 1000);
}

function hideProcessing() {
    document.getElementById('processingOverlay').classList.add('hidden');
}

// ==================== Results Display ====================
function displayResults(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    const extractedValues = document.getElementById('extractedValues');
    
    const html = `
        <div class="lipid-grid">
            <div class="lipid-card">
                <h4>Total Cholesterol</h4>
                <p class="value">${data.total_cholesterol || 'N/A'} mg/dL</p>
            </div>
            <div class="lipid-card">
                <h4>LDL Cholesterol</h4>
                <p class="value">${data.ldl || 'N/A'} mg/dL</p>
            </div>
            <div class="lipid-card">
                <h4>HDL Cholesterol</h4>
                <p class="value">${data.hdl || 'N/A'} mg/dL</p>
            </div>
            <div class="lipid-card">
                <h4>Triglycerides</h4>
                <p class="value">${data.triglycerides || 'N/A'} mg/dL</p>
            </div>
        </div>
        <div class="risk-display">
            <h3>Risk Level: <span class="risk-${data.risk_level}">${data.risk_level || 'Unknown'}</span></h3>
        </div>
    `;
    
    extractedValues.innerHTML = html;
    resultsContainer.classList.remove('hidden');
    
    // Store data for report page
    localStorage.setItem('lastReport', JSON.stringify(data));
}

function viewFullReport() {
    const data = JSON.parse(localStorage.getItem('lastReport'));
    if (data) {
        const params = new URLSearchParams({
            tc: data.total_cholesterol,
            ldl: data.ldl,
            hdl: data.hdl,
            tg: data.triglycerides,
            risk: data.risk_level
        });
        window.location.href = `/report?${params.toString()}`;
    }
}

function viewDashboard() {
    window.location.href = '/dashboard';
}

// ==================== Load Recent Uploads ====================
function loadRecentUploads() {
    // This would typically fetch from backend
    const recentList = document.getElementById('recentUploadsList');
    const uploads = JSON.parse(localStorage.getItem('recentUploads') || '[]');
    
    if (uploads.length === 0) {
        recentList.innerHTML = '<p class="empty-state">No recent uploads</p>';
        return;
    }
    
    recentList.innerHTML = uploads.map(upload => `
        <div class="upload-item">
            <i class="fas fa-file-medical"></i>
            <div>
                <p><strong>${upload.name}</strong></p>
                <p class="date">${upload.date}</p>
            </div>
        </div>
    `).join('');
}

loadRecentUploads();