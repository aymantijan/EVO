/**
 * API Client Helper - Centralized API calls
 */

const API_BASE = '/api';

class APIClient {
    constructor() {
        this.setupInterceptors();
    }

    setupInterceptors() {
        axios.interceptors.request.use(config => {
            const token = localStorage.getItem('auth_token');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });

        axios.interceptors.response.use(
            response => response,
            error => {
                if (error.response?.status === 401) {
                    localStorage.removeItem('auth_token');
                    window.location.href = '/login/';
                }
                return Promise.reject(error);
            }
        );
    }

    // Users
    async getProfile() {
        return axios.get(`${API_BASE}/users/profile/`);
    }

    async getStats() {
        return axios.get(`${API_BASE}/users/stats/`);
    }

    async getLeaderboard(limit = 100) {
        return axios.get(`${API_BASE}/users/leaderboard/?limit=${limit}`);
    }

    async updateProfile(data) {
        return axios.put(`${API_BASE}/users/update_profile/`, data);
    }

    // Actions
    async getActions() {
        return axios.get(`${API_BASE}/actions/`);
    }

    async createAction(data) {
        return axios.post(`${API_BASE}/actions/`, data);
    }

    async getActionsThisWeek() {
        return axios.get(`${API_BASE}/actions/this_week/`);
    }

    async getActionsThisMonth() {
        return axios.get(`${API_BASE}/actions/this_month/`);
    }

    // Categories
    async getCategories() {
        return axios.get(`${API_BASE}/categories/`);
    }

    // Achievements
    async getAchievementsUnlocked() {
        return axios.get(`${API_BASE}/achievements/unlocked/`);
    }

    async getAchievementsLocked() {
        return axios.get(`${API_BASE}/achievements/locked/`);
    }

    async getAchievementsProgress() {
        return axios.get(`${API_BASE}/achievements/progress/`);
    }

    // Challenges
    async getChallengesActive() {
        return axios.get(`${API_BASE}/challenges/active/`);
    }

    async getChallengesCompleted() {
        return axios.get(`${API_BASE}/challenges/completed/`);
    }

    // Study - Subjects
    async getSubjects() {
        return axios.get(`${API_BASE}/subjects/`);
    }

    async getSubjectStats() {
        return axios.get(`${API_BASE}/subjects/stats/`);
    }

    async getSubjectDetail(id) {
        return axios.get(`${API_BASE}/subjects/${id}/details/`);
    }

    async createSubject(data) {
        return axios.post(`${API_BASE}/subjects/`, data);
    }

    // Study - Sections
    async getSections(chapterId) {
        return axios.get(`${API_BASE}/sections/?chapter_id=${chapterId}`);
    }

    async markSectionCompleted(id) {
        return axios.post(`${API_BASE}/sections/${id}/mark_completed/`);
    }

    async markSectionIncomplete(id) {
        return axios.post(`${API_BASE}/sections/${id}/mark_incomplete/`);
    }

    // Study - Sessions
    async createStudySession(data) {
        return axios.post(`${API_BASE}/study-sessions/`, data);
    }

    async getStudySessionsThisWeek() {
        return axios.get(`${API_BASE}/study-sessions/this_week/`);
    }

    async getStudySessionsThisMonth() {
        return axios.get(`${API_BASE}/study-sessions/this_month/`);
    }

    // Study - Goals
    async getStudyGoalsActive() {
        return axios.get(`${API_BASE}/study-goals/active/`);
    }

    async getStudyGoalsAchieved() {
        return axios.get(`${API_BASE}/study-goals/achieved/`);
    }

    async createStudyGoal(data) {
        return axios.post(`${API_BASE}/study-goals/`, data);
    }

    // Study - Streaks
    async getStudyStreaks() {
        return axios.get(`${API_BASE}/study-streaks/`);
    }

    async getStudyStreaksGlobalStats() {
        return axios.get(`${API_BASE}/study-streaks/global_stats/`);
    }
}

// Create global instance
const apiClient = new APIClient();
