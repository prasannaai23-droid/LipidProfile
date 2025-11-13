// ==================== Global Variables ====================
let currentStep = 1;
let formData = {};

// ==================== Page Initialization ====================
document.addEventListener('DOMContentLoaded', function() {
    initializeForm();
    initializeMobileMenu();
    initializeSmoothScroll();
});

// ==================== Mobile Menu ====================
function initializeMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
        });
    }
}

// ==================== Smooth Scroll ====================
function initializeSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function scrollToAssessment() {
    const section = document.getElementById('assessmentSection');
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// ==================== Form Initialization ====================
function initializeForm() {
    const form = document.getElementById('lipidForm');
    if (!form) return;

    form.addEventListener('submit', handleFormSubmit);
    
    // Add real-time validation
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });
}

function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    const fieldName = field.name;
    
    // Clear previous errors
    clearFieldError(e);
    
    // Validation rules
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    if (field.type === 'number') {
        const min = parseFloat(field.getAttribute('min'));
        const max = parseFloat(field.getAttribute('max'));
        const numValue = parseFloat(value);
        
        if (value && (numValue < min || numValue > max)) {
            showFieldError(field, `Value must be between ${min} and ${max}`);
            return false;
        }
    }
    
    return true;
}

function showFieldError(field, message) {
    field.style.borderColor = 'var(--danger-color)';
    
    let errorEl = field.parentElement.querySelector('.field-error');
    if (!errorEl) {
        errorEl = document.createElement('span');
        errorEl.className = 'field-error';
        errorEl.style.cssText = `
            color: var(--danger-color);
            font-size: 0.75rem;
            margin-top: 0.25rem;
            display: block;
        `;
        field.parentElement.appendChild(errorEl);
    }
    errorEl.textContent = message;
}

function clearFieldError(e) {
    const field = e.target;
    field.style.borderColor = '';
    
    const errorEl = field.parentElement.querySelector('.field-error');
    if (errorEl) {
        errorEl.remove();
    }
}

// ==================== Multi-Step Form Navigation ====================
function nextStep() {
    // Validate current step
    const currentStepEl = document.querySelector(`.form-step[data-step="${currentStep}"]`);
    const inputs = currentStepEl.querySelectorAll('input[required], select[required]');
    
    let isValid = true;
    inputs.forEach(input => {
        const event = { target: input };
        if (!validateField(event)) {
            isValid = false;
        }
    });
    
    if (!isValid) {
        showNotification('Please fill in all required fields correctly', 'error');
        return;
    }
    
    // Save current step data
    saveStepData(currentStep);
    
    // Move to next step
    if (currentStep < 3) {
        currentStep++;
        updateStep();
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateStep();
    }
}

