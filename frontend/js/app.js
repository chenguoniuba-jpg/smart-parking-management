/**
 * 智能停车场管理系统 - 主应用逻辑
 */

// ========== 全局状态 ==========
let currentUser = null;
let pieChartInstance = null;
let histogramChartInstance = null;

// ========== Toast 通知 ==========
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || 'ℹ️'}</span>
        <span>${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    container.appendChild(toast);
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }
    }, 4000);
}

// ========== 登录 ==========
async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    const loginError = document.getElementById('loginError');
    const loginBtn = event.target.querySelector('button[type="submit"]');

    if (!username || !password) {
        loginError.textContent = '请输入用户名和密码';
        loginError.style.display = 'block';
        return false;
    }

    loginError.style.display = 'none';
    loginBtn.disabled = true;
    loginBtn.textContent = '登录中...';

    try {
        const data = await ApiClient.login(username, password);
        currentUser = { username };
        document.getElementById('loginPage').style.display = 'none';
        document.getElementById('appContainer').classList.add('active');
        document.getElementById('userName').textContent = username;
        document.getElementById('userAvatar').textContent = username.charAt(0).toUpperCase();
        showToast(`欢迎回来，${username}！`, 'success');
        // 加载初始数据
        Promise.all([
            refreshDashboard(),
            refreshSpots(),
            refreshUsers(),
            refreshRecords(),
            refreshReservations(),
            refreshAI(),
            refreshConfigs(),
        ]);
    } catch (error) {
        loginError.textContent = error.message || '登录失败，请检查用户名和密码';
        loginError.style.display = 'block';
        showToast('登录失败', 'error');
    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = '登 录';
    }
    return false;
}

// ========== 退出登录 ==========
function handleLogout() {
    ApiClient.clearToken();
    currentUser = null;
    document.getElementById('appContainer').classList.remove('active');
    document.getElementById('loginPage').style.display = 'flex';
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
    showToast('已退出登录', 'info');
}

// ========== 页面切换 ==========
function switchPage(pageId) {
    // 更新导航高亮
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === pageId);
    });
    // 显示对应页面
    document.querySelectorAll('.page-section').forEach(section => {
        section.classList.toggle('active', section.id === `page-${pageId}`);
    });
    // 关闭移动端侧边栏
    document.getElementById('sidebar').classList.remove('active');
    document.getElementById('overlay').classList.remove('active');
}

function toggleMobileMenu() {
    document.getElementById('sidebar').classList.toggle('active');
    document.getElementById('overlay').classList.toggle('active');
}

document.getElementById('overlay').addEventListener('click', () => {
    document.getElementById('sidebar').classList.remove('active');
    document.getElementById('overlay').classList.remove('active');
});

// ========== 折叠面板 ==========
function toggleAccordion(header) {
    const item = header.parentElement;
    item.classList.toggle('open');
}

