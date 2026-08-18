// SCRIPT.JS – SMARTFULFILL BUSINESS LOGIC ENGINE

// ==========================================
// STATE MANAGEMENT & DATA SCHEMAS
// ==========================================
let state = {
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
    logs: []
};

// Default Products Seed Data (30 Products from database.py)
const defaultProducts = [
    { product_code: "P001", name: "Wireless Mouse", category: "Electronics", location: "A-01-03", total_stock: 100, reserved_stock: 20, damaged_stock: 5, reorder_level: 25, reorder_quantity: 50, unit_cost: 400.0, selling_price: 650.0 },
    { product_code: "P002", name: "Keyboard", category: "Electronics", location: "A-01-05", total_stock: 50, reserved_stock: 15, damaged_stock: 2, reorder_level: 15, reorder_quantity: 30, unit_cost: 800.0, selling_price: 1200.0 },
    { product_code: "P003", name: "USB Cable", category: "Accessories", location: "B-02-01", total_stock: 30, reserved_stock: 20, damaged_stock: 3, reorder_level: 10, reorder_quantity: 25, unit_cost: 150.0, selling_price: 300.0 },
    { product_code: "P004", name: "Laptop", category: "Electronics", location: "C-01-01", total_stock: 15, reserved_stock: 10, damaged_stock: 0, reorder_level: 10, reorder_quantity: 20, unit_cost: 45000.0, selling_price: 55000.0 },
    { product_code: "P005", name: "Headphones", category: "Audio", location: "B-03-02", total_stock: 5, reserved_stock: 2, damaged_stock: 1, reorder_level: 8, reorder_quantity: 15, unit_cost: 1000.0, selling_price: 1800.0 },
    { product_code: "P006", name: "Smart Watch", category: "Wearables", location: "A-01-01", total_stock: 6, reserved_stock: 0, damaged_stock: 0, reorder_level: 8, reorder_quantity: 15, unit_cost: 2500.0, selling_price: 3999.0 },
    { product_code: "P007", name: "Bluetooth Speaker", category: "Audio", location: "A-01-02", total_stock: 45, reserved_stock: 5, damaged_stock: 1, reorder_level: 10, reorder_quantity: 20, unit_cost: 1500.0, selling_price: 2499.0 },
    { product_code: "P008", name: "Power Bank", category: "Accessories", location: "A-01-04", total_stock: 80, reserved_stock: 10, damaged_stock: 2, reorder_level: 15, reorder_quantity: 30, unit_cost: 900.0, selling_price: 1499.0 },
    { product_code: "P009", name: "Smartphone", category: "Electronics", location: "B-01-01", total_stock: 0, reserved_stock: 0, damaged_stock: 0, reorder_level: 5, reorder_quantity: 10, unit_cost: 18000.0, selling_price: 22999.0 },
    { product_code: "P010", name: "Tablet", category: "Electronics", location: "B-01-02", total_stock: 25, reserved_stock: 2, damaged_stock: 0, reorder_level: 5, reorder_quantity: 10, unit_cost: 15000.0, selling_price: 19999.0 },
    { product_code: "P011", name: "Webcam", category: "Electronics", location: "B-01-03", total_stock: 40, reserved_stock: 4, damaged_stock: 1, reorder_level: 8, reorder_quantity: 15, unit_cost: 1200.0, selling_price: 1999.0 },
    { product_code: "P012", name: "Gaming Mouse", category: "Gaming", location: "B-01-04", total_stock: 60, reserved_stock: 8, damaged_stock: 2, reorder_level: 12, reorder_quantity: 25, unit_cost: 1000.0, selling_price: 1799.0 },
    { product_code: "P013", name: "Gaming Keyboard", category: "Gaming", location: "B-01-05", total_stock: 35, reserved_stock: 5, damaged_stock: 0, reorder_level: 8, reorder_quantity: 15, unit_cost: 2000.0, selling_price: 3499.0 },
    { product_code: "P014", name: "T-Shirt", category: "Clothing", location: "C-01-02", total_stock: 200, reserved_stock: 20, damaged_stock: 5, reorder_level: 15, reorder_quantity: 50, unit_cost: 400.0, selling_price: 799.0 },
    { product_code: "P015", name: "Jeans", category: "Clothing", location: "C-01-03", total_stock: 120, reserved_stock: 10, damaged_stock: 2, reorder_level: 10, reorder_quantity: 25, unit_cost: 900.0, selling_price: 1599.0 },
    { product_code: "P016", name: "Backpack", category: "Bags", location: "C-01-04", total_stock: 75, reserved_stock: 6, damaged_stock: 1, reorder_level: 10, reorder_quantity: 20, unit_cost: 700.0, selling_price: 1299.0 },
    { product_code: "P017", name: "Running Shoes", category: "Footwear", location: "C-01-05", total_stock: 55, reserved_stock: 5, damaged_stock: 1, reorder_level: 8, reorder_quantity: 15, unit_cost: 1500.0, selling_price: 2499.0 },
    { product_code: "P018", name: "Water Bottle", category: "Home & Lifestyle", location: "A-01-01", total_stock: 110, reserved_stock: 10, damaged_stock: 0, reorder_level: 15, reorder_quantity: 30, unit_cost: 250.0, selling_price: 499.0 },
    { product_code: "P019", name: "LED Bulb", category: "Home & Electrical", location: "A-01-02", total_stock: 150, reserved_stock: 0, damaged_stock: 3, reorder_level: 20, reorder_quantity: 50, unit_cost: 120.0, selling_price: 249.0 },
    { product_code: "P020", name: "Calculator", category: "Stationery", location: "A-01-03", total_stock: 90, reserved_stock: 5, damaged_stock: 1, reorder_level: 10, reorder_quantity: 20, unit_cost: 200.0, selling_price: 399.0 },
    { product_code: "P021", name: "Notebook", category: "Stationery", location: "A-01-04", total_stock: 300, reserved_stock: 0, damaged_stock: 0, reorder_level: 30, reorder_quantity: 100, unit_cost: 60.0, selling_price: 120.0 },
    { product_code: "P022", name: "Pen Pack", category: "Stationery", location: "A-01-05", total_stock: 500, reserved_stock: 20, damaged_stock: 0, reorder_level: 50, reorder_quantity: 150, unit_cost: 50.0, selling_price: 100.0 },
    { product_code: "P023", name: "Desk Lamp", category: "Home & Electrical", location: "B-01-01", total_stock: 65, reserved_stock: 5, damaged_stock: 2, reorder_level: 10, reorder_quantity: 20, unit_cost: 500.0, selling_price: 899.0 },
    { product_code: "P024", name: "Earbuds", category: "Audio", location: "B-01-02", total_stock: 85, reserved_stock: 8, damaged_stock: 1, reorder_level: 12, reorder_quantity: 25, unit_cost: 1200.0, selling_price: 1999.0 },
    { product_code: "P025", name: "Smartphone Charger", category: "Accessories", location: "B-01-03", total_stock: 120, reserved_stock: 15, damaged_stock: 4, reorder_level: 15, reorder_quantity: 30, unit_cost: 350.0, selling_price: 699.0 },
    { product_code: "P026", name: "HDMI Cable", category: "Accessories", location: "B-01-04", total_stock: 140, reserved_stock: 10, damaged_stock: 2, reorder_level: 10, reorder_quantity: 25, unit_cost: 250.0, selling_price: 499.0 },
    { product_code: "P027", name: "SSD 1TB", category: "Computer Hardware", location: "B-01-05", total_stock: 45, reserved_stock: 4, damaged_stock: 0, reorder_level: 5, reorder_quantity: 10, unit_cost: 5000.0, selling_price: 6999.0 },
    { product_code: "P028", name: "RAM 16GB", category: "Computer Hardware", location: "C-01-01", total_stock: 60, reserved_stock: 6, damaged_stock: 1, reorder_level: 8, reorder_quantity: 15, unit_cost: 3500.0, selling_price: 4999.0 },
    { product_code: "P029", name: "Monitor", category: "Computer Hardware", location: "C-01-02", total_stock: 0, reserved_stock: 0, damaged_stock: 0, reorder_level: 2, reorder_quantity: 5, unit_cost: 8000.0, selling_price: 11999.0 },
    { product_code: "P030", name: "Printer", category: "Office Equipment", location: "C-01-03", total_stock: 12, reserved_stock: 2, damaged_stock: 0, reorder_level: 3, reorder_quantity: 5, unit_cost: 9000.0, selling_price: 12999.0 }
];

// Default Orders Seed Data
const defaultOrders = [
    { order_code: "ORD001", customer: "ABC Technologies", product_code: "P004", quantity: 10, priority: "Critical", priority_score: 95, status: "Pending", created_at: "2026-08-18T12:00:00" },
    { order_code: "ORD002", customer: "Retail Store", product_code: "P001", quantity: 15, priority: "High", priority_score: 78, status: "Pending", created_at: "2026-08-18T12:15:00" },
    { order_code: "ORD003", customer: "College Store", product_code: "P002", quantity: 5, priority: "Medium", priority_score: 55, status: "Picking", created_at: "2026-08-18T12:30:00" },
    { order_code: "ORD004", customer: "Online Customer", product_code: "P003", quantity: 8, priority: "Low", priority_score: 30, status: "Packed", created_at: "2026-08-18T12:45:00" }
];

// Default picking tasks seed
const defaultPicking = [
    { id: "PCK001", order_code: "ORD003", product_code: "P002", quantity: 5, location: "A-01-05", status: "Picking", created_at: "2026-08-18T12:30:00" },
    { id: "PCK002", order_code: "ORD004", product_code: "P003", quantity: 8, location: "B-02-01", status: "Picked", created_at: "2026-08-18T12:45:00" }
];

// Default packing operations seed
const defaultPacking = [
    { order_code: "ORD004", packaging_type: "Medium Box", packaging_cost: 35.0, handling_cost: 10.0, total_cost: 45.0, status: "Packed", packed_by: "System", created_at: "2026-08-18T12:45:00", packed_at: "2026-08-18T13:00:00" }
];

// Helper: Load data from localStorage
function loadState() {
    const rawState = localStorage.getItem("smart_fulfill_db");
    if (rawState) {
        state = JSON.parse(rawState);
    } else {
        resetLocalDataset();
    }
}

