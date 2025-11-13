// ==================== Global State ====================
let currentMonth = new Date().getMonth();
let currentYear = new Date().getFullYear();
let progressData = JSON.parse(localStorage.getItem('progressData')) || {};
let currentStreak = 0;
let totalActiveDays = 0;

// ==================== Tab Management ====================
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeCalendar();
    initializeCharts();
    loadProgressData();
    calculateStats();
    loadPatientData();
});

function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');

            // Remove active class from all buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));

            // Add active class to clicked button and corresponding pane
            button.classList.add('active');
            document.getElementById(targetTab).classList.add('active');

            // Trigger animations or updates for specific tabs
            if (targetTab === 'calendar') {
                renderCalendar();
            }
        });
    });
}

// ==================== Patient Data Loading ====================
function loadPatientData() {
    // Get data from URL parameters or localStorage
    const urlParams = new URLSearchParams(window.location.search);
    const patientData = {
        id: urlParams.get('id') || 'PT0001',
        name: urlParams.get('name') || 'John Doe',
        age: urlParams.get('age') || '45',
        gender: urlParams.get('gender') || 'Male',
        tc: parseFloat(urlParams.get('tc')) || 220,
        ldl: parseFloat(urlParams.get('ldl')) || 140,
        hdl: parseFloat(urlParams.get('hdl')) || 45,
        tg: parseFloat(urlParams.get('tg')) || 180,
        risk: urlParams.get('risk') || 'Moderate Risk'
    };

    // Update patient info
    document.getElementById('patientId').textContent = patientData.id;
    document.getElementById('patientName').textContent = patientData.name;
    document.getElementById('patientAge').textContent = `${patientData.age} years`;
    document.getElementById('patientGender').textContent = patientData.gender;
    document.getElementById('reportDate').textContent = new Date().toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    // Update risk level
    updateRiskLevel(patientData.risk);

    // Update lipid values
    updateLipidValues(patientData);
}

function updateRiskLevel(risk) {
    const riskBadge = document.getElementById('riskBadge');
    const riskLevel = document.getElementById('riskLevel');
    
    riskLevel.textContent = risk;

    // Update colors based on risk level
    const riskValue = document.querySelector('.risk-value');
    if (risk.toLowerCase().includes('high')) {
        riskValue.style.color = '#ef4444';
        riskBadge.querySelector('.risk-icon').textContent = '🔴';
        riskBadge.style.borderColor = '#ef4444';
    } else if (risk.toLowerCase().includes('moderate')) {
        riskValue.style.color = '#f59e0b';
        riskBadge.querySelector('.risk-icon').textContent = '⚠️';
        riskBadge.style.borderColor = '#f59e0b';
    } else {
        riskValue.style.color = '#10b981';
        riskBadge.querySelector('.risk-icon').textContent = '✅';
        riskBadge.style.borderColor = '#10b981';
    }
}

function updateLipidValues(data) {
    // Calculate derived values
    const vldl = data.tg / 5;
    const nonHdl = data.tc - data.hdl;
    const tcHdlRatio = data.tc / data.hdl;

    // Update display values
    document.getElementById('tcValue').textContent = `${data.tc} mg/dL`;
    document.getElementById('ldlValue').textContent = `${data.ldl} mg/dL`;
    document.getElementById('hdlValue').textContent = `${data.hdl} mg/dL`;
    document.getElementById('tgValue').textContent = `${data.tg} mg/dL`;
    document.getElementById('ratioValue').textContent = tcHdlRatio.toFixed(1);
    document.getElementById('nonHdlValue').textContent = `${nonHdl.toFixed(1)} mg/dL`;

    // Update interpretation
    updateInterpretation(data);
}

function updateInterpretation(data) {
    const tcAbove = Math.max(0, data.tc - 200);
    const ldlAbove = Math.max(0, data.ldl - 100);
    const hdlBelow = Math.max(0, 60 - data.hdl);
    const tgAbove = Math.max(0, data.tg - 150);

    const interpretationText = `
        <p><strong>Summary:</strong> Your lipid profile indicates <span class="highlight">${data.risk.toLowerCase()}</span>. ${data.ldl > 130 ? 'Your LDL cholesterol and total cholesterol levels are elevated, which increases your risk of heart disease and stroke.' : 'Your lipid levels show room for improvement.'}</p>
        
        <p><strong>Key Findings:</strong></p>
        <ul>
            <li>Total cholesterol is <strong>${data.tc} mg/dL</strong> ${tcAbove > 0 ? `(${tcAbove} mg/dL above optimal)` : '(within optimal range)'}</li>
            <li>LDL cholesterol is <strong>${data.ldl} mg/dL</strong> ${ldlAbove > 0 ? `(${ldlAbove} mg/dL above optimal)` : '(within optimal range)'}</li>
            <li>HDL cholesterol is <strong>${data.hdl} mg/dL</strong> ${hdlBelow > 0 ? `(${hdlBelow} mg/dL below optimal)` : '(within optimal range)'}</li>
            <li>Triglycerides are <strong>${data.tg} mg/dL</strong> ${tgAbove > 0 ? `(${tgAbove} mg/dL above normal)` : '(within normal range)'}</li>
        </ul>

        <p><strong>Recommendations:</strong> Lifestyle modifications are strongly recommended, including dietary changes, regular exercise, and weight management. Follow-up lipid panel in 3 months to assess progress.</p>
    `;

    document.getElementById('interpretationText').innerHTML = interpretationText;
}