// ========== 工具函数 ==========
function formatDateTime(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

function formatDateTimeShort(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function getStatusBadge(status) {
    const map = {
        'AVAILABLE': '<span class="badge badge-success">可用</span>',
        'OCCUPIED': '<span class="badge badge-danger">已用</span>',
        'RESERVED': '<span class="badge badge-warning">预约</span>',
        'MAINTENANCE': '<span class="badge badge-secondary">维护</span>',
        'active': '<span class="badge badge-success">活跃</span>',
        'suspended': '<span class="badge badge-danger">停用</span>',
        'confirmed': '<span class="badge badge-success">已确认</span>',
        'completed': '<span class="badge badge-info">已完成</span>',
        'cancelled': '<span class="badge badge-secondary">已取消</span>',
        'expired': '<span class="badge badge-danger">已过期</span>',
        'parked': '<span class="badge badge-success">已停放</span>',
        'not_parked': '<span class="badge badge-secondary">未停放</span>',
    };
    return map[status] || `<span class="badge badge-secondary">${escapeHtml(status)}</span>`;
}

function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function getSizeLabel(size) {
    const map = { 'SMALL': '小型', 'MEDIUM': '中型', 'LARGE': '大型' };
    return map[size] || size;
}

// ========== 数据看板 ==========
async function refreshDashboard() {
    try {
        const [stats, users, compliance, records] = await Promise.all([
            ApiClient.getDashboardStats(),
            ApiClient.getUsers(),
            ApiClient.getComplianceStats(),
            ApiClient.getParkingRecords(10),
        ]);

        // 统计卡片
        const statsGrid = document.getElementById('dashboardStats');
        const activeUsers = users ? users.filter(u => u.status === 'active').length : 0;
        statsGrid.innerHTML = `
            <div class="stat-card">
                <div class="stat-card-header">
                    <span class="stat-card-label">总车位</span>
                    <div class="stat-card-icon" style="background:#e8f0fe;color:#1a73e8;">🅿️</div>
                </div>
                <div class="stat-card-value">${stats?.total_spots || 0}</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-header">
                    <span class="stat-card-label">可用车位</span>
                    <div class="stat-card-icon" style="background:#e6f4ea;color:#34a853;">🟢</div>
                </div>
                <div class="stat-card-value">${stats?.available_spots || 0}</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-header">
                    <span class="stat-card-label">已用车位</span>
                    <div class="stat-card-icon" style="background:#fce8e6;color:#ea4335;">🔴</div>
                </div>
                <div class="stat-card-value">${stats?.occupied_spots || 0}</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-header">
                    <span class="stat-card-label">预约车位</span>
                    <div class="stat-card-icon" style="background:#fef7e0;color:#fbbc04;">🟡</div>
                </div>
                <div class="stat-card-value">${stats?.reserved_spots || 0}</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-header">
                    <span class="stat-card-label">总用户数</span>
                    <div class="stat-card-icon" style="background:#e8f0fe;color:#1a73e8;">👥</div>
                </div>
                <div class="stat-card-value">${users ? users.length : 0}</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-header">
                    <span class="stat-card-label">活跃用户</span>
                    <div class="stat-card-icon" style="background:#e6f4ea;color:#34a853;">✅</div>
                </div>
                <div class="stat-card-value">${activeUsers}</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-header">
                    <span class="stat-card-label">履约率</span>
                    <div class="stat-card-icon" style="background:#e6f4ea;color:#34a853;">📊</div>
                </div>
                <div class="stat-card-value">${compliance?.compliance_rate || 0}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-header">
                    <span class="stat-card-label">总记录</span>
                    <div class="stat-card-icon" style="background:#e8f0fe;color:#1a73e8;">📋</div>
                </div>
                <div class="stat-card-value">${compliance?.total_records || 0}</div>
            </div>
        `;

        // 饼图 - 车位占用
        const pieCtx = document.getElementById('pieChart').getContext('2d');
        if (pieChartInstance) pieChartInstance.destroy();
        pieChartInstance = new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                labels: ['可用', '已用', '预约'],
                datasets: [{
                    data: [stats?.available_spots || 0, stats?.occupied_spots || 0, stats?.reserved_spots || 0],
                    backgroundColor: ['#34a853', '#ea4335', '#fbbc04'],
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });

        // 直方图 - 信誉积分分布
        const histCtx = document.getElementById('histogramChart').getContext('2d');
        if (histogramChartInstance) histogramChartInstance.destroy();
        if (users && users.length > 0) {
            const scores = users.map(u => u.credit_score).filter(s => s != null);
            const bins = 20;
            const min = Math.min(...scores);
            const max = Math.max(...scores);
            const binWidth = (max - min) / bins || 1;
            const labels = [];
            const counts = [];
            for (let i = 0; i < bins; i++) {
                const binStart = Math.round(min + i * binWidth);
                const binEnd = Math.round(min + (i + 1) * binWidth);
                labels.push(i === 0 ? `${binStart}-${binEnd}` : `${binStart}-${binEnd}`);
                counts.push(scores.filter(s => s >= binStart && (i === bins - 1 ? s <= binEnd : s < binEnd)).length);
            }
            histogramChartInstance = new Chart(histCtx, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [{
                        label: '用户数量',
                        data: counts,
                        backgroundColor: '#1a73e8',
                        borderRadius: 4,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: { title: { display: true, text: '信誉积分' } },
                        y: { title: { display: true, text: '用户数量' }, beginAtZero: true }
                    }
                }
            });
        } else {
            histogramChartInstance = new Chart(histCtx, {
                type: 'bar',
                data: { labels: ['无数据'], datasets: [{ data: [0] }] },
                options: { responsive: true, plugins: { legend: { display: false } } }
            });
        }

        // 最新停车记录
        renderTable('recentRecords', records, [
            { key: 'id', label: 'ID' },
            { key: 'user_id', label: '用户ID' },
            { key: 'parking_spot_id', label: '车位ID' },
            { key: 'entry_time', label: '入场时间', format: formatDateTime },
        ]);

        showToast('看板数据已刷新', 'info');
    } catch (error) {
        console.error('刷新看板失败:', error);
        showToast('刷新看板数据失败', 'error');
    }
}

// ========== 表格渲染工具 ==========
function renderTable(containerId, data, columns) {
    const container = document.getElementById(containerId);
    if (!data || data.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <div class="empty-state-text">暂无数据</div>
            </div>
        `;
        return;
    }
    let html = '<table><thead><tr>';
    columns.forEach(col => {
        html += `<th>${escapeHtml(col.label)}</th>`;
    });
    html += '</tr></thead><tbody>';
    data.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            let value = row[col.key];
            let trustedHtml = false;
            if (col.format) {
                value = col.format(value);
            } else if (col.badge) {
                value = getStatusBadge(value);
                trustedHtml = true;
            } else if (value === null || value === undefined) {
                value = '-';
            }
            html += `<td>${trustedHtml ? value : escapeHtml(value)}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}

// ========== 车位管理 ==========
async function refreshSpots() {
    try {
        const spots = await ApiClient.getParkingSpots();
        renderTable('spotsTable', spots, [
            { key: 'spot_number', label: '车位号' },
            { key: 'floor', label: '楼层' },
            { key: 'zone', label: '区域' },
            { key: 'size', label: '尺寸', format: getSizeLabel },
            { key: 'status', label: '状态', badge: true },
            { key: 'is_special_needs', label: '特殊需求', format: v => v ? '✅' : '❌' },
        ]);
    } catch (error) {
        showToast('获取车位列表失败', 'error');
    }
}

async function addParkingSpot() {
    const data = {
        spot_number: document.getElementById('spotNumber').value.trim(),
        floor: parseInt(document.getElementById('spotFloor').value) || 1,
        zone: document.getElementById('spotZone').value.trim() || 'A',
        size: document.getElementById('spotSize').value,
        is_special_needs: document.getElementById('spotSpecial').checked,
    };
    if (!data.spot_number) {
        showToast('请输入车位号', 'warning');
        return;
    }
    try {
        await ApiClient.createParkingSpot(data);
        showToast('车位添加成功！', 'success');
        document.getElementById('addSpotResult').innerHTML = '✅ 车位添加成功！';
        refreshSpots();
    } catch (error) {
        showToast(`添加失败: ${error.message}`, 'error');
        document.getElementById('addSpotResult').innerHTML = `❌ 添加失败: ${error.message}`;
    }
}

// ========== 用户管理 ==========
async function refreshUsers() {
    try {
        const users = await ApiClient.getUsers();
        renderTable('usersTable', users, [
            { key: 'id', label: 'ID' },
            { key: 'username', label: '用户名' },
            { key: 'phone', label: '手机号' },
            { key: 'license_plate', label: '车牌号' },
            { key: 'member_level', label: '会员等级' },
            { key: 'credit_score', label: '信誉积分' },
            { key: 'points', label: '积分' },
            { key: 'status', label: '状态', badge: true },
        ]);
    } catch (error) {
        showToast('获取用户列表失败', 'error');
    }
}

async function addUser() {
    const data = {
        username: document.getElementById('newUsername').value.trim(),
        phone: document.getElementById('newPhone').value.trim(),
        license_plate: document.getElementById('newLicensePlate').value.trim(),
        vehicle_size: document.getElementById('newVehicleSize').value,
        is_special_needs: document.getElementById('newUserSpecial').checked,
    };
    if (!data.username || !data.phone || !data.license_plate) {
        showToast('请填写完整信息', 'warning');
        return;
    }
    try {
        await ApiClient.createUser(data);
        showToast('用户添加成功！', 'success');
        document.getElementById('addUserResult').innerHTML = '✅ 用户添加成功！';
        refreshUsers();
    } catch (error) {
        showToast(`添加失败: ${error.message}`, 'error');
        document.getElementById('addUserResult').innerHTML = `❌ 添加失败: ${error.message}`;
    }
}

async function findVehicle() {
    const licensePlate = document.getElementById('searchLicensePlate').value.trim();
    const resultDiv = document.getElementById('searchVehicleResult');
    if (!licensePlate) {
        showToast('请输入车牌号', 'warning');
        return;
    }
    try {
        const result = await ApiClient.findVehicle(licensePlate);
        if (result.status === 'parked') {
            resultDiv.innerHTML = `
                ✅ 车辆在 <strong>${result.floor}</strong> 层 <strong>${result.zone}</strong> 区 
                <strong>${result.spot_number}</strong> 号车位<br>
                已停时长: <strong>${result.duration_hours}</strong> 小时
            `;
            showToast('车辆已定位！', 'success');
        } else {
            resultDiv.innerHTML = 'ℹ️ 车辆当前未在停车场';
            showToast('车辆未在停车场', 'info');
        }
    } catch (error) {
        resultDiv.innerHTML = `❌ 未找到该车辆: ${error.message}`;
        showToast('未找到该车辆', 'error');
    }
}

// ========== 停车记录 ==========
async function refreshRecords() {
    try {
        const [activeRecords, allRecords] = await Promise.all([
            ApiClient.getActiveRecords(),
            ApiClient.getParkingRecords(50),
        ]);

        renderTable('activeRecordsTable', activeRecords, [
            { key: 'id', label: 'ID' },
            { key: 'user_id', label: '用户ID' },
            { key: 'parking_spot_id', label: '车位ID' },
            { key: 'entry_time', label: '入场时间', format: formatDateTime },
        ]);

        renderTable('allRecordsTable', allRecords, [
            { key: 'id', label: 'ID' },
            { key: 'user_id', label: '用户ID' },
            { key: 'parking_spot_id', label: '车位ID' },
            { key: 'entry_time', label: '入场时间', format: formatDateTime },
            { key: 'exit_time', label: '离场时间', format: formatDateTime },
            { key: 'duration_hours', label: '时长(h)', format: v => v != null ? v.toFixed(2) : '-' },
            { key: 'fee', label: '费用(¥)', format: v => v != null ? `¥${v.toFixed(2)}` : '-' },
        ]);
    } catch (error) {
        showToast('获取停车记录失败', 'error');
    }
}

async function vehicleExit() {
    const recordId = parseInt(document.getElementById('exitRecordId').value);
    const resultDiv = document.getElementById('exitResult');
    if (!recordId) {
        showToast('请输入停车记录ID', 'warning');
        return;
    }
    try {
        const result = await ApiClient.vehicleExit(recordId);
        resultDiv.innerHTML = `✅ 离场成功！停车时长: ${result.duration_hours} 小时，费用: ¥${result.fee}`;
        showToast(`离场成功！费用: ¥${result.fee}`, 'success');
        refreshRecords();
    } catch (error) {
        resultDiv.innerHTML = `❌ 离场失败: ${error.message}`;
        showToast(`离场失败: ${error.message}`, 'error');
    }
}

// ========== 预约管理 ==========
async function refreshReservations() {
    try {
        const [reservations, flashSale] = await Promise.all([
            ApiClient.getReservations(),
            ApiClient.getFlashSaleSpots(),
        ]);

        renderTable('reservationsTable', reservations, [
            { key: 'id', label: 'ID' },
            { key: 'user_id', label: '用户ID' },
            { key: 'parking_spot_id', label: '车位ID' },
            { key: 'start_time', label: '开始时间', format: formatDateTimeShort },
            { key: 'end_time', label: '结束时间', format: formatDateTimeShort },
            { key: 'status', label: '状态', badge: true },
            { key: 'is_flash_sale', label: '秒杀', format: v => v ? '🔥' : '-' },
        ]);

        // 秒杀信息
        const flashCount = document.getElementById('flashCount');
        if (flashSale && flashSale.count > 0) {
            flashCount.textContent = `当前有 ${flashSale.count} 个秒杀车位可用！`;
        } else {
            flashCount.textContent = '当前没有可用的秒杀车位';
        }
    } catch (error) {
        showToast('获取预约列表失败', 'error');
    }
}

async function createReservation() {
    const startTimeInput = document.getElementById('resStartTime').value;
    const endTimeInput = document.getElementById('resEndTime').value;
    const data = {
        user_id: parseInt(document.getElementById('resUserId').value),
        parking_spot_id: parseInt(document.getElementById('resSpotId').value),
        start_time: startTimeInput ? new Date(startTimeInput).toISOString() : '',
        end_time: endTimeInput ? new Date(endTimeInput).toISOString() : '',
    };
    const resultDiv = document.getElementById('createResResult');
    if (!data.user_id || !data.parking_spot_id || !data.start_time || !data.end_time) {
        showToast('请填写完整信息', 'warning');
        return;
    }
    try {
        await ApiClient.createReservation(data);
        resultDiv.innerHTML = '✅ 预约创建成功！';
        showToast('预约创建成功！', 'success');
        refreshReservations();
    } catch (error) {
        resultDiv.innerHTML = `❌ 创建失败: ${error.message}`;
        showToast(`创建失败: ${error.message}`, 'error');
    }
}

async function participateFlashSale() {
    const userId = parseInt(document.getElementById('flashUserId').value);
    const resultDiv = document.getElementById('flashResult');
    if (!userId) {
        showToast('请输入用户ID', 'warning');
        return;
    }
    try {
        const result = await ApiClient.participateFlashSale(userId);
        if (result.success) {
            resultDiv.innerHTML = `🎉 秒杀成功！预约ID: ${result.reservation_id}`;
            showToast('秒杀成功！', 'success');
            refreshReservations();
        } else {
            resultDiv.innerHTML = `❌ 秒杀失败: ${result.message}`;
            showToast('秒杀失败', 'error');
        }
    } catch (error) {
        resultDiv.innerHTML = `❌ 秒杀失败: ${error.message}`;
        showToast(`秒杀失败: ${error.message}`, 'error');
    }
}

// ========== 规则调度 ==========
async function refreshAI() {
    try {
        const [predictions, violations] = await Promise.all([
            ApiClient.getTrafficPredictions(),
            ApiClient.getLongTermViolations(),
        ]);

        // 预测表格
        renderTable('predictionsTable', predictions, [
            { key: 'prediction_date', label: '预测日期', format: formatDateTimeShort },
            { key: 'predicted_peak_hour', label: '高峰时段', format: v => `${v}:00` },
            { key: 'predicted_volume', label: '预测流量' },
            { key: 'confidence', label: '置信度', format: v => `${(v * 100).toFixed(1)}%` },
        ]);

        // 违规信息
        const violationsDiv = document.getElementById('violationsInfo');
        if (violations && violations.violations && violations.violations.length > 0) {
            let html = `⚠️ 发现 <strong>${violations.violations.length}</strong> 个长时停车违规<br><br>`;
            violations.violations.forEach(v => {
                html += `⚠️ 用户 ${v.username} (车牌: ${v.license_plate}) 本月停车 ${v.monthly_days} 天<br>`;
            });
            violationsDiv.innerHTML = html;
        } else {
            violationsDiv.innerHTML = '✅ 没有发现长时停车违规';
        }
    } catch (error) {
        showToast('获取规则数据失败', 'error');
    }
}

async function generatePredictions() {
    const daysAhead = parseInt(document.getElementById('daysAhead').value) || 7;
    const resultDiv = document.getElementById('genPredResult');
    try {
        const result = await ApiClient.generateTrafficPredictions(daysAhead);
        resultDiv.innerHTML = `✅ 预测生成成功！生成 ${result.predictions_count} 天的预测`;
        showToast('流量预测生成成功！', 'success');
        refreshAI();
    } catch (error) {
        resultDiv.innerHTML = `❌ 预测生成失败: ${error.message}`;
        showToast('生成预测失败', 'error');
    }
}

async function checkCapacity() {
    const resultDiv = document.getElementById('capacityResult');
    try {
        const result = await ApiClient.checkCapacityExpansion();
        if (result.should_expand) {
            resultDiv.innerHTML = `⚠️ ${result.message}`;
            showToast('建议扩容', 'warning');
        } else {
            resultDiv.innerHTML = `✅ ${result.message}`;
            showToast('当前容量充足', 'success');
        }
    } catch (error) {
        resultDiv.innerHTML = `❌ 检查失败: ${error.message}`;
        showToast('检查失败', 'error');
    }
}

async function smartAssign() {
    const userId = parseInt(document.getElementById('assignUserId').value);
    const resultDiv = document.getElementById('assignResult');
    if (!userId) {
        showToast('请输入用户ID', 'warning');
        return;
    }
    try {
        const result = await ApiClient.smartAssignParking(userId);
        resultDiv.innerHTML = `✅ 分配成功！车位ID: ${result.spot_id}`;
        showToast('智能分配成功！', 'success');
        refreshSpots();
    } catch (error) {
        resultDiv.innerHTML = `❌ 分配失败: ${error.message}`;
        showToast('分配失败', 'error');
    }
}

// ========== 系统配置 ==========
async function refreshConfigs() {
    try {
        const configs = await ApiClient.getSystemConfigs();
        renderTable('configsTable', configs, [
            { key: 'config_key', label: '配置键' },
            { key: 'config_value', label: '配置值' },
            { key: 'description', label: '描述' },
            { key: 'updated_at', label: '更新时间', format: formatDateTime },
        ]);
    } catch (error) {
        showToast('获取配置列表失败', 'error');
    }
}

async function updateConfig() {
    const configKey = document.getElementById('configKey').value;
    const configValue = document.getElementById('configValue').value.trim();
    const resultDiv = document.getElementById('updateConfigResult');
    if (!configValue) {
        showToast('请输入新值', 'warning');
        return;
    }
    try {
        await ApiClient.updateSystemConfig(configKey, configValue);
        resultDiv.innerHTML = '✅ 配置更新成功！';
        showToast('配置更新成功！', 'success');
        refreshConfigs();
    } catch (error) {
        resultDiv.innerHTML = `❌ 更新失败: ${error.message}`;
        showToast('更新失败', 'error');
    }
}

async function initConfigs() {
    const resultDiv = document.getElementById('initConfigResult');
    try {
        const result = await ApiClient.initDefaultConfigs();
        resultDiv.innerHTML = `✅ 初始化完成！创建 ${result.created_count} 个默认配置`;
        showToast('默认配置初始化完成！', 'success');
        refreshConfigs();
    } catch (error) {
        resultDiv.innerHTML = `❌ 初始化失败: ${error.message}`;
        showToast('初始化失败', 'error');
    }
}

// ========== 初始化 ==========
// 检查是否已有 token
document.addEventListener('DOMContentLoaded', async () => {
    const token = ApiClient.getToken();
    if (token) {
        try {
            const admin = await ApiClient.getCurrentAdmin();
            document.getElementById('loginPage').style.display = 'none';
            document.getElementById('appContainer').classList.add('active');
            currentUser = { username: admin.username };
            document.getElementById('userName').textContent = admin.username;
            document.getElementById('userAvatar').textContent = admin.username.charAt(0).toUpperCase();
            Promise.all([
                refreshDashboard(),
                refreshSpots(),
                refreshUsers(),
                refreshRecords(),
                refreshReservations(),
                refreshAI(),
                refreshConfigs(),
            ]);
        } catch (error) {
            ApiClient.clearToken();
            document.getElementById('loginError').textContent = '登录已过期，请重新登录';
            document.getElementById('loginError').style.display = 'block';
        }
    }
});
