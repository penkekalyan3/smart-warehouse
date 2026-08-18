// SCRIPT.JS – UPGRADED SMARTFULFILL OPERATIONS ENGINE

// ==========================================
// STATE MANAGEMENT & DATA SCHEMAS
// ==========================================
let state = {
    activeRole: "Admin",
    products: [],
    orders: [],
    transactions: [],
    returns: [],
    pickingTasks: [],
    packingOps: [],
    qualityChecks: [],
    exceptions: [],
    backorders: [],
    allocations: [],
    inventoryTransactions: [],
    logs: [],
    customers: [],
    warehouseZones: [],
    activityLogs: []
};

// Default Products Seed Data (Realistic Hackathon Stock)
const defaultProducts = [
    { product_code: "P001", name: "Smart Watch", category: "Wearables", location: "A2-01-01", total_stock: 45, reserved_stock: 5, damaged_stock: 1, reorder_level: 15, reorder_quantity: 30, unit_cost: 2500.0, selling_price: 3999.0, supplier: "TitanCorp Wearables" },
    { product_code: "P002", name: "Wireless Earbuds", category: "Audio", location: "B1-02-04", total_stock: 90, reserved_stock: 10, damaged_stock: 3, reorder_level: 25, reorder_quantity: 50, unit_cost: 1000.0, selling_price: 1899.0, supplier: "WaveSound Audio" },
    { product_code: "P003", name: "Bluetooth Speaker", category: "Audio", location: "B1-03-02", total_stock: 65, reserved_stock: 8, damaged_stock: 2, reorder_level: 20, reorder_quantity: 40, unit_cost: 1500.0, selling_price: 2499.0, supplier: "WaveSound Audio" },
    { product_code: "P004", name: "Smartphone", category: "Electronics", location: "A1-01-01", total_stock: 25, reserved_stock: 2, damaged_stock: 0, reorder_level: 8, reorder_quantity: 15, unit_cost: 18000.0, selling_price: 22999.0, supplier: "Apex Mobiles" },
    { product_code: "P005", name: "Laptop", category: "Electronics", location: "A1-01-02", total_stock: 15, reserved_stock: 4, damaged_stock: 0, reorder_level: 5, reorder_quantity: 10, unit_cost: 45000.0, selling_price: 55000.0, supplier: "Intellect Computers" },
    { product_code: "P006", name: "Keyboard", category: "Computer Accessories", location: "B2-01-01", total_stock: 35, reserved_stock: 5, damaged_stock: 1, reorder_level: 10, reorder_quantity: 25, unit_cost: 800.0, selling_price: 1200.0, supplier: "KeyTech Devices" },
    { product_code: "P007", name: "Mouse", category: "Computer Accessories", location: "B2-01-02", total_stock: 120, reserved_stock: 15, damaged_stock: 4, reorder_level: 30, reorder_quantity: 60, unit_cost: 400.0, selling_price: 650.0, supplier: "KeyTech Devices" },
    { product_code: "P008", name: "Power Bank", category: "Mobile Accessories", location: "B1-01-01", total_stock: 85, reserved_stock: 6, damaged_stock: 2, reorder_level: 20, reorder_quantity: 45, unit_cost: 900.0, selling_price: 1499.0, supplier: "Apex Mobiles" },
    { product_code: "P009", name: "USB Cable", category: "Mobile Accessories", location: "B1-01-02", total_stock: 150, reserved_stock: 25, damaged_stock: 5, reorder_level: 40, reorder_quantity: 100, unit_cost: 150.0, selling_price: 300.0, supplier: "KeyTech Devices" },
    { product_code: "P010", name: "Smart Band", category: "Wearables", location: "A2-01-02", total_stock: 8, reserved_stock: 3, damaged_stock: 1, reorder_level: 15, reorder_quantity: 30, unit_cost: 1200.0, selling_price: 1999.0, supplier: "TitanCorp Wearables" }
];

// Default Customers Seed
const defaultCustomers = [
    { name: "Kalyan Penke", email: "kalyan@example.com", phone: "+91 98765 43210", total_orders: 2, total_spending: 5790.0, last_order: "ORD001" },
    { name: "Suresh Kumar", email: "suresh@example.com", phone: "+91 87654 32109", total_orders: 1, total_spending: 650.0, last_order: "ORD002" },
    { name: "Ramesh Naidu", email: "ramesh@example.com", phone: "+91 76543 21098", total_orders: 1, total_spending: 9495.0, last_order: "ORD003" }
];

// Default Warehouse Zones Capacity
const defaultZones = [
    { code: "A1", name: "Electronics", capacity: 50, occupied: 40 },
    { code: "A2", name: "Smart Watches", capacity: 80, occupied: 53 },
    { code: "B1", name: "Mobile Accessories", capacity: 400, occupied: 300 },
    { code: "B2", name: "Computer Accessories", capacity: 200, occupied: 155 },
    { code: "C1", name: "General Products", capacity: 100, occupied: 10 }
];

// Default Orders
const defaultOrders = [
    { order_code: "ORD001", customer: "Kalyan Penke", email: "kalyan@example.com", phone: "+91 98765 43210", product_code: "P001", quantity: 1, total_amount: 3999.0, status: "Pending", created_at: "2026-08-18T12:00:00", address: "Tech Park, Hyderabad" },
    { order_code: "ORD002", customer: "Suresh Kumar", email: "suresh@example.com", phone: "+91 87654 32109", product_code: "P007", quantity: 1, total_amount: 650.0, status: "Processing", created_at: "2026-08-18T12:30:00", address: "Ameerpet, Hyderabad" },
    { order_code: "ORD003", customer: "Ramesh Naidu", email: "ramesh@example.com", phone: "+91 76543 21098", product_code: "P002", quantity: 5, total_amount: 9495.0, status: "Delivered", created_at: "2026-08-18T13:00:00", address: "Gachibowli, Hyderabad" }
];

// Helper: Load/Save LocalStorage
function loadState() {
    const raw = localStorage.getItem("smart_fulfill_v2_db");
    if (raw) {
        state = JSON.parse(raw);
    } else {
        resetLocalDataset();
    }
}

function saveState() {
    localStorage.setItem("smart_fulfill_v2_db", JSON.stringify(state));
}

// System Logs
function logEvent(type, message) {
    const timeStr = new Date().toLocaleTimeString();
    const cleanMsg = `[${timeStr}] [${type.toUpperCase()}] ${message}`;
    state.logs.push({ type, message: cleanMsg });
    if (state.logs.length > 50) state.logs.shift();
    saveState();
    
    const consoleEl = document.getElementById("demo-log-console");
    if (consoleEl) {
        const line = document.createElement("div");
        line.className = `log-line ${type}`;
        line.innerText = cleanMsg;
        consoleEl.appendChild(line);
        consoleEl.scrollTop = consoleEl.scrollHeight;
    }
}

// Activity Log Audit Seeder
function addActivityLog(userRole, action) {
    const now = new Date();
    const log = {
        role: userRole,
        action: action,
        date: now.toLocaleDateString(),
        time: now.toLocaleTimeString()
    };
    state.activityLogs.unshift(log); // newest first
    if (state.activityLogs.length > 100) state.activityLogs.pop();
    saveState();
}

// Toast Notifications System
function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    
    let icon = "fa-info-circle";
    if (type === "success") icon = "fa-check-circle";
    if (type === "warning") icon = "fa-exclamation-triangle";
    if (type === "danger") icon = "fa-exclamation-circle";
    
    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <div>${message}</div>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-10px)";
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Format INR Currency
function formatINR(val) {
    if (val === undefined || val === null) return "₹0";
    const num = Math.abs(parseFloat(val));
    const isNegative = parseFloat(val) < 0;
    
    let res = "";
    let str = num.toFixed(2);
    let parts = str.split(".");
    let integerPart = parts[0];
    let decimalPart = parts[1] === "00" ? "" : "." + parts[1];

    if (integerPart.length <= 3) {
        res = integerPart;
    } else {
        let last3 = integerPart.substring(integerPart.length - 3);
        let remaining = integerPart.substring(0, integerPart.length - 3);
        let groups = [];
        while (remaining.length > 2) {
            groups.unshift(remaining.substring(remaining.length - 2));
            remaining = remaining.substring(0, remaining.length - 2);
        }
        if (remaining.length > 0) {
            groups.unshift(remaining);
        }
        res = groups.join(",") + "," + last3;
    }
    
    let formatted = "₹" + res + decimalPart;
    return isNegative ? "-" + formatted : formatted;
}

// Stock Helpers
function getAvailableStock(p) {
    return Math.max(0, p.total_stock - p.reserved_stock - p.damaged_stock);
}

function getStockStatus(p) {
    const avail = getAvailableStock(p);
    if (avail === 0) return "OUT OF STOCK";
    if (avail <= p.reorder_level) return "LOW STOCK";
    return "HEALTHY";
}

// Intelligent Order Priority Calculator
function calculatePriorityScore(urgency, quantity, availableStock, sellingPrice = 0.0, unitCost = 0.0) {
    const urgencyVal = Math.min(10, Math.max(1, urgency));
    const urgencyPoints = urgencyVal * 3.5;
    const qtyPoints = Math.min(15.0, quantity * 0.3);
    const shortage = Math.max(0, quantity - availableStock);
    let shortagePoints = shortage > 0 ? 20.0 : 0.0;
    const basePoints = 15.0;

    const margin = sellingPrice - unitCost;
    const estProfit = quantity * margin;
    const financialBonus = Math.min(5.0, (Math.max(0.0, estProfit) / 10000.0) * 5.0);

    const totalScore = Math.floor(Math.min(100.0, Math.max(0.0, urgencyPoints + qtyPoints + shortagePoints + basePoints + financialBonus)));

    let priority = "Medium";
    let action = "Standard pick queue.";
    if (totalScore >= 80) {
        priority = "Critical";
        action = "Prioritize immediate allocation & dispatch.";
    } else if (totalScore >= 60) {
        priority = "High";
        action = "Run allocation check and queue.";
    }

    return { score: totalScore, level: priority, action };
}

// Picking Route Optimization Savings (Manhattan)
function calculatePickingRouteSavings(locations) {
    if (!locations || locations.length < 2) return { stdDist: 0, optDist: 0, pct: 0 };
    
    function parseLoc(loc) {
        if (!loc || typeof loc !== "string") return [1, 1, 1];
        const parts = loc.split("-");
        if (parts.length < 3) return [1, 1, 1];
        const zoneChar = parts[0].substring(0, 1).toUpperCase();
        const zone = zoneChar.charCodeAt(0) - 65 + 1;
        const aisle = parseInt(parts[1]) || 1;
        const shelf = parseInt(parts[2]) || 1;
        return [zone, aisle, shelf];
    }

    function dist(c1, c2) {
        return Math.abs(c1[0] - c2[0]) * 20 + Math.abs(c1[1] - c2[1]) * 10 + Math.abs(c1[2] - c2[2]) * 2;
    }

    const coords = locations.map(parseLoc);
    let stdDist = 0;
    for (let i = 0; i < coords.length - 1; i++) {
        stdDist += dist(coords[i], coords[i + 1]);
    }

    const sortedLocations = [...locations].sort();
    const sortedCoords = sortedLocations.map(parseLoc);
    let optDist = 0;
    for (let i = 0; i < sortedCoords.length - 1; i++) {
        optDist += dist(sortedCoords[i], sortedCoords[i + 1]);
    }

    const savings = Math.max(0, stdDist - optDist);
    const pct = stdDist > 0 ? (savings / stdDist) * 100 : 0;

    return { stdDist, optDist, pct: pct.toFixed(1), sortedLocations };
}

