// Global state
let currentData = null;
let chatHistory = [];
let charts = {};

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupNavigation();
    setupEventListeners();
    loadPatientData();
});

// ==========================================
// INITIALIZATION
// ==========================================

function initializeDashboard() {
    console.log('🚀 Initializing dashboard...');
    
    // Get patient ID from URL or localStorage
    const urlParams = new URLSearchParams(window.location.search);
    const patientId = urlParams.get('patient_id') || localStorage.getItem('patient_id') || 'DEMO001';
    
    localStorage.setItem('patient_id', patientId);
    document.getElementById('patientId').textContent = patientId;
    
    // Initialize with demo data if no real data available
    if (!currentData) {
        loadDemoData();
    }
}

// ==========================================
// NAVIGATION
// ==========================================

function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all items
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Get target section
            const target = this.getAttribute('href').substring(1);
            
            // Hide all sections
            document.querySelectorAll('.dashboard-section').forEach(section => {
                section.classList.add('hidden');
            });
            
            // Show target section
            const targetSection = document.getElementById(target);
            if (targetSection) {
                targetSection.classList.remove('hidden');
                
                // Load section-specific content
                loadSectionContent(target);
            }
        });
    });
}

function loadSectionContent(section) {
    switch(section) {
        case 'overview':
            updateDashboardMetrics();
            break;
        case 'reports':
            loadReportsHistory();
            break;
        case 'trends':
            loadTrendsCharts();
            break;
        case 'chatbot':
            initializeChatbot();
            break;
        case 'recommendations':
            loadRecommendations();
            break;
    }
}

// ==========================================
// DATA LOADING
// ==========================================

async function loadPatientData() {
    const patientId = localStorage.getItem('patient_id');
    
    try {
        // Try to load latest assessment from backend
        const response = await fetch(`/api/patient-history/${patientId}`);
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.success && data.history && data.history.length > 0) {
                currentData = data.history[0];
                updateDashboardMetrics();
                createCharts();
            } else {
                loadDemoData();
            }
        } else {
            loadDemoData();
        }
    } catch (error) {
        console.error('Error loading patient data:', error);
        loadDemoData();
    }
}

function loadDemoData() {
    console.log('📊 Loading demo data...');
    
    currentData = {
        patient_name: 'John Doe',
        age: 45,
        sex: 'M',
        risk_level: 'Moderate Risk',
        lipid_values: {
            total_cholesterol: 220,
            ldl: 140,
            hdl: 45,
            triglycerides: 180,
            vldl: 36,
            non_hdl: 175,
            tc_hdl_ratio: 4.9,
            ldl_hdl_ratio: 3.1,
            tg_hdl_ratio: 4.0
        },
        timestamp: new Date().toISOString()
    };
    
    document.getElementById('userName').textContent = currentData.patient_name;
    updateDashboardMetrics();
    createCharts();
}

// ==========================================
// METRICS UPDATE
// ==========================================

function updateDashboardMetrics() {
    if (!currentData || !currentData.lipid_values) {
        console.warn('No data available to update metrics');
        return;
    }
    
    const lipids = currentData.lipid_values;
    
    // Update risk level
    const riskLevel = currentData.risk_level || 'Unknown';
    document.getElementById('riskLevel').textContent = riskLevel;
    
    const riskCard = document.querySelector('.risk-card .metric-value');
    if (riskCard) {
        riskCard.style.color = getRiskColor(riskLevel);
    }
    
    // Update lipid values
    document.getElementById('totalCholesterol').textContent = `${lipids.total_cholesterol} mg/dL`;
    document.getElementById('ldlValue').textContent = `${lipids.ldl} mg/dL`;
    document.getElementById('hdlValue').textContent = `${lipids.hdl} mg/dL`;
    document.getElementById('tgValue').textContent = `${lipids.triglycerides} mg/dL`;
    document.getElementById('ratioValue').textContent = lipids.tc_hdl_ratio?.toFixed(2) || 'N/A';
    
    // Update metric card styles based on values
    updateMetricCardStyles(lipids);
    
    // Create charts
    createCharts();
}