// ==================== Charts Initialization ====================
function initializeCharts() {
    createRiskChart();
}

function createRiskChart() {
    const ctx = document.getElementById('riskChart');
    if (!ctx) return;

    const urlParams = new URLSearchParams(window.location.search);
    const tc = parseFloat(urlParams.get('tc')) || 220;
    const ldl = parseFloat(urlParams.get('ldl')) || 140;
    const hdl = parseFloat(urlParams.get('hdl')) || 45;
    const tg = parseFloat(urlParams.get('tg')) || 180;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Total Cholesterol Risk', 'LDL Risk', 'HDL Protection', 'Triglyceride Risk'],
            datasets: [{
                data: [
                    calculateRiskScore(tc, 200, 240),
                    calculateRiskScore(ldl, 100, 160),
                    100 - calculateRiskScore(hdl, 40, 60, true),
                    calculateRiskScore(tg, 150, 200)
                ],
                backgroundColor: [
                    '#ef4444',
                    '#f59e0b',
                    '#10b981',
                    '#6366f1'
                ],
                borderWidth: 2,
                borderColor: '#1e293b'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#f1f5f9',
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
}

function calculateRiskScore(value, optimal, high, inverse = false) {
    if (inverse) {
        // For HDL, higher is better
        if (value >= high) return 100;
        if (value <= optimal) return 0;
        return ((value - optimal) / (high - optimal)) * 100;
    } else {
        // For others, lower is better
        if (value <= optimal) return 0;
        if (value >= high) return 100;
        return ((value - optimal) / (high - optimal)) * 100;
    }
}

// ==================== Calendar Functions ====================
function initializeCalendar() {
    renderCalendar();
}

function renderCalendar() {
    const calendarGrid = document.getElementById('calendarGrid');
    if (!calendarGrid) return;

    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    const today = new Date();

    // Update month display
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'];
    document.getElementById('calendarMonth').textContent = `${monthNames[currentMonth]} ${currentYear}`;

    // Clear calendar
    calendarGrid.innerHTML = '';

    // Add day headers
    const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    dayHeaders.forEach(day => {
        const dayEl = document.createElement('div');
        dayEl.className = 'calendar-day header';
        dayEl.textContent = day;
        calendarGrid.appendChild(dayEl);
    });

    // Add empty cells before first day
    for (let i = 0; i < firstDay; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'calendar-day empty';
        calendarGrid.appendChild(emptyDay);
    }

    // Add days
    for (let day = 1; day <= daysInMonth; day++) {
        const dayEl = document.createElement('div');
        dayEl.className = 'calendar-day';
        dayEl.textContent = day;

        const dateKey = `${currentYear}-${currentMonth + 1}-${day}`;
        
        // Mark today
        if (day === today.getDate() && 
            currentMonth === today.getMonth() && 
            currentYear === today.getFullYear()) {
            dayEl.classList.add('today');
        }

        // Add progress status
        if (progressData[dateKey]) {
            const completion = calculateDayCompletion(progressData[dateKey]);
            if (completion === 100) {
                dayEl.classList.add('completed');
            } else if (completion > 0) {
                dayEl.classList.add('partial');
            }
        } else if (new Date(currentYear, currentMonth, day) < today) {
            dayEl.classList.add('missed');
        }

        dayEl.addEventListener('click', () => showDayDetails(dateKey));
        calendarGrid.appendChild(dayEl);
    }
}

function calculateDayCompletion(dayData) {
    if (!dayData) return 0;
    const tasks = ['diet', 'exercise', 'water', 'medication', 'stress'];
    const completedTasks = tasks.filter(task => dayData[task]).length;
    return (completedTasks / tasks.length) * 100;
}

function showDayDetails(dateKey) {
    const data = progressData[dateKey];
    if (!data) {
        alert(`No data recorded for ${dateKey}`);
        return;
    }

    const completion = calculateDayCompletion(data);
    alert(`Progress for ${dateKey}:\n\nCompletion: ${completion}%\n\nTasks completed:\n${
        Object.entries(data)
            .map(([task, done]) => `${task}: ${done ? '✓' : '✗'}`)
            .join('\n')
    }`);
}

function previousMonth() {
    currentMonth--;
    if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
    }
    renderCalendar();
}

function nextMonth() {
    currentMonth++;
    if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
    }
    renderCalendar();
}