// ==========================================
// ROLE SWITCHING ENGINE
// ==========================================
function changeActiveRole(role) {
    state.activeRole = role;
    saveState();
    
    // Update Header Display
    document.getElementById("user-role-display").innerText = `${role} (penkekalyan3)`;
    
    // Setup Header Avatar depending on role
    const avatar = document.getElementById("user-role-avatar");
    if (role === "Admin") avatar.className = "fa-solid fa-user-shield text-blue";
    else if (role === "Manager") avatar.className = "fa-solid fa-user-tie text-yellow";
    else if (role === "Staff") avatar.className = "fa-solid fa-user-gear text-green";
    else avatar.className = "fa-solid fa-user text-muted";

    addActivityLog(state.activeRole, `Switched view perspective to role: ${role}`);
    showToast(`Logged in as ${role}`, "info");

    applyRolePermissions();
    
    // Switch to Dashboard section by default when switching roles
    document.querySelector(".nav-item[data-target='dashboard']").click();
}

function applyRolePermissions() {
    const role = state.activeRole;
    const navItems = document.querySelectorAll(".sidebar-nav li.nav-item");
    
    navItems.forEach(item => {
        const allowedRoles = item.getAttribute("data-roles");
        if (!allowedRoles) {
            item.style.display = ""; // visible to everyone
            return;
        }
        
        const rolesList = allowedRoles.split(",");
        if (rolesList.includes(role)) {
            item.style.display = ""; // visible
        } else {
            item.style.display = "none"; // hidden
        }
    });

    // Disable/Enable CRUD Buttons on Inventory screen depending on role
    const addProductBtn = document.getElementById("inv-add-product-btn");
    if (addProductBtn) {
        if (role === "Admin") {
            addProductBtn.removeAttribute("disabled");
            addProductBtn.style.opacity = "1";
        } else {
            addProductBtn.setAttribute("disabled", "true");
            addProductBtn.style.opacity = "0.4";
        }
    }
}

// ==========================================
// INITIAL DATABASE SEEDERS
// ==========================================
function resetLocalDataset() {
    localStorage.removeItem("smart_fulfill_v2_db");
    
    state.activeRole = "Admin";
    state.products = JSON.parse(JSON.stringify(defaultProducts));
    state.orders = JSON.parse(JSON.stringify(defaultOrders));
    state.customers = JSON.parse(JSON.stringify(defaultCustomers));
    state.warehouseZones = JSON.parse(JSON.stringify(defaultZones));
    
    // Seed transactions
    state.transactions = [];
    state.orders.forEach(o => {
        const prod = state.products.find(p => p.product_code === o.product_code);
        const subtotal = o.quantity * (prod ? prod.selling_price : 0);
        state.transactions.push({
            transaction_reference: `TXN-${o.order_code}`,
            order_code: o.order_code,
            customer: o.customer,
            product_code: o.product_code,
            quantity: o.quantity,
            total_amount: o.total_amount,
            payment_method: "UPI",
            payment_status: o.status === "Delivered" ? "Paid" : "Pending Payment",
            created_at: o.created_at
        });
    });

    state.pickingTasks = [
        { id: "PCK001", order_code: "ORD002", product_code: "P007", quantity: 1, location: "B2-01-02", status: "Picking", created_at: new Date().toISOString() }
    ];
    state.packingOps = [];
    state.qualityChecks = [];
    state.exceptions = [];
    state.backorders = [];
    state.allocations = [];
    state.inventoryTransactions = [
        { product_code: "P001", transaction_type: "IN", quantity: 45, previous_stock: 0, new_stock: 45, reason: "First Load Seeding", performed_by: "System Engine", created_at: new Date().toISOString() }
    ];

    state.activityLogs = [
        { role: "System", action: "Seeded initial hackathon demo database", date: new Date().toLocaleDateString(), time: new Date().toLocaleTimeString() }
    ];

    state.logs = [
        { type: "success", message: "[DATABASE] Cleaned database successfully seeded!" }
    ];

    saveState();
    showToast("Sample database loaded successfully!", "success");
    renderAll();
}

// ==========================================
// RENDER ALL SYSTEMS
// ==========================================
function renderAll() {
    populateProductSelectors();
    populateReturnOrderSelectors();
    
    renderDashboard();
    renderInventory();
    renderPredictions();
    renderOrders();
    renderTransactions();
    renderReturns();
    renderAllocation();
    renderPicking();
    renderPacking();
    renderQuality();
    renderExceptions();
    renderBackorders();
    renderWarehouseZones();
    renderCustomers();
    renderActivityLog();
    renderDemoConsole();
}

// 1. DASHBOARD
function renderDashboard() {
    // Operations Metrics
    const totalProd = state.products.length;
    const totalOrd = state.orders.length;
    
    let availStock = 0;
    let lowStock = 0;
    state.products.forEach(p => {
        const avail = getAvailableStock(p);
        availStock += avail;
        if (getStockStatus(p) === "LOW STOCK" || getStockStatus(p) === "OUT OF STOCK") {
            lowStock++;
        }
    });

    const pending = state.orders.filter(o => o.status === "Pending").length;
    const processing = state.orders.filter(o => o.status === "Processing").length;
    const shipped = state.orders.filter(o => o.status === "Shipped" || o.status === "Out for Delivery").length;
    const delivered = state.orders.filter(o => o.status === "Delivered").length;
    const cancelled = state.orders.filter(o => o.status === "Cancelled").length;

    // Today's Date helpers
    const todayStr = new Date().toLocaleDateString();
    let todaysOrders = 0;
    let todaysRevenue = 0;
    let totalRevenue = 0;

    state.transactions.forEach(t => {
        if (t.payment_status === "Paid") {
            totalRevenue += t.total_amount;
            const txnDate = new Date(t.created_at).toLocaleDateString();
            if (txnDate === todayStr) {
                todaysRevenue += t.total_amount;
            }
        }
    });

    state.orders.forEach(o => {
        const orderDate = new Date(o.created_at).toLocaleDateString();
        if (orderDate === todayStr) {
            todaysOrders++;
        }
    });

    // Update operational views
    document.getElementById("db-total-products").innerText = totalProd;
    document.getElementById("db-available-stock").innerText = availStock;
    document.getElementById("db-low-stock").innerText = lowStock;
    document.getElementById("db-total-orders").innerText = totalOrd;
    document.getElementById("db-pending-orders").innerText = pending;
    document.getElementById("db-processing-orders").innerText = processing;
    document.getElementById("db-shipped-orders").innerText = shipped;
    document.getElementById("db-delivered-orders").innerText = delivered;
    document.getElementById("db-cancelled-orders").innerText = cancelled;
    document.getElementById("db-todays-orders").innerText = todaysOrders;

    // Financial calculations
    let totalInvVal = 0;
    let potentialSalesVal = 0;
    let potentialProfit = 0;

    state.products.forEach(p => {
        const avail = getAvailableStock(p);
        totalInvVal += p.total_stock * p.unit_cost;
        potentialSalesVal += avail * p.selling_price;
        potentialProfit += avail * (p.selling_price - p.unit_cost);
    });

    document.getElementById("db-total-revenue").innerText = formatINR(totalRevenue);
    document.getElementById("db-todays-revenue").innerText = formatINR(todaysRevenue);
    document.getElementById("db-total-inv-val").innerText = formatINR(totalInvVal);
    document.getElementById("db-potential-sales-val").innerText = formatINR(potentialSalesVal);
    document.getElementById("db-potential-profit").innerText = formatINR(potentialProfit);

    // AI Risk calculation
    const openExceptions = state.exceptions.filter(e => e.status === "Open").length;
    const calculatedRisk = Math.min(100, (openExceptions * 20) + (lowStock * 10) + (pending * 5));
    
    const riskBadge = document.getElementById("db-risk-badge");
    const riskFill = document.getElementById("db-risk-fill");
    const riskScoreText = document.getElementById("db-risk-score");

    riskScoreText.innerText = `Warehouse Risk Score: ${calculatedRisk}/100`;
    riskFill.style.width = `${calculatedRisk}%`;

    if (calculatedRisk >= 60) {
        riskBadge.innerText = "HIGH";
        riskBadge.style.backgroundColor = "var(--danger)";
        riskFill.style.backgroundColor = "var(--danger)";
    } else if (calculatedRisk >= 30) {
        riskBadge.innerText = "MEDIUM";
        riskBadge.style.backgroundColor = "var(--warning)";
        riskFill.style.backgroundColor = "var(--warning)";
    } else {
        riskBadge.innerText = "LOW";
        riskBadge.style.backgroundColor = "var(--success)";
        riskFill.style.backgroundColor = "var(--success)";
    }

    // Dynamic alert generation
    const alertList = document.getElementById("db-alerts-list");
    alertList.innerHTML = "";
    
    state.products.forEach(p => {
        const avail = getAvailableStock(p);
        if (avail === 0) {
            alertList.innerHTML += `<div class="alert-item alert-danger"><i class="fa-solid fa-circle-xmark"></i> <div><strong>Depleted Stock:</strong> SKU ${p.product_code} (${p.name}) is fully OUT OF STOCK.</div></div>`;
        } else if (avail <= p.reorder_level) {
            alertList.innerHTML += `<div class="alert-item alert-warning"><i class="fa-solid fa-triangle-exclamation"></i> <div><strong>Reorder Level Reached:</strong> SKU ${p.product_code} stock is ${avail} (Reorder level is ${p.reorder_level}).</div></div>`;
        }
    });

    state.exceptions.forEach(e => {
        if (e.status === "Open") {
            alertList.innerHTML += `<div class="alert-item alert-danger"><i class="fa-solid fa-triangle-exclamation"></i> <div><strong>Open Exception:</strong> Order ${e.order_code} flags '${e.exception_type}': ${e.description}</div></div>`;
        }
    });

    if (alertList.innerHTML === "") {
        alertList.innerHTML = `<div class="alert-item alert-success"><i class="fa-solid fa-circle-check"></i> <div>All systems optimal. No alerts recorded.</div></div>`;
    }

    renderCharts();
}

