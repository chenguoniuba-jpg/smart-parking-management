/**
 * API 客户端模块
 * 处理所有与后端 API 的通信
 */

// const API_BASE_URL = 'http://localhost:8000';
const API_BASE_URL = '';

const ApiClient = {
    _token: null,

    setToken(token) {
        this._token = token;
        localStorage.setItem('parking_token', token);
    },

    getToken() {
        if (!this._token) {
            this._token = localStorage.getItem('parking_token');
        }
        return this._token;
    },

    clearToken() {
        this._token = null;
        localStorage.removeItem('parking_token');
    },

    _getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    },

    async _request(method, endpoint, data = null) {
        const url = `${API_BASE_URL}${endpoint}`;
        const options = {
            method,
            headers: this._getHeaders(),
        };
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        try {
            const response = await fetch(url, options);
            if (response.status === 401 && !endpoint.startsWith('/api/auth/login')) {
                this.clearToken();
            }
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const json = await response.json();
                if (!response.ok) {
                    throw new Error(json.detail || `请求失败: ${response.status}`);
                }
                return json;
            }
            if (!response.ok) {
                throw new Error(`请求失败: ${response.status}`);
            }
            return null;
        } catch (error) {
            console.error(`API 请求错误: ${method} ${endpoint}`, error);
            throw error;
        }
    },

    async get(endpoint) {
        return this._request('GET', endpoint);
    },

    async post(endpoint, data = null) {
        return this._request('POST', endpoint, data);
    },

    async put(endpoint, data) {
        return this._request('PUT', endpoint, data);
    },

    async delete(endpoint) {
        return this._request('DELETE', endpoint);
    },

    // ========== 认证 ==========
    async login(username, password) {
        const data = await this.post('/api/auth/login/json', { username, password });
        this.setToken(data.access_token);
        return data;
    },

    async getCurrentAdmin() {
        return this.get('/api/auth/me');
    },

    // ========== 看板 ==========
    async getDashboardStats() {
        return this.get('/api/parking-spots/stats/summary');
    },

    async getComplianceStats() {
        return this.get('/api/parking-records/stats/compliance');
    },

    // ========== 车位管理 ==========
    async getParkingSpots(statusFilter = null) {
        let endpoint = '/api/parking-spots/';
        if (statusFilter) {
            endpoint += `?status_filter=${statusFilter}`;
        }
        return this.get(endpoint);
    },

    async createParkingSpot(data) {
        return this.post('/api/parking-spots/', data);
    },

    // ========== 用户管理 ==========
    async getUsers() {
        return this.get('/api/users/');
    },

    async createUser(data) {
        return this.post('/api/users/', data);
    },

    async findVehicle(licensePlate) {
        return this.get(`/api/parking-records/license-plate/${licensePlate}`);
    },

    // ========== 停车记录 ==========
    async getParkingRecords(limit = 50) {
        return this.get(`/api/parking-records/?limit=${limit}`);
    },

    async getActiveRecords() {
        return this.get('/api/parking-records/active');
    },

    async vehicleExit(recordId) {
        return this.post(`/api/parking-records/${recordId}/exit`);
    },

    // ========== 预约管理 ==========
    async getReservations() {
        return this.get('/api/reservations/');
    },

    async createReservation(data) {
        return this.post('/api/reservations/', data);
    },

    async getFlashSaleSpots() {
        return this.get('/api/reservations/flash-sale/available');
    },

    async participateFlashSale(userId) {
        return this.post(`/api/reservations/flash-sale/${userId}`);
    },

    // ========== 规则调度 ==========
    async getTrafficPredictions(daysAhead = 7) {
        return this.get(`/api/ai/traffic-predictions?days_ahead=${daysAhead}`);
    },

    async generateTrafficPredictions(daysAhead = 7) {
        return this.post(`/api/ai/traffic-predictions/generate?days_ahead=${daysAhead}`);
    },

    async getLongTermViolations() {
        return this.get('/api/ai/long-term-violations');
    },

    async checkCapacityExpansion() {
        return this.post('/api/ai/check-capacity-expansion');
    },

    async smartAssignParking(userId) {
        return this.post(`/api/parking-spots/smart-assign/${userId}`);
    },

    // ========== 系统配置 ==========
    async getSystemConfigs() {
        return this.get('/api/ai/configs');
    },

    async updateSystemConfig(configKey, configValue) {
        return this.put(`/api/ai/configs/${configKey}`, configValue);
    },

    async initDefaultConfigs() {
        return this.post('/api/ai/init-default-configs');
    },
};
