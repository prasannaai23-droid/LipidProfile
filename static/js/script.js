const API_URL = 'http://localhost:5000/api';

// Form submission handler
document.getElementById('lipidForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show loading
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    
    const formData = new FormData(e.target);
    
    // Build data object
    const data = {
        patient_id: formData.get('patient_id'),
        age: parseInt(formData.get('age')),
        gender: formData.get('gender'),
        bmi: parseFloat(formData.get('bmi')) || 25,
        total_cholesterol: parseFloat(formData.get('total_cholesterol')),
        ldl: parseFloat(formData.get('ldl')),
        hdl: parseFloat(formData.get('hdl')),
        triglycerides: parseFloat(formData.get('triglycerides')),
        blood_glucose: parseFloat(formData.get('blood_glucose')),
        smoking: formData.get('smoking') === 'on',
        family_history: formData.get('family_history') === 'on',
        chest_pain: formData.get('chest_pain') === 'on',
        existing_conditions: []
    };
    
    // Add existing conditions
    if (formData.get('hypertension') === 'on') {
        data.existing_conditions.push('hypertension');
    }
    if (formData.get('diabetes') === 'on') {
        data.existing_conditions.push('diabetes');
    }
    
    try {
        const response = await fetch(`${API_URL}/analyze-lipid-profile`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        // Hide loading
        document.getElementById('loading').classList.add('hidden');
        
        if (result.success) {
            displayResults(result);
            
            // Store patient data
            localStorage.setItem('currentPatient', data.patient_id);
            localStorage.setItem('latestAssessment', JSON.stringify(result));
            localStorage.setItem('lifestylePlan', JSON.stringify(result.lifestyle_plan));
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        document.getElementById('loading').classList.add('hidden');
        alert('Connection error: ' + error.message);
        console.error('Error:', error);
    }
});

function displayResults(result) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.classList.remove('hidden');
    
    // Risk Level Badge
    const riskLevel = document.getElementById('riskLevel');
    riskLevel.className = `risk-badge risk-${result.risk_analysis.risk_level}`;
    riskLevel.innerHTML = `
        ${getRiskIcon(result.risk_analysis.risk_level)} 
        Risk Level: ${result.risk_analysis.risk_level.toUpperCase()}
        <span style="font-size: 0.8em; display: block; margin-top: 5px;">
            Risk Score: ${result.risk_analysis.risk_score}/1.0
        </span>
    `;
    
    // Interpretation
    const interpretationBox = document.getElementById('interpretation');
    interpretationBox.innerHTML = `
        <h3>📋 Clinical Interpretation</h3>
        <div class="interpretation-text">
            ${result.risk_analysis.interpretation.replace(/\n/g, '<br>')}
        </div>
        
        <div class="lipid-status">
            <h4>Your Lipid Panel Status:</h4>
            <ul>
                <li><strong>LDL Cholesterol:</strong> ${result.risk_analysis.ldl_status}</li>
                <li><strong>HDL Cholesterol:</strong> ${result.risk_analysis.hdl_status}</li>
                <li><strong>Triglycerides:</strong> ${result.risk_analysis.triglyceride_status}</li>
                <li><strong>Blood Glucose:</strong> ${result.risk_analysis.glucose_status}</li>
            </ul>
        </div>
        
        <div class="critical-factors">
            <h4>⚠️ Critical Risk Factors:</h4>
            <ul>
                ${result.risk_analysis.critical_factors.map(f => `<li>${f}</li>`).join('')}
            </ul>
        </div>
        
        <div class="atherosclerosis-risk">
            <h4>🫀 Atherosclerosis Risk Assessment:</h4>
            <p>${result.risk_analysis.atherosclerosis_risk}</p>
        </div>
    `;
    
    // Management Type
    const managementDiv = document.getElementById('management');
    managementDiv.innerHTML = `
        <h3>💊 Recommended Management Approach</h3>
        <div class="management-card">
            <h4>${result.management_type.primary.replace('_', ' ').toUpperCase()}</h4>
            <p class="management-message">${result.management_type.message}</p>
            
            ${result.management_type.requires_statin ? 
                '<div class="alert-box alert-warning"><strong>⚠️ Statin Therapy Recommended</strong><br>Discuss with your physician about starting cholesterol-lowering medication.</div>' : ''}
            
            ${result.management_type.requires_immediate_consultation ? 
                '<div class="alert-box alert-danger"><strong>🚨 URGENT: Immediate Medical Consultation Required</strong><br>Contact your healthcare provider within 24 hours.</div>' : ''}
            
            <h5>Recommended Actions:</h5>
            <ul>
                ${result.management_type.recommended_actions.map(action => `<li>${action}</li>`).join('')}
            </ul>
        </div>
    `;
    
    // Lifestyle Plan
    displayLifestylePlan(result.lifestyle_plan);
    
    // Schedule
    displaySchedule(result.lifestyle_plan.checkup_schedule);
    
    // Show safety disclaimer
    showDisclaimer(result.safety_disclaimer);
    
    // Show adherence tracker
    document.getElementById('adherenceTracker').classList.remove('hidden');
    displayTodaysTasks(result.lifestyle_plan);
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function displayLifestylePlan(plan) {
    const lifestyleDiv = document.getElementById('lifestyle');
    
    lifestyleDiv.innerHTML = `
        <h2>🥗 Your Personalized Lifestyle Plan</h2>
        <p class="plan-intro">Follow this comprehensive plan to improve your cardiovascular health</p>
        
        <div class="lifestyle-plan">
            <!-- Meal Plan Card -->
            <div class="plan-card">
                <h3>🍽️ Daily Meal Plan</h3>
                
                <div class="meal-section">
                    <h4>Breakfast Options:</h4>
                    ${plan.meal_plan.daily_meals.breakfast.map(m => 
                        `<div class="meal-item">
                            <strong>${m.name}</strong>
                            <p class="meal-benefit">${m.benefits}</p>
                            <small>Nutrients: ${m.nutrients}</small>
                        </div>`
                    ).join('')}
                </div>
                
                <div class="meal-section">
                    <h4>Lunch Options:</h4>
                    ${plan.meal_plan.daily_meals.lunch.map(m => 
                        `<div class="meal-item">
                            <strong>${m.name}</strong>
                            <p class="meal-benefit">${m.benefits}</p>
                            <small>Nutrients: ${m.nutrients}</small>
                        </div>`
                    ).join('')}
                </div>
                
                <div class="meal-section">
                    <h4>Dinner Options:</h4>
                    ${plan.meal_plan.daily_meals.dinner.map(m => 
                        `<div class="meal-item">
                            <strong>${m.name}</strong>
                            <p class="meal-benefit">${m.benefits}</p>
                            <small>Nutrients: ${m.nutrients}</small>
                        </div>`
                    ).join('')}
                </div>
                
                ${plan.meal_plan.restrictions.length > 0 ? `
                    <div class="restrictions-section">
                        <h4>⛔ Foods to Avoid:</h4>
                        <ul class="restrictions-list">
                            ${plan.meal_plan.restrictions.map(r => `<li>${r}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div class="supplements-section">
                    <h4>💊 Recommended Supplements:</h4>
                    <ul>
                        ${plan.meal_plan.supplements.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                </div>
            </div>
            
            <!-- Exercise Plan Card -->
            <div class="plan-card">
                <h3>🏃 Exercise Plan</h3>
                <div class="exercise-details">
                    <p><strong>Type:</strong> ${plan.exercise_plan.type}</p>
                    <p><strong>Duration:</strong> ${plan.exercise_plan.duration}</p>
                    <p><strong>Frequency:</strong> ${plan.exercise_plan.frequency}</p>
                    ${plan.exercise_plan.intensity ? 
                        `<p><strong>Intensity:</strong> ${plan.exercise_plan.intensity}</p>` : ''}
                    
                    ${plan.exercise_plan.warning ? 
                        `<div class="alert-box alert-warning">${plan.exercise_plan.warning}</div>` : ''}
                    
                    <h4>Recommended Activities:</h4>
                    <ul>
                        ${plan.exercise_plan.activities.map(a => `<li>${a}</li>`).join('')}
                    </ul>
                    
                    <div class="benefits-note">
                        <strong>💪 Benefits:</strong> ${plan.exercise_plan.benefits || plan.exercise_plan.heart_health_note}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Educational Content -->
        <div class="plan-card education-card">
            <h3>📚 Daily Health Education</h3>
            <div class="daily-facts">
                ${plan.educational_content.daily_facts.slice(0, 3).map(fact => 
                    `<div class="fact-item">
                        <span class="fact-bullet">💡</span>
                        <p>${fact}</p>
                    </div>`
                ).join('')}
            </div>
            
            <div class="warning-signs">
                <h4>⚠️ Warning Signs - Seek Immediate Medical Attention:</h4>
                <ul class="warning-list">
                    ${plan.educational_content.warning_signs.map(sign => 
                        `<li>${sign}</li>`
                    ).join('')}
                </ul>
            </div>
            
            <div class="emergency-note">
                ${plan.educational_content.emergency_note}
            </div>
        </div>
    `;
}

function displaySchedule(schedule) {
    const scheduleDiv = document.getElementById('schedule');
    
    let html = `
        <h2>📅 Follow-Up & Checkup Schedule</h2>
        <div class="schedule-card">
    `;
    
    if (schedule.immediate) {
        html += `<div class="alert-box alert-danger">
            <strong>🚨 IMMEDIATE ACTION REQUIRED:</strong><br>
            ${schedule.immediate}
        </div>`;
    }
    
    if (schedule.initial) {
        html += `<div class="alert-box alert-warning">
            <strong>📞 Schedule Appointment:</strong><br>
            ${schedule.initial}
        </div>`;
    }
    
    if (schedule.routine) {
        html += `<div class="schedule-item">
            <strong>Routine Monitoring:</strong> ${schedule.routine}
        </div>`;
    }
    
    if (schedule.follow_ups && schedule.follow_ups.length > 0) {
        html += `
            <h4>Upcoming Follow-up Appointments:</h4>
            <div class="followup-timeline">
                ${schedule.follow_ups.map(fu => `
                    <div class="timeline-item">
                        <div class="timeline-date">${fu.date}</div>
                        <div class="timeline-content">
                            <strong>${fu.type}</strong>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    html += `</div>`;
    scheduleDiv.innerHTML = html;
}

function displayTodaysTasks(plan) {
    const tasksDiv = document.getElementById('todaysTasks');
    const reminders = plan.daily_reminders;
    
    tasksDiv.innerHTML = `
        <div class="tasks-header">
            <h3>Today's Activities</h3>
            <p>Track your daily adherence to improve cardiovascular health</p>
        </div>
        ${reminders.map((reminder, index) => `
            <div class="task-item" id="task-${index}">
                <div class="task-info">
                    <div class="task-time">${reminder.time}</div>
                    <div class="task-details">
                        <strong>${reminder.message}</strong>
                        <span class="priority-badge priority-${reminder.priority}">${reminder.priority.toUpperCase()}</span>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="btn-done" onclick="markTask('${index}', 'done', '${reminder.message}')">
                        ✓ Done
                    </button>
                    <button class="btn-skip" onclick="markTask('${index}', 'skip', '${reminder.message}')">
                        Skip
                    </button>
                </div>
            </div>
        `).join('')}
    `;
    
    updateAdherenceStats();
}

async function markTask(taskId, status, activity) {
    const patientId = localStorage.getItem('currentPatient');
    
    if (!patientId) {
        alert('Patient ID not found. Please complete the assessment first.');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/track-adherence`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient_id: patientId,
                activity: activity,
                status: status
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            const taskElement = document.getElementById(`task-${taskId}`);
            taskElement.classList.add(status === 'done' ? 'task-completed' : 'task-skipped');
            
            // Disable buttons
            const buttons = taskElement.querySelectorAll('button');
            buttons.forEach(btn => btn.disabled = true);
            
            // Update adherence stats
            updateAdherenceStats();
            
            // Show escalation warning if needed
            if (result.escalation) {
                showEscalationAlert(result.escalation);
            }
        }
    } catch (error) {
        console.error('Error tracking adherence:', error);
        alert('Failed to track adherence. Please try again.');
    }
}

function updateAdherenceStats() {
    const statsDiv = document.getElementById('adherenceStats');
    const tasks = document.querySelectorAll('.task-item');
    const completedTasks = document.querySelectorAll('.task-completed').length;
    const skippedTasks = document.querySelectorAll('.task-skipped').length;
    const totalTasks = tasks.length;
    const pendingTasks = totalTasks - completedTasks - skippedTasks;
    
    const adherenceRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    
    statsDiv.innerHTML = `
        <div class="stats-summary">
            <div class="stat-item">
                <div class="stat-value">${completedTasks}</div>
                <div class="stat-label">Completed</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${pendingTasks}</div>
                <div class="stat-label">Pending</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${skippedTasks}</div>
                <div class="stat-label">Skipped</div>
            </div>
            <div class="stat-item highlight">
                <div class="stat-value">${adherenceRate}%</div>
                <div class="stat-label">Adherence Rate</div>
            </div>
        </div>
    `;
}

function showEscalationAlert(escalation) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert-box alert-warning escalation-alert';
    alertDiv.innerHTML = `
        <strong>⚠️ ${escalation.flag.replace('_', ' ').toUpperCase()}</strong><br>
        ${escalation.message}
        <br><small>Adherence Rate: ${escalation.adherence_rate}%</small>
    `;
    
    document.getElementById('adherenceTracker').prepend(alertDiv);
    
    setTimeout(() => alertDiv.remove(), 10000);
}

function showDisclaimer(disclaimer) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>⚠️ Important Medical Disclaimer</h3>
            <div class="disclaimer-text">${disclaimer.replace(/\n/g, '<br>')}</div>
            <button onclick="this.parentElement.parentElement.remove()" class="btn-primary">
                I Understand
            </button>
        </div>
    `;
    document.body.appendChild(modal);
}

function getRiskIcon(level) {
    const icons = {
        'urgent': '🚨',
        'high': '⚠️',
        'medium': '⚡',
        'low': '✅'
    };
    return icons[level] || '📊';
}

function resetForm() {
    document.getElementById('lipidForm').reset();
    document.getElementById('results').classList.add('hidden');
    document.getElementById('adherenceTracker').classList.add('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Auto-save form data
const form = document.getElementById('lipidForm');
form.addEventListener('input', () => {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    localStorage.setItem('formDraft', JSON.stringify(data));
});

// Restore form data on load
window.addEventListener('load', () => {
    const savedData = localStorage.getItem('formDraft');
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(key => {
            const input = form.elements[key];
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = data[key] === 'on';
                } else {
                    input.value = data[key];
                }
            }
        });
    }
});