// 2. SMART INVENTORY
function renderInventory() {
    const tbody = document.getElementById("inv-table-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.products.forEach(p => {
        const avail = getAvailableStock(p);
        const status = getStockStatus(p);
        
        let statusClass = "bg-green";
        if (status === "LOW STOCK") statusClass = "bg-yellow";
        if (status === "OUT OF STOCK") statusClass = "bg-red";

        tbody.innerHTML += `
            <tr data-category="${p.category}" data-location="${p.location.substring(0, 2)}" data-status="${status}">
                <td><strong>${p.product_code}</strong></td>
                <td>${p.name}</td>
                <td>${p.category}</td>
                <td><strong>${formatINR(p.selling_price)}</strong></td>
                <td><strong>${avail}</strong></td>
                <td>${p.total_stock}</td>
                <td>${p.reorder_level}</td>
                <td><span class="badge bg-blue"><i class="fa-solid fa-location-dot"></i> ${p.location}</span></td>
                <td>${p.supplier || 'N/A'}</td>
                <td><span class="badge ${statusClass}">${status}</span></td>
                <td>
                    <div style="display: flex; gap: 6px;">
                        <button class="btn btn-secondary btn-sm" onclick="openProductModal('edit', '${p.product_code}')" ${state.activeRole !== 'Admin' ? 'disabled style="opacity:0.4;"' : ''}><i class="fa-solid fa-pen"></i></button>
                        <button class="btn btn-danger btn-sm" onclick="deleteProductClient('${p.product_code}')" ${state.activeRole !== 'Admin' ? 'disabled style="opacity:0.4;"' : ''}><i class="fa-solid fa-trash"></i></button>
                    </div>
                </td>
            </tr>
        `;
    });

    // Ledger transactions history
    const ledger = document.getElementById("inv-ledger-body");
    ledger.innerHTML = "";
    const sortedTxns = [...state.inventoryTransactions].sort((a,b) => new Date(b.created_at) - new Date(a.created_at));
    
    sortedTxns.slice(0, 10).forEach(t => {
        const typeBadge = t.transaction_type === "IN" ? "bg-green" : t.transaction_type === "OUT" ? "bg-red" : "bg-yellow";
        ledger.innerHTML += `
            <tr>
                <td><span class="badge ${typeBadge}">${t.transaction_type}</span></td>
                <td><strong>${t.product_code}</strong></td>
                <td>${t.quantity}</td>
                <td>${t.previous_stock} &rarr; ${t.new_stock}</td>
                <td>${t.reason}</td>
                <td>${t.performed_by}</td>
                <td><span style="font-size:0.75rem; color:var(--text-muted);">${new Date(t.created_at).toLocaleTimeString()}</span></td>
            </tr>
        `;
    });

    if (ledger.innerHTML === "") {
        ledger.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No stock logs recorded.</td></tr>`;
    }
}

// 3. SMART PREDICTION
function renderPredictions() {
    const tbody = document.getElementById("prediction-table-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.products.forEach(p => {
        const avail = getAvailableStock(p);
        
        // Dynamic sales velocity simulation: calculate recent sales from transactions
        let recentSales = 0;
        state.transactions.forEach(t => {
            if (t.product_code === p.product_code && t.payment_status === "Paid") {
                recentSales += t.quantity;
            }
        });
        
        // Pad sales slightly for the simulator if empty so it looks realistic
        if (recentSales === 0) {
            recentSales = p.product_code === "P002" ? 18 : p.product_code === "P007" ? 12 : 5;
        }

        const avgDailySales = parseFloat((recentSales / 14).toFixed(2)); // over 14 days
        const daysRemaining = avgDailySales > 0 ? Math.ceil(avail / avgDailySales) : 999;
        
        let msg = "Inventory healthy";
        let levelClass = "bg-green";

        if (avail === 0) {
            msg = "Reorder immediately (Depleted)";
            levelClass = "bg-red";
        } else if (daysRemaining <= 3) {
            msg = `Critical: Stock runs out in ${daysRemaining} days`;
            levelClass = "bg-red";
        } else if (daysRemaining <= 10) {
            msg = `Warning: Reorder recommended (${daysRemaining} days remaining)`;
            levelClass = "bg-yellow";
        } else if (recentSales >= 10) {
            msg = "High demand product (Monitor closely)";
            levelClass = "bg-blue";
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${p.product_code}</strong></td>
                <td>${p.name}</td>
                <td><strong>${avail}</strong></td>
                <td>${recentSales} units (14d)</td>
                <td>${avgDailySales} units/day</td>
                <td><strong>${daysRemaining === 999 ? 'No active sales' : daysRemaining + ' days'}</strong></td>
                <td><strong>${daysRemaining <= 10 ? p.reorder_quantity : 0} units</strong></td>
                <td><span class="badge ${levelClass}">${msg}</span></td>
            </tr>
        `;
    });
}

// 4. ORDER MANAGEMENT
function renderOrders() {
    const tbody = document.getElementById("orders-board-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.orders.forEach(o => {
        let statusClass = "bg-blue";
        if (o.status === "Processing") statusClass = "bg-yellow";
        if (o.status === "Packed") statusClass = "bg-yellow";
        if (o.status === "Shipped" || o.status === "Out for Delivery") statusClass = "bg-blue";
        if (o.status === "Delivered") statusClass = "bg-green";
        if (o.status === "Cancelled") statusClass = "bg-red";

        // Operations actions based on current workflow status:
        // Pending -> Processing -> Packed -> Shipped -> Out for Delivery -> Delivered
        let actions = "";
        
        // Check permissions: Warehouse Staff can edit workflow, Manager/Admin can too
        const isStaffOrAbove = ["Admin", "Manager", "Staff"].includes(state.activeRole);

        if (isStaffOrAbove) {
            if (o.status === "Pending") {
                actions = `<button class="btn btn-success btn-sm" onclick="advanceOrderStatus('${o.order_code}', 'Processing')">Confirm & Process</button>`;
            } else if (o.status === "Processing") {
                actions = `<button class="btn btn-primary btn-sm" onclick="advanceOrderStatus('${o.order_code}', 'Packed')">Mark Packed</button>`;
            } else if (o.status === "Packed") {
                actions = `<button class="btn btn-secondary btn-sm" onclick="advanceOrderStatus('${o.order_code}', 'Shipped')">Ship Order</button>`;
            } else if (o.status === "Shipped") {
                actions = `<button class="btn btn-secondary btn-sm" onclick="advanceOrderStatus('${o.order_code}', 'Out for Delivery')">Out for Delivery</button>`;
            } else if (o.status === "Out for Delivery") {
                actions = `<button class="btn btn-success btn-sm" onclick="advanceOrderStatus('${o.order_code}', 'Delivered')">Confirm Delivered</button>`;
            }
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${o.order_code}</strong></td>
                <td>${o.customer}</td>
                <td><strong>${o.product_code}</strong></td>
                <td>${o.quantity}</td>
                <td><span class="badge bg-blue">${o.priority_score || 50}</span></td>
                <td><strong>${formatINR(o.total_amount)}</strong></td>
                <td><span style="font-size: 0.8rem; color: var(--text-secondary);">${new Date(o.created_at).toLocaleDateString()}</span></td>
                <td><span class="badge ${statusClass}">${o.status}</span></td>
                <td>
                    <div style="display:flex; gap:6px;">
                        ${actions}
                        ${["Pending", "Processing"].includes(o.status) && isStaffOrAbove ? 
                          `<button class="btn btn-danger btn-sm" onclick="cancelOrderClient('${o.order_code}')"><i class="fa-solid fa-ban"></i></button>` : ''}
                    </div>
                </td>
            </tr>
        `;
    });
}

function updateOrderPreview() {
    const pCode = document.getElementById("ord-product").value;
    const qty = parseInt(document.getElementById("ord-qty").value) || 0;
    const urgency = parseInt(document.getElementById("ord-urgency").value) || 5;

    document.getElementById("ord-urgency-val").innerText = urgency;

    const prod = state.products.find(p => p.product_code === pCode);
    if (!prod) return;

    const avail = getAvailableStock(prod);
    const shortage = Math.max(0, qty - avail);
    const subtotal = qty * prod.selling_price;
    const estProfit = qty * (prod.selling_price - prod.unit_cost);

    const calc = calculatePriorityScore(urgency, qty, avail, prod.selling_price, prod.unit_cost);

    document.getElementById("pre-avail-stock").innerText = avail;
    document.getElementById("pre-shortage").innerText = shortage;
    document.getElementById("pre-price").innerText = formatINR(prod.selling_price);
    document.getElementById("pre-value").innerText = formatINR(subtotal);
    document.getElementById("pre-profit").innerText = formatINR(estProfit);
    document.getElementById("pre-priority-score").innerText = calc.score;
    
    const badge = document.getElementById("pre-priority-level");
    badge.innerText = calc.level;
    badge.className = `badge ${calc.level === 'Critical' ? 'bg-red' : 'bg-yellow'}`;

    document.getElementById("pre-explanation").innerText = `Action: ${calc.action}`;
}

// Order Management submissions
document.getElementById("create-order-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const customer = document.getElementById("ord-customer").value;
    const phone = document.getElementById("ord-phone").value;
    const address = document.getElementById("ord-address").value;
    const pCode = document.getElementById("ord-product").value;
    const qty = parseInt(document.getElementById("ord-qty").value);
    const urgency = parseInt(document.getElementById("ord-urgency").value);

    const prod = state.products.find(p => p.product_code === pCode);
    if (!prod) return;

    const avail = getAvailableStock(prod);
    
    // Prevent checkout if stock unavailable
    if (qty > avail) {
        showToast(`Checkout Rejected: Only ${avail} units of ${prod.name} available!`, "danger");
        addActivityLog(state.activeRole, `Attempted order placement of ${qty}x ${prod.name} failed due to shortage.`);
        return;
    }

    const calc = calculatePriorityScore(urgency, qty, avail, prod.selling_price, prod.unit_cost);

    const lastIdNum = state.orders.length > 0 ? parseInt(state.orders[state.orders.length - 1].order_code.substring(3)) : 0;
    const nextCode = `ORD${(lastIdNum + 1).toString().padStart(3, '0')}`;

    const newOrder = {
        order_code: nextCode,
        customer,
        email: phone.includes("@") ? phone : "customer@example.com",
        phone: phone.includes("@") ? "+91 99999 88888" : phone,
        product_code: pCode,
        quantity: qty,
        total_amount: qty * prod.selling_price,
        priority: calc.level,
        priority_score: calc.score,
        status: "Pending",
        created_at: new Date().toISOString(),
        address
    };

    state.orders.push(newOrder);

    // Save transaction
    state.transactions.push({
        transaction_reference: `TXN-${nextCode}`,
        order_code: nextCode,
        customer,
        product_code: pCode,
        quantity: qty,
        total_amount: qty * prod.selling_price,
        payment_method: "Cash on Delivery",
        payment_status: "Pending Payment",
        created_at: new Date().toISOString()
    });

    // Check if customer exists in database, else create one
    let cust = state.customers.find(c => c.name.toLowerCase() === customer.toLowerCase());
    if (!cust) {
        state.customers.push({
            name: customer,
            email: phone.includes("@") ? phone : "newcustomer@example.com",
            phone: phone.includes("@") ? "+91 90000 00000" : phone,
            total_orders: 1,
            total_spending: qty * prod.selling_price,
            last_order: nextCode
        });
    } else {
        cust.total_orders += 1;
        cust.total_spending += qty * prod.selling_price;
        cust.last_order = nextCode;
    }

    saveState();
    logEvent("info", `Sales order ${nextCode} generated for ${customer}. Amount: ${formatINR(qty * prod.selling_price)}.`);
    addActivityLog(state.activeRole, `Created sales order ${nextCode} for customer: ${customer}`);
    showToast(`Order ${nextCode} created successfully!`, "success");

    // reset fields
    document.getElementById("ord-customer").value = "";
    document.getElementById("ord-phone").value = "";
    document.getElementById("ord-address").value = "";
    document.getElementById("ord-qty").value = 1;
    document.getElementById("ord-urgency").value = 5;

    renderAll();
});

// Update workflow order status
function advanceOrderStatus(orderCode, nextStatus) {
    const o = state.orders.find(ord => ord.order_code === orderCode);
    if (!o) return;

    const previousStatus = o.status;
    o.status = nextStatus;

    const prod = state.products.find(p => p.product_code === o.product_code);

    // Automatically update inventory when order is CONFIRMED (Pending -> Processing)
    if (previousStatus === "Pending" && nextStatus === "Processing") {
        if (prod) {
            const prevStock = prod.total_stock;
            
            // Subtract from stock levels
            prod.total_stock -= o.quantity;
            
            // Log inventory transaction
            state.inventoryTransactions.push({
                product_code: o.product_code,
                transaction_type: "OUT",
                quantity: o.quantity,
                previous_stock: prevStock,
                new_stock: prod.total_stock,
                reason: `Sales Order ${orderCode} Confirmed`,
                performed_by: "Workflow Engine",
                created_at: new Date().toISOString()
            });

            // Adjust Visual Warehouse capacity Zone occupancy
            const zoneCode = prod.location.substring(0, 2);
            const zone = state.warehouseZones.find(z => z.code === zoneCode);
            if (zone) {
                zone.occupied = Math.max(0, zone.occupied - o.quantity);
            }
        }
        showToast(`Order ${orderCode} Confirmed. Stock deducted automatically!`, "success");
    }

    // Auto add picking task when Shifting to Processing
    if (nextStatus === "Processing") {
        const lastPckNum = state.pickingTasks.length > 0 ? parseInt(state.pickingTasks[state.pickingTasks.length - 1].id.substring(3)) : 0;
        state.pickingTasks.push({
            id: `PCK${(lastPckNum + 1).toString().padStart(3, '0')}`,
            order_code: orderCode,
            product_code: o.product_code,
            quantity: o.quantity,
            location: prod ? prod.location : "C1-01-01",
            status: "Picking",
            created_at: new Date().toISOString()
        });
    }

    // If order delivered, clear payments
    if (nextStatus === "Delivered") {
        const txn = state.transactions.find(t => t.order_code === orderCode);
        if (txn) {
            txn.payment_status = "Paid";
        }
    }

    saveState();
    logEvent("success", `Order ${orderCode} status advanced: ${previousStatus} &rarr; ${nextStatus}.`);
    addActivityLog(state.activeRole, `Updated order status ${orderCode} to: ${nextStatus}`);
    renderAll();
}

function cancelOrderClient(orderCode) {
    const o = state.orders.find(ord => ord.order_code === orderCode);
    if (!o) return;

    const previousStatus = o.status;
    o.status = "Cancelled";

    // Revert stock if it was already processing/deducted
    if (previousStatus !== "Pending") {
        const prod = state.products.find(p => p.product_code === o.product_code);
        if (prod) {
            const prevStock = prod.total_stock;
            prod.total_stock += o.quantity;

            state.inventoryTransactions.push({
                product_code: o.product_code,
                transaction_type: "IN",
                quantity: o.quantity,
                previous_stock: prevStock,
                new_stock: prod.total_stock,
                reason: `Order ${orderCode} Cancellation Reversal`,
                performed_by: "Workflow Engine",
                created_at: new Date().toISOString()
            });

            const zoneCode = prod.location.substring(0, 2);
            const zone = state.warehouseZones.find(z => z.code === zoneCode);
            if (zone) {
                zone.occupied = Math.min(zone.capacity, zone.occupied + o.quantity);
            }
        }
    }

    const txn = state.transactions.find(t => t.order_code === orderCode);
    if (txn) {
        txn.payment_status = "Cancelled";
    }

    saveState();
    logEvent("danger", `Order ${orderCode} cancelled successfully.`);
    addActivityLog(state.activeRole, `Cancelled sales order: ${orderCode}`);
    showToast(`Order ${orderCode} cancelled.`, "warning");
    renderAll();
}

// 5. ORDER TRANSACTIONS
function renderTransactions() {
    let totalSales = 0;
    let paidVal = 0;
    let pendingVal = 0;

    state.transactions.forEach(t => {
        if (t.payment_status === "Paid") {
            totalSales += t.total_amount;
            paidVal += t.total_amount;
        } else if (t.payment_status === "Pending Payment") {
            totalSales += t.total_amount;
            pendingVal += t.total_amount;
        }
    });

    document.getElementById("ar-total-sales").innerText = formatINR(totalSales);
    document.getElementById("ar-paid-amount").innerText = formatINR(paidVal);
    document.getElementById("ar-pending-amount").innerText = formatINR(pendingVal);

    const tbody = document.getElementById("transactions-ledger-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.transactions.forEach(t => {
        const isPaid = t.payment_status === "Paid";
        
        let action = "";
        if (!isPaid && t.payment_status !== "Cancelled") {
            action = `<button class="btn btn-success btn-sm" onclick="confirmPaymentClient('${t.order_code}')">Confirm Payment</button>`;
        } else if (t.payment_status === "Cancelled") {
            action = `<span class="badge bg-red">Cancelled</span>`;
        } else {
            action = `<span class="badge bg-green"><i class="fa-solid fa-circle-check"></i> Paid</span>`;
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${t.transaction_reference}</strong></td>
                <td><strong>${t.order_code}</strong></td>
                <td>${t.customer}</td>
                <td>${t.quantity}</td>
                <td><strong>${formatINR(t.total_amount)}</strong></td>
                <td>${t.payment_method}</td>
                <td><span class="badge ${isPaid ? 'bg-green' : t.payment_status === 'Cancelled' ? 'bg-red' : 'bg-yellow'}">${t.payment_status}</span></td>
                <td>${action}</td>
            </tr>
        `;
    });
}