function updateMetricCardStyles(lipids) {
    // Total Cholesterol
    const tcCard = document.querySelector('.cholesterol-card .metric-value');
    if (tcCard) {
        tcCard.style.color = lipids.total_cholesterol > 200 ? 'var(--warning-color)' : 'var(--success-color)';
    }
    
    // LDL
    const ldlCard = document.querySelector('.ldl-card .metric-value');
    if (ldlCard) {
        ldlCard.style.color = lipids.ldl > 130 ? 'var(--danger-color)' : 'var(--success-color)';
    }
    
    // HDL
    const hdlCard = document.querySelector('.hdl-card .metric-value');
    if (hdlCard) {
        hdlCard.style.color = lipids.hdl < 40 ? 'var(--warning-color)' : 'var(--success-color)';
    }
    
    // Triglycerides
    const tgCard = document.querySelector('.triglycerides-card .metric-value');
    if (tgCard) {
        tgCard.style.color = lipids.triglycerides > 150 ? 'var(--warning-color)' : 'var(--success-color)';
    }
}

function getRiskColor(riskLevel) {
    const riskLower = riskLevel.toLowerCase();
    if (riskLower.includes('high')) return 'var(--danger-color)';
    if (riskLower.includes('moderate')) return 'var(--warning-color)';
    return 'var(--success-color)';
}

// ==========================================
// CHARTS CREATION
// ==========================================

function createCharts() {
    if (!currentData || !currentData.lipid_values) return;
    
    createRadarChart();
    createPieChart();
    createTrendChart();
}

function createRadarChart() {
    const ctx = document.getElementById('lipidRadarChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (charts.radar) {
        charts.radar.destroy();
    }
    
    const lipids = currentData.lipid_values;
    
    // Normalize values to 0-100 scale for better visualization
    const normalizeValue = (value, max) => (value / max) * 100;
    
    charts.radar = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Total Cholesterol', 'LDL', 'HDL', 'Triglycerides', 'VLDL', 'Non-HDL'],
            datasets: [{
                label: 'Current Values',
                data: [
                    normalizeValue(lipids.total_cholesterol, 300),
                    normalizeValue(lipids.ldl, 200),
                    normalizeValue(lipids.hdl, 100),
                    normalizeValue(lipids.triglycerides, 300),
                    normalizeValue(lipids.vldl || 0, 100),
                    normalizeValue(lipids.non_hdl || 0, 200)
                ],
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(99, 102, 241, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(99, 102, 241, 1)'
            }, {
                label: 'Optimal Range',
                data: [
                    normalizeValue(200, 300),
                    normalizeValue(100, 200),
                    normalizeValue(60, 100),
                    normalizeValue(150, 300),
                    normalizeValue(30, 100),
                    normalizeValue(130, 200)
                ],
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderColor: 'rgba(16, 185, 129, 0.5)',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#f1f5f9',
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.95)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#94a3b8',
                    borderColor: '#334155',
                    borderWidth: 1
                }
            },
            scales: {
                r: {
                    angleLines: { color: '#334155' },
                    grid: { color: '#334155' },
                    pointLabels: {
                        color: '#94a3b8',
                        font: { size: 11 }
                    },
                    ticks: {
                        color: '#94a3b8',
                        backdropColor: 'transparent'
                    }
                }
            }
        }
    });
}

function createPieChart() {
    const ctx = document.getElementById('riskPieChart');
    if (!ctx) return;
    
    if (charts.pie) {
        charts.pie.destroy();
    }
    
    // Mock probability data (replace with actual ML model output)
    const probabilities = {
        'Low Risk': 25,
        'Moderate Risk': 55,
        'High Risk': 20
    };
    
    charts.pie = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(probabilities),
            datasets: [{
                data: Object.values(probabilities),
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderColor: '#1e293b',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#f1f5f9',
                        padding: 15,
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.95)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#94a3b8',
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed + '%';
                        }
                    }
                }
            }
        }
    });
}