// Helper: Save data to localStorage
function saveState() {
    localStorage.setItem("smart_fulfill_db", JSON.stringify(state));
}

// Helper: Log message to Demo Console
function logEvent(type, message) {
    const timeStr = new Date().toLocaleTimeString();
    const cleanMsg = `[${timeStr}] [${type.toUpperCase()}] ${message}`;
    state.logs.push({ type, message: cleanMsg });
    if (state.logs.length > 100) state.logs.shift();
    saveState();
    
    // Auto-update log elements if demo tab is visible
    const consoleEl = document.getElementById("demo-log-console");
    if (consoleEl) {
        const line = document.createElement("div");
        line.className = `log-line ${type}`;
        line.innerText = cleanMsg;
        consoleEl.appendChild(line);
        consoleEl.scrollTop = consoleEl.scrollHeight;
    }
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

// ==========================================
// CORE ALGORITHMS
// ==========================================

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
    // Urgency component (max 35 pts)
    const urgencyVal = Math.min(10, Math.max(1, urgency));
    const urgencyPoints = urgencyVal * 3.5;

    // Quantity component (max 15 pts)
    const qtyPoints = Math.min(15.0, quantity * 0.3);

    // Shortage component (max 20 pts)
    const shortage = Math.max(0, quantity - availableStock);
    let shortagePoints = 0.0;
    if (shortage > 0 && quantity > 0) {
        shortagePoints = Math.min(20.0, (shortage / quantity) * 20.0);
    }

    // Status component & base priority points (approx 25 pts)
    const basePoints = 15.0; // Assume High-level priority boost dynamically

    let baseOperationalScore = urgencyPoints + qtyPoints + shortagePoints + basePoints;

    // Financial margin tie-breaker (max 5 pts)
    const margin = sellingPrice - unitCost;
    const estProfit = quantity * margin;
    const financialBonus = Math.min(5.0, (Math.max(0.0, estProfit) / 10000.0) * 5.0);

    const totalScore = Math.floor(Math.min(100.0, Math.max(0.0, baseOperationalScore + financialBonus)));

    let priority = "Medium";
    let action = "Process in standard queue. Release for picking once stock is verified.";
    if (totalScore >= 80) {
        priority = "Critical";
        action = "Prioritize immediate allocation, dispatch pickers. Escalate low stock immediately.";
    } else if (totalScore >= 60) {
        priority = "High";
        action = "Run allocation check and place in picking queue. Monitor packing progress.";
    } else if (totalScore >= 40) {
        priority = "Medium";
        action = "Process in standard queue. Release for picking once stock is verified.";
    } else {
        priority = "Low";
        action = "Consolidate dispatch or process during off-peak operational windows.";
    }

    let reason = `Customer urgency ${urgencyVal}/10 (+${urgencyPoints.toFixed(1)} pts). Quantity complexity (+${qtyPoints.toFixed(1)} pts). Shortage penalty (+${shortagePoints.toFixed(1)} pts). Financial profit bonus applied (+${financialBonus.toFixed(1)} pts).`;

    return { score: totalScore, level: priority, reason, action };
}

// Manhattan Picking Route Optimizer
function calculatePickingRouteSavings(locations) {
    if (!locations || locations.length < 2) return { stdDist: 0, optDist: 0, pct: 0 };

    function parseLoc(loc) {
        if (!loc || typeof loc !== "string") return [1, 1, 1];
        const parts = loc.split("-");
        if (parts.length < 3) return [1, 1, 1];
        const zoneChar = parts[0].toUpperCase();
        const zone = zoneChar.charCodeAt(0) - 65 + 1; // A=1, B=2, etc.
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
// SYSTEM SEEDING & RESETS
// ==========================================

function loadDefaultDataset() {
    state.products = JSON.parse(JSON.stringify(defaultProducts));
    state.orders = JSON.parse(JSON.stringify(defaultOrders));
    state.pickingTasks = JSON.parse(JSON.stringify(defaultPicking));
    state.packingOps = JSON.parse(JSON.stringify(defaultPacking));
    state.qualityChecks = [
        { order_code: "ORD004", product_code: "P003", quantity: 8, location: "B-02-01", checker: "System", status: "Pending" }
    ];
    state.exceptions = [
        { id: "EXP001", order_code: "ORD001", exception_type: "Stock Shortage", description: "Insufficient laptops (P004) to fulfill order quantity.", status: "Open", created_at: new Date().toISOString() }
    ];
    state.backorders = [
        { id: "BKO001", order_code: "ORD001", product_code: "P004", quantity: 10, status: "Open", created_at: new Date().toISOString() }
    ];
    state.allocations = [
        { order_code: "ORD001", product_code: "P004", requested_qty: 10, allocated_qty: 5, shortage_qty: 5, decision: "PARTIAL ALLOCATION" },
        { order_code: "ORD002", product_code: "P001", requested_qty: 15, allocated_qty: 15, shortage_qty: 0, decision: "FULL ALLOCATION" }
    ];
    
    // Seed initial order transactions
    state.transactions = [];
    state.orders.forEach(o => {
        const prod = state.products.find(p => p.product_code === o.product_code);
        const price = prod ? prod.selling_price : 0;
        const subtotal = o.quantity * price;
        const tax = Math.round(subtotal * 0.18);
        const shipping = subtotal >= 1000 ? 0 : 100;
        const total = subtotal + tax + shipping;
        const pStatus = (o.status === "Pending" || o.status === "Backordered") ? "Pending Payment" : "Paid";
        
        state.transactions.push({
            transaction_reference: `TXN-${o.order_code}`,
            order_code: o.order_code,
            customer: o.customer,
            product_code: o.product_code,
            quantity: o.quantity,
            unit_selling_price: price,
            subtotal,
            discount: 0,
            tax,
            shipping_fee: shipping,
            total_amount: total,
            payment_method: pStatus === "Paid" ? "UPI" : "Cash on Delivery",
            payment_status: pStatus,
            transaction_type: pStatus === "Paid" ? "DEBIT" : "PENDING",
            created_at: o.created_at
        });
    });

    state.returns = [
        { return_code: "RET001", order_code: "ORD004", customer: "Online Customer", product_code: "P003", quantity: 2, reason: "Defective Product", description: "Cable insulation was torn.", status: "Approved for Refund", inspection_condition: "Damaged", refund_amount: 600.0, requested_at: new Date().toISOString() }
    ];

    state.inventoryTransactions = [
        { product_code: "P001", transaction_type: "IN", quantity: 100, previous_stock: 0, new_stock: 100, reference: "Initial Seed", reason: "Warehouse setup", performed_by: "System", created_at: new Date().toISOString() }
    ];

    state.logs = [
        { type: "info", message: "[SYSTEM] Default database dataset successfully seeded." }
    ];

    saveState();
    logEvent("info", "Sample database loaded successfully!");
    renderAll();
}

function resetLocalDataset() {
    localStorage.removeItem("smart_fulfill_db");
    state = {
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
        logs: []
    };
    loadDefaultDataset();
}

// ==========================================
// TABS & INTERFACE ROUTING
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
    // Navigation Tabs
    const navItems = document.querySelectorAll(".nav-item");
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            navItems.forEach(i => i.classList.remove("active"));
            item.classList.add("active");
            
            const target = item.getAttribute("data-target");
            const sections = document.querySelectorAll(".content-section");
            sections.forEach(sec => sec.classList.remove("active-section"));
            
            const targetSec = document.getElementById(`${target}-section`);
            if (targetSec) {
                targetSec.classList.add("active-section");
            }
            
            // Re-render components for specific sections if needed (e.g. charts)
            if (target === "dashboard" || target === "analytics") {
                renderCharts();
            }
        });
    });

    // Sidebar clock
    setInterval(() => {
        const timeEl = document.getElementById("sidebar-time");
        const headerTimeEl = document.getElementById("header-timestamp");
        const now = new Date();
        const str = now.toLocaleString();
        if (timeEl) timeEl.innerText = str;
        if (headerTimeEl) headerTimeEl.innerText = str;
    }, 1000);

    // Initial load
    loadState();
    renderAll();
});

// ==========================================
// RENDERERS
// ==========================================

function renderAll() {
    populateProductSelectors();
    populateReturnOrderSelector();
    populateTimelineOrderSelector();

    renderDashboard();
    renderInventory();
    renderOrders();
    renderTransactions();
    renderReturns();
    renderAllocation();
    renderPicking();
    renderPacking();
    renderQuality();
    renderExceptions();
    renderBackorders();
    renderTimeline();
    renderAnalytics();
    renderDemoConsole();
}