// ==================== Progress Tracking ====================
async function saveProgress() {
    const today = new Date();
    const dateKey = `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`;

    const tasks = {
        diet: document.getElementById('task_diet').checked,
        exercise: document.getElementById('task_exercise').checked,
        water: document.getElementById('task_water').checked,
        medication: document.getElementById('task_medication').checked,
        stress: document.getElementById('task_stress').checked
    };

    // Save locally
    progressData[dateKey] = tasks;
    localStorage.setItem('progressData', JSON.stringify(progressData));

    // Get patient ID from URL or localStorage
    const urlParams = new URLSearchParams(window.location.search);
    const patientId = urlParams.get('id') || localStorage.getItem('patientId') || 'default_user';

    // Sync with backend
    try {
        const response = await fetch('/api/log-activity', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                patient_id: patientId,
                date: dateKey,
                diet_followed: tasks.diet ? 1 : 0,
                exercise_completed: tasks.exercise ? 1 : 0,
                medication_taken: tasks.medication ? 1 : 0,
                water_intake_met: tasks.water ? 1 : 0,
                sleep_quality: 7,  // You can add a slider for this
                stress_level: tasks.stress ? 3 : 7,  // Lower is better
                notes: ''
            })
        });

        const result = await response.json();
        
        if (result.success) {
            calculateStats();
            renderCalendar();
            checkBadges();
            
            // Update streak display
            if (result.current_streak) {
                document.getElementById('currentStreak').textContent = result.current_streak;
            }
            
            showNotification(`Progress saved! Current streak: ${result.current_streak} days 🎉`, 'success');
        }
    } catch (error) {
        console.error('Failed to sync with server:', error);
        showNotification('Saved locally. Will sync when online.', 'warning');
    }
}

function loadProgressData() {
    const today = new Date();
    const dateKey = `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`;

    if (progressData[dateKey]) {
        const tasks = progressData[dateKey];
        document.getElementById('task_diet').checked = tasks.diet || false;
        document.getElementById('task_exercise').checked = tasks.exercise || false;
        document.getElementById('task_water').checked = tasks.water || false;
        document.getElementById('task_medication').checked = tasks.medication || false;
        document.getElementById('task_stress').checked = tasks.stress || false;
    }

    // Add event listeners for auto-save
    const checkboxes = document.querySelectorAll('.checklist-item input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const today = new Date();
            const dateKey = `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`;
            
            if (!progressData[dateKey]) {
                progressData[dateKey] = {};
            }
            
            const taskId = checkbox.id.replace('task_', '');
            progressData[dateKey][taskId] = checkbox.checked;
            
            localStorage.setItem('progressData', JSON.stringify(progressData));
            calculateStats();
        });
    });
}

function calculateStats() {
    // Calculate current streak
    currentStreak = 0;
    const today = new Date();
    let checkDate = new Date(today);

    while (true) {
        const dateKey = `${checkDate.getFullYear()}-${checkDate.getMonth() + 1}-${checkDate.getDate()}`;
        if (progressData[dateKey] && calculateDayCompletion(progressData[dateKey]) === 100) {
            currentStreak++;
            checkDate.setDate(checkDate.getDate() - 1);
        } else {
            break;
        }
    }

    // Calculate total active days
    totalActiveDays = Object.values(progressData).filter(day => 
        calculateDayCompletion(day) > 0
    ).length;

    // Calculate adherence rate
    const totalDays = Object.keys(progressData).length;
    const adherenceRate = totalDays > 0 ? (totalActiveDays / totalDays * 100).toFixed(0) : 0;

    // Update UI
    document.getElementById('currentStreak').textContent = currentStreak;
    document.getElementById('totalDays').textContent = totalActiveDays;
    document.getElementById('adherenceRate').textContent = `${adherenceRate}%`;

    // Update badges count
    updateBadgesCount();
}