function updateStep() {
    // Update step indicators
    document.querySelectorAll('.step').forEach((step, index) => {
        if (index + 1 <= currentStep) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
    
    // Update form step content
    document.querySelectorAll('.form-step').forEach((step, index) => {
        if (index + 1 === currentStep) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

function saveStepData(step) {
    const stepEl = document.querySelector(`.form-step[data-step="${step}"]`);
    const inputs = stepEl.querySelectorAll('input, select');
    
    inputs.forEach(input => {
        if (input.type === 'checkbox') {
            formData[input.name] = input.checked ? 1 : 0;
        } else {
            formData[input.name] = input.value;
        }
    });
}

// ==================== Form Submission ====================
async function handleFormSubmit(e) {
    e.preventDefault();
    
    // Save final step data
    saveStepData(currentStep);
    
    // Validate all required fields
    const form = e.target;
    if (!form.checkValidity()) {
        showNotification('Please fill in all required fields', 'error');
        return;
    }
    
    // Prepare data for submission
    const submitData = {
        patient_id: formData.patient_id,
        patient_name: formData.patient_name,
        age: parseInt(formData.age),
        gender: formData.gender,
        bmi: parseFloat(formData.bmi),
        total_cholesterol: parseFloat(formData.total_cholesterol),
        ldl: parseFloat(formData.ldl),
        hdl: parseFloat(formData.hdl),
        triglycerides: parseFloat(formData.triglycerides),
        blood_glucose: parseFloat(formData.blood_glucose),
        smoking: formData.smoking || 0,
        family_history: formData.family_history || 0,
        hypertension: formData.hypertension || 0,
        diabetes: formData.diabetes || 0
    };
    
    // Show loading state
    showProcessingOverlay();
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(submitData)
        });
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Server returned non-JSON response. Please check your backend configuration.');
        }
        
        const result = await response.json();
        
        hideProcessingOverlay();
        
        if (response.ok && result.success) {
            displayResults(result);
            
            // Save to localStorage
            localStorage.setItem('lastAnalysis', JSON.stringify(result));
            
            // Show results section
            showResultsSection();
        } else {
            throw new Error(result.error || 'Analysis failed');
        }
        
    } catch (error) {
        hideProcessingOverlay();
        console.error('Submission error:', error);
        showNotification(`Error: ${error.message}`, 'error');
    }
}

// ==================== Processing Overlay ====================
function showProcessingOverlay() {
    let overlay = document.getElementById('processingOverlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'processingOverlay';
        overlay.innerHTML = `
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(15, 23, 42, 0.95);
                backdrop-filter: blur(10px);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <div style="
                    text-align: center;
                    color: var(--text-primary);
                ">
                    <div class="spinner" style="
                        width: 80px;
                        height: 80px;
                        border: 4px solid var(--border-color);
                        border-top: 4px solid var(--primary-color);
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                        margin: 0 auto 2rem;
                    "></div>
                    <h2 style="font-size: 1.5rem; margin-bottom: 1rem;">
                        <i class="fas fa-brain"></i> Analyzing Your Data
                    </h2>
                    <p id="processingStatus" style="color: var(--text-secondary); font-size: 1rem;">
                        Running AI analysis...
                    </p>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
        
        // Add spinner animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }
    
    overlay.style.display = 'block';
    
    // Simulate processing steps
    const statuses = [
        'Validating input data...',
        'Calculating risk factors...',
        'Running ML prediction model...',
        'Generating personalized recommendations...',
        'Finalizing analysis...'
    ];
    
    let statusIndex = 0;
    const statusInterval = setInterval(() => {
        const statusEl = document.getElementById('processingStatus');
        if (statusEl && statusIndex < statuses.length) {
            statusEl.textContent = statuses[statusIndex];
            statusIndex++;
        } else {
            clearInterval(statusInterval);
        }
    }, 800);
}

function hideProcessingOverlay() {
    const overlay = document.getElementById('processingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// ==================== Display Results ====================
function displayResults(data) {
    const resultsContent = document.getElementById('resultsContent');
    if (!resultsContent) return;
    
    // Calculate additional metrics
    const vldl = data.triglycerides / 5;
    const nonHdl = data.total_cholesterol - data.hdl;
    const tcHdlRatio = (data.total_cholesterol / data.hdl).toFixed(1);
    
    // Determine risk level color
    let riskColor, riskIcon;
    if (data.risk_level === 'High Risk') {
        riskColor = 'var(--danger-color)';
        riskIcon = '🔴';
    } else if (data.risk_level === 'Moderate Risk') {
        riskColor = 'var(--warning-color)';
        riskIcon = '⚠️';
    } else {
        riskColor = 'var(--success-color)';
        riskIcon = '✅';
    }
    
    resultsContent.innerHTML = `
        <div style="text-align: center; margin-bottom: 3rem;">
            <div style="
                font-size: 4rem;
                margin-bottom: 1rem;
            ">${riskIcon}</div>
            <h3 style="
                font-size: 2rem;
                color: ${riskColor};
                margin-bottom: 0.5rem;
            ">${data.risk_level}</h3>
            <p style="color: var(--text-secondary);">Based on your lipid profile analysis</p>
        </div>
        
        <div style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        ">
            ${createLipidCard('Total Cholesterol', data.total_cholesterol, 'mg/dL', '<200', data.total_cholesterol > 200)}
            ${createLipidCard('LDL (Bad)', data.ldl, 'mg/dL', '<100', data.ldl > 100)}
            ${createLipidCard('HDL (Good)', data.hdl, 'mg/dL', '>60', data.hdl < 60)}
            ${createLipidCard('Triglycerides', data.triglycerides, 'mg/dL', '<150', data.triglycerides > 150)}
            ${createLipidCard('VLDL', vldl.toFixed(1), 'mg/dL', '<30', vldl > 30)}
            ${createLipidCard('TC/HDL Ratio', tcHdlRatio, '', '<3.5', parseFloat(tcHdlRatio) > 3.5)}
        </div>
        
        <div style="
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
        ">
            <h4 style="
                font-size: 1.25rem;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            ">
                <i class="fas fa-info-circle"></i> Analysis Summary
            </h4>
            <p style="line-height: 1.8; color: var(--text-secondary);">
                ${generateSummary(data)}
            </p>
        </div>
        
        <div style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        ">
            ${createRecommendationCard('Diet', 'utensils', [
                'Reduce saturated fat intake',
                'Increase omega-3 rich foods',
                'Eat more fruits and vegetables',
                'Limit processed foods'
            ])}
            ${createRecommendationCard('Exercise', 'running', [
                '30 minutes of aerobic exercise daily',
                'Strength training 2-3 times per week',
                'Regular walking or jogging',
                'Stay active throughout the day'
            ])}
            ${createRecommendationCard('Lifestyle', 'heartbeat', [
                'Maintain healthy weight',
                'Quit smoking if applicable',
                'Manage stress levels',
                'Get 7-8 hours of sleep'
            ])}
        </div>
    `;
}

function createLipidCard(title, value, unit, optimal, isHigh) {
    const statusColor = isHigh ? 'var(--danger-color)' : 'var(--success-color)';
    const statusText = isHigh ? 'High' : 'Normal';
    
    return `
        <div style="
            background: var(--dark-bg);
            border: 2px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
        ">
            <h4 style="
                color: var(--text-secondary);
                font-size: 0.875rem;
                margin-bottom: 1rem;
            ">${title}</h4>
            <div style="
                font-size: 2.5rem;
                font-weight: 700;
                color: var(--text-primary);
                margin-bottom: 0.5rem;
            ">${value} <span style="font-size: 1rem; color: var(--text-secondary);">${unit}</span></div>
            <div style="
                display: inline-block;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                background: ${statusColor}22;
                color: ${statusColor};
                font-size: 0.875rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            ">${statusText}</div>
            <div style="
                color: var(--text-secondary);
                font-size: 0.75rem;
            ">Optimal: ${optimal}</div>
        </div>
    `;
}

function createRecommendationCard(title, icon, items) {
    return `
        <div style="
            background: var(--dark-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
        ">
            <h4 style="
                font-size: 1.25rem;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            ">
                <i class="fas fa-${icon}" style="color: var(--primary-light);"></i>
                ${title}
            </h4>
            <ul style="
                list-style: none;
                padding: 0;
                margin: 0;
            ">
                ${items.map(item => `
                    <li style="
                        padding: 0.5rem 0;
                        padding-left: 1.5rem;
                        position: relative;
                        color: var(--text-secondary);
                    ">
                        <span style="
                            position: absolute;
                            left: 0;
                            color: var(--success-color);
                            font-weight: 700;
                        ">✓</span>
                        ${item}
                    </li>
                `).join('')}
            </ul>
        </div>
    `;
}

function generateSummary(data) {
    let summary = `Your cardiovascular risk assessment indicates <strong>${data.risk_level.toLowerCase()}</strong>. `;
    
    if (data.ldl > 130) {
        summary += `Your LDL cholesterol is elevated at ${data.ldl} mg/dL. `;
    }
    if (data.hdl < 40) {
        summary += `Your HDL cholesterol is low at ${data.hdl} mg/dL. `;
    }
    if (data.triglycerides > 150) {
        summary += `Your triglycerides are elevated at ${data.triglycerides} mg/dL. `;
    }
    
    summary += `We recommend following the personalized lifestyle modifications and consulting with your healthcare provider for a comprehensive treatment plan.`;
    
    return summary;
}

// ==================== Show Results Section ====================
function showResultsSection() {
    const resultsSection = document.getElementById('resultsSection');
    const assessmentSection = document.getElementById('assessmentSection');
    
    if (resultsSection) {
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    if (assessmentSection) {
        assessmentSection.style.opacity = '0.5';
    }
}

// ==================== Results Actions ====================
function viewFullReport() {
    const data = JSON.parse(localStorage.getItem('lastAnalysis'));
    if (data) {
        const params = new URLSearchParams({
            id: data.patient_id,
            name: data.patient_name,
            age: data.age,
            gender: data.gender,
            tc: data.total_cholesterol,
            ldl: data.ldl,
            hdl: data.hdl,
            tg: data.triglycerides,
            risk: data.risk_level
        });
        window.location.href = `/report?${params.toString()}`;
    }
}

function downloadReport() {
    window.print();
}

function resetForm() {
    // Reset form
    document.getElementById('lipidForm').reset();
    
    // Reset step
    currentStep = 1;
    updateStep();
    
    // Hide results
    const resultsSection = document.getElementById('resultsSection');
    const assessmentSection = document.getElementById('assessmentSection');
    
    if (resultsSection) {
        resultsSection.classList.add('hidden');
    }
    
    if (assessmentSection) {
        assessmentSection.style.opacity = '1';
        assessmentSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Clear form data
    formData = {};
}

// ==================== Notifications ====================
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    
    const colors = {
        success: 'var(--success-color)',
        error: 'var(--danger-color)',
        warning: 'var(--warning-color)',
        info: 'var(--info-color)'
    };
    
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
    `;
    
    notification.innerHTML = `
        <i class="fas fa-${icons[type] || icons.info}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Add animation styles
const animationStyles = document.createElement('style');
animationStyles.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(animationStyles);