function confirmPaymentClient(orderCode) {
    const txn = state.transactions.find(t => t.order_code === orderCode);
    if (txn) {
        txn.payment_status = "Paid";
        saveState();
        logEvent("success", `AR Invoice paid for Order ${orderCode}. Amount: ${formatINR(txn.total_amount)}.`);
        addActivityLog(state.activeRole, `Confirmed invoice payment for order: ${orderCode}`);
        showToast("Payment confirmed successfully!", "success");
        renderAll();
    }
}

// 6. RETURN MANAGEMENT
function renderReturns() {
    const tbody = document.getElementById("returns-board-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.returns.forEach(r => {
        let action = "";
        if (r.status === "Requested") {
            action = `
                <button class="btn btn-primary btn-sm" onclick="updateReturnStatus('${r.return_code}', 'Received')">Receive Item</button>
            `;
        } else if (r.status === "Received") {
            action = `
                <button class="btn btn-secondary btn-sm" onclick="updateReturnStatus('${r.return_code}', 'Inspection')">Inspect Item</button>
            `;
        } else if (r.status === "Inspection") {
            action = `
                <button class="btn btn-success btn-sm" onclick="completeInspection('${r.return_code}', 'Approved for Refund', 'Resellable')">Approve & Restock</button>
                <button class="btn btn-danger btn-sm" onclick="completeInspection('${r.return_code}', 'Approved for Refund', 'Damaged')">Approve (Scrap)</button>
            `;
        } else if (r.status === "Approved for Refund") {
            action = `<button class="btn btn-success btn-sm" onclick="processRefundClient('${r.return_code}')">Process Refund</button>`;
        } else {
            action = `<span class="badge bg-green">RMA Complete</span>`;
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${r.return_code}</strong></td>
                <td><strong>${r.order_code}</strong></td>
                <td>${r.customer}</td>
                <td><strong>${r.product_code}</strong></td>
                <td>${r.quantity}</td>
                <td>${r.reason}</td>
                <td><span class="badge bg-blue">${r.inspection_condition || 'Pending'}</span></td>
                <td>${formatINR(r.refund_amount)}</td>
                <td><span class="badge ${r.status === 'Refunded' ? 'bg-green' : 'bg-yellow'}">${r.status}</span></td>
                <td>${action}</td>
            </tr>
        `;
    });
}

function populateReturnOrderSelectors() {
    const select = document.getElementById("ret-order-select");
    if (!select) return;
    select.innerHTML = "<option value=''>Select Completed Order</option>";
    state.orders.forEach(o => {
        if (o.status === "Delivered") {
            select.innerHTML += `<option value="${o.order_code}">${o.order_code} - ${o.customer} (${o.product_code})</option>`;
        }
    });
}

function updateReturnPreview() {
    const orderCode = document.getElementById("ret-order-select").value;
    const preview = document.getElementById("ret-order-preview");
    if (!orderCode) {
        preview.innerText = "Select an order to view customer and details.";
        return;
    }

    const order = state.orders.find(o => o.order_code === orderCode);
    const prod = state.products.find(p => p.product_code === order.product_code);

    preview.innerHTML = `
        <strong>Customer:</strong> ${order.customer} | <strong>Product:</strong> ${order.product_code} (${prod ? prod.name : 'N/A'})<br>
        <strong>Delivered Qty:</strong> ${order.quantity} units | <strong>Value:</strong> ${formatINR(order.total_amount)}
    `;
    document.getElementById("ret-qty").max = order.quantity;
    document.getElementById("ret-qty").value = order.quantity;
}

document.getElementById("create-return-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const orderCode = document.getElementById("ret-order-select").value;
    const qty = parseInt(document.getElementById("ret-qty").value);
    const reason = document.getElementById("ret-reason").value;
    const desc = document.getElementById("ret-desc").value;

    const order = state.orders.find(o => o.order_code === orderCode);
    const prod = state.products.find(p => p.product_code === order.product_code);
    const price = prod ? prod.selling_price : 0;

    const lastId = state.returns.length > 0 ? parseInt(state.returns[state.returns.length - 1].return_code.substring(3)) : 0;
    const nextCode = `RET${(lastId + 1).toString().padStart(3, '0')}`;

    state.returns.push({
        return_code: nextCode,
        order_code: orderCode,
        customer: order.customer,
        product_code: order.product_code,
        quantity: qty,
        reason,
        description: desc,
        status: "Requested",
        inspection_condition: "Pending",
        refund_amount: qty * price,
        requested_at: new Date().toISOString()
    });

    saveState();
    logEvent("warning", `RMA filed for Order ${orderCode}. Return Code: ${nextCode}.`);
    addActivityLog(state.activeRole, `Filed RMA return request ${nextCode} for order: ${orderCode}`);
    showToast(`RMA return filed successfully. Code: ${nextCode}`, "warning");

    document.getElementById("ret-order-select").value = "";
    document.getElementById("ret-order-preview").innerText = "Select an order to view customer and details.";
    document.getElementById("ret-desc").value = "";

    renderAll();
});

function updateReturnStatus(returnCode, nextStatus) {
    const ret = state.returns.find(r => r.return_code === returnCode);
    if (ret) {
        ret.status = nextStatus;
        saveState();
        logEvent("info", `RMA ${returnCode} advanced to status: ${nextStatus}.`);
        renderAll();
    }
}

function completeInspection(returnCode, nextStatus, condition) {
    const ret = state.returns.find(r => r.return_code === returnCode);
    if (ret) {
        ret.status = nextStatus;
        ret.inspection_condition = condition;

        // If resellable, automatically restock returned product
        if (condition === "Resellable") {
            const prod = state.products.find(p => p.product_code === ret.product_code);
            if (prod) {
                const prev = prod.total_stock;
                prod.total_stock += ret.quantity;

                // Log inventory log
                state.inventoryTransactions.push({
                    product_code: prod.product_code,
                    transaction_type: "IN",
                    quantity: ret.quantity,
                    previous_stock: prev,
                    new_stock: prod.total_stock,
                    reason: `RMA Restock: ${returnCode}`,
                    performed_by: "RMA Agent",
                    created_at: new Date().toISOString()
                });

                // adjust visual zone occupancy
                const zoneCode = prod.location.substring(0, 2);
                const zone = state.warehouseZones.find(z => z.code === zoneCode);
                if (zone) {
                    zone.occupied = Math.min(zone.capacity, zone.occupied + ret.quantity);
                }
            }
            showToast(`RMA restocked automatically into inventory!`, "success");
        }

        saveState();
        logEvent("success", `RMA ${returnCode} inspection complete. Condition: ${condition}.`);
        addActivityLog(state.activeRole, `Processed RMA inspection for ${returnCode}. Condition: ${condition}`);
        renderAll();
    }
}

function processRefundClient(returnCode) {
    const ret = state.returns.find(r => r.return_code === returnCode);
    if (ret) {
        ret.status = "Refunded";
        
        // Find order transaction and void or set status
        const txn = state.transactions.find(t => t.order_code === ret.order_code);
        if (txn) {
            txn.payment_status = "Refunded";
        }

        saveState();
        logEvent("success", `Refund of ${formatINR(ret.refund_amount)} issued for Return ${returnCode}.`);
        addActivityLog(state.activeRole, `Issued refund for return reference: ${returnCode}`);
        showToast("Refund processed successfully!", "success");
        renderAll();
    }
}

// 7. SMART ALLOCATION
function renderAllocation() {
    const tbody = document.getElementById("allocation-queue-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    
    // Select pending orders
    const pending = state.orders.filter(o => o.status === "Pending");

    pending.forEach(o => {
        const prod = state.products.find(p => p.product_code === o.product_code);
        const avail = prod ? getAvailableStock(prod) : 0;
        
        let rec = "";
        let details = "";
        let action = "";

        if (avail >= o.quantity) {
            rec = `<span class="badge bg-green">${prod.location.substring(0, 2)}</span> (Optimal Pick Area)`;
            details = `Recommended picking location: <strong>${prod.location}</strong>. Stock is healthy.`;
            action = `<button class="btn btn-success btn-sm" onclick="advanceOrderStatus('${o.order_code}', 'Processing')">Approve & Queue</button>`;
        } else {
            rec = `<span class="badge bg-red">HOLD</span>`;
            details = `Insufficient stock available. Backorder recommended.`;
            action = `<button class="btn btn-danger btn-sm" onclick="cancelOrderClient('${o.order_code}')">Cancel Order</button>`;
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${o.order_code}</strong></td>
                <td><strong>${o.product_code}</strong></td>
                <td>${o.quantity} units</td>
                <td>${avail} units</td>
                <td>${rec}</td>
                <td><span style="font-size:0.85rem;">${details}</span></td>
                <td>${action}</td>
            </tr>
        `;
    });

    if (tbody.innerHTML === "") {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No orders awaiting smart allocation check.</td></tr>`;
    }
}

// 8. PICKING WORKFLOW
function renderPicking() {
    const tbody = document.getElementById("picking-tasks-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    const activeLocations = [];

    state.pickingTasks.forEach(p => {
        if (p.status === "Picking") {
            activeLocations.push(p.location);
        }

        let action = "";
        if (p.status === "Picking") {
            action = `<button class="btn btn-success btn-sm" onclick="completePickingTask('${p.id}')">Complete Pick</button>`;
        } else {
            action = `<span class="badge bg-green"><i class="fa-solid fa-check"></i> Picked</span>`;
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${p.id}</strong></td>
                <td><strong>${p.order_code}</strong></td>
                <td>${p.product_code}</td>
                <td><span class="badge bg-blue">${p.location}</span></td>
                <td>${p.quantity} units</td>
                <td><span class="badge ${p.status === 'Picking' ? 'bg-yellow' : 'bg-green'}">${p.status}</span></td>
                <td>${action}</td>
            </tr>
        `;
    });

    if (tbody.innerHTML === "") {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No active pick tasks.</td></tr>`;
    }

    // Update optimized picker route path
    const calc = calculatePickingRouteSavings(activeLocations);
    document.getElementById("opt-std-dist").innerText = `${calc.stdDist} meters`;
    document.getElementById("opt-opt-dist").innerText = `${calc.optDist} meters`;
    document.getElementById("opt-savings").innerText = `${calc.pct}%`;

    const seq = document.getElementById("opt-sequence-list");
    seq.innerHTML = `<span class="node">Start (Loading Dock)</span>`;
    if (calc.sortedLocations && calc.sortedLocations.length > 0) {
        calc.sortedLocations.forEach(loc => {
            seq.innerHTML += `
                <span class="arrow"><i class="fa-solid fa-arrow-right"></i></span>
                <span class="node">${loc}</span>
            `;
        });
    }
    seq.innerHTML += `
        <span class="arrow"><i class="fa-solid fa-arrow-right"></i></span>
        <span class="node finish">Finish (Packing Aisle)</span>
    `;
}

function completePickingTask(taskId) {
    const task = state.pickingTasks.find(t => t.id === taskId);
    if (task) {
        task.status = "Picked";

        const order = state.orders.find(o => o.order_code === task.order_code);
        if (order) {
            order.status = "Picking Completed";
            
            // Automatically push to packing workflow queue
            state.packingOps.push({
                order_code: task.order_code,
                packaging_type: "Pending",
                packaging_cost: 0,
                status: "Pending",
                created_at: new Date().toISOString()
            });
        }

        saveState();
        logEvent("success", `Picker completed task ${taskId} at picking slot.`);
        addActivityLog(state.activeRole, `Completed picking task: ${taskId}`);
        renderAll();
    }
}

// 9. PACKING WORKFLOW
function renderPacking() {
    const tbody = document.getElementById("packing-queue-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.packingOps.forEach(p => {
        const order = state.orders.find(o => o.order_code === p.order_code);
        if (!order) return;

        let actions = "";
        if (p.status === "Pending") {
            actions = `
                <button class="btn btn-primary btn-sm" onclick="packOrderQuick('${p.order_code}', 'Small Box', 15.0)">Small Box (₹15)</button>
                <button class="btn btn-secondary btn-sm" onclick="packOrderQuick('${p.order_code}', 'Medium Box', 35.0)">Medium Box (₹35)</button>
                <button class="btn btn-success btn-sm" onclick="packOrderQuick('${p.order_code}', 'Pallet Box', 90.0)">Pallet Box (₹90)</button>
            `;
        } else {
            actions = `<span class="badge bg-green"><i class="fa-solid fa-check"></i> Packed (${p.packaging_type})</span>`;
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${p.order_code}</strong></td>
                <td>${order.product_code}</td>
                <td>${order.quantity} units</td>
                <td><span class="badge ${p.status === 'Pending' ? 'bg-yellow' : 'bg-green'}">${p.status}</span></td>
                <td>${p.packaging_type}</td>
                <td><strong>${formatINR(p.packaging_cost)}</strong></td>
                <td>${actions}</td>
            </tr>
        `;
    });

    if (tbody.innerHTML === "") {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No orders in packing list.</td></tr>`;
    }
}

function packOrderQuick(orderCode, type, cost) {
    const pack = state.packingOps.find(p => p.order_code === orderCode);
    if (pack) {
        pack.status = "Packed";
        pack.packaging_type = type;
        pack.packaging_cost = cost;

        const o = state.orders.find(ord => ord.order_code === orderCode);
        if (o) {
            o.status = "Packed";
            
            // Push to quality check queue
            state.qualityChecks.push({
                order_code: orderCode,
                product_code: o.product_code,
                quantity: o.quantity,
                checker: "QC Agent",
                status: "Pending"
            });
        }

        saveState();
        logEvent("success", `Packed Order ${orderCode} using ${type}. Cost: ${formatINR(cost)}.`);
        addActivityLog(state.activeRole, `Packed order ${orderCode} in container: ${type}`);
        renderAll();
    }
}

// 10. QUALITY CHECK
function renderQuality() {
    const tbody = document.getElementById("quality-queue-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.qualityChecks.forEach(q => {
        let action = "";
        if (q.status === "Pending") {
            action = `
                <button class="btn btn-success btn-sm" onclick="completeQC('${q.order_code}', 'Passed')">Pass</button>
                <button class="btn btn-danger btn-sm" onclick="completeQC('${q.order_code}', 'Failed')">Fail</button>
            `;
        } else {
            const isPass = q.status === "Passed";
            action = `<span class="badge ${isPass ? 'bg-green' : 'bg-red'}">${q.status}</span>`;
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${q.order_code}</strong></td>
                <td><strong>${q.product_code}</strong></td>
                <td>${q.quantity} units</td>
                <td>Automatic Checks</td>
                <td>${q.checker}</td>
                <td><span class="badge ${q.status === 'Pending' ? 'bg-yellow' : q.status === 'Passed' ? 'bg-green' : 'bg-red'}">${q.status}</span></td>
                <td>${action}</td>
            </tr>
        `;
    });

    if (tbody.innerHTML === "") {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No orders waiting for QC.</td></tr>`;
    }
}

function completeQC(orderCode, status) {
    const check = state.qualityChecks.find(q => q.order_code === orderCode);
    if (check) {
        check.status = status;

        const o = state.orders.find(ord => ord.order_code === orderCode);
        if (o) {
            if (status === "Passed") {
                o.status = "Ready for Shipment"; // transitions to workflow
                logEvent("success", `QC Verification Passed for Order ${orderCode}. Ready for shipping.`);
            } else {
                o.status = "Cancelled";
                
                // Add exception log
                const lastExp = state.exceptions.length > 0 ? parseInt(state.exceptions[state.exceptions.length - 1].id.substring(3)) : 0;
                state.exceptions.push({
                    id: `EXP${(lastExp + 1).toString().padStart(3, '0')}`,
                    order_code: orderCode,
                    exception_type: "Quality Failure",
                    description: `Order ${orderCode} failed quality checks. Order voided.`,
                    status: "Open",
                    created_at: new Date().toISOString()
                });
                logEvent("danger", `QC Verification FAILED for Order ${orderCode}. Exception logged.`);
            }
        }

        saveState();
        renderAll();
    }
}

// 11. EXCEPTION LOG
function renderExceptions() {
    const tbody = document.getElementById("exceptions-ledger-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.exceptions.forEach(e => {
        let action = "";
        if (e.status === "Open") {
            action = `<button class="btn btn-primary btn-sm" onclick="resolveExceptionClient('${e.id}')">Resolve</button>`;
        } else {
            action = `<span class="badge bg-green">Resolved</span>`;
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${e.id}</strong></td>
                <td><strong>${e.order_code}</strong></td>
                <td><span class="badge bg-red">${e.exception_type}</span></td>
                <td>${e.description}</td>
                <td><code style="color:#60a5fa;">Escalate & Void</code></td>
                <td>${new Date(e.created_at).toLocaleDateString()}</td>
                <td><span class="badge ${e.status === 'Open' ? 'bg-red' : 'bg-green'}">${e.status}</span></td>
                <td>${action}</td>
            </tr>
        `;
    });

    if (tbody.innerHTML === "") {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:var(--text-muted);">No exceptions recorded.</td></tr>`;
    }
}