function updateBadgesCount() {
    const badgesGrid = document.getElementById('badgesGrid');
    let unlockedCount = 0;

    // Check 7-Day Streak
    if (currentStreak >= 7) {
        badgesGrid.children[0].classList.remove('locked');
        badgesGrid.children[0].classList.add('unlocked');
        badgesGrid.children[0].querySelector('i').className = 'fas fa-fire';
        unlockedCount++;
    }

    // Check 30-Day Warrior
    if (totalActiveDays >= 30) {
        badgesGrid.children[1].classList.remove('locked');
        badgesGrid.children[1].classList.add('unlocked');
        badgesGrid.children[1].querySelector('i').className = 'fas fa-trophy';
        unlockedCount++;
    }

    // Check Perfect Week
    if (checkPerfectWeek()) {
        badgesGrid.children[2].classList.remove('locked');
        badgesGrid.children[2].classList.add('unlocked');
        badgesGrid.children[2].querySelector('i').className = 'fas fa-star';
        unlockedCount++;
    }

    // Check Hydration Hero
    if (checkHydrationStreak()) {
        badgesGrid.children[3].classList.remove('locked');
        badgesGrid.children[3].classList.add('unlocked');
        badgesGrid.children[3].querySelector('i').className = 'fas fa-tint';
        unlockedCount++;
    }

    document.getElementById('badges').textContent = unlockedCount;
}

function checkPerfectWeek() {
    const today = new Date();
    for (let i = 0; i < 7; i++) {
        const checkDate = new Date(today);
        checkDate.setDate(today.getDate() - i);
        const dateKey = `${checkDate.getFullYear()}-${checkDate.getMonth() + 1}-${checkDate.getDate()}`;
        
        if (!progressData[dateKey] || calculateDayCompletion(progressData[dateKey]) !== 100) {
            return false;
        }
    }
    return true;
}

function checkHydrationStreak() {
    let streak = 0;
    const today = new Date();
    
    for (let i = 0; i < 14; i++) {
        const checkDate = new Date(today);
        checkDate.setDate(today.getDate() - i);
        const dateKey = `${checkDate.getFullYear()}-${checkDate.getMonth() + 1}-${checkDate.getDate()}`;
        
        if (progressData[dateKey] && progressData[dateKey].water) {
            streak++;
        } else {
            break;
        }
    }
    
    return streak >= 14;
}

function checkBadges() {
    const newBadges = [];
    
    if (currentStreak === 7) {
        newBadges.push('🔥 7-Day Streak unlocked!');
    }
    if (totalActiveDays === 30) {
        newBadges.push('🏆 30-Day Warrior unlocked!');
    }
    if (checkPerfectWeek()) {
        newBadges.push('⭐ Perfect Week unlocked!');
    }
    
    if (newBadges.length > 0) {
        showNotification(newBadges.join('\n'), 'success');
    }
}

// ==================== Utility Functions ====================
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : '#6366f1'};
        color: white;
        padding: 1rem 2rem;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function downloadPDF() {
    window.print();
}

function viewFullReport() {
    // Scroll to top and show all tabs
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function viewDashboard() {
    window.location.href = '/dashboard';
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
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
document.head.appendChild(style);

// Initialize checklist event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadProgressData();
    loadAdherenceAnalytics();
});

// Load adherence analytics from backend
async function loadAdherenceAnalytics() {
    const urlParams = new URLSearchParams(window.location.search);
    const patientId = urlParams.get('id') || localStorage.getItem('patientId') || 'default_user';
    
    try {
        const response = await fetch(`/api/adherence-score/${patientId}?days=30`);
        const data = await response.json();
        
        if (data.success && data.adherence_score) {
            // Update UI with backend data
            document.getElementById('adherenceRate').textContent = 
                `${Math.round(data.adherence_score.overall_score)}%`;
            
            document.getElementById('currentStreak').textContent = data.current_streak;
            
            // Show risk warning if needed
            if (data.risk_analysis && data.risk_analysis.risk === 'high') {
                showNotification(data.risk_analysis.recommendation, 'warning');
            }
            
            // Update detailed scores
            updateDetailedScores(data.adherence_score);
        }
    } catch (error) {
        console.error('Failed to load adherence analytics:', error);
    }
}

function updateDetailedScores(scores) {
    // Add a detailed scores section to your report.html
    const detailedScoresHTML = `
        <div class="detailed-scores">
            <h3><i class="fas fa-chart-bar"></i> Detailed Adherence Metrics</h3>
            <div class="score-grid">
                <div class="score-card">
                    <h4>Diet</h4>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${scores.diet_score}%"></div>
                    </div>
                    <p>${Math.round(scores.diet_score)}%</p>
                </div>
                <div class="score-card">
                    <h4>Exercise</h4>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${scores.exercise_score}%"></div>
                    </div>
                    <p>${Math.round(scores.exercise_score)}%</p>
                </div>
                <div class="score-card">
                    <h4>Medication</h4>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${scores.medication_score}%"></div>
                    </div>
                    <p>${Math.round(scores.medication_score)}%</p>
                </div>
            </div>
        </div>
    `;
    
    // Insert into appropriate location
    const container = document.getElementById('adherenceDetails');
    if (container) {
        container.innerHTML = detailedScoresHTML;
    }
}