/**
 * Study Tracker Logic
 */

let currentSubjectId = null;
let chartInstances = {};

async function initializeStudyTracker() {
    setupTabListeners();
    loadSubjectsForTracker();
}

function setupTabListeners() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', handleTabSwitch);
    });
}

async function handleTabSwitch(e) {
    const tab = e.target.dataset.tab;

    // Reset display
    document.querySelectorAll('.study-section').forEach(s => s.style.display = 'none');

    switch(tab) {
        case 'subjects':
            document.getElementById('subjects-section').style.display = 'block';
            await loadSubjectsForTracker();
            break;
        case 'sessions':
            document.getElementById('sessions-section').style.display = 'block';
            await loadSessionsForTracker();
            break;
        case 'goals':
            document.getElementById('goals-section').style.display = 'block';
            await loadGoalsForTracker();
            break;
        case 'analytics':
            document.getElementById('analytics-section').style.display = 'block';
            await loadAnalyticsForTracker();
            break;
    }
}

async function loadSubjectsForTracker() {
    try {
        const response = await apiClient.getSubjectStats();
        const data = response.data;

        const list = document.getElementById('subjects-list');
        list.innerHTML = data.subjects.map(subject => `
            <div class="subject-card" style="border-color: ${subject.color}">
                <div class="card-header">
                    <h3>${subject.name}</h3>
                    <span class="progress-badge">${subject.progress_percentage}%</span>
                </div>
                <p>${subject.completed_sections}/${subject.total_sections} sections</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${subject.progress_percentage}%; background: ${subject.color}"></div>
                </div>
                <button class="btn btn-sm" onclick="viewSubjectDetail(${subject.id})">Détails</button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading subjects:', error);
    }
}

async function viewSubjectDetail(subjectId) {
    try {
        currentSubjectId = subjectId;
        const response = await apiClient.getSubjectDetail(subjectId);
        const subject = response.data;

        document.getElementById('subjects-section').style.display = 'none';
        document.getElementById('subject-detail-section').style.display = 'block';

        const header = document.getElementById('subject-header');
        header.innerHTML = `
            <h2>${subject.name}</h2>
            <p>${subject.description}</p>
            <div class="stat-line">${subject.progress_percentage}% • ${subject.completed_sections}/${subject.total_sections} sections</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${subject.progress_percentage}%"></div>
            </div>
        `;

        await loadChaptersForTracker(subjectId);
    } catch (error) {
        console.error('Error loading subject detail:', error);
    }
}

async function loadChaptersForTracker(subjectId) {
    try {
        const response = await axios.get(`/api/chapters/?subject_id=${subjectId}`);
        const chapters = response.data.results || response.data;

        const list = document.getElementById('chapters-list');
        list.innerHTML = chapters.map(chapter => `
            <div class="chapter-item">
                <h4>Ch${chapter.chapter_number}: ${chapter.title}</h4>
                <p class="chapter-stats">${chapter.completed_sections}/${chapter.total_sections} sections • ${chapter.progress_percentage}%</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${chapter.progress_percentage}%"></div>
                </div>
                <div class="sections-list">
                    ${chapter.sections.map(section => `
                        <label class="section-checkbox ${section.completed ? 'completed' : ''}">
                            <input type="checkbox" ${section.completed ? 'checked' : ''} 
                                onchange="toggleSectionCompletion(${section.id}, this.checked)">
                            <span>${section.title}</span>
                        </label>
                    `).join('')}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading chapters:', error);
    }
}

async function toggleSectionCompletion(sectionId, completed) {
    try {
        if (completed) {
            await apiClient.markSectionCompleted(sectionId);
        } else {
            await apiClient.markSectionIncomplete(sectionId);
        }
        if (currentSubjectId) {
            await loadChaptersForTracker(currentSubjectId);
        }
    } catch (error) {
        console.error('Error toggling section:', error);
    }
}

async function loadSessionsForTracker() {
    try {
        const response = await apiClient.getStudySessionsThisWeek();
        const data = response.data;
        const sessions = data.sessions || [];

        const list = document.getElementById('sessions-list');
        list.innerHTML = sessions.length === 0
            ? '<p class="no-data">Aucune session cette semaine</p>'
            : sessions.map(session => `
                <div class="session-item">
                    <h4>${session.section_title}</h4>
                    <p>📚 ${session.subject_name}</p>
                    <p>⏱️ ${session.duration_hours}h ${session.duration_minutes % 60}min</p>
                    <p>⭐ Focus: ${session.focus_level}/5</p>
                    <p>📊 Productivité: ${session.productivity_score}%</p>
                </div>
            `).join('');
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

async function loadGoalsForTracker() {
    try {
        const response = await apiClient.getStudyGoalsActive();
        const goals = Array.isArray(response.data) ? response.data : response.data.results || [];

        const list = document.getElementById('goals-list');
        list.innerHTML = goals.length === 0
            ? '<p class="no-data">Aucun objectif actif</p>'
            : goals.map(goal => `
                <div class="goal-item">
                    <h4>${goal.goal_type.replace(/_/g, ' ')}</h4>
                    <p>${goal.current_value}/${goal.target_value}</p>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${goal.progress_percentage}%"></div>
                    </div>
                    <p class="goal-reward">+${goal.xp_reward} XP</p>
                </div>
            `).join('');
    } catch (error) {
        console.error('Error loading goals:', error);
    }
}

async function loadAnalyticsForTracker() {
    try {
        const subjectResponse = await apiClient.getSubjectStats();
        const subjects = subjectResponse.data.subjects;

        const sessionResponse = await apiClient.getStudySessionsThisWeek();
        const sessions = sessionResponse.data.sessions || [];

        // Progress chart
        destroyChart('progress-chart');
        const ctx1 = document.getElementById('progress-chart');
        if (ctx1) {
            chartInstances['progress-chart'] = new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: subjects.map(s => s.name),
                    datasets: [{
                        label: 'Progression',
                        data: subjects.map(s => s.progress_percentage),
                        backgroundColor: '#667eea',
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // Hours chart
        const hoursByDate = {};
        sessions.forEach(session => {
            const date = new Date(session.start_time).toLocaleDateString('fr-FR');
            hoursByDate[date] = (hoursByDate[date] || 0) + session.duration_hours;
        });

        destroyChart('hours-chart');
        const ctx2 = document.getElementById('hours-chart');
        if (ctx2) {
            chartInstances['hours-chart'] = new Chart(ctx2, {
                type: 'line',
                data: {
                    labels: Object.keys(hoursByDate),
                    datasets: [{
                        label: 'Heures d\'étude',
                        data: Object.values(hoursByDate),
                        borderColor: '#06d6a0',
                        tension: 0.4,
                        fill: true,
                        backgroundColor: 'rgba(6, 214, 160, 0.1)',
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function destroyChart(chartId) {
    if (chartInstances[chartId]) {
        chartInstances[chartId].destroy();
    }
}

function backToSubjects() {
    currentSubjectId = null;
    document.getElementById('subject-detail-section').style.display = 'none';
    document.getElementById('subjects-section').style.display = 'block';
}

// Initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeStudyTracker);
} else {
    initializeStudyTracker();
}