function resolveExceptionClient(id) {
    const exp = state.exceptions.find(e => e.id === id);
    if (exp) {
        exp.status = "Resolved";
        saveState();
        logEvent("success", `Exception ${id} resolved.`);
        renderAll();
    }
}

// 12. BACKORDER MANAGEMENT
function renderBackorders() {
    const tbody = document.getElementById("backorders-ledger-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.backorders.forEach(b => {
        const prod = state.products.find(p => p.product_code === b.product_code);
        const avail = prod ? getAvailableStock(prod) : 0;

        let action = "";
        if (b.status === "Open" && avail >= b.quantity) {
            action = `<button class="btn btn-success btn-sm" onclick="fulfillBackorderClient('${b.id}')">Fulfill</button>`;
        } else if (b.status === "Open") {
            action = `<button class="btn btn-secondary btn-sm" disabled style="opacity:0.4;">Awaiting Stock</button>`;
        } else {
            action = `<span class="badge bg-green">${b.status}</span>`;
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${b.id}</strong></td>
                <td><strong>${b.order_code}</strong></td>
                <td><strong>${b.product_code}</strong></td>
                <td>${b.quantity} units</td>
                <td>${avail} available</td>
                <td><span class="badge ${b.status === 'Open' ? 'bg-yellow' : 'bg-green'}">${b.status}</span></td>
                <td>${action}</td>
            </tr>
        `;
    });

    if (tbody.innerHTML === "") {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No backordered queues.</td></tr>`;
    }
}

function fulfillBackorderClient(id) {
    const bko = state.backorders.find(b => b.id === id);
    if (bko) {
        const prod = state.products.find(p => p.product_code === bko.product_code);
        if (prod && getAvailableStock(prod) >= bko.quantity) {
            prod.reserved_stock += bko.quantity;
            bko.status = "Fulfilled";

            // Resolve shortage exception if any
            const exp = state.exceptions.find(e => e.order_code === bko.order_code && e.status === "Open");
            if (exp) exp.status = "Resolved";

            // release order back
            const o = state.orders.find(ord => ord.order_code === bko.order_code);
            if (o) o.status = "Pending";

            saveState();
            logEvent("success", `Backorder ${id} fulfilled using restocked inventory.`);
            renderAll();
        }
    }
}

// 13. TIMELINE (CUSTOMER ORDER TRACKING PORTAL)
function searchTimelineOrder() {
    const val = document.getElementById("timeline-order-input").value.trim().toUpperCase();
    if (!val) {
        showToast("Please enter an Order ID", "danger");
        return;
    }
    
    // Find order
    const order = state.orders.find(o => o.order_code === val);
    if (!order) {
        showToast(`Order ID ${val} not found in database!`, "danger");
        document.getElementById("trace-results-box").style.display = "none";
        return;
    }

    // Display timeline results
    document.getElementById("trace-results-box").style.display = "block";
    renderOrderTimeline(order);
}

function renderOrderTimeline(order) {
    const prod = state.products.find(p => p.product_code === order.product_code);
    
    document.getElementById("trace-customer").innerText = order.customer;
    document.getElementById("trace-product").innerText = `${order.product_code} (${prod ? prod.name : 'N/A'})`;
    document.getElementById("trace-value").innerText = formatINR(order.total_amount);
    
    const statusBadge = document.getElementById("trace-status");
    statusBadge.innerText = order.status;
    
    let colorClass = "bg-blue";
    if (order.status === "Delivered") colorClass = "bg-green";
    if (order.status === "Cancelled") colorClass = "bg-red";
    statusBadge.className = `badge ${colorClass}`;

    // Workflow Mapping (6 Stages):
    // 1. Order Placed (Pending)
    // 2. Processing (Processing / Allocated)
    // 3. Packed
    // 4. Shipped
    // 5. Out for Delivery
    // 6. Delivered
    const stages = ["Pending", "Processing", "Packed", "Shipped", "Out for Delivery", "Delivered"];
    
    // Determine active index
    let activeIndex = 1;
    if (order.status === "Pending") activeIndex = 1;
    else if (order.status === "Processing" || order.status === "Allocated") activeIndex = 2;
    else if (order.status === "Picking Completed" || order.status === "Packed") activeIndex = 3;
    else if (order.status === "Ready for Shipment" || order.status === "Shipped") activeIndex = 4;
    else if (order.status === "Out for Delivery") activeIndex = 5;
    else if (order.status === "Delivered") activeIndex = 6;
    else if (order.status === "Cancelled") activeIndex = 0; // Cancelled resets it

    const progressPct = activeIndex === 0 ? 0 : Math.round((activeIndex / 6) * 100);
    document.getElementById("trace-pct").innerText = `${progressPct}%`;
    document.getElementById("trace-progress-fill").style.width = `${progressPct}%`;

    // Reset styles
    for (let i = 1; i <= 6; i++) {
        const node = document.getElementById(`step-${i}`);
        if (!node) continue;
        node.className = "step-node";
        
        if (i < activeIndex) {
            node.classList.add("completed");
        } else if (i === activeIndex) {
            node.classList.add("active");
        } else {
            node.classList.add("pending");
        }
    }

    // Dynamic actions panel
    const actionPanel = document.getElementById("timeline-actions-panel");
    actionPanel.innerHTML = "";

    // Allow staff to update status in the timeline view as well
    const isStaff = ["Admin", "Manager", "Staff"].includes(state.activeRole);
    if (isStaff && order.status !== "Cancelled" && order.status !== "Delivered") {
        let next = "";
        let label = "";
        
        if (order.status === "Pending") { next = "Processing"; label = "Confirm Order"; }
        else if (order.status === "Processing") { next = "Packed"; label = "Pack Completed"; }
        else if (order.status === "Picking Completed" || order.status === "Packed") { next = "Shipped"; label = "Dispatch Carrier"; }
        else if (order.status === "Ready for Shipment" || order.status === "Shipped") { next = "Out for Delivery"; label = "Out for Delivery"; }
        else if (order.status === "Out for Delivery") { next = "Delivered"; label = "Confirm Delivery"; }

        if (next) {
            actionPanel.innerHTML = `<button class="btn btn-success" onclick="advanceOrderStatus('${order.order_code}', '${next}'); setTimeout(() => renderOrderTimeline(state.orders.find(o => o.order_code === '${order.order_code}')), 100);"><i class="fa-solid fa-truck-moving"></i> ${label}</button>`;
        }
    }
}

// 14. WAREHOUSE MANAGEMENT
function renderWarehouseZones() {
    const grid = document.getElementById("warehouse-zones-grid");
    if (!grid) return;

    grid.innerHTML = "";
    state.warehouseZones.forEach(z => {
        const pct = Math.round((z.occupied / z.capacity) * 100);
        let colorClass = "";
        if (pct >= 80) colorClass = "high";
        else if (pct >= 40) colorClass = "mid";

        // Count products located in this zone
        const prods = state.products.filter(p => p.location.substring(0, 2) === z.code);
        const lowStockProds = prods.filter(p => getAvailableStock(p) <= p.reorder_level);
        
        // Find fast and slow moving (mocking based on category)
        const fastMoving = prods.length > 0 ? prods[0].product_code : 'N/A';
        const slowMoving = prods.length > 1 ? prods[prods.length - 1].product_code : 'N/A';

        // Generate visual layout slots
        let slotsHtml = "";
        for (let i = 1; i <= 10; i++) {
            let slotClass = "";
            let label = `${z.code}-${i}`;
            
            if (i <= Math.ceil(z.occupied / (z.capacity / 10))) {
                slotClass = "occupied";
                if (i === 1) { slotClass += " fast-moving"; label = "FAST"; }
                if (i === 9) { slotClass += " slow-moving"; label = "SLOW"; }
            }
            slotsHtml += `<div class="slot-item ${slotClass}">${label}</div>`;
        }

        grid.innerHTML += `
            <div class="zone-card">
                <div class="zone-header">
                    <span class="zone-title">${z.code} - ${z.name}</span>
                    <span class="badge bg-blue">${prods.length} Products</span>
                </div>
                <div class="zone-capacity-text">
                    <span>Occupancy Rate</span>
                    <strong>${pct}% (${z.occupied}/${z.capacity} units)</strong>
                </div>
                <div class="zone-capacity-bar">
                    <div class="zone-capacity-fill ${colorClass}" style="width: ${pct}%;"></div>
                </div>
                
                <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 10px; display:flex; flex-direction:column; gap:4px;">
                    <div>Low Stock Items: <span style="color:var(--danger); font-weight:700;">${lowStockProds.length}</span></div>
                    <div>Fastest Mover: <strong>${fastMoving}</strong></div>
                    <div>Slowest Mover: <strong>${slowMoving}</strong></div>
                </div>

                <div class="zone-visual-slots">
                    ${slotsHtml}
                </div>
            </div>
        `;
    });
}

// 15. CUSTOMERS
function renderCustomers() {
    const tbody = document.getElementById("customers-table-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.customers.forEach(c => {
        tbody.innerHTML += `
            <tr>
                <td><strong>${c.name}</strong></td>
                <td>${c.email}</td>
                <td>${c.phone}</td>
                <td>${c.total_orders} orders</td>
                <td><strong>${formatINR(c.total_spending)}</strong></td>
                <td><strong>${c.last_order || 'N/A'}</strong></td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="showCustomerDetail('${c.name}')"><i class="fa-solid fa-address-card"></i> View History</button>
                </td>
            </tr>
        `;
    });
}