// 1. DASHBOARD
function renderDashboard() {
    // Count stats
    const totalProd = state.products.length;
    let availUnits = 0;
    let lowStock = 0;
    let outStock = 0;
    
    state.products.forEach(p => {
        const avail = getAvailableStock(p);
        availUnits += avail;
        const status = getStockStatus(p);
        if (status === "LOW STOCK") lowStock++;
        if (status === "OUT OF STOCK") outStock++;
    });

    const totalOrd = state.orders.length;
    const pendingOrd = state.orders.filter(o => o.status === "Pending").length;
    const criticalOrd = state.orders.filter(o => o.priority === "Critical").length;
    const pickingOrd = state.orders.filter(o => o.status === "Picking" || o.status === "Picked").length;
    const packedOrd = state.orders.filter(o => o.status === "Packed" || o.status === "Ready for Dispatch").length;
    const dispatchedOrd = state.orders.filter(o => o.status === "Dispatched" || o.status === "Completed").length;

    const openExceptions = state.exceptions.filter(e => e.status === "Open" || e.status === "In Progress").length;
    const openBackorders = state.backorders.filter(b => b.status === "Open" || b.status === "Partially Fulfilled").length;

    // Financial numbers
    let totalInvVal = 0;
    let potentialSalesVal = 0;
    let potentialProfit = 0;
    let totalOrderVal = 0;
    let revenueAtRisk = 0;
    let profitAtRisk = 0;

    state.products.forEach(p => {
        const avail = getAvailableStock(p);
        totalInvVal += p.total_stock * p.unit_cost;
        potentialSalesVal += avail * p.selling_price;
        potentialProfit += avail * (p.selling_price - p.unit_cost);
    });

    state.transactions.forEach(t => {
        totalOrderVal += t.total_amount;
        if (t.payment_status === "Pending Payment") {
            revenueAtRisk += t.total_amount;
            const o = state.orders.find(ord => ord.order_code === t.order_code);
            const prod = state.products.find(p => p.product_code === t.product_code);
            if (prod) {
                profitAtRisk += t.quantity * (prod.selling_price - prod.unit_cost);
            }
        }
    });

    // Update DOM
    document.getElementById("db-total-products").innerText = totalProd;
    document.getElementById("db-available-stock").innerText = availUnits;
    document.getElementById("db-low-stock").innerText = lowStock;
    document.getElementById("db-out-stock").innerText = outStock;
    
    document.getElementById("db-total-orders").innerText = totalOrd;
    document.getElementById("db-pending-orders").innerText = pendingOrd;
    document.getElementById("db-critical-orders").innerText = criticalOrd;
    document.getElementById("db-picking-orders").innerText = pickingOrd;
    document.getElementById("db-packed-orders").innerText = packedOrd;
    document.getElementById("db-dispatched-orders").innerText = dispatchedOrd;
    
    document.getElementById("db-open-exceptions").innerText = openExceptions;
    document.getElementById("db-open-backorders").innerText = openBackorders;

    // Financial DOM
    document.getElementById("db-total-inv-val").innerText = formatINR(totalInvVal);
    document.getElementById("db-potential-sales-val").innerText = formatINR(potentialSalesVal);
    document.getElementById("db-potential-profit").innerText = formatINR(potentialProfit);
    document.getElementById("db-total-order-val").innerText = formatINR(totalOrderVal);
    document.getElementById("db-revenue-risk").innerText = formatINR(revenueAtRisk);
    document.getElementById("db-profit-risk").innerText = formatINR(profitAtRisk);

    // Calculate Risk Score (exceptions count, backorders, and out of stock items contribution)
    const calculatedRisk = Math.min(100, (openExceptions * 15) + (openBackorders * 10) + (outStock * 20));
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

    // Trigger System alerts lists
    const alertsList = document.getElementById("db-alerts-list");
    alertsList.innerHTML = "";
    
    // Low stock warnings
    state.products.forEach(p => {
        const avail = getAvailableStock(p);
        if (avail === 0) {
            alertsList.innerHTML += `<div class="alert-item alert-danger"><i class="fa-solid fa-triangle-exclamation"></i> <div><strong>Out of Stock:</strong> Product ${p.product_code} (${p.name}) is fully depleted.</div></div>`;
        } else if (avail <= p.reorder_level) {
            alertsList.innerHTML += `<div class="alert-item alert-warning"><i class="fa-solid fa-circle-exclamation"></i> <div><strong>Low Stock Warning:</strong> Product ${p.product_code} is at ${avail} units (Reorder at ${p.reorder_level}).</div></div>`;
        }
    });

    // Exception alert
    state.exceptions.forEach(e => {
        if (e.status === "Open") {
            alertsList.innerHTML += `<div class="alert-item alert-danger"><i class="fa-solid fa-bolt"></i> <div><strong>Open Exception:</strong> Order ${e.order_code} flags '${e.exception_type}': ${e.description}</div></div>`;
        }
    });

    if (alertsList.innerHTML === "") {
        alertsList.innerHTML = `<div class="alert-item alert-info"><i class="fa-solid fa-check-double"></i> <div>No critical operational alerts recorded. Warehouse is running smoothly.</div></div>`;
    }

    renderCharts();
}

// Charts generator
let orderStatusChart = null;
let orderPriorityChart = null;
let analyticsCategoryChart = null;
let analyticsMovementChart = null;

