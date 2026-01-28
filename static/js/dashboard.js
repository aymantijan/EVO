/**
 * Dashboard Logic
 */

async function initializeDashboard() {
    await loadProfileStats();
    await loadRecentActions();
    await loadAchievementsProgress();
}

async function loadProfileStats() {
    try {
        const response = await apiClient.getStats();
        const stats = response.data;

        // Update header stats
        document.getElementById('user-level').textContent = stats.level;
        document.getElementById('user-streak').textContent = stats.current_streak;
        document.getElementById('user-hp').textContent = Math.round(stats.hp_global);

        // Update XP progress
        const xpPercent = ((stats.total_xp % 1000) / 1000) * 100;
        document.getElementById('xp-progress').style.width = xpPercent + '%';

        // Create HP radar chart
        createHPChart(stats.hp);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function createHPChart(hpData) {
    const ctx = document.getElementById('hpChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Physical', 'Mental', 'Social', 'Productivity', 'Creativity'],
            datasets: [{
                label: 'HP Stats',
                data: [
                    hpData.physical,
                    hpData.mental,
                    hpData.social,
                    hpData.productivity,
                    hpData.creativity
                ],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#667eea',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    max: 100,
                    beginAtZero: true,
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                }
            }
        }
    });
}

async function loadRecentActions() {
    try {
        const response = await apiClient.getActionsThisWeek();
        const actions = Array.isArray(response.data) ? response.data : response.data.results || [];

        const list = document.getElementById('recent-list');
        if (!list) return;

        if (actions.length === 0) {
            list.innerHTML = '<p class="no-data">Aucune action cette semaine</p>';
            return;
        }

        list.innerHTML = actions.slice(0, 5).map(action => `
            <div class="recent-action-item">
                <div class="action-info">
                    <h4>${action.title}</h4>
                    <p class="action-category">${action.category_name}</p>
                </div>
                <div class="action-xp">+${action.xp_earned} XP</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading recent actions:', error);
    }
}

async function loadAchievementsProgress() {
    try {
        const response = await apiClient.getAchievementsProgress();
        const progress = response.data;

        const progressBar = document.getElementById('achievement-progress-bar');
        if (progressBar) {
            progressBar.style.width = progress.percentage + '%';
        }
    } catch (error) {
        console.error('Error loading achievements:', error);
    }
}

// Initialize on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDashboard);
} else {
    initializeDashboard();
}