function showCustomerDetail(name) {
    const c = state.customers.find(cust => cust.name === name);
    if (!c) return;

    const detailCard = document.getElementById("customer-detail-card");
    detailCard.style.display = "block";
    
    document.getElementById("customer-detail-name").innerText = `${c.name} - Profile Details`;
    document.getElementById("customer-detail-email").innerText = c.email;
    document.getElementById("customer-detail-phone").innerText = c.phone;
    document.getElementById("customer-detail-orders").innerText = c.total_orders;
    document.getElementById("customer-detail-spent").innerText = formatINR(c.total_spending);

    // Render history
    const tbody = document.getElementById("customer-history-body");
    tbody.innerHTML = "";
    
    const hist = state.orders.filter(o => o.customer === c.name);
    hist.forEach(o => {
        tbody.innerHTML += `
            <tr>
                <td><strong>${o.order_code}</strong></td>
                <td>${o.product_code}</td>
                <td>${o.quantity} units</td>
                <td><strong>${formatINR(o.total_amount)}</strong></td>
                <td><span class="badge bg-blue">${o.status}</span></td>
            </tr>
        `;
    });

    if (tbody.innerHTML === "") {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No order logs.</td></tr>`;
    }

    // Scroll to details card
    detailCard.scrollIntoView({ behavior: 'smooth' });
}

// 16. ACTIVITY LOG
function renderActivityLog() {
    const tbody = document.getElementById("activity-log-table-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.activityLogs.forEach(l => {
        let badgeClass = "bg-blue";
        if (l.role === "Admin") badgeClass = "bg-red";
        if (l.role === "Manager") badgeClass = "bg-yellow";
        if (l.role === "Staff") badgeClass = "bg-green";

        tbody.innerHTML += `
            <tr>
                <td><span class="badge ${badgeClass}">${l.role}</span></td>
                <td>${l.action}</td>
                <td>${l.date}</td>
                <td><span style="font-family:monospace;">${l.time}</span></td>
            </tr>
        `;
    });
}

// 17. DEMO CONSOLE
function renderDemoConsole() {
    const consoleEl = document.getElementById("demo-log-console");
    if (consoleEl) {
        consoleEl.innerHTML = "";
        state.logs.forEach(l => {
            const line = document.createElement("div");
            line.className = `log-line ${l.type}`;
            line.innerText = l.message;
            consoleEl.appendChild(line);
        });
        consoleEl.scrollTop = consoleEl.scrollHeight;
    }
}

// ==========================================
// INTERACTIVE CHARTS (CHART.JS)
// ==========================================
let lowStockChart = null;

function renderCharts() {
    // Doughnut chart: Orders by Status
    const statusCounts = {};
    state.orders.forEach(o => {
        statusCounts[o.status] = (statusCounts[o.status] || 0) + 1;
    });

    const statusCtx = document.getElementById("chart-order-status");
    if (statusCtx) {
        if (orderStatusChart) orderStatusChart.destroy();
        orderStatusChart = new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(statusCounts),
                datasets: [{
                    data: Object.values(statusCounts),
                    backgroundColor: ['#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#64748b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'right', labels: { color: '#94a3b8' } }
                }
            }
        });
    }

    // Low stock products chart (Horizontal bar)
    const lowStockCtx = document.getElementById("chart-low-stock");
    if (lowStockCtx) {
        const lowProducts = state.products.filter(p => getAvailableStock(p) <= p.reorder_level);
        const labels = lowProducts.map(p => p.product_code);
        const data = lowProducts.map(p => getAvailableStock(p));

        if (lowStockChart) lowStockChart.destroy();
        lowStockChart = new Chart(lowStockCtx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Available Stock Units',
                    data,
                    backgroundColor: '#ef4444',
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { display: false } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    // Analytics: Category values (Doughnut)
    const catCtx = document.getElementById("chart-analytics-categories");
    if (catCtx) {
        const catVals = {};
        state.products.forEach(p => {
            catVals[p.category] = (catVals[p.category] || 0) + (p.total_stock * p.unit_cost);
        });

        if (analyticsCategoryChart) analyticsCategoryChart.destroy();
        analyticsCategoryChart = new Chart(catCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(catVals),
                datasets: [{
                    data: Object.values(catVals),
                    backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6', '#ec4899', '#14b8a6', '#64748b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#94a3b8' } }
                }
            }
        });
    }

    // Analytics: Top selling products (Vertical Bar)
    const salesCtx = document.getElementById("chart-analytics-topselling");
    if (salesCtx) {
        const topSellers = {};
        state.transactions.forEach(t => {
            if (t.payment_status === "Paid") {
                topSellers[t.product_code] = (topSellers[t.product_code] || 0) + t.quantity;
            }
        });

        const labels = Object.keys(topSellers);
        const data = Object.values(topSellers);

        if (analyticsMovementChart) analyticsMovementChart.destroy();
        analyticsMovementChart = new Chart(salesCtx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Units Sold',
                    data,
                    backgroundColor: '#10b981',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }
}

// ==========================================
// INVENTORY CRUD MODULES
// ==========================================
function openProductModal(action, sku = "") {
    const modal = document.getElementById("product-crud-modal");
    const title = document.getElementById("product-modal-title");
    const submitBtn = document.getElementById("product-submit-btn");
    
    document.getElementById("product-modal-action").value = action;
    document.getElementById("product-modal-original-code").value = sku;
    
    modal.classList.add("active");

    if (action === "add") {
        title.innerText = "Add New Product SKU";
        submitBtn.innerText = "Save Product";
        
        // Clear inputs
        document.getElementById("prod-sku").value = "";
        document.getElementById("prod-sku").removeAttribute("disabled");
        document.getElementById("prod-name").value = "";
        document.getElementById("prod-cat").value = "";
        document.getElementById("prod-location").value = "";
        document.getElementById("prod-price").value = "";
        document.getElementById("prod-cost").value = "";
        document.getElementById("prod-stock").value = "";
        document.getElementById("prod-reorder").value = "";
        document.getElementById("prod-supplier").value = "";
    } else {
        title.innerText = `Edit Product SKU: ${sku}`;
        submitBtn.innerText = "Apply Updates";
        
        const p = state.products.find(prod => prod.product_code === sku);
        if (p) {
            document.getElementById("prod-sku").value = p.product_code;
            document.getElementById("prod-sku").setAttribute("disabled", "true");
            document.getElementById("prod-name").value = p.name;
            document.getElementById("prod-cat").value = p.category;
            document.getElementById("prod-location").value = p.location;
            document.getElementById("prod-price").value = p.selling_price;
            document.getElementById("prod-cost").value = p.unit_cost;
            document.getElementById("prod-stock").value = p.total_stock;
            document.getElementById("prod-reorder").value = p.reorder_level;
            document.getElementById("prod-supplier").value = p.supplier || "";
        }
    }
}

function closeProductModal() {
    document.getElementById("product-crud-modal").classList.remove("active");
}

function submitProductCrud(e) {
    e.preventDefault();
    const action = document.getElementById("product-modal-action").value;
    const sku = document.getElementById("prod-sku").value.trim().toUpperCase();
    const name = document.getElementById("prod-name").value.trim();
    const cat = document.getElementById("prod-cat").value.trim();
    const location = document.getElementById("prod-location").value.trim().toUpperCase();
    const price = parseFloat(document.getElementById("prod-price").value);
    const cost = parseFloat(document.getElementById("prod-cost").value);
    const stock = parseInt(document.getElementById("prod-stock").value);
    const reorder = parseInt(document.getElementById("prod-reorder").value);
    const supplier = document.getElementById("prod-supplier").value.trim();

    if (action === "add") {
        // Check uniqueness
        if (state.products.find(p => p.product_code === sku)) {
            showToast(`Product code ${sku} already exists!`, "danger");
            return;
        }

        const newProd = {
            product_code: sku,
            name,
            category: cat,
            location,
            total_stock: stock,
            reserved_stock: 0,
            damaged_stock: 0,
            reorder_level: reorder,
            reorder_quantity: reorder * 2,
            unit_cost: cost,
            selling_price: price,
            supplier
        };

        state.products.push(newProd);
        
        // Log transaction
        state.inventoryTransactions.push({
            product_code: sku,
            transaction_type: "IN",
            quantity: stock,
            previous_stock: 0,
            new_stock: stock,
            reason: "Initial Product Creation Check-in",
            performed_by: state.activeRole,
            created_at: new Date().toISOString()
        });

        // Update warehouse occupied counts
        const zoneCode = location.substring(0, 2);
        const zone = state.warehouseZones.find(z => z.code === zoneCode);
        if (zone) {
            zone.occupied = Math.min(zone.capacity, zone.occupied + stock);
        }

        logEvent("success", `Created new Product SKU: ${sku}. Seed stock: ${stock} units.`);
        addActivityLog(state.activeRole, `Added new product ${sku}: ${name}`);
        showToast(`Product ${sku} added successfully!`, "success");
    } else {
        // Edit update
        const p = state.products.find(prod => prod.product_code === sku);
        if (p) {
            const previousStock = p.total_stock;
            p.name = name;
            p.category = cat;
            p.location = location;
            p.selling_price = price;
            p.unit_cost = cost;
            p.total_stock = stock;
            p.reorder_level = reorder;
            p.supplier = supplier;

            if (stock !== previousStock) {
                state.inventoryTransactions.push({
                    product_code: sku,
                    transaction_type: stock > previousStock ? "IN" : "OUT",
                    quantity: Math.abs(stock - previousStock),
                    previous_stock: previousStock,
                    new_stock: stock,
                    reason: "Manual CRUD adjustment",
                    performed_by: state.activeRole,
                    created_at: new Date().toISOString()
                });
                
                // Adjust occupied zone capacity
                const zoneCode = location.substring(0, 2);
                const zone = state.warehouseZones.find(z => z.code === zoneCode);
                if (zone) {
                    zone.occupied = Math.max(0, Math.min(zone.capacity, zone.occupied + (stock - previousStock)));
                }
            }

            logEvent("info", `Updated details for Product SKU: ${sku}.`);
            addActivityLog(state.activeRole, `Updated product fields for SKU: ${sku}`);
            showToast(`Product ${sku} details updated!`, "success");
        }
    }

    saveState();
    closeProductModal();
    renderAll();
}

function deleteProductClient(sku) {
    if (!confirm(`Are you sure you want to permanently delete Product SKU: ${sku}?`)) return;

    // Check if referenced in orders
    const ordersWithProduct = state.orders.filter(o => o.product_code === sku && o.status !== "Completed" && o.status !== "Cancelled");
    if (ordersWithProduct.length > 0) {
        showToast(`Cannot delete product ${sku}. It is referenced in ${ordersWithProduct.length} open orders!`, "danger");
        return;
    }

    const index = state.products.findIndex(p => p.product_code === sku);
    if (index !== -1) {
        const prod = state.products[index];
        
        // Revert warehouse zone occupied capacity
        const zoneCode = prod.location.substring(0, 2);
        const zone = state.warehouseZones.find(z => z.code === zoneCode);
        if (zone) {
            zone.occupied = Math.max(0, zone.occupied - prod.total_stock);
        }

        state.products.splice(index, 1);
        
        saveState();
        logEvent("danger", `Permanently deleted Product SKU: ${sku}.`);
        addActivityLog(state.activeRole, `Deleted product SKU: ${sku}`);
        showToast(`Product SKU ${sku} deleted.`, "warning");
        renderAll();
    }
}

// ==========================================
// GLOBAL SEARCH ENGINE
// ==========================================
function handleGlobalSearch(e) {
    const query = e.target.value.toLowerCase().trim();
    const resultsBox = document.getElementById("global-search-results");
    const resultsList = document.getElementById("global-search-results-list");

    if (!query) {
        resultsBox.style.display = "none";
        return;
    }

    resultsBox.style.display = "block";
    resultsList.innerHTML = "";

    // 1. Search Products (SKU, Name)
    const prods = state.products.filter(p => p.product_code.toLowerCase().includes(query) || p.name.toLowerCase().includes(query));
    prods.slice(0, 3).forEach(p => {
        resultsList.innerHTML += `
            <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.02); padding:8px 12px; border-radius:4px;">
                <div><i class="fa-solid fa-cube text-blue"></i> <strong>${p.product_code}</strong> - ${p.name} (${p.category})</div>
                <button class="btn btn-secondary btn-sm" onclick="switchToSection('inventory'); setTimeout(() => { document.getElementById('inv-search').value = '${p.product_code}'; filterInventoryTable(); }, 100);">View Inventory</button>
            </div>
        `;
    });

    // 2. Search Orders (Order ID, Customer)
    const ords = state.orders.filter(o => o.order_code.toLowerCase().includes(query) || o.customer.toLowerCase().includes(query));
    ords.slice(0, 3).forEach(o => {
        resultsList.innerHTML += `
            <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.02); padding:8px 12px; border-radius:4px;">
                <div><i class="fa-solid fa-cart-shopping text-yellow"></i> <strong>${o.order_code}</strong> - ${o.customer} (${o.status})</div>
                <button class="btn btn-secondary btn-sm" onclick="switchToSection('timeline'); setTimeout(() => { document.getElementById('timeline-order-input').value = '${o.order_code}'; searchTimelineOrder(); }, 100);">Track Timeline</button>
            </div>
        `;
    });

    // 3. Search Customers
    const custs = state.customers.filter(c => c.name.toLowerCase().includes(query) || c.email.toLowerCase().includes(query));
    custs.slice(0, 3).forEach(c => {
        resultsList.innerHTML += `
            <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.02); padding:8px 12px; border-radius:4px;">
                <div><i class="fa-solid fa-user text-green"></i> <strong>${c.name}</strong> - ${c.email}</div>
                <button class="btn btn-secondary btn-sm" onclick="switchToSection('customers'); showCustomerDetail('${c.name}');">View Details</button>
            </div>
        `;
    });

    if (resultsList.innerHTML === "") {
        resultsList.innerHTML = `<div style="text-align:center; color:var(--text-muted); font-size:0.85rem;">No results match query.</div>`;
    }
}

function switchToSection(targetSection) {
    const navItem = document.querySelector(`.sidebar-nav li.nav-item[data-target='${targetSection}']`);
    if (navItem) navItem.click();
    
    // Clear global search input
    document.getElementById("global-search-input").value = "";
    document.getElementById("global-search-results").style.display = "none";
}

// ==========================================
// INVENTORY POPUPS & ACTIONS (STOCK IN / OUT)
// ==========================================
function openInventoryModal(actionType) {
    const modal = document.getElementById("inventory-modal");
    const title = document.getElementById("modal-title");
    const actionInput = document.getElementById("modal-action-type");
    const submitBtn = document.getElementById("modal-submit-btn");

    actionInput.value = actionType;
    modal.classList.add("active");

    if (actionType === "stock-in") {
        title.innerText = "Process Stock Check In";
        submitBtn.innerText = "Execute Check In";
    } else if (actionType === "stock-out") {
        title.innerText = "Process Stock Check Out";
        submitBtn.innerText = "Execute Check Out";
    } else if (actionType === "stock-adjust") {
        title.innerText = "Physical Stock Adjustment";
        submitBtn.innerText = "Adjust Count";
    } else if (actionType === "mark-damaged") {
        title.innerText = "Register Damaged Goods";
        submitBtn.innerText = "Report Damage";
    }
}

function closeInventoryModal() {
    document.getElementById("inventory-modal").classList.remove("active");
}

function submitInventoryAction(e) {
    e.preventDefault();
    const action = document.getElementById("modal-action-type").value;
    const pCode = document.getElementById("modal-product-select").value;
    const qty = parseInt(document.getElementById("modal-qty").value);
    const reason = document.getElementById("modal-reason").value.trim();

    const prod = state.products.find(p => p.product_code === pCode);
    if (!prod) return;

    const prev = prod.total_stock;

    if (action === "stock-in") {
        prod.total_stock += qty;
        state.inventoryTransactions.push({
            product_code: pCode,
            transaction_type: "IN",
            quantity: qty,
            previous_stock: prev,
            new_stock: prod.total_stock,
            reason: reason || "Manual Stock check in",
            performed_by: state.activeRole,
            created_at: new Date().toISOString()
        });
        
        // adjust capacity
        const zoneCode = prod.location.substring(0, 2);
        const zone = state.warehouseZones.find(z => z.code === zoneCode);
        if (zone) zone.occupied = Math.min(zone.capacity, zone.occupied + qty);

        logEvent("success", `Stock In: Added ${qty} units of ${pCode}. New stock: ${prod.total_stock}.`);
        addActivityLog(state.activeRole, `Executed stock check in: ${qty}x ${prod.name}`);
        showToast(`Stock in processed for ${pCode}`, "success");
    } else if (action === "stock-out") {
        const avail = getAvailableStock(prod);
        if (qty > avail) {
            showToast(`Rejected: Insufficient available stock (Only ${avail} units available)!`, "danger");
            return;
        }
        prod.total_stock -= qty;
        state.inventoryTransactions.push({
            product_code: pCode,
            transaction_type: "OUT",
            quantity: qty,
            previous_stock: prev,
            new_stock: prod.total_stock,
            reason: reason || "Manual stock check out",
            performed_by: state.activeRole,
            created_at: new Date().toISOString()
        });
        
        // adjust capacity
        const zoneCode = prod.location.substring(0, 2);
        const zone = state.warehouseZones.find(z => z.code === zoneCode);
        if (zone) zone.occupied = Math.max(0, zone.occupied - qty);

        logEvent("danger", `Stock Out: Shipped ${qty} units of ${pCode}. Remaining: ${prod.total_stock}.`);
        addActivityLog(state.activeRole, `Executed stock check out: ${qty}x ${prod.name}`);
        showToast(`Stock out processed for ${pCode}`, "warning");
    } else if (action === "stock-adjust") {
        prod.total_stock = qty;
        state.inventoryTransactions.push({
            product_code: pCode,
            transaction_type: "ADJUSTMENT",
            quantity: qty - prev,
            previous_stock: prev,
            new_stock: qty,
            reason: reason || "Physical stock count reconcile",
            performed_by: state.activeRole,
            created_at: new Date().toISOString()
        });

        const zoneCode = prod.location.substring(0, 2);
        const zone = state.warehouseZones.find(z => z.code === zoneCode);
        if (zone) zone.occupied = Math.max(0, Math.min(zone.capacity, zone.occupied + (qty - prev)));

        logEvent("warning", `Inventory count adjusted for ${pCode} to ${qty} units. Count deviation: ${qty - prev}.`);
        addActivityLog(state.activeRole, `Adjusted product count for ${prod.name} to ${qty}`);
        showToast(`Adjustment processed for ${pCode}`, "info");
    } else if (action === "mark-damaged") {
        const avail = getAvailableStock(prod);
        if (qty > avail) {
            showToast(`Error: Only ${avail} available units can be flagged damaged!`, "danger");
            return;
        }
        prod.damaged_stock += qty;
        logEvent("danger", `Registered ${qty} damaged units of ${pCode}. Alarms flagged.`);
        addActivityLog(state.activeRole, `Flagged damaged goods: ${qty}x ${prod.name}`);
        showToast(`${qty} units of ${pCode} flagged damaged`, "danger");
    }

    saveState();
    closeInventoryModal();
    renderAll();
}

// Helpers for product inputs
function populateProductSelectors() {
    const selects = ["ord-product", "modal-product-select"];
    selects.forEach(id => {
        const select = document.getElementById(id);
        if (!select) return;
        select.innerHTML = "";
        state.products.forEach(p => {
            select.innerHTML += `<option value="${p.product_code}">${p.product_code} - ${p.name} (Available: ${getAvailableStock(p)})</option>`;
        });
    });

    const catSelect = document.getElementById("inv-filter-category");
    if (catSelect) {
        const categories = [...new Set(state.products.map(p => p.category))];
        catSelect.innerHTML = `<option value="ALL">All Categories</option>`;
        categories.forEach(cat => {
            catSelect.innerHTML += `<option value="${cat}">${cat}</option>`;
        });
    }
}

function filterInventoryTable() {
    const searchVal = document.getElementById("inv-search").value.toLowerCase();
    const catVal = document.getElementById("inv-filter-category").value;
    const locVal = document.getElementById("inv-filter-location").value;
    const statusVal = document.getElementById("inv-filter-status").value;

    const rows = document.querySelectorAll("#inv-table-body tr");
    rows.forEach(row => {
        const sku = row.querySelector("td:nth-child(1)").innerText.toLowerCase();
        const name = row.querySelector("td:nth-child(2)").innerText.toLowerCase();
        const sup = row.querySelector("td:nth-child(9)").innerText.toLowerCase();
        const cat = row.getAttribute("data-category");
        const locZone = row.getAttribute("data-location");
        const status = row.getAttribute("data-status");

        const matchesSearch = sku.includes(searchVal) || name.includes(searchVal) || sup.includes(searchVal);
        const matchesCategory = catVal === "ALL" || cat === catVal;
        const matchesLocation = locVal === "ALL" || locZone === locVal;
        const matchesStatus = statusVal === "ALL" || status === statusVal;

        if (matchesSearch && matchesCategory && matchesLocation && matchesStatus) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}

// ==========================================
// SIMULATOR HANDLERS (PRESENTATION CRITICAL)
// ==========================================
function simulateOrder() {
    const customers = ["Kalyan Penke", "Suresh Kumar", "Ramesh Naidu", "John Doe", "Jane Smith"];
    const randomCustomer = customers[Math.floor(Math.random() * customers.length)];
    const randomProduct = state.products[Math.floor(Math.random() * state.products.length)];
    const qty = Math.floor(Math.random() * 4) + 1;
    const urgency = Math.floor(Math.random() * 9) + 2;

    const avail = getAvailableStock(randomProduct);
    if (qty > avail) {
        logEvent("warning", `[SIMULATION] Simulated Order failed: Shortage of ${randomProduct.name} (${qty} requested, only ${avail} available).`);
        return;
    }

    const calc = calculatePriorityScore(urgency, qty, avail, randomProduct.selling_price, randomProduct.unit_cost);

    const lastId = state.orders.length > 0 ? parseInt(state.orders[state.orders.length - 1].order_code.substring(3)) : 0;
    const nextCode = `ORD${(lastId + 1).toString().padStart(3, '0')}`;

    const newOrder = {
        order_code: nextCode,
        customer: randomCustomer,
        email: "customer@example.com",
        phone: "+91 99999 88888",
        product_code: randomProduct.product_code,
        quantity: qty,
        total_amount: qty * randomProduct.selling_price,
        priority: calc.level,
        priority_score: calc.score,
        status: "Pending",
        created_at: new Date().toISOString(),
        address: "DLF Cyber City, Gachibowli"
    };

    state.orders.push(newOrder);

    // Auto transaction
    state.transactions.push({
        transaction_reference: `TXN-${nextCode}`,
        order_code: nextCode,
        customer: randomCustomer,
        product_code: randomProduct.product_code,
        quantity: qty,
        total_amount: qty * randomProduct.selling_price,
        payment_method: "Cash on Delivery",
        payment_status: "Pending Payment",
        created_at: new Date().toISOString()
    });

    saveState();
    logEvent("info", `[SIMULATION] Simulated New Order ${nextCode} for ${randomCustomer}. Value: ${formatINR(qty * randomProduct.selling_price)}.`);
    addActivityLog("System", `Simulated sales order ${nextCode} for ${randomCustomer}`);
    showToast(`Simulated Order ${nextCode} placed!`, "success");
    renderAll();
}

function simulatePayment() {
    const pending = state.transactions.filter(t => t.payment_status === "Pending Payment");
    if (pending.length === 0) {
        logEvent("warning", "[SIMULATION] No pending order transactions available to pay.");
        return;
    }

    const t = pending[Math.floor(Math.random() * pending.length)];
    t.payment_status = "Paid";
    t.payment_method = "UPI";

    saveState();
    logEvent("success", `[SIMULATION] Simulated Payment for Order ${t.order_code}. Received ${formatINR(t.total_amount)}.`);
    addActivityLog("System", `Simulated invoice payment for order: ${t.order_code}`);
    showToast(`Payment of ${formatINR(t.total_amount)} received!`, "success");
    renderAll();
}

function simulateReturn() {
    const delivered = state.orders.filter(o => o.status === "Delivered");
    if (delivered.length === 0) {
        logEvent("warning", "[SIMULATION] No delivered orders available to trigger customer return.");
        return;
    }

    const o = delivered[Math.floor(Math.random() * delivered.length)];
    const prod = state.products.find(p => p.product_code === o.product_code);
    const qty = o.quantity;
    const price = prod ? prod.selling_price : 0;

    const lastId = state.returns.length > 0 ? parseInt(state.returns[state.returns.length - 1].return_code.substring(3)) : 0;
    const nextCode = `RET${(lastId + 1).toString().padStart(3, '0')}`;

    state.returns.push({
        return_code: nextCode,
        order_code: o.order_code,
        customer: o.customer,
        product_code: o.product_code,
        quantity: qty,
        reason: "Defective Product",
        description: "Visual defects on casing shell.",
        status: "Requested",
        inspection_condition: "Pending",
        refund_amount: qty * price,
        requested_at: new Date().toISOString()
    });

    saveState();
    logEvent("warning", `[SIMULATION] Simulated Return request ${nextCode} filed for Order ${o.order_code}.`);
    showToast(`Simulated Return filed: ${nextCode}`, "warning");
    renderAll();
}

function simulateShortage() {
    const smartBand = state.products.find(p => p.product_code === "P010");
    if (smartBand) {
        smartBand.total_stock = 0;
        smartBand.reserved_stock = 0;
        smartBand.damaged_stock = 0;
    }
    const laptop = state.products.find(p => p.product_code === "P005");
    if (laptop) {
        laptop.total_stock = 0;
        laptop.reserved_stock = 0;
        laptop.damaged_stock = 0;
    }

    saveState();
    logEvent("danger", "[SIMULATION] Force Depleted Stock triggered for P010 and P005 to trigger system alerts.");
    showToast("Simulation Alert: Depleted P010 & P005 stock!", "danger");
    renderAll();
}

function simulateDispatch() {
    const pendingOrders = state.orders.filter(o => o.status === "Pending");
    if (pendingOrders.length === 0) {
        logEvent("warning", "[SIMULATION] No pending orders available to process.");
        return;
    }

    const o = pendingOrders[0];
    
    // Fast-track: Pending -> Processing -> Packed -> Shipped -> Delivered
    setTimeout(() => advanceOrderStatus(o.order_code, "Processing"), 100);
    setTimeout(() => advanceOrderStatus(o.order_code, "Packed"), 800);
    setTimeout(() => advanceOrderStatus(o.order_code, "Shipped"), 1500);
    setTimeout(() => advanceOrderStatus(o.order_code, "Delivered"), 2200);
    
    logEvent("info", `[SIMULATION] Initiated direct automated workflow dispatch for Order ${o.order_code}.`);
}

// Initial configuration
document.addEventListener("DOMContentLoaded", () => {
    loadState();
    
    // Active Role setting
    changeActiveRole(state.activeRole);
    document.getElementById("header-role-select").value = state.activeRole;
});