function renderCharts() {
    // Fetch data for statuses
    const statusCounts = {};
    state.orders.forEach(o => {
        statusCounts[o.status] = (statusCounts[o.status] || 0) + 1;
    });

    const priorityCounts = {};
    state.orders.forEach(o => {
        priorityCounts[o.priority] = (priorityCounts[o.priority] || 0) + 1;
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
                    backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#64748b', '#8b5cf6', '#ec4899', '#14b8a6'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#94a3b8' }
                    }
                }
            }
        });
    }

    const priorityCtx = document.getElementById("chart-order-priority");
    if (priorityCtx) {
        if (orderPriorityChart) orderPriorityChart.destroy();
        orderPriorityChart = new Chart(priorityCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(priorityCounts),
                datasets: [{
                    label: 'Orders',
                    data: Object.values(priorityCounts),
                    backgroundColor: '#3b82f6',
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

// 2. SMART INVENTORY
function renderInventory() {
    const tbody = document.getElementById("inv-table-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.products.forEach(p => {
        const avail = getAvailableStock(p);
        const status = getStockStatus(p);
        const value = p.total_stock * p.unit_cost;
        
        let statusClass = "bg-green";
        if (status === "LOW STOCK") statusClass = "bg-yellow";
        if (status === "OUT OF STOCK") statusClass = "bg-red";

        tbody.innerHTML += `
            <tr data-category="${p.category}" data-location="${p.location.charAt(0)}" data-status="${status}">
                <td><strong>${p.product_code}</strong></td>
                <td>${p.name}</td>
                <td>${p.category}</td>
                <td><span class="badge bg-blue"><i class="fa-solid fa-location-dot"></i> ${p.location}</span></td>
                <td>${p.total_stock}</td>
                <td>${p.reserved_stock}</td>
                <td>${p.damaged_stock}</td>
                <td><strong>${avail}</strong></td>
                <td>${p.reorder_level}</td>
                <td>${formatINR(p.unit_cost)}</td>
                <td>${formatINR(p.selling_price)}</td>
                <td><strong>${formatINR(value)}</strong></td>
                <td><span class="badge ${statusClass}">${status}</span></td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="triggerFastRestock('${p.product_code}')"><i class="fa-solid fa-arrows-rotate"></i> Quick Restock</button>
                </td>
            </tr>
        `;
    });

    // Render smart reorder recommendations
    const recList = document.getElementById("reorder-recommendations-list");
    recList.innerHTML = "";
    
    state.products.forEach(p => {
        const avail = getAvailableStock(p);
        if (avail <= p.reorder_level) {
            const urgency = avail === 0 ? "URGENT" : "HIGH";
            const itemClass = avail === 0 ? "reorder-item urgent" : "reorder-item high";
            const cost = p.reorder_quantity * p.unit_cost;
            recList.innerHTML += `
                <div class="${itemClass}">
                    <div class="reorder-info">
                        <h4>Replenish ${p.product_code} (${p.name})</h4>
                        <p>Available: ${avail} | Recommended Order: <strong>${p.reorder_quantity} units</strong> (Est. Cost: ${formatINR(cost)})</p>
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="executeReplenishOrder('${p.product_code}')">Order Now</button>
                </div>
            `;
        }
    });

    if (recList.innerHTML === "") {
        recList.innerHTML = `<div class="alert-item alert-info" style="width:100%;"><i class="fa-solid fa-check"></i> All products are healthy. No reorders needed!</div>`;
    }

    // Render stock movement ledger
    const ledgerBody = document.getElementById("inv-ledger-body");
    ledgerBody.innerHTML = "";
    
    const sortedTxns = [...state.inventoryTransactions].sort((a,b) => new Date(b.created_at) - new Date(a.created_at));
    sortedTxns.slice(0, 10).forEach(t => {
        const typeBadge = t.transaction_type === "IN" ? "bg-green" : "bg-red";
        ledgerBody.innerHTML += `
            <tr>
                <td><span class="badge ${typeBadge}">${t.transaction_type}</span></td>
                <td><strong>${t.product_code}</strong></td>
                <td>${t.quantity}</td>
                <td>${t.previous_stock} &rarr; ${t.new_stock}</td>
                <td>${t.reason || t.reference}</td>
                <td>${t.performed_by}</td>
                <td><span style="font-size:0.75rem; color:var(--text-muted);">${new Date(t.created_at).toLocaleTimeString()}</span></td>
            </tr>
        `;
    });

    if (ledgerBody.innerHTML === "") {
        ledgerBody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No transactions logged yet.</td></tr>`;
    }
}

// Dropdowns populator
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

    // Also populate categories dropdown
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
        const code = row.querySelector("td:nth-child(1)").innerText.toLowerCase();
        const name = row.querySelector("td:nth-child(2)").innerText.toLowerCase();
        const cat = row.getAttribute("data-category");
        const locZone = row.getAttribute("data-location");
        const status = row.getAttribute("data-status");

        const matchesSearch = code.includes(searchVal) || name.includes(searchVal);
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

// 3. ORDER MANAGEMENT
function renderOrders() {
    const tbody = document.getElementById("orders-board-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.orders.forEach(o => {
        const prod = state.products.find(p => p.product_code === o.product_code);
        const price = prod ? prod.selling_price : 0;
        const value = o.quantity * price;
        const cost = o.quantity * (prod ? prod.unit_cost : 0);
        const profit = value - cost;

        let statusClass = "bg-yellow";
        if (o.status === "Pending") statusClass = "bg-blue";
        if (o.status === "Dispatched") statusClass = "bg-green";
        if (o.status === "Completed") statusClass = "bg-green";
        if (o.status === "Cancelled") statusClass = "bg-red";

        let actionBtn = "";
        if (o.status === "Pending") {
            actionBtn = `<button class="btn btn-primary btn-sm" onclick="allocateOrderQuick('${o.order_code}')"><i class="fa-solid fa-brain"></i> Allocate</button>`;
        } else if (o.status === "Allocated") {
            actionBtn = `<button class="btn btn-secondary btn-sm" onclick="releaseToPicking('${o.order_code}')"><i class="fa-solid fa-person-shelves"></i> Release Picking</button>`;
        } else if (o.status === "Picking") {
            actionBtn = `<span class="badge bg-yellow">In Picking</span>`;
        } else {
            actionBtn = `<span class="badge bg-green">Processed</span>`;
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${o.order_code}</strong></td>
                <td>${o.customer}</td>
                <td><strong>${o.product_code}</strong> (${prod ? prod.name : 'N/A'})</td>
                <td>${o.quantity}</td>
                <td><strong class="badge bg-blue">${o.priority_score}</strong> (${o.priority})</td>
                <td>${formatINR(profit)}</td>
                <td><strong>${formatINR(value)}</strong></td>
                <td><span class="badge ${statusClass}">${o.status}</span></td>
                <td>
                    <div style="display:flex; gap:6px;">
                        ${actionBtn}
                        ${o.status !== "Cancelled" && o.status !== "Completed" && o.status !== "Dispatched" ? 
                          `<button class="btn btn-danger btn-sm" onclick="cancelOrderClient('${o.order_code}')"><i class="fa-solid fa-ban"></i></button>` : ''}
                    </div>
                </td>
            </tr>
        `;
    });
}

function updateOrderPreview() {
    const customer = document.getElementById("ord-customer").value;
    const pCode = document.getElementById("ord-product").value;
    const qty = parseInt(document.getElementById("ord-qty").value) || 0;
    const urgency = parseInt(document.getElementById("ord-urgency").value) || 5;
    
    // Update urgency value display
    document.getElementById("ord-urgency-val").innerText = urgency;

    const prod = state.products.find(p => p.product_code === pCode);
    if (!prod) return;

    const avail = getAvailableStock(prod);
    const shortage = Math.max(0, qty - avail);
    const subtotal = qty * prod.selling_price;
    const estProfit = qty * (prod.selling_price - prod.unit_cost);

    const calc = calculatePriorityScore(urgency, qty, avail, prod.selling_price, prod.unit_cost);

    // Update fields
    document.getElementById("pre-avail-stock").innerText = avail;
    document.getElementById("pre-shortage").innerText = shortage;
    document.getElementById("pre-price").innerText = formatINR(prod.selling_price);
    document.getElementById("pre-value").innerText = formatINR(subtotal);
    document.getElementById("pre-profit").innerText = formatINR(estProfit);
    document.getElementById("pre-priority-score").innerText = calc.score;
    
    const badge = document.getElementById("pre-priority-level");
    badge.innerText = calc.level;
    badge.className = `badge ${calc.level === 'Critical' || calc.level === 'High' ? 'bg-red' : 'bg-yellow'}`;

    document.getElementById("pre-explanation").innerText = `${calc.action} Reasoning: ${calc.reason}`;
}

// Generate sales order form submit
document.getElementById("create-order-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const customer = document.getElementById("ord-customer").value;
    const pCode = document.getElementById("ord-product").value;
    const qty = parseInt(document.getElementById("ord-qty").value);
    const urgency = parseInt(document.getElementById("ord-urgency").value);

    const prod = state.products.find(p => p.product_code === pCode);
    if (!prod) return;

    const avail = getAvailableStock(prod);
    const calc = calculatePriorityScore(urgency, qty, avail, prod.selling_price, prod.unit_cost);

    // Generate code
    const lastIdNum = state.orders.length > 0 ? parseInt(state.orders[state.orders.length - 1].order_code.substring(3)) : 0;
    const nextCode = `ORD${(lastIdNum + 1).toString().padStart(3, '0')}`;

    const newOrder = {
        order_code: nextCode,
        customer,
        product_code: pCode,
        quantity: qty,
        priority: calc.level,
        priority_score: calc.score,
        status: "Pending",
        created_at: new Date().toISOString()
    };

    state.orders.push(newOrder);

    // Automatically create order transaction
    const subtotal = qty * prod.selling_price;
    const tax = Math.round(subtotal * 0.18);
    const shipping = subtotal >= 1000 ? 0 : 100;
    const total = subtotal + tax + shipping;

    state.transactions.push({
        transaction_reference: `TXN-${nextCode}`,
        order_code: nextCode,
        customer,
        product_code: pCode,
        quantity: qty,
        unit_selling_price: prod.selling_price,
        subtotal,
        discount: 0,
        tax,
        shipping_fee: shipping,
        total_amount: total,
        payment_method: "Cash on Delivery",
        payment_status: "Pending Payment",
        transaction_type: "PENDING",
        created_at: new Date().toISOString()
    });

    // Save
    saveState();
    logEvent("success", `New order ${nextCode} generated for ${customer}. Priority: ${calc.level}.`);
    
    // Clear form
    document.getElementById("ord-customer").value = "";
    document.getElementById("ord-qty").value = 1;
    document.getElementById("ord-urgency").value = 5;

    renderAll();
});

// 4. ORDER TRANSACTIONS
function renderTransactions() {
    let totalInvoiced = 0;
    let paidAmount = 0;
    let pendingAmount = 0;

    state.transactions.forEach(t => {
        totalInvoiced += t.total_amount;
        if (t.payment_status === "Paid") {
            paidAmount += t.total_amount;
        } else if (t.payment_status === "Pending Payment") {
            pendingAmount += t.total_amount;
        }
    });

    document.getElementById("ar-total-sales").innerText = formatINR(totalInvoiced);
    document.getElementById("ar-paid-amount").innerText = formatINR(paidAmount);
    document.getElementById("ar-pending-amount").innerText = formatINR(pendingAmount);

    const tbody = document.getElementById("transactions-ledger-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.transactions.forEach(t => {
        const isPaid = t.payment_status === "Paid";
        const badgeClass = isPaid ? "bg-green" : "bg-yellow";
        
        let actions = "";
        if (!isPaid) {
            actions = `<button class="btn btn-success btn-sm" onclick="confirmPaymentClient('${t.order_code}')">Confirm Payment</button>`;
        } else {
            actions = `<span class="badge bg-green"><i class="fa-solid fa-circle-check"></i> Cleared</span>`;
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${t.transaction_reference}</strong></td>
                <td><strong>${t.order_code}</strong></td>
                <td>${t.customer}</td>
                <td>${t.quantity}</td>
                <td>${formatINR(t.subtotal)}</td>
                <td>${formatINR(t.tax)}</td>
                <td>${formatINR(t.shipping_fee)}</td>
                <td><strong>${formatINR(t.total_amount)}</strong></td>
                <td>${t.payment_method}</td>
                <td><span class="badge ${badgeClass}">${t.payment_status}</span></td>
                <td>${actions}</td>
            </tr>
        `;
    });
}

function confirmPaymentClient(orderCode) {
    const txn = state.transactions.find(t => t.order_code === orderCode);
    if (txn) {
        txn.payment_status = "Paid";
        txn.transaction_type = "DEBIT";
        txn.payment_method = "UPI"; // assume demo pays with UPI
        txn.updated_at = new Date().toISOString();
        saveState();
        logEvent("success", `Payment confirmed for Order ${orderCode}. Amount: ${formatINR(txn.total_amount)}.`);
        renderAll();
    }
}

// 5. RETURN MANAGEMENT
function renderReturns() {
    const tbody = document.getElementById("returns-board-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.returns.forEach(r => {
        let actions = "";
        
        if (r.status === "Requested") {
            actions = `
                <button class="btn btn-primary btn-sm" onclick="updateReturnStatus('${r.return_code}', 'Pickup Scheduled')">Schedule Pickup</button>
                <button class="btn btn-danger btn-sm" onclick="updateReturnStatus('${r.return_code}', 'Rejected')">Reject</button>
            `;
        } else if (r.status === "Pickup Scheduled") {
            actions = `<button class="btn btn-secondary btn-sm" onclick="updateReturnStatus('${r.return_code}', 'Received')">Receive Item</button>`;
        } else if (r.status === "Received") {
            actions = `<button class="btn btn-secondary btn-sm" onclick="updateReturnStatus('${r.return_code}', 'Inspection')">Inspect</button>`;
        } else if (r.status === "Inspection") {
            actions = `
                <button class="btn btn-success btn-sm" onclick="completeInspection('${r.return_code}', 'Approved for Refund', 'Resellable')">Approve (Resellable)</button>
                <button class="btn btn-danger btn-sm" onclick="completeInspection('${r.return_code}', 'Approved for Refund', 'Damaged')">Approve (Damaged)</button>
            `;
        } else if (r.status === "Approved for Refund") {
            actions = `<button class="btn btn-success btn-sm" onclick="processRefundClient('${r.return_code}')">Process Refund</button>`;
        } else if (r.status === "Refunded") {
            if (r.inspection_condition === "Resellable") {
                actions = `<button class="btn btn-primary btn-sm" onclick="restockReturnedItem('${r.return_code}')">Restock Product</button>`;
            } else {
                actions = `<button class="btn btn-secondary btn-sm" onclick="updateReturnStatus('${r.return_code}', 'Closed')">Close File</button>`;
            }
        } else {
            actions = `<span class="badge bg-green">RMA Closed</span>`;
        }

        let statusClass = "bg-blue";
        if (r.status === "Refunded" || r.status === "Restocked") statusClass = "bg-green";
        if (r.status === "Rejected") statusClass = "bg-red";
        if (r.status === "Inspection") statusClass = "bg-yellow";

        tbody.innerHTML += `
            <tr>
                <td><strong>${r.return_code}</strong></td>
                <td><strong>${r.order_code}</strong></td>
                <td>${r.customer}</td>
                <td><strong>${r.product_code}</strong></td>
                <td>${r.quantity}</td>
                <td>${r.reason}</td>
                <td><span class="badge bg-blue">${r.inspection_condition || 'Pending'}</span></td>
                <td>${formatINR(r.refund_amount || 0)}</td>
                <td><span class="badge ${statusClass}">${r.status}</span></td>
                <td>
                    <div style="display:flex; gap:6px;">${actions}</div>
                </td>
            </tr>
        `;
    });
}

function populateReturnOrderSelector() {
    const select = document.getElementById("ret-order-select");
    if (!select) return;
    select.innerHTML = "<option value=''>Select Completed/Dispatched Order</option>";
    state.orders.forEach(o => {
        if (o.status === "Dispatched" || o.status === "Completed" || o.status === "Packed") {
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
    const subtotal = order.quantity * (prod ? prod.selling_price : 0);

    preview.innerHTML = `
        <strong>Customer:</strong> ${order.customer} | <strong>Product:</strong> ${order.product_code} (${prod ? prod.name : 'N/A'})<br>
        <strong>Fulfilled Qty:</strong> ${order.quantity} units | <strong>Est. Value:</strong> ${formatINR(subtotal)}
    `;
    
    // Set max range for returning qty
    document.getElementById("ret-qty").max = order.quantity;
    document.getElementById("ret-qty").value = order.quantity;
}

document.getElementById("create-return-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const orderCode = document.getElementById("ret-order-select").value;
    const qty = parseInt(document.getElementById("ret-qty").value);
    const reason = document.getElementById("ret-reason").value;
    const desc = document.getElementById("ret-desc").value;

    if (!orderCode) return;

    const order = state.orders.find(o => o.order_code === orderCode);
    const prod = state.products.find(p => p.product_code === order.product_code);
    const refundAmount = qty * (prod ? prod.selling_price : 0);

    const lastRetIdNum = state.returns.length > 0 ? parseInt(state.returns[state.returns.length - 1].return_code.substring(3)) : 0;
    const nextRetCode = `RET${(lastRetIdNum + 1).toString().padStart(3, '0')}`;

    state.returns.push({
        return_code: nextRetCode,
        order_code: orderCode,
        customer: order.customer,
        product_code: order.product_code,
        quantity: qty,
        reason,
        description: desc,
        status: "Requested",
        inspection_condition: "Pending",
        refund_amount: refundAmount,
        requested_at: new Date().toISOString()
    });

    saveState();
    logEvent("warning", `RMA Return Request ${nextRetCode} filed for Order ${orderCode}. Reason: ${reason}.`);
    
    // reset form
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
        logEvent("info", `RMA ${returnCode} status updated to: ${nextStatus}.`);
        renderAll();
    }
}

function completeInspection(returnCode, nextStatus, condition) {
    const ret = state.returns.find(r => r.return_code === returnCode);
    if (ret) {
        ret.status = nextStatus;
        ret.inspection_condition = condition;
        saveState();
        logEvent("info", `RMA ${returnCode} inspection complete. Condition: ${condition}.`);
        renderAll();
    }
}

function processRefundClient(returnCode) {
    const ret = state.returns.find(r => r.return_code === returnCode);
    if (ret) {
        ret.status = "Refunded";
        saveState();
        logEvent("success", `Refund processed for RMA ${returnCode}. Amount: ${formatINR(ret.refund_amount)}.`);
        renderAll();
    }
}

function restockReturnedItem(returnCode) {
    const ret = state.returns.find(r => r.return_code === returnCode);
    if (ret) {
        const prod = state.products.find(p => p.product_code === ret.product_code);
        if (prod) {
            const prev = prod.total_stock;
            prod.total_stock += ret.quantity;
            ret.status = "Restocked";

            // Log stock transaction
            state.inventoryTransactions.push({
                product_code: prod.product_code,
                transaction_type: "IN",
                quantity: ret.quantity,
                previous_stock: prev,
                new_stock: prod.total_stock,
                reference: returnCode,
                reason: "Returned items restocked",
                performed_by: "Supervisor",
                created_at: new Date().toISOString()
            });

            saveState();
            logEvent("success", `RMA ${returnCode} closed. Restocked ${ret.quantity} units of ${prod.product_code}.`);
            renderAll();
        }
    }
}

// 6. SMART ALLOCATION
function renderAllocation() {
    const tbody = document.getElementById("allocation-queue-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    
    // Find pending orders
    const pendingOrders = state.orders.filter(o => o.status === "Pending");

    pendingOrders.forEach(o => {
        const prod = state.products.find(p => p.product_code === o.product_code);
        const avail = prod ? getAvailableStock(prod) : 0;
        
        let recommendation = "";
        let actionBtn = "";
        let textClass = "";

        if (avail >= o.quantity) {
            recommendation = `🟢 FULL ALLOCATION. Usable inventory is completely sufficient.`;
            actionBtn = `<button class="btn btn-success btn-sm" onclick="allocateOrderQuick('${o.order_code}')">Approve & Release</button>`;
        } else if (o.priority === "Critical" || o.priority === "High") {
            recommendation = `🟡 PARTIAL ALLOCATION. Release available ${avail} units, push shortage (${o.quantity - avail}) to backorder queue.`;
            actionBtn = `<button class="btn btn-warning btn-sm" onclick="allocateOrderQuick('${o.order_code}')">Release Partial</button>`;
        } else {
            recommendation = `🔴 HOLD ORDER. Insufficient stock. Backorder registered until restocked.`;
            actionBtn = `<button class="btn btn-danger btn-sm" onclick="allocateOrderQuick('${o.order_code}')">Hold & Backorder</button>`;
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${o.order_code}</strong> <span class="badge ${o.priority === 'Critical' ? 'bg-red' : 'bg-yellow'}">${o.priority}</span></td>
                <td><strong>${o.product_code}</strong> (${prod ? prod.name : 'N/A'})</td>
                <td><strong>${o.quantity}</strong></td>
                <td>${avail}</td>
                <td><span style="font-size:0.85rem;">${recommendation}</span></td>
                <td>${actionBtn}</td>
            </tr>
        `;
    });

    if (tbody.innerHTML === "") {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No orders awaiting allocation.</td></tr>`;
    }
}

// Smart Allocation engine execution
function allocateOrderQuick(orderCode) {
    const o = state.orders.find(ord => ord.order_code === orderCode);
    if (!o) return;

    const prod = state.products.find(p => p.product_code === o.product_code);
    if (!prod) return;

    const avail = getAvailableStock(prod);

    if (avail >= o.quantity) {
        // FULL ALLOCATION
        prod.reserved_stock += o.quantity;
        o.status = "Allocated";

        state.allocations.push({
            order_code: orderCode,
            product_code: o.product_code,
            requested_qty: o.quantity,
            allocated_qty: o.quantity,
            shortage_qty: 0,
            decision: "FULL ALLOCATION",
            created_at: new Date().toISOString()
        });

        logEvent("success", `Fully allocated ${o.quantity} units for Order ${orderCode}.`);
    } else if (o.priority === "Critical" || o.priority === "High") {
        // PARTIAL ALLOCATION
        const allocated = avail;
        const shortage = o.quantity - avail;

        prod.reserved_stock += allocated;
        o.status = "Allocated";

        state.allocations.push({
            order_code: orderCode,
            product_code: o.product_code,
            requested_qty: o.quantity,
            allocated_qty: allocated,
            shortage_qty: shortage,
            decision: "PARTIAL ALLOCATION",
            created_at: new Date().toISOString()
        });

        // Add backorder
        const lastBkoNum = state.backorders.length > 0 ? parseInt(state.backorders[state.backorders.length - 1].id.substring(3)) : 0;
        state.backorders.push({
            id: `BKO${(lastBkoNum + 1).toString().padStart(3, '0')}`,
            order_code: orderCode,
            product_code: o.product_code,
            quantity: shortage,
            status: "Open",
            created_at: new Date().toISOString()
        });

        // Add exception
        const lastExpNum = state.exceptions.length > 0 ? parseInt(state.exceptions[state.exceptions.length - 1].id.substring(3)) : 0;
        state.exceptions.push({
            id: `EXP${(lastExpNum + 1).toString().padStart(3, '0')}`,
            order_code: orderCode,
            exception_type: "Stock Shortage",
            description: `Order ${orderCode} partially filled. Awaiting replenishment of ${shortage} units.`,
            status: "Open",
            created_at: new Date().toISOString()
        });

        logEvent("warning", `Partially allocated ${allocated}/${o.quantity} for Order ${orderCode}. Registered backorder for shortage.`);
    } else {
        // HOLD ORDER
        o.status = "Backordered";

        state.allocations.push({
            order_code: orderCode,
            product_code: o.product_code,
            requested_qty: o.quantity,
            allocated_qty: 0,
            shortage_qty: o.quantity,
            decision: "HOLD ORDER",
            created_at: new Date().toISOString()
        });

        // Add backorder
        const lastBkoNum = state.backorders.length > 0 ? parseInt(state.backorders[state.backorders.length - 1].id.substring(3)) : 0;
        state.backorders.push({
            id: `BKO${(lastBkoNum + 1).toString().padStart(3, '0')}`,
            order_code: orderCode,
            product_code: o.product_code,
            quantity: o.quantity,
            status: "Open",
            created_at: new Date().toISOString()
        });

        // Add exception
        const lastExpNum = state.exceptions.length > 0 ? parseInt(state.exceptions[state.exceptions.length - 1].id.substring(3)) : 0;
        state.exceptions.push({
            id: `EXP${(lastExpNum + 1).toString().padStart(3, '0')}`,
            order_code: orderCode,
            exception_type: "Stock Shortage",
            description: `Order ${orderCode} is on HOLD due to stock depletion. Awaiting ${o.quantity} units.`,
            status: "Open",
            created_at: new Date().toISOString()
        });

        logEvent("danger", `Order ${orderCode} placed on HOLD due to insufficient stock.`);
    }

    saveState();
    renderAll();
}

function releaseToPicking(orderCode) {
    const o = state.orders.find(ord => ord.order_code === orderCode);
    if (o) {
        o.status = "Picking";
        
        // Find allocation count
        const alloc = state.allocations.find(a => a.order_code === orderCode);
        const qtyToPick = alloc ? alloc.allocated_qty : o.quantity;
        const prod = state.products.find(p => p.product_code === o.product_code);

        const lastPckNum = state.pickingTasks.length > 0 ? parseInt(state.pickingTasks[state.pickingTasks.length - 1].id.substring(3)) : 0;
        state.pickingTasks.push({
            id: `PCK${(lastPckNum + 1).toString().padStart(3, '0')}`,
            order_code: orderCode,
            product_code: o.product_code,
            quantity: qtyToPick,
            location: prod ? prod.location : "A-01-01",
            status: "Picking",
            created_at: new Date().toISOString()
        });

        saveState();
        logEvent("info", `Picking task registered for Order ${orderCode}. Relocated to aisle location.`);
        renderAll();
    }
}

// 7. PICKING WORKFLOW
function renderPicking() {
    const tbody = document.getElementById("picking-tasks-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    
    // Track picking locations to display savings
    const activeLocations = [];

    state.pickingTasks.forEach(p => {
        if (p.status === "Picking") {
            activeLocations.push(p.location);
        }

        let actionBtn = "";
        if (p.status === "Picking") {
            actionBtn = `<button class="btn btn-success btn-sm" onclick="completePickingClient('${p.id}')">Complete Pick</button>`;
        } else {
            actionBtn = `<span class="badge bg-green"><i class="fa-solid fa-circle-check"></i> Picked</span>`;
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${p.id}</strong></td>
                <td><strong>${p.order_code}</strong></td>
                <td>${p.product_code}</td>
                <td><span class="badge bg-blue">${p.location}</span></td>
                <td><strong>${p.quantity}</strong></td>
                <td><span class="badge ${p.status === 'Picking' ? 'bg-yellow' : 'bg-green'}">${p.status}</span></td>
                <td>${actionBtn}</td>
            </tr>
        `;
    });

    if (tbody.innerHTML === "") {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No active picking tasks.</td></tr>`;
    }

    // Display route calculations
    const calc = calculatePickingRouteSavings(activeLocations);
    document.getElementById("opt-std-dist").innerText = `${calc.stdDist} meters`;
    document.getElementById("opt-opt-dist").innerText = `${calc.optDist} meters`;
    document.getElementById("opt-savings").innerText = `${calc.pct}%`;

    const seqList = document.getElementById("opt-sequence-list");
    seqList.innerHTML = `<span class="node">Start (Dock)</span>`;
    
    if (calc.sortedLocations && calc.sortedLocations.length > 0) {
        calc.sortedLocations.forEach(loc => {
            seqList.innerHTML += `
                <span class="arrow"><i class="fa-solid fa-arrow-right"></i></span>
                <span class="node">${loc}</span>
            `;
        });
    }

    seqList.innerHTML += `
        <span class="arrow"><i class="fa-solid fa-arrow-right"></i></span>
        <span class="node finish">Finish (Packing Station)</span>
    `;
}

function completePickingClient(taskId) {
    const task = state.pickingTasks.find(t => t.id === taskId);
    if (task) {
        task.status = "Picked";

        const order = state.orders.find(o => o.order_code === task.order_code);
        if (order) {
            order.status = "Picking Completed"; // transition state
            
            // Push to packing queue
            state.packingOps.push({
                order_code: task.order_code,
                packaging_type: "Pending",
                packaging_cost: 0,
                handling_cost: 0,
                total_cost: 0,
                status: "Pending",
                packed_by: "Supervisor",
                created_at: new Date().toISOString()
            });
        }

        saveState();
        logEvent("success", `Picking task ${taskId} complete. Items delivered to packing lines.`);
        renderAll();
    }
}

// 8. PACKING WORKFLOW
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
                <button class="btn btn-primary btn-sm" onclick="packOrderQuick('${p.order_code}', 'Small Box', 15.0)">Pack Small Box (₹15)</button>
                <button class="btn btn-secondary btn-sm" onclick="packOrderQuick('${p.order_code}', 'Medium Box', 35.0)">Pack Medium Box (₹35)</button>
                <button class="btn btn-success btn-sm" onclick="packOrderQuick('${p.order_code}', 'Pallet', 120.0)">Pack Pallet (₹120)</button>
            `;
        } else {
            actions = `<span class="badge bg-green"><i class="fa-solid fa-circle-check"></i> Packed (${p.packaging_type})</span>`;
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${p.order_code}</strong></td>
                <td>${order.product_code}</td>
                <td><strong>${order.quantity}</strong></td>
                <td><span class="badge ${p.status === 'Pending' ? 'bg-yellow' : 'bg-green'}">${p.status}</span></td>
                <td>${p.packaging_type}</td>
                <td>${formatINR(p.total_cost)}</td>
                <td>
                    <div style="display:flex; gap:6px;">${actions}</div>
                </td>
            </tr>
        `;
    });

    if (tbody.innerHTML === "") {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No orders in packing queue.</td></tr>`;
    }
}