function createTrendChart() {
    const ctx = document.getElementById('trendLineChart');
    if (!ctx) return;
    
    if (charts.trend) {
        charts.trend.destroy();
    }
    
    // Mock historical data (replace with actual data from backend)
    const dates = generatePastDates(6);
    const lipids = currentData.lipid_values;
    
    charts.trend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Total Cholesterol',
                    data: generateTrendData(lipids.total_cholesterol, 6, 20),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'LDL',
                    data: generateTrendData(lipids.ldl, 6, 15),
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'HDL',
                    data: generateTrendData(lipids.hdl, 6, 10),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Triglycerides',
                    data: generateTrendData(lipids.triglycerides, 6, 25),
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.95)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#94a3b8',
                    borderColor: '#334155',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { color: '#334155' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    grid: { color: '#334155' },
                    ticks: { color: '#94a3b8' },
                    beginAtZero: true
                }
            }
        }
    });
}

// ==========================================
// HELPER FUNCTIONS
// ==========================================

function generatePastDates(months) {
    const dates = [];
    const today = new Date();
    
    for (let i = months; i >= 0; i--) {
        const date = new Date(today);
        date.setMonth(date.getMonth() - i);
        dates.push(date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }));
    }
    
    return dates;
}

function generateTrendData(currentValue, points, variance) {
    const data = [];
    
    for (let i = 0; i < points; i++) {
        const randomChange = (Math.random() - 0.5) * variance;
        const trendValue = currentValue - (points - i) * 5 + randomChange;
        data.push(Math.max(0, trendValue));
    }
    
    data.push(currentValue);
    return data;
}

// ==========================================
// CHATBOT FUNCTIONALITY
// ==========================================

function initializeChatbot() {
    console.log('🤖 Initializing chatbot...');
    
    if (chatHistory.length === 0) {
        // Add welcome message if not already added
        addBotMessage("Hello! I'm your AI health assistant. I can help you understand your lipid profile results, provide lifestyle recommendations, and answer questions about cardiovascular health. How can I assist you today?");
    }
}

function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    addUserMessage(message);
    input.value = '';
    
    // Process message and generate response
    setTimeout(() => {
        const response = generateChatbotResponse(message);
        addBotMessage(response);
    }, 500);
}

function askQuestion(question) {
    document.getElementById('chatInput').value = question;
    sendMessage();
}

