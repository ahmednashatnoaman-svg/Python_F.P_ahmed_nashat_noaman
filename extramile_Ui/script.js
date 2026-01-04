document.addEventListener('DOMContentLoaded', () => {
    // 1. Navigation Logic
    setupNavigation();

    // 2. Data Fetching
    fetchDashboardData();
});

function setupNavigation() {
    const navLinks = document.querySelectorAll('.sidebar li');
    const sections = document.querySelectorAll('.page-section');
    const pageTitle = document.getElementById('page-title');

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Toggle Active Link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Switch Section
            const target = link.getAttribute('data-target');
            sections.forEach(sec => sec.classList.remove('active'));
            document.getElementById(`page-${target}`).classList.add('active');

            // Update Title
            pageTitle.textContent = link.querySelector('span').nextElementSibling.textContent;
        });
    });
}

function fetchDashboardData() {
    try {
        if (typeof DASHBOARD_DATA === 'undefined') {
            throw new Error("Dashboard Data not found. Please ensure dashboard_data.js is loaded.");
        }

        renderOverview(DASHBOARD_DATA);
        renderRiskTable(DASHBOARD_DATA);
        renderTransactionTable(DASHBOARD_DATA);

    } catch (error) {
        console.error("Dashboard Load Error:", error);
        document.querySelector('.main-content').innerHTML += `<div class="error-toast">Error loading data: ${error.message}</div>`;
    }
}

function renderOverview(data) {
    // KPI Cards
    if (data.risk_summary) {
        setText('kpi-total-customers', formatNumber(data.risk_summary.total_scored));
        setText('kpi-critical-risk', formatNumber(data.risk_summary.bands['Critical'] || 0));
    }
    if (data.flagged_summary) {
        setText('kpi-flagged-count', formatNumber(data.flagged_summary.total_flagged));
    }
    if (data.daily_stats) {
        setText('kpi-avg-daily', formatCurrency(data.daily_stats.avg_daily_per_cust));
    }
}

function renderRiskTable(data) {
    const tbody = document.querySelector('#table-risky-customers tbody');
    tbody.innerHTML = '';

    if (data.top_risky_customers) {
        data.top_risky_customers.forEach(cust => {
            const row = `
                <tr>
                    <td>${cust.customer_id}</td>
                    <td>${cust.risk_score.toFixed(2)}</td>
                    <td><span class="badge badge-critical">${cust.risk_band}</span></td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    }
}

function renderTransactionTable(data) {
    const tbody = document.querySelector('#table-payment-types tbody');
    tbody.innerHTML = '';

    if (data.payment_types) {
        data.payment_types.forEach(type => {
            const row = `
                <tr>
                    <td>${type.type}</td>
                    <td>${formatNumber(type.count)}</td>
                    <td>${formatCurrency(type.mean)}</td>
                    <td>${formatCurrency(type.max)}</td>
                    <td>${formatCurrency(type.sum)}</td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    }
}

// Helpers
function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

function formatCurrency(num) {
    // Shorten large numbers for cards if needed, but standard currency for tables
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
}