function packOrderQuick(orderCode, type, cost) {
    const pack = state.packingOps.find(p => p.order_code === orderCode);
    if (pack) {
        pack.status = "Packed";
        pack.packaging_type = type;
        pack.packaging_cost = cost;
        pack.handling_cost = 10.0; // standard handling cost
        pack.total_cost = cost + 10.0;
        pack.packed_at = new Date().toISOString();

        const o = state.orders.find(ord => ord.order_code === orderCode);
        if (o) {
            o.status = "Packed";
            
            // Add to quality queue
            state.qualityChecks.push({
                order_code: orderCode,
                product_code: o.product_code,
                quantity: o.quantity,
                checker: "Supervisor",
                status: "Pending"
            });
        }

        saveState();
        logEvent("success", `Order ${orderCode} packed in ${type}. Handling & packing: ${formatINR(pack.total_cost)}.`);
        renderAll();
    }
}

// 9. QUALITY CHECK
function renderQuality() {
    const tbody = document.getElementById("quality-queue-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.qualityChecks.forEach(q => {
        let actions = "";
        if (q.status === "Pending") {
            actions = `
                <button class="btn btn-success btn-sm" onclick="completeQC('${q.order_code}', 'Passed')">QC Pass</button>
                <button class="btn btn-danger btn-sm" onclick="completeQC('${q.order_code}', 'Failed')">QC Fail</button>
            `;
        } else {
            const cls = q.status === "Passed" ? "bg-green" : "bg-red";
            actions = `<span class="badge ${cls}"><i class="fa-solid fa-square-check"></i> ${q.status}</span>`;
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${q.order_code}</strong></td>
                <td><strong>${q.product_code}</strong></td>
                <td>${q.quantity}</td>
                <td>System Verification</td>
                <td>${q.checker}</td>
                <td><span class="badge ${q.status === 'Pending' ? 'bg-yellow' : q.status === 'Passed' ? 'bg-green' : 'bg-red'}">${q.status}</span></td>
                <td>
                    <div style="display:flex; gap:6px;">${actions}</div>
                </td>
            </tr>
        `;
    });

    if (tbody.innerHTML === "") {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No orders in Quality Check queue.</td></tr>`;
    }
}

function completeQC(orderCode, status) {
    const check = state.qualityChecks.find(q => q.order_code === orderCode);
    if (check) {
        check.status = status;

        const o = state.orders.find(ord => ord.order_code === orderCode);
        if (o) {
            if (status === "Passed") {
                o.status = "Ready for Dispatch";
                logEvent("success", `Quality check PASSED for Order ${orderCode}. ready for dispatch.`);
            } else {
                o.status = "Pending Exception";
                // File exception
                const lastExpNum = state.exceptions.length > 0 ? parseInt(state.exceptions[state.exceptions.length - 1].id.substring(3)) : 0;
                state.exceptions.push({
                    id: `EXP${(lastExpNum + 1).toString().padStart(3, '0')}`,
                    order_code: orderCode,
                    exception_type: "Quality Failure",
                    description: `Order ${orderCode} failed Quality Check. Retained in exception queue.`,
                    status: "Open",
                    created_at: new Date().toISOString()
                });
                logEvent("danger", `Quality check FAILED for Order ${orderCode}. Exception logged.`);
            }
        }

        saveState();
        renderAll();
    }
}

// 10. EXCEPTION MANAGEMENT
function renderExceptions() {
    const tbody = document.getElementById("exceptions-ledger-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.exceptions.forEach(e => {
        let actionBtn = "";
        if (e.status === "Open" || e.status === "In Progress") {
            actionBtn = `<button class="btn btn-primary btn-sm" onclick="resolveExceptionClient('${e.id}')">Resolve exception</button>`;
        } else {
            actionBtn = `<span class="badge bg-green">Resolved</span>`;
        }

        // Resolution mapping
        let rec = "Escalate to supervisor.";
        if (e.exception_type === "Stock Shortage") rec = "Check priority &rarr; Partial allocation &rarr; Create backorder &rarr; Trigger reorder";
        if (e.exception_type === "Damaged Item") rec = "Remove damaged quantity &rarr; Check replacement stock &rarr; Allocate replacement";
        if (e.exception_type === "Quality Failure") rec = "Hold order &rarr; Replace failed items &rarr; Perform quality check";

        tbody.innerHTML += `
            <tr>
                <td><strong>${e.id}</strong></td>
                <td><strong>${e.order_code}</strong></td>
                <td><span class="badge bg-red">${e.exception_type}</span></td>
                <td>${e.description}</td>
                <td><code style="color:#38bdf8;">${rec}</code></td>
                <td>${new Date(e.created_at).toLocaleDateString()}</td>
                <td><span class="badge ${e.status === 'Open' ? 'bg-red' : 'bg-green'}">${e.status}</span></td>
                <td>${actionBtn}</td>
            </tr>
        `;
    });

    if (tbody.innerHTML === "") {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:var(--text-muted);">No logged exceptions.</td></tr>`;
    }
}