function addUserMessage(message) {
    const chatMessages = document.getElementById('chatMessages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message user';
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-user"></i>
        </div>
        <div class="message-content">
            <p>${escapeHtml(message)}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    chatHistory.push({ role: 'user', message });
}

function addBotMessage(message) {
    const chatMessages = document.getElementById('chatMessages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message bot';
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <p>${message}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    chatHistory.push({ role: 'bot', message });
}

function generateChatbotResponse(userMessage) {
    const messageLower = userMessage.toLowerCase();
    
    if (!currentData || !currentData.lipid_values) {
        return "I don't have access to your lipid profile data yet. Please upload your medical report first.";
    }
    
    const lipids = currentData.lipid_values;
    const risk = currentData.risk_level || 'Unknown';
    
    // Risk level query
    if (messageLower.includes('risk level') || messageLower.includes('my risk')) {
        return `Based on your lipid profile, your current cardiovascular risk level is <strong>${risk}</strong>. ${getRiskExplanation(risk)}`;
    }
    
    // Cholesterol lowering
    if (messageLower.includes('lower cholesterol') || messageLower.includes('reduce cholesterol')) {
        return `Here are evidence-based ways to lower your cholesterol:
        <br><br>
        <strong>1. Dietary Changes:</strong>
        <ul>
            <li>Reduce saturated fats (red meat, full-fat dairy)</li>
            <li>Eliminate trans fats (fried foods, processed snacks)</li>
            <li>Increase soluble fiber (oats, beans, fruits)</li>
            <li>Add omega-3 fatty acids (fish, walnuts, flaxseed)</li>
        </ul>
        <strong>2. Lifestyle:</strong>
        <ul>
            <li>Exercise 30 minutes daily</li>
            <li>Maintain healthy weight</li>
            <li>Quit smoking</li>
            <li>Limit alcohol</li>
        </ul>
        Your LDL is currently ${lipids.ldl} mg/dL. Aim to get it below 100 mg/dL.`;
    }
    
    // Foods to avoid
    if (messageLower.includes('foods') && (messageLower.includes('avoid') || messageLower.includes('bad'))) {
        return `<strong>Foods to Avoid for Better Cholesterol:</strong>
        <br><br>
        ❌ <strong>Red meat</strong> - High in saturated fat
        <br>❌ <strong>Full-fat dairy</strong> - Butter, cheese, whole milk
        <br>❌ <strong>Fried foods</strong> - Trans fats damage arteries
        <br>❌ <strong>Processed meats</strong> - Bacon, sausage, deli meats
        <br>❌ <strong>Baked goods</strong> - Cookies, cakes, pastries
        <br>❌ <strong>Hydrogenated oils</strong> - Check labels!
        <br><br>
        ✅ <strong>Instead, eat:</strong> Vegetables, fruits, whole grains, lean proteins, nuts, and fish.`;
    }
    
    // Explain results
    if (messageLower.includes('explain') && (messageLower.includes('result') || messageLower.includes('profile'))) {
        return `<strong>Your Lipid Profile Breakdown:</strong>
        <br><br>
        📊 <strong>Total Cholesterol:</strong> ${lipids.total_cholesterol} mg/dL ${lipids.total_cholesterol > 200 ? '(High - should be <200)' : '(Normal)'}
        <br>🔴 <strong>LDL (Bad):</strong> ${lipids.ldl} mg/dL ${lipids.ldl > 130 ? '(High - should be <100)' : '(Good)'}
        <br>🟢 <strong>HDL (Good):</strong> ${lipids.hdl} mg/dL ${lipids.hdl < 40 ? '(Low - should be >60)' : '(Good)'}
        <br>💧 <strong>Triglycerides:</strong> ${lipids.triglycerides} mg/dL ${lipids.triglycerides > 150 ? '(High - should be <150)' : '(Normal)'}
        <br>⚖️ <strong>TC/HDL Ratio:</strong> ${lipids.tc_hdl_ratio?.toFixed(2)} ${lipids.tc_hdl_ratio > 5 ? '(High - should be <5)' : '(Good)'}
        <br><br>
        ${risk.includes('High') ? 'Your results indicate elevated cardiovascular risk. Please consult your doctor about treatment options.' : 
          risk.includes('Moderate') ? 'Your results show moderate risk. Focus on lifestyle changes to improve your numbers.' :
          'Your results look good! Maintain a healthy lifestyle.'}`;
    }
    
    // HDL information
    if (messageLower.includes('hdl')) {
        return `HDL is "good cholesterol" that helps remove LDL from your arteries. Your HDL is ${lipids.hdl} mg/dL.
        <br><br>
        ${lipids.hdl < 40 ? '⚠️ This is LOW. To increase HDL:' : '✅ This is good! To maintain it:'}
        <ul>
            <li>Exercise regularly (30+ min/day)</li>
            <li>Eat healthy fats (olive oil, avocados, nuts)</li>
            <li>Quit smoking (smoking lowers HDL)</li>
            <li>Lose excess weight</li>
            <li>Choose whole grains over refined carbs</li>
        </ul>`;
    }
    
    // LDL information
    if (messageLower.includes('ldl')) {
        return `LDL is "bad cholesterol" that builds up in your arteries. Your LDL is ${lipids.ldl} mg/dL.
        <br><br>
        ${lipids.ldl > 130 ? '⚠️ This is HIGH. Target: <100 mg/dL' : '✅ This is in a good range!'}
        <br><br>
        To lower LDL:
        <ul>
            <li>Reduce saturated fat intake</li>
            <li>Eat more plant-based foods</li>
            <li>Add soluble fiber (oats, beans)</li>
            <li>Exercise regularly</li>
            <li>Consider medication if lifestyle changes aren't enough</li>
        </ul>`;
    }
    
    // Triglycerides
    if (messageLower.includes('triglycerides')) {
        return `Triglycerides are a type of fat in your blood. Your level is ${lipids.triglycerides} mg/dL.
        <br><br>
        ${lipids.triglycerides > 150 ? '⚠️ This is HIGH. Target: <150 mg/dL' : '✅ This is normal!'}
        <br><br>
        To lower triglycerides:
        <ul>
            <li>Limit sugar and refined carbs</li>
            <li>Reduce alcohol consumption</li>
            <li>Eat more omega-3s (fish)</li>
            <li>Exercise regularly</li>
            <li>Lose excess weight</li>
        </ul>`;
    }
    
    // Exercise
    if (messageLower.includes('exercise') || messageLower.includes('workout')) {
        return `<strong>Exercise Recommendations for Heart Health:</strong>
        <br><br>
        🏃 <strong>Aerobic Exercise:</strong> 30 minutes, 5+ days/week
        <br>• Brisk walking, jogging, cycling, swimming
        <br><br>
        💪 <strong>Strength Training:</strong> 2-3 days/week
        <br>• Helps improve metabolism and weight management
        <br><br>
        🧘 <strong>Flexibility:</strong> Daily stretching
        <br>• Yoga, tai chi for stress reduction
        <br><br>
        Start slowly and gradually increase intensity. Consult your doctor before starting a new exercise program.`;
    }
    
    // Default response
    return `I understand you're asking about "${userMessage}". 
    <br><br>
    I can help you with:
    <ul>
        <li>Understanding your lipid profile results</li>
        <li>Explaining your risk level</li>
        <li>Dietary recommendations</li>
        <li>Exercise suggestions</li>
        <li>Lifestyle modifications</li>
    </ul>
    <br>
    Try asking: "What is my risk level?" or "How can I lower my cholesterol?"`;
}

function getRiskExplanation(risk) {
    if (risk.toLowerCase().includes('high')) {
        return 'This indicates elevated cardiovascular risk. Please consult your healthcare provider about treatment options, which may include lifestyle changes and medication.';
    } else if (risk.toLowerCase().includes('moderate')) {
        return 'This indicates some cardiovascular risk. Focus on lifestyle modifications like diet, exercise, and stress management. Regular monitoring is recommended.';
    }
    return 'This is a healthy range! Continue maintaining a healthy lifestyle to keep your heart healthy.';
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ==========================================
// REPORTS HISTORY
// ==========================================

async function loadReportsHistory() {
    const patientId = localStorage.getItem('patient_id');
    const reportsList = document.getElementById('reportsList');
    
    try {
        const response = await fetch(`/api/patient-history/${patientId}`);
        const data = await response.json();
        
        if (data.success && data.history && data.history.length > 0) {
            reportsList.innerHTML = '';
            
            data.history.forEach((report, index) => {
                const reportCard = createReportCard(report, index);
                reportsList.appendChild(reportCard);
            });
        }
    } catch (error) {
        console.error('Error loading reports:', error);
    }
}

function createReportCard(report, index) {
    const card = document.createElement('div');
    card.className = 'report-card';
    
    const date = new Date(report.timestamp).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    card.innerHTML = `
        <div class="report-header">
            <h3>Report #${index + 1}</h3>
            <span class="report-date">${date}</span>
        </div>
        <div class="report-body">
            <div class="report-metric">
                <span>Risk Level:</span>
                <strong style="color: ${getRiskColor(report.risk_level)}">${report.risk_level}</strong>
            </div>
            <div class="report-values">
                <div>TC: ${report.lipid_values?.total_cholesterol || 'N/A'}</div>
                <div>LDL: ${report.lipid_values?.ldl || 'N/A'}</div>
                <div>HDL: ${report.lipid_values?.hdl || 'N/A'}</div>
                <div>TG: ${report.lipid_values?.triglycerides || 'N/A'}</div>
            </div>
        </div>
        <button class="btn-view-report" onclick="viewReport(${index})">View Details</button>
    `;
    
    return card;
}

// ==========================================
// RECOMMENDATIONS
// ==========================================

function loadRecommendations() {
    const grid = document.getElementById('recommendationsGrid');
    
    if (!currentData) {
        grid.innerHTML = '<div class="empty-state"><p>No data available for recommendations</p></div>';
        return;
    }
    
    const recommendations = generateRecommendations();
    grid.innerHTML = '';
    
    recommendations.forEach(rec => {
        const card = createRecommendationCard(rec);
        grid.appendChild(card);
    });
}

function generateRecommendations() {
    const lipids = currentData.lipid_values;
    const recommendations = [];
    
    // Dietary recommendations
    recommendations.push({
        icon: 'fa-utensils',
        title: 'Dietary Changes',
        color: 'var(--success-color)',
        items: [
            'Increase fiber intake (oats, beans, fruits)',
            'Choose lean proteins (fish, poultry)',
            'Eat more vegetables and whole grains',
            'Limit saturated and trans fats',
            'Add omega-3 rich foods (salmon, walnuts)'
        ]
    });
    
    // Exercise recommendations
    recommendations.push({
        icon: 'fa-running',
        title: 'Physical Activity',
        color: 'var(--info-color)',
        items: [
            'Aim for 150 min/week of moderate exercise',
            'Include both cardio and strength training',
            'Start with 10-minute walks if needed',
            'Find activities you enjoy',
            'Stay consistent - schedule it!'
        ]
    });
    
    // Lifestyle modifications
    recommendations.push({
        icon: 'fa-heart',
        title: 'Lifestyle Modifications',
        color: 'var(--warning-color)',
        items: [
            'Quit smoking if applicable',
            'Limit alcohol consumption',
            'Manage stress (meditation, yoga)',
            'Maintain healthy weight',
            'Get 7-9 hours of sleep nightly'
        ]
    });
    
    // Monitoring
    recommendations.push({
        icon: 'fa-clipboard-check',
        title: 'Regular Monitoring',
        color: 'var(--secondary-color)',
        items: [
            'Check lipids every 3-6 months',
            'Monitor blood pressure regularly',
            'Keep a health diary',
            'Schedule regular doctor visits',
            'Track your progress'
        ]
    });
    
    return recommendations;
}

function createRecommendationCard(rec) {
    const card = document.createElement('div');
    card.className = 'recommendation-card';
    
    card.innerHTML = `
        <div class="rec-header">
            <div class="rec-icon" style="color: ${rec.color}">
                <i class="fas ${rec.icon}"></i>
            </div>
            <h3>${rec.title}</h3>
        </div>
        <ul class="rec-list">
            ${rec.items.map(item => `<li>${item}</li>`).join('')}
        </ul>
    `;
    
    return card;
}

// ==========================================
// EVENT LISTENERS
// ==========================================

function setupEventListeners() {
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }
    
    // Date filter
    const dateFilter = document.getElementById('dateFilter');
    if (dateFilter) {
        dateFilter.addEventListener('change', handleDateFilterChange);
    }
}

function handleSearch(e) {
    const query = e.target.value.toLowerCase();
    console.log('Searching for:', query);
    // Implement search functionality
}

function handleDateFilterChange(e) {
    const days = e.target.value;
    console.log('Filter changed to:', days, 'days');
    // Implement date filtering
}

function toggleChat() {
    // Navigate to chatbot section
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.getAttribute('href') === '#chatbot') {
            item.click();
        }
    });
}

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

function viewReport(index) {
    console.log('Viewing report:', index);
    // Implement report viewing functionality
}

function downloadChart(chartId) {
    const canvas = document.getElementById(chartId);
    if (canvas) {
        const url = canvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = url;
        a.download = `${chartId}_${new Date().toISOString()}.png`;
        a.click();
    }
}

console.log('✅ Dashboard JavaScript loaded successfully');