function resolveExceptionClient(exceptionId) {
    const exp = state.exceptions.find(e => e.id === exceptionId);
    if (exp) {
        exp.status = "Resolved";
        
        // If it was a quality failure, send it back to "Ready for Dispatch"
        if (exp.exception_type === "Quality Failure") {
            const o = state.orders.find(ord => ord.order_code === exp.order_code);
            if (o) o.status = "Ready for Dispatch";
        }

        saveState();
        logEvent("success", `Exception ${exceptionId} resolved successfully.`);
        renderAll();
    }
}

// 11. BACKORDER MANAGEMENT
function renderBackorders() {
    const tbody = document.getElementById("backorders-ledger-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    state.backorders.forEach(b => {
        const prod = state.products.find(p => p.product_code === b.product_code);
        const avail = prod ? getAvailableStock(prod) : 0;
        
        let action = "";
        if (b.status === "Open" && avail >= b.quantity) {
            action = `<button class="btn btn-success btn-sm" onclick="fulfillBackorderClient('${b.id}')">Fulfill Backorder</button>`;
        } else if (b.status === "Open") {
            action = `
                <button class="btn btn-secondary btn-sm" disabled>Awaiting Stock</button>
                <button class="btn btn-danger btn-sm" onclick="cancelBackorderClient('${b.id}')">Cancel</button>
            `;
        } else {
            action = `<span class="badge bg-green">${b.status}</span>`;
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${b.id}</strong></td>
                <td><strong>${b.order_code}</strong></td>
                <td><strong>${b.product_code}</strong></td>
                <td><strong>${b.quantity}</strong></td>
                <td>${avail}</td>
                <td><span class="badge ${b.status === 'Open' ? 'bg-yellow' : 'bg-green'}">${b.status}</span></td>
                <td>${action}</td>
            </tr>
        `;
    });

    if (tbody.innerHTML === "") {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">No backordered items.</td></tr>`;
    }
}

function fulfillBackorderClient(bkoId) {
    const bko = state.backorders.find(b => b.id === bkoId);
    if (bko) {
        const prod = state.products.find(p => p.product_code === bko.product_code);
        if (prod && getAvailableStock(prod) >= bko.quantity) {
            const prevReserved = prod.reserved_stock;
            prod.reserved_stock += bko.quantity;
            bko.status = "Fulfilled";

            // Resolve associated exception if any
            const exp = state.exceptions.find(e => e.order_code === bko.order_code && e.exception_type === "Stock Shortage" && e.status === "Open");
            if (exp) exp.status = "Resolved";

            // Check if order is fully allocated
            const o = state.orders.find(ord => ord.order_code === bko.order_code);
            if (o) o.status = "Allocated"; // release to workflow

            saveState();
            logEvent("success", `Backorder ${bkoId} fulfilled. Awaiting order release.`);
            renderAll();
        }
    }
}

function cancelBackorderClient(bkoId) {
    const bko = state.backorders.find(b => b.id === bkoId);
    if (bko) {
        bko.status = "Cancelled";
        const o = state.orders.find(ord => ord.order_code === bko.order_code);
        if (o) o.status = "Cancelled";

        saveState();
        logEvent("danger", `Backorder ${bkoId} was cancelled.`);
        renderAll();
    }
}

// 12. DISPATCH & TIMELINE
function populateTimelineOrderSelector() {
    const select = document.getElementById("timeline-order-id");
    if (!select) return;
    select.innerHTML = "<option value=''>Select Order</option>";
    state.orders.forEach(o => {
        select.innerHTML += `<option value="${o.order_code}">${o.order_code} - ${o.customer} (${o.status})</option>`;
    });
}

function renderTimeline() {
    // Just a placeholder call, actual rendering is done when selected or simulated
    renderOrderTimeline();
}

function renderOrderTimeline() {
    const orderCode = document.getElementById("timeline-order-id").value;
    const box = document.getElementById("trace-results-box");
    if (!orderCode) {
        box.style.opacity = "0.5";
        return;
    }
    box.style.opacity = "1";

    const o = state.orders.find(ord => ord.order_code === orderCode);
    if (!o) return;

    const prod = state.products.find(p => p.product_code === o.product_code);
    const subtotal = o.quantity * (prod ? prod.selling_price : 0);

    // Update details
    document.getElementById("trace-customer").innerText = o.customer;
    document.getElementById("trace-product").innerText = `${o.product_code} (${prod ? prod.name : 'N/A'})`;
    document.getElementById("trace-value").innerText = formatINR(subtotal);
    
    const statusBadge = document.getElementById("trace-status");
    statusBadge.innerText = o.status;
    statusBadge.className = `badge ${o.status === 'Completed' || o.status === 'Dispatched' ? 'bg-green' : 'bg-yellow'}`;

    // Determine timeline stage index (1-8)
    const stages = [
        "Pending",               // 1
        "Allocated",             // 2
        "Picking",               // 3
        "Picking Completed",     // 4 (translates to ready for packing / packing in progress)
        "Packed",                // 4 (packed, ready for QC)
        "Ready for Dispatch",    // 6
        "Dispatched",            // 7
        "Completed"              // 8
    ];

    // Let's map order status directly to stage index
    let currentStageIndex = 1;
    if (o.status === "Pending") currentStageIndex = 1;
    else if (o.status === "Allocated") currentStageIndex = 2;
    else if (o.status === "Picking") currentStageIndex = 3;
    else if (o.status === "Picking Completed") currentStageIndex = 4;
    else if (o.status === "Packed") currentStageIndex = 5;
    else if (o.status === "Ready for Dispatch") currentStageIndex = 6;
    else if (o.status === "Dispatched") currentStageIndex = 7;
    else if (o.status === "Completed") currentStageIndex = 8;
    else if (o.status === "Cancelled") currentStageIndex = 0;

    const progressPct = currentStageIndex === 0 ? 0 : Math.round((currentStageIndex / 8) * 100);
    document.getElementById("trace-pct").innerText = `${progressPct}%`;
    document.getElementById("trace-progress-fill").style.width = `${progressPct}%`;

    // Reset stages classes
    for (let i = 1; i <= 8; i++) {
        const node = document.getElementById(`step-${i}`);
        if (!node) continue;
        node.className = "step-node";
        
        if (i < currentStageIndex) {
            node.classList.add("completed");
        } else if (i === currentStageIndex) {
            node.classList.add("active");
        } else {
            node.classList.add("pending");
        }
    }

    // Action button
    const actionsPanel = document.getElementById("timeline-actions-panel");
    actionsPanel.innerHTML = "";

    if (o.status === "Ready for Dispatch") {
        actionsPanel.innerHTML = `<button class="btn btn-success" onclick="dispatchOrderClient('${o.order_code}')"><i class="fa-solid fa-truck"></i> Ship & Dispatch Order</button>`;
    } else if (o.status === "Dispatched") {
        actionsPanel.innerHTML = `<button class="btn btn-success" onclick="completeOrderClient('${o.order_code}')"><i class="fa-solid fa-circle-check"></i> Mark Completed (Delivered)</button>`;
    }
}

function dispatchOrderClient(orderCode) {
    const o = state.orders.find(ord => ord.order_code === orderCode);
    if (o) {
        o.status = "Dispatched";
        
        // Subtract inventory reserved stock
        const prod = state.products.find(p => p.product_code === o.product_code);
        if (prod) {
            const prev = prod.total_stock;
            prod.total_stock -= o.quantity;
            prod.reserved_stock -= o.quantity;

            // Log stock out transaction
            state.inventoryTransactions.push({
                product_code: prod.product_code,
                transaction_type: "OUT",
                quantity: o.quantity,
                previous_stock: prev,
                new_stock: prod.total_stock,
                reference: orderCode,
                reason: "Sales Order Dispatch",
                performed_by: "Shipping Agent",
                created_at: new Date().toISOString()
            });
        }

        saveState();
        logEvent("success", `Order ${orderCode} dispatched. Carrier assigned.`);
        renderAll();
    }
}

function completeOrderClient(orderCode) {
    const o = state.orders.find(ord => ord.order_code === orderCode);
    if (o) {
        o.status = "Completed";
        saveState();
        logEvent("success", `Order ${orderCode} marked Completed. Delivery confirmed.`);
        renderAll();
    }
}

function cancelOrderClient(orderCode) {
    const o = state.orders.find(ord => ord.order_code === orderCode);
    if (o) {
        // Release reservation if allocated
        const prod = state.products.find(p => p.product_code === o.product_code);
        const alloc = state.allocations.find(a => a.order_code === orderCode);
        
        if (prod && alloc && alloc.allocated_qty > 0) {
            prod.reserved_stock -= alloc.allocated_qty;
        }

        o.status = "Cancelled";
        
        // Cancel transaction
        const txn = state.transactions.find(t => t.order_code === orderCode);
        if (txn) {
            txn.payment_status = "Cancelled";
            txn.transaction_type = "VOIDED";
        }

        saveState();
        logEvent("danger", `Order ${orderCode} has been cancelled.`);
        renderAll();
    }
}

// 13. ANALYTICS & INSIGHTS
function renderAnalytics() {
    // KPI metrics
    let revenue = 0;
    let profit = 0;
    let refunds = 0;
    let stockIn = 0;
    let stockOut = 0;

    state.transactions.forEach(t => {
        if (t.payment_status === "Paid") {
            revenue += t.total_amount;
            const prod = state.products.find(p => p.product_code === t.product_code);
            if (prod) {
                profit += t.quantity * (prod.selling_price - prod.unit_cost);
            }
        }
    });

    state.returns.forEach(r => {
        if (r.status === "Refunded" || r.status === "Restocked" || r.status === "Closed") {
            refunds += r.refund_amount;
        }
    });

    state.inventoryTransactions.forEach(t => {
        if (t.transaction_type === "IN") stockIn += t.quantity;
        if (t.transaction_type === "OUT") stockOut += t.quantity;
    });

    const returnRate = state.orders.length > 0 ? ((state.returns.length / state.orders.length) * 100).toFixed(1) : 0;

    document.getElementById("kpi-revenue").innerText = formatINR(revenue);
    document.getElementById("kpi-profit").innerText = formatINR(profit);
    document.getElementById("kpi-refunds").innerText = formatINR(refunds);
    document.getElementById("kpi-return-rate").innerText = `${returnRate}%`;
    document.getElementById("kpi-turnover").innerText = "4.2x"; // Static placeholder
    document.getElementById("kpi-stock-in").innerText = `${stockIn} units`;
    document.getElementById("kpi-stock-out").innerText = `${stockOut} units`;

    // Analytics Chart (Categories and stock movements)
    const catCtx = document.getElementById("chart-analytics-categories");
    if (catCtx) {
        // Collect category sales value
        const catSales = {};
        state.transactions.forEach(t => {
            const prod = state.products.find(p => p.product_code === t.product_code);
            if (prod) {
                catSales[prod.category] = (catSales[prod.category] || 0) + t.total_amount;
            }
        });

        if (analyticsCategoryChart) analyticsCategoryChart.destroy();
        analyticsCategoryChart = new Chart(catCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(catSales),
                datasets: [{
                    label: 'Sales Revenue',
                    data: Object.values(catSales),
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

    const mvmtCtx = document.getElementById("chart-analytics-movements");
    if (mvmtCtx) {
        if (analyticsMovementChart) analyticsMovementChart.destroy();
        analyticsMovementChart = new Chart(mvmtCtx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [
                    { label: 'Stock IN', data: [50, 120, 80, stockIn], borderColor: '#10b981', fill: false, tension: 0.1 },
                    { label: 'Stock OUT', data: [30, 90, 70, stockOut], borderColor: '#ef4444', fill: false, tension: 0.1 }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                },
                plugins: { legend: { labels: { color: '#94a3b8' } } }
            }
        });
    }
}

// 14. HACKATHON DEMO MODE
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

function clearLogConsole() {
    state.logs = [];
    saveState();
    renderDemoConsole();
}

// ==========================================
// SIMULATOR FUNCTIONS (PRESENTATION CRITICAL)
// ==========================================

// 1. Simulate Order
function simulateOrder() {
    const customers = ["Global Retailers", "Tech Distributors LLC", "Metro Electronics", "Express Shipments"];
    const randomCustomer = customers[Math.floor(Math.random() * customers.length)];
    const randomProduct = state.products[Math.floor(Math.random() * state.products.length)];
    const qty = Math.floor(Math.random() * 8) + 2;
    const urgency = Math.floor(Math.random() * 9) + 2;

    const avail = getAvailableStock(randomProduct);
    const calc = calculatePriorityScore(urgency, qty, avail, randomProduct.selling_price, randomProduct.unit_cost);

    const lastIdNum = state.orders.length > 0 ? parseInt(state.orders[state.orders.length - 1].order_code.substring(3)) : 0;
    const nextCode = `ORD${(lastIdNum + 1).toString().padStart(3, '0')}`;

    const newOrder = {
        order_code: nextCode,
        customer: randomCustomer,
        product_code: randomProduct.product_code,
        quantity: qty,
        priority: calc.level,
        priority_score: calc.score,
        status: "Pending",
        created_at: new Date().toISOString()
    };

    state.orders.push(newOrder);

    // Auto transaction
    const subtotal = qty * randomProduct.selling_price;
    const tax = Math.round(subtotal * 0.18);
    const shipping = subtotal >= 1000 ? 0 : 100;
    const total = subtotal + tax + shipping;

    state.transactions.push({
        transaction_reference: `TXN-${nextCode}`,
        order_code: nextCode,
        customer: randomCustomer,
        product_code: randomProduct.product_code,
        quantity: qty,
        unit_selling_price: randomProduct.selling_price,
        subtotal,
        discount: 0,
        tax,
        shipping_fee: shipping,
        total_amount: total,
        payment_method: "Cash on Delivery",
        payment_status: "Pending Payment",
        transaction_type: "PENDING",
        created_at: new Date().toISOString()
    });

    saveState();
    logEvent("info", `[SIMULATION] Simulated New Order ${nextCode} for ${randomCustomer} requesting ${qty}x ${randomProduct.product_code}. Priority: ${calc.level}.`);
    renderAll();
}

// 2. Simulate Payment
function simulatePayment() {
    const pendingTxns = state.transactions.filter(t => t.payment_status === "Pending Payment");
    if (pendingTxns.length === 0) {
        logEvent("warning", "[SIMULATION] No pending transactions available to pay.");
        return;
    }

    const t = pendingTxns[Math.floor(Math.random() * pendingTxns.length)];
    t.payment_status = "Paid";
    t.transaction_type = "DEBIT";
    t.payment_method = "UPI";
    t.updated_at = new Date().toISOString();

    saveState();
    logEvent("success", `[SIMULATION] Simulated Payment for Order ${t.order_code}. Amount received: ${formatINR(t.total_amount)} via UPI.`);
    renderAll();
}

// 3. Simulate Return
function simulateReturn() {
    const fulfilledOrders = state.orders.filter(o => o.status === "Dispatched" || o.status === "Completed");
    if (fulfilledOrders.length === 0) {
        logEvent("warning", "[SIMULATION] No dispatched or completed orders available to return.");
        return;
    }

    const o = fulfilledOrders[Math.floor(Math.random() * fulfilledOrders.length)];
    const prod = state.products.find(p => p.product_code === o.product_code);
    const qty = Math.ceil(o.quantity / 2);
    const refund = qty * (prod ? prod.selling_price : 0);

    const lastRetIdNum = state.returns.length > 0 ? parseInt(state.returns[state.returns.length - 1].return_code.substring(3)) : 0;
    const nextRetCode = `RET${(lastRetIdNum + 1).toString().padStart(3, '0')}`;

    state.returns.push({
        return_code: nextRetCode,
        order_code: o.order_code,
        customer: o.customer,
        product_code: o.product_code,
        quantity: qty,
        reason: "Wrong Product",
        description: "Customer requested a different specs size.",
        status: "Requested",
        inspection_condition: "Pending",
        refund_amount: refund,
        requested_at: new Date().toISOString()
    });

    saveState();
    logEvent("warning", `[SIMULATION] Simulated Return request ${nextRetCode} filed for Order ${o.order_code}. Refund value: ${formatINR(refund)}.`);
    renderAll();
}

// 4. Simulate Stock Shortage
function simulateShortage() {
    // depleted smartphones or laptops
    const laptop = state.products.find(p => p.product_code === "P004");
    if (laptop) {
        laptop.total_stock = 0;
        laptop.reserved_stock = 0;
        laptop.damaged_stock = 0;
    }
    const watch = state.products.find(p => p.product_code === "P006");
    if (watch) {
        watch.total_stock = 0;
        watch.reserved_stock = 0;
        watch.damaged_stock = 0;
    }

    saveState();
    logEvent("danger", "[SIMULATION] Forced Stock Shortage simulation triggered: Depleted P004 and P006 to 0 units. Stock reorder alarms activated.");
    renderAll();
}

// 5. Simulate Dispatch
function simulateDispatch() {
    const readyOrders = state.orders.filter(o => o.status === "Ready for Dispatch");
    if (readyOrders.length === 0) {
        // Find any order and force it to ready first
        const pending = state.orders.find(o => o.status === "Pending" || o.status === "Allocated");
        if (pending) {
            pending.status = "Ready for Dispatch";
            logEvent("info", `[SIMULATION] Fast-tracked Order ${pending.order_code} status to Ready for Dispatch.`);
            dispatchOrderClient(pending.order_code);
        } else {
            logEvent("warning", "[SIMULATION] No orders available for dispatch. Generate or release some orders first.");
        }
        return;
    }

    const o = readyOrders[0];
    dispatchOrderClient(o.order_code);
}

// ==========================================
// INVENTORY POPUPS & FORMS
// ==========================================

function openInventoryModal(actionType) {
    const modal = document.getElementById("inventory-modal");
    const title = document.getElementById("modal-title");
    const actionInput = document.getElementById("modal-action-type");
    const submitBtn = document.getElementById("modal-submit-btn");

    actionInput.value = actionType;
    modal.classList.add("active");

    if (actionType === "stock-in") {
        title.innerText = "Execute Stock Check In";
        submitBtn.innerText = "Process Check In";
    } else if (actionType === "stock-out") {
        title.innerText = "Execute Stock Check Out";
        submitBtn.innerText = "Process Check Out";
    } else if (actionType === "stock-adjust") {
        title.innerText = "Reconcile / Adjust Stock";
        submitBtn.innerText = "Process Adjustment";
    } else if (actionType === "mark-damaged") {
        title.innerText = "Register Damaged Goods";
        submitBtn.innerText = "Report Damaged";
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
    const reason = document.getElementById("modal-reason").value;

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
            reason: reason || "Manual Stock Check In",
            performed_by: "Supervisor",
            created_at: new Date().toISOString()
        });
        logEvent("success", `Stock In Completed: ${qty} units of ${pCode} received. New count: ${prod.total_stock}.`);
    } else if (action === "stock-out") {
        const avail = getAvailableStock(prod);
        if (qty > avail) {
            alert(`Error: Insufficient available stock. Cannot ship ${qty} units (Only ${avail} available).`);
            return;
        }
        prod.total_stock -= qty;
        state.inventoryTransactions.push({
            product_code: pCode,
            transaction_type: "OUT",
            quantity: qty,
            previous_stock: prev,
            new_stock: prod.total_stock,
            reason: reason || "Manual Stock Check Out",
            performed_by: "Supervisor",
            created_at: new Date().toISOString()
        });
        logEvent("danger", `Stock Out Completed: ${qty} units of ${pCode} shipped. New count: ${prod.total_stock}.`);
    } else if (action === "stock-adjust") {
        prod.total_stock = qty; // adjust sets absolute total
        state.inventoryTransactions.push({
            product_code: pCode,
            transaction_type: "ADJUSTMENT",
            quantity: qty - prev,
            previous_stock: prev,
            new_stock: qty,
            reason: reason || "Physical audit adjustment",
            performed_by: "Supervisor",
            created_at: new Date().toISOString()
        });
        logEvent("warning", `Inventory Count Adjusted: ${pCode} set to ${qty}. Deviation: ${qty - prev} units.`);
    } else if (action === "mark-damaged") {
        const avail = getAvailableStock(prod);
        if (qty > avail) {
            alert(`Error: Cannot mark ${qty} units as damaged. Only ${avail} units are available.`);
            return;
        }
        prod.damaged_stock += qty;
        logEvent("danger", `Goods Damaged Alert: Registered ${qty} units of ${pCode} as unsellable damaged goods.`);
    }

    saveState();
    closeInventoryModal();
    renderAll();
}

function triggerFastRestock(pCode) {
    const prod = state.products.find(p => p.product_code === pCode);
    if (prod) {
        executeReplenishOrder(pCode);
    }
}

function executeReplenishOrder(pCode) {
    const prod = state.products.find(p => p.product_code === pCode);
    if (prod) {
        const prev = prod.total_stock;
        const addQty = prod.reorder_quantity;
        prod.total_stock += addQty;

        // Log transaction
        state.inventoryTransactions.push({
            product_code: pCode,
            transaction_type: "IN",
            quantity: addQty,
            previous_stock: prev,
            new_stock: prod.total_stock,
            reason: "Smart Reorder Auto-replenish",
            performed_by: "System Engine",
            created_at: new Date().toISOString()
        });

        // Resolve associated stock shortage exceptions
        const associatedExceptions = state.exceptions.filter(e => e.exception_type === "Stock Shortage" && e.status === "Open");
        associatedExceptions.forEach(e => {
            const o = state.orders.find(ord => ord.order_code === e.order_code);
            if (o && o.product_code === pCode) {
                // If we now have enough stock to fulfill this order, we can mark exception as in progress or resolved
                e.status = "Resolved";
            }
        });

        saveState();
        logEvent("success", `Replenishment complete for ${pCode} (${prod.name}). Added ${addQty} units. System reconciled exceptions.`);
        renderAll();
    }
}
