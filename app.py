import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Import database helper functions
from database import (
    get_connection,
    initialize_database,
    create_order,
    execute_allocation,
    update_order_status,
    create_exception,
    get_exceptions,
    close_exception,
    update_exception_status,
    get_backorders,
    update_backorder_status,
    fulfill_backorder_db,
    create_picking_task,
    get_picking_tasks,
    update_picking_task_status,
    create_packing_operation,
    update_packing_operation,
    get_packing_history,
    record_stock_in,
    record_stock_out,
    record_stock_adjustment,
    record_damaged_stock,
    get_inventory_transactions,
    get_order_transactions,
    update_order_transaction_payment_status,
    cancel_order_db,
    get_return_orders,
    create_return_order,
    update_return_order_status
)

# Import smart engine helper functions
from smart_engine import (
    calculate_priority_score,
    get_available_stock,
    get_stock_status,
    allocate_inventory,
    get_reorder_recommendation,
    resolve_exception,
    optimize_picking_route,
    calculate_picking_route_savings,
    explain_decision,
    format_inr
)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="SmartFulfill - Smart Warehouse Operations",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database tables and add sample data (safe from overwriting)
initialize_database()

# ============================================================
# DYNAMIC STYLING & BRANDING
# ============================================================
st.markdown("""
<style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1e293b;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    .timeline-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2rem 0;
        padding: 1rem;
        background-color: #f8fafc;
        border-radius: 0.5rem;
    }
    .timeline-step {
        text-align: center;
        flex: 1;
        position: relative;
    }
    .timeline-step:not(:last-child)::after {
        content: '';
        position: absolute;
        top: 25%;
        left: 50%;
        width: 100%;
        height: 2px;
        background-color: #cbd5e1;
        z-index: 1;
    }
    .timeline-icon {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.5rem auto;
        font-weight: bold;
        z-index: 2;
        position: relative;
    }
    .timeline-active .timeline-icon {
        background-color: #3b82f6;
        color: white;
    }
    .timeline-completed .timeline-icon {
        background-color: #10b981;
        color: white;
    }
    .customer-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 0.5rem;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
    }
    .customer-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Branding Header
st.markdown("""
<div style="background-color:#1e293b; padding:1.5rem; border-radius:0.5rem; margin-bottom:2rem; color:white">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h1 style="margin:0; font-weight:700; color:#f8fafc;">📦 SmartFulfill</h1>
            <p style="margin:0.25rem 0 0 0; color:#cbd5e1; font-size:1.1rem;">Intelligent Smart Warehouse Operations & Financial Intelligence Platform</p>
        </div>
        <div style="text-align:right;">
            <span style="background-color:#10b981; color:white; padding:0.3rem 0.6rem; border-radius:1rem; font-size:0.85rem; font-weight:600;">🟢 Warehouse System Online</span>
            <p style="margin:0.25rem 0 0 0; color:#94a3b8; font-size:0.8rem;">Data Sync: SQLite Connected</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# DATA INGESTION
# ============================================================
def get_products():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            product_code,
            name,
            category,
            location,
            total_stock,
            reserved_stock,
            damaged_stock,
            reorder_level,
            reorder_quantity,
            unit_cost,
            selling_price
        FROM products
        ORDER BY product_code
        """,
        conn
    )
    conn.close()
    if not df.empty:
        df["available_stock"] = df.apply(
            lambda r: get_available_stock(r["total_stock"], r["reserved_stock"], r["damaged_stock"]),
            axis=1
        )
        # Financial Calculations
        df["inventory_value"] = df["available_stock"] * df["unit_cost"]
        df["potential_sales_value"] = df["available_stock"] * df["selling_price"]
        df["potential_profit"] = df["potential_sales_value"] - df["inventory_value"]
    else:
        df["available_stock"] = pd.Series(dtype="int64")
        df["inventory_value"] = pd.Series(dtype="float64")
        df["potential_sales_value"] = pd.Series(dtype="float64")
        df["potential_profit"] = pd.Series(dtype="float64")
    return df

def get_orders():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            order_code,
            customer,
            product_code,
            quantity,
            priority,
            priority_score,
            status,
            created_at
        FROM orders
        ORDER BY priority_score DESC, id DESC
        """,
        conn
    )
    conn.close()
    return df

def get_allocations():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            order_code,
            product_code,
            requested_quantity,
            allocated_quantity,
            shortage_quantity,
            decision,
            created_at
        FROM allocations
        ORDER BY id DESC
        """,
        conn
    )
    conn.close()
    return df

def get_backorders():
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            """
            SELECT
                id,
                order_code,
                product_code,
                quantity,
                status,
                created_at
            FROM backorders
            ORDER BY id DESC
            """,
            conn
        )
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

def add_product_names(df, products_df):
    if df.empty or products_df.empty:
        return df
    result = df.copy()
    product_map = dict(zip(products_df["product_code"], products_df["name"]))
    if "product_code" in result.columns and "product_name" not in result.columns:
        result.insert(
            result.columns.get_loc("product_code") + 1,
            "product_name",
            result["product_code"].map(product_map)
        )
    elif "Product Code" in result.columns and "product_name" not in result.columns:
        result.insert(
            result.columns.get_loc("Product Code") + 1,
            "product_name",
            result["Product Code"].map(product_map)
        )
    return result

# Load central dataframes
products = get_products()
orders = get_orders()

# ============================================================
# DATABASE-LEVEL FILTERING FUNCTIONS (CUSTOMER PORTAL PRIVACY)
# ============================================================
def get_customer_orders_db(customer_name):
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            order_code,
            customer,
            product_code,
            quantity,
            priority,
            priority_score,
            status,
            created_at
        FROM orders
        WHERE UPPER(customer) = UPPER(?)
        ORDER BY id DESC
        """,
        conn,
        params=(customer_name,)
    )
    conn.close()
    return df

def get_customer_order_db(order_code, customer_name):
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            order_code,
            customer,
            product_code,
            quantity,
            priority,
            priority_score,
            status,
            created_at
        FROM orders
        WHERE UPPER(order_code) = UPPER(?) AND UPPER(customer) = UPPER(?)
        """,
        conn,
        params=(order_code, customer_name)
    )
    conn.close()
    return df

def get_customer_backorders_count_db(customer_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT COUNT(DISTINCT o.order_code)
        FROM orders o
        LEFT JOIN backorders b ON o.order_code = b.order_code
        WHERE UPPER(o.customer) = UPPER(?) AND (o.status = 'Backordered' OR b.status = 'Open')
        """,
        (customer_name,)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ============================================================
# PERSPECTIVE SWITCHING (WAREHOUSE SIDE vs CUSTOMER SIDE)
# ============================================================
perspective = st.sidebar.selectbox("🔑 Select View Perspective", ["🏢 Warehouse Staff", "👤 Customer"])

# ============================================================
# OPERATIONAL METRICS CALCULATION (GLOBAL FOR ENGINE)
# ============================================================
total_products = len(products)
available_stock_sum = int(products["available_stock"].sum()) if not products.empty else 0
low_stock_count = int(((products["available_stock"] > 0) & (products["available_stock"] <= products["reorder_level"])).sum()) if not products.empty else 0
out_of_stock_count = int((products["available_stock"] <= 0).sum()) if not products.empty else 0

total_orders = len(orders)
pending_orders_count = int((orders["status"] == "Pending").sum()) if not orders.empty else 0
critical_orders_count = int((orders["priority"] == "Critical").sum()) if not orders.empty else 0
picking_orders_count = int((orders["status"] == "Picking").sum()) if not orders.empty else 0
packed_orders_count = int((orders["status"] == "Packed").sum()) if not orders.empty else 0
dispatched_orders_count = int((orders["status"] == "Dispatched").sum()) if not orders.empty else 0

exceptions_rows = get_exceptions()
total_exceptions_count = len(exceptions_rows)
open_exceptions_count = sum(1 for r in exceptions_rows if r[5] in ["Open", "In Progress"])

backorders_df = get_backorders()
open_backorders_count = int((backorders_df["status"] == "Open").sum()) if not backorders_df.empty else 0

# Financial Metrics Calculation
total_inventory_value = 0.0
potential_sales_value = 0.0
potential_profit = 0.0

if not products.empty:
    total_inventory_value = float(products["inventory_value"].sum())
    potential_sales_value = float(products["potential_sales_value"].sum())
    potential_profit = float(products["potential_profit"].sum())

# Total Order Value, Total Order Cost, and Estimated Order Profit from DB
total_order_value = 0.0
total_order_cost = 0.0
estimated_order_profit = 0.0
revenue_at_risk = 0.0
profit_at_risk = 0.0

product_financials = {}
if not products.empty:
    for _, row in products.iterrows():
        product_financials[row["product_code"]] = (row["unit_cost"], row["selling_price"])

# Retrieve packing operations costs
conn = get_connection()
cursor = conn.cursor()
try:
    cursor.execute("SELECT order_code, total_cost FROM packing_operations")
    packing_costs = {row[0]: row[1] for row in cursor.fetchall()}
except Exception:
    packing_costs = {}
conn.close()

if not orders.empty:
    for _, row in orders.iterrows():
        o_code = row["order_code"]
        p_code = row["product_code"]
        qty = row["quantity"]
        if p_code in product_financials:
            cost, price = product_financials[p_code]
            o_val = qty * price
            o_cost = qty * cost
            p_cost = packing_costs.get(o_code, 0.0)
            total_order_value += o_val
            total_order_cost += (o_cost + p_cost)
            estimated_order_profit += (o_val - o_cost - p_cost)

if not backorders_df.empty:
    open_b = backorders_df[backorders_df["status"] == "Open"]
    for _, row in open_b.iterrows():
        p_code = row["product_code"]
        qty = row["quantity"]
        if p_code in product_financials:
            cost, price = product_financials[p_code]
            r_risk = qty * price
            p_risk = qty * (price - cost)
            revenue_at_risk += r_risk
            profit_at_risk += p_risk

# --------------------------------------------------------
# NEW FINANCIAL & RETURN TRANSACTIONS METRICS (GLOBAL)
# --------------------------------------------------------
conn = get_connection()
cursor = conn.cursor()

# Order Transactions count and values
try:
    cursor.execute("SELECT COUNT(*), SUM(total_amount) FROM order_transactions")
    txn_count, txn_total_val = cursor.fetchone()
    txn_count = txn_count or 0
    txn_total_val = txn_total_val or 0.0
except Exception:
    txn_count = 0
    txn_total_val = 0.0

try:
    cursor.execute("SELECT COUNT(*), SUM(total_amount) FROM order_transactions WHERE payment_status = 'Paid'")
    paid_count, paid_total_val = cursor.fetchone()
    paid_count = paid_count or 0
    paid_total_val = paid_total_val or 0.0
except Exception:
    paid_count = 0
    paid_total_val = 0.0

try:
    cursor.execute("SELECT COUNT(*), SUM(total_amount) FROM order_transactions WHERE payment_status = 'Pending Payment'")
    pending_pay_count, pending_pay_val = cursor.fetchone()
    pending_pay_count = pending_pay_count or 0
    pending_pay_val = pending_pay_val or 0.0
except Exception:
    pending_pay_count = 0
    pending_pay_val = 0.0

# Returns count and values
try:
    # Active returns: not Rejected, Refunded, Restocked, Closed
    cursor.execute("SELECT COUNT(*) FROM return_orders WHERE status NOT IN ('Rejected', 'Refunded', 'Restocked', 'Closed')")
    active_returns_count = cursor.fetchone()[0] or 0
except Exception:
    active_returns_count = 0

try:
    # Refunded amount: sum of refund_amount for returned orders in Refunded, Restocked, Closed status
    cursor.execute("SELECT SUM(refund_amount) FROM return_orders WHERE status IN ('Refunded', 'Restocked', 'Closed')")
    refund_amount_sum = cursor.fetchone()[0] or 0.0
except Exception:
    refund_amount_sum = 0.0

try:
    # Restocked count
    cursor.execute("SELECT COUNT(*) FROM return_orders WHERE status = 'Restocked'")
    restocked_returns_count = cursor.fetchone()[0] or 0
except Exception:
    restocked_returns_count = 0

try:
    # Returned Quantity (sum of quantities from all return orders)
    cursor.execute("SELECT SUM(quantity) FROM return_orders")
    returned_quantity_sum = cursor.fetchone()[0] or 0
except Exception:
    returned_quantity_sum = 0

try:
    # Restocked Quantity (sum of quantities from return orders that were restocked)
    cursor.execute("SELECT SUM(quantity) FROM return_orders WHERE status = 'Restocked'")
    restocked_quantity_sum = cursor.fetchone()[0] or 0
except Exception:
    restocked_quantity_sum = 0

# Stock In, Stock Out, Adjustments counts from inventory_transactions
try:
    cursor.execute("SELECT SUM(quantity) FROM inventory_transactions WHERE transaction_type = 'STOCK IN'")
    stock_in_qty = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(quantity) FROM inventory_transactions WHERE transaction_type = 'STOCK OUT'")
    stock_out_qty = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(quantity) FROM inventory_transactions WHERE transaction_type = 'ADJUSTMENT'")
    stock_adj_qty = cursor.fetchone()[0] or 0
except Exception:
    stock_in_qty = 0
    stock_out_qty = 0
    stock_adj_qty = 0

# Category return trends
category_return_trend_msg = ""
try:
    cursor.execute("""
        SELECT p.category, COUNT(r.id) 
        FROM return_orders r 
        JOIN products p ON r.product_code = p.product_code 
        GROUP BY p.category
    """)
    cat_returns = cursor.fetchall()
    if cat_returns:
        max_cat, max_count = max(cat_returns, key=lambda x: x[1])
        if max_count > 0:
            category_return_trend_msg = f"Return rate for {max_cat} is increasing ({max_count} returned items)."
except Exception:
    pass

# Check if returned products are available for restocking
avail_restock_count = 0
try:
    cursor.execute("SELECT COUNT(*) FROM return_orders WHERE status = 'Approved for Refund' AND inspection_condition = 'Good Condition'")
    avail_restock_count = cursor.fetchone()[0] or 0
except Exception:
    pass

# High-value refunds check
high_value_refunds_pending = []
try:
    cursor.execute("SELECT order_code, refund_amount FROM return_orders WHERE refund_amount >= 10000 AND status NOT IN ('Refunded', 'Closed')")
    high_value_refunds_pending = cursor.fetchall()
except Exception:
    pass

# Return rate
try:
    cursor.execute("SELECT COUNT(DISTINCT order_code) FROM return_orders")
    total_return_orders_count = cursor.fetchone()[0] or 0
except Exception:
    total_return_orders_count = 0

conn.close()

total_orders_for_rate = total_orders if total_orders > 0 else 1
return_rate = (total_return_orders_count / total_orders_for_rate) * 100

# Inventory Turnover calculation
cogs = 0.0
if not orders.empty:
    dispatched_orders = orders[orders["status"] == "Dispatched"]
    for _, row in dispatched_orders.iterrows():
        p_code = row["product_code"]
        qty = row["quantity"]
        if p_code in product_financials:
            cogs += qty * product_financials[p_code][0]
avg_inv_val = total_inventory_value if total_inventory_value > 0 else 1.0
inventory_turnover = cogs / avg_inv_val

# Warehouse Operational Risk
risk_score = 0
risk_score += out_of_stock_count * 20
risk_score += low_stock_count * 8
risk_score += critical_orders_count * 15
risk_score += pending_orders_count * 4
risk_score += open_exceptions_count * 12
risk_score += open_backorders_count * 10
risk_score = min(risk_score, 100)

if risk_score >= 70:
    risk_status = "HIGH"
    risk_reason = "Critical stockouts, backorders, and pending unresolved exceptions are placing operational strain on dispatch teams. Immediate stock replenishment and exception clearing recommended."
elif risk_score >= 35:
    risk_status = "MEDIUM"
    risk_reason = "Warehouse experiences moderate backlogs or low stock warnings. Check picking routes and prioritize high-urgency order processing."
else:
    risk_status = "LOW"
    risk_reason = "Warehouse is operating within healthy parameters. Inventory levels are stable, and the exception queue is clear."

# Bottleneck Detection
process_values = {
    "Order Processing": pending_orders_count,
    "Picking Queue": picking_orders_count,
    "Packing Station": packed_orders_count,
    "Quality Check": int((orders["status"] == "Packed").sum()) if not orders.empty else 0,
    "Dispatch Release": int((orders["status"] == "Ready for Dispatch").sum()) if not orders.empty else 0
}
bottleneck = max(process_values, key=process_values.get)
bottleneck_count = process_values[bottleneck]


# ============================================================
# PERSPECTIVE 1: 🏢 WAREHOUSE STAFF VIEW
# ============================================================
if perspective == "🏢 Warehouse Staff":
    st.sidebar.divider()
    st.sidebar.markdown("### 🏢 Operations Navigation")
    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📦 Smart Inventory",
            "🛒 Order Management",
            "💳 Order Transactions",
            "🔄 Return Management",
            "🧠 Smart Allocation",
            "👷 Picking Workflow",
            "📦 Packing Workflow",
            "🔍 Quality Check",
            "🚨 Exception Management",
            "📦 Backorder Management",
            "🚚 Dispatch & Timeline",
            "📊 Analytics & Insights",
            "🚀 Hackathon Demo Mode"
        ]
    )

    # 🏠 DASHBOARD VIEW
    if page == "🏠 Dashboard":
        st.header("🏠 Warehouse & Financial Dashboard")
        st.write("Real-time database-driven operations overview and financial intelligence statistics.")
        st.divider()

        # Metric Row 1: Operations Metrics
        st.subheader("📋 Operational Statistics")
        m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)
        m_col1.metric("Total Products", total_products)
        m_col2.metric("Available Stock Units", available_stock_sum)
        m_col3.metric("Low Stock Items", low_stock_count)
        m_col4.metric("Out of Stock Items", out_of_stock_count)
        m_col5.metric("Total Orders", total_orders)
        m_col6.metric("Pending Allocation", pending_orders_count)

        m_col7, m_col8, m_col9, m_col10, m_col11, m_col12 = st.columns(6)
        m_col7.metric("Critical Orders", critical_orders_count)
        m_col8.metric("Orders in Picking", picking_orders_count)
        m_col9.metric("Packed Orders", packed_orders_count)
        m_col10.metric("Dispatched Orders", dispatched_orders_count)
        m_col11.metric("Open Exceptions", open_exceptions_count)
        m_col12.metric("Open Backorders", open_backorders_count)

        st.divider()

        # Metric Row 2: Financial Intelligence Metrics
        st.subheader("💰 Financial Intelligence Overview")
        f_col1, f_col2, f_col3, f_col4, f_col5, f_col6 = st.columns(6)
        f_col1.metric("Total Inventory Value", format_inr(total_inventory_value))
        f_col2.metric("Potential Sales Value", format_inr(potential_sales_value))
        f_col3.metric("Potential Profit Margins", format_inr(potential_profit))
        f_col4.metric("Total Active Order Value", format_inr(total_order_value))
        f_col5.metric("Fulfillment Revenue at Risk", format_inr(revenue_at_risk), delta=f"-{format_inr(profit_at_risk)} profit at risk", delta_color="inverse")
        f_col6.metric("Projected Profit at Risk", format_inr(profit_at_risk), delta_color="inverse")

        # Metric Row 2b: Order Transactions & Returns Metrics
        st.subheader("💳 Order Transactions & Returns Dashboard")
        tr_col1, tr_col2, tr_col3, tr_col4, tr_col5, tr_col6 = st.columns(6)
        tr_col1.metric("Total Order Value", format_inr(txn_total_val))
        tr_col2.metric("Paid Transactions", format_inr(paid_total_val))
        tr_col3.metric("Active Returns", active_returns_count)
        tr_col4.metric("Refunds Processed", format_inr(refund_amount_sum))
        tr_col5.metric("Restocked Returns", restocked_returns_count)
        tr_col6.metric("Order Return Rate", f"{return_rate:.1f}%")

        st.divider()

        # Visual Charts & Gauges
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            st.subheader("📊 Orders by Status")
            if not orders.empty:
                status_df = orders["status"].value_counts().reset_index()
                status_df.columns = ["Status", "Order Count"]
                st.bar_chart(status_df.set_index("Status"), height=250)
            else:
                st.info("No orders in database to chart.")

        with c_col2:
            st.subheader("🚨 Orders by Priority")
            if not orders.empty:
                priority_df = orders["priority"].value_counts().reset_index()
                priority_df.columns = ["Priority", "Order Count"]
                st.bar_chart(priority_df.set_index("Priority"), height=250)
            else:
                st.info("No orders in database to chart.")

        c_col3, c_col4 = st.columns(2)
        with c_col3:
            st.subheader("📦 Inventory Financial Performance (Profit by Product)")
            if not products.empty:
                st.bar_chart(products.set_index("name")["potential_profit"], height=250)
            else:
                st.info("No products registered in database.")

        with c_col4:
            st.subheader("⚡ Operational Risk & Security")
            risk_color = "#10b981" if risk_status == "LOW" else "#f59e0b" if risk_status == "MEDIUM" else "#ef4444"
            st.markdown(f"""
            <div style="background-color: #f8fafc; padding: 1.5rem; border-radius: 0.5rem; border-left: 10px solid {risk_color}; height: 250px;">
                <h4 style="margin: 0; color: #64748b;">Risk Classification</h4>
                <h1 style="margin: 0.5rem 0; color: {risk_color}; font-weight: 800;">{risk_status} ({risk_score}/100)</h1>
                <p style="margin: 0; color: #334155; font-size: 0.95rem; line-height:1.5;">
                    {risk_reason}
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Active System Alerts
        st.subheader("🚨 Real-time Warehouse Alerts")
        alert_found = False
        for _, product in products.iterrows():
            avail = product["available_stock"]
            if avail <= 0:
                st.error(f"🔴 **OUT OF STOCK** — **{product['name']}** (Code: `{product['product_code']}`) | Potential Revenue Blocked: **{format_inr(product['selling_price'] * product['reorder_quantity'])}** | Location: `{product['location']}`")
                alert_found = True
            elif avail <= product["reorder_level"]:
                st.warning(f"🟡 **LOW STOCK ALERT** — **{product['name']}** (Code: `{product['product_code']}`) | Available: **{avail}** (Reorder Threshold: **{product['reorder_level']}**) | Location: `{product['location']}`")
                alert_found = True

        if open_exceptions_count > 0:
            st.error(f"🚨 **UNRESOLVED EXCEPTIONS** — There are **{open_exceptions_count}** unresolved exceptions that block order releases. Please check the Exception Center.")
            alert_found = True

        if not alert_found:
            st.success("✅ No critical alerts. Warehouse inventory levels are healthy.")

    # 📦 SMART INVENTORY VIEW
    elif page == "📦 Smart Inventory":
        st.header("📦 Smart Inventory Management")
        st.write("Browse warehouse layout locations, monitor stock buffers, and manage replenishment limits.")
        st.divider()

        # Tabs for Catalog, Operations, and History
        tab_catalog, tab_ops, tab_history = st.tabs([
            "📋 Warehouse Inventory Catalog",
            "⚙️ Inventory Operations",
            "📋 Transaction History"
        ])

        with tab_catalog:
            # Inventory Metrics
            i_col1, i_col2, i_col3 = st.columns(3)
            i_col1.metric("Available Stock Units", available_stock_sum)
            i_col2.metric("Low Stock Alert Items", low_stock_count)
            i_col3.metric("Out of Stock Outages", out_of_stock_count)

            st.divider()

            # Advanced Filters
            st.subheader("🔍 Advanced Inventory Filtering")
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            with f_col1:
                search_query = st.text_input("Search Product Name / Code / Location / Category", "")
            with f_col2:
                categories = ["All", "Electronics", "Accessories", "Audio", "Wearables", "Gaming", "Clothing", "Bags", "Footwear", "Home & Lifestyle", "Home & Electrical", "Stationery", "Computer Hardware", "Office Equipment"]
                selected_cat = st.selectbox("Category Filter", categories)
            with f_col3:
                locations_list = ["All"] + sorted(list(products["location"].unique())) if not products.empty else ["All"]
                selected_loc = st.selectbox("Warehouse Location Filter", locations_list)
            with f_col4:
                status_options = ["All", "Healthy", "Low Stock", "Out of Stock"]
                selected_status = st.selectbox("Stock Status Filter", status_options)

            # Filter Dataframe
            filtered_products = products.copy()
            if search_query:
                filtered_products = filtered_products[
                    filtered_products["name"].str.contains(search_query, case=False) |
                    filtered_products["product_code"].str.contains(search_query, case=False) |
                    filtered_products["location"].str.contains(search_query, case=False) |
                    filtered_products["category"].str.contains(search_query, case=False)
                ]
            if selected_cat != "All":
                filtered_products = filtered_products[filtered_products["category"] == selected_cat]
            if selected_loc != "All":
                filtered_products = filtered_products[filtered_products["location"] == selected_loc]
            
            if selected_status == "Healthy":
                filtered_products = filtered_products[filtered_products["available_stock"] > filtered_products["reorder_level"]]
            elif selected_status == "Low Stock":
                filtered_products = filtered_products[
                    (filtered_products["available_stock"] > 0) & 
                    (filtered_products["available_stock"] <= filtered_products["reorder_level"])
                ]
            elif selected_status == "Out of Stock":
                filtered_products = filtered_products[filtered_products["available_stock"] <= 0]

            # Display Product Table
            if not filtered_products.empty:
                disp_df = filtered_products.copy()
                disp_df["Unit Cost"] = disp_df["unit_cost"].apply(format_inr)
                disp_df["Selling Price"] = disp_df["selling_price"].apply(format_inr)
                disp_df["Inventory Value"] = disp_df["inventory_value"].apply(format_inr)
                disp_df["Sales Value"] = disp_df["potential_sales_value"].apply(format_inr)
                disp_df["Potential Profit"] = disp_df["potential_profit"].apply(format_inr)
                
                st.dataframe(
                    disp_df[[
                        "product_code", "name", "category", "location", 
                        "total_stock", "reserved_stock", "damaged_stock", 
                        "available_stock", "reorder_level", "reorder_quantity",
                        "Unit Cost", "Selling Price", "Inventory Value", "Sales Value", "Potential Profit"
                    ]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No products match the selected filters.")

            st.divider()

            # Smart Reorder Section
            st.subheader("🤖 Rule-based Smart Reorder Recommendations")
            reorder_list = []
            for _, product in products.iterrows():
                avail = product["available_stock"]
                if avail <= product["reorder_level"]:
                    rec = get_reorder_recommendation(avail, product["reorder_level"], product["reorder_quantity"])
                    if rec["reorder"]:
                        risk_lbl = "🔴 URGENT OUTAGE" if avail <= 0 else "🟡 WARNING LOW"
                        est_cost = product["reorder_quantity"] * product["unit_cost"]
                        reorder_list.append({
                            "Product Code": product["product_code"],
                            "Product Name": product["name"],
                            "Available Stock": avail,
                            "Reorder Level": product["reorder_level"],
                            "Recommended Order Qty": product["reorder_quantity"],
                            "Unit Cost": format_inr(product["unit_cost"]),
                            "Estimated Reorder Cost": format_inr(est_cost),
                            "Warehouse Location": product["location"],
                            "Stock Risk Level": risk_lbl,
                            "Fulfillment Warning": rec["message"]
                        })
                        
            if reorder_list:
                reorder_df = pd.DataFrame(reorder_list)
                st.dataframe(reorder_df, use_container_width=True, hide_index=True)
            else:
                st.success("✅ All product warehouse volumes are within healthy thresholds.")

        with tab_ops:
            st.subheader("⚙️ Record Inventory Movements")
            
            # Select Operation
            op_type = st.selectbox("Select Operation Type", [
                "Stock In",
                "Stock Out",
                "Stock Adjustment",
                "Mark Damaged"
            ])
            
            if products.empty:
                st.error("No products registered in the database.")
            else:
                product_list = [f"{row['product_code']} - {row['name']}" for _, row in products.iterrows()]
                selected_prod_str = st.selectbox("Select Product", product_list, key="inv_op_prod")
                p_code = selected_prod_str.split(" - ")[0]
                
                with st.form("inventory_ops_form"):
                    if op_type == "Stock In":
                        st.markdown("### 📥 Stock In (Receive Incoming Cargo)")
                        qty = st.number_input("Quantity", min_value=1, value=10, step=1)
                        supplier = st.text_input("Supplier", placeholder="e.g. Acme Corp")
                        ref_num = st.text_input("Reference Number", placeholder="e.g. PO-12345")
                        date_str = st.date_input("Date").strftime("%Y-%m-%d")
                        
                        submitted = st.form_submit_button("Confirm Stock In")
                        if submitted:
                            if not supplier.strip() or not ref_num.strip():
                                st.error("Supplier and Reference Number are required.")
                            else:
                                try:
                                    record_stock_in(p_code, int(qty), supplier.strip(), ref_num.strip(), date_str, "Warehouse Staff")
                                    st.success(f"Successfully stocked in {qty} units of {p_code}!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                                    
                    elif op_type == "Stock Out":
                        st.markdown("### 📤 Stock Out (Remove Outbound Stock)")
                        qty = st.number_input("Quantity", min_value=1, value=5, step=1)
                        reason = st.text_input("Reason", placeholder="e.g. Internal Transfer")
                        ref_num = st.text_input("Reference / Order ID", placeholder="e.g. ORD-987")
                        
                        submitted = st.form_submit_button("Confirm Stock Out")
                        if submitted:
                            if not reason.strip() or not ref_num.strip():
                                st.error("Reason and Reference/Order ID are required.")
                            else:
                                try:
                                    record_stock_out(p_code, int(qty), reason.strip(), ref_num.strip(), "Warehouse Staff")
                                    st.success(f"Successfully stocked out {qty} units of {p_code}!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                                    
                    elif op_type == "Stock Adjustment":
                        st.markdown("### 🔧 Stock Adjustment (Inventory Count Correction)")
                        adj_qty = st.number_input("Adjustment Quantity (use negative for deduction)", value=0, step=1)
                        reason = st.selectbox("Reason", [
                            "Inventory Count Correction",
                            "System Error",
                            "Lost Item",
                            "Found Item",
                            "Other"
                        ])
                        custom_reason = st.text_input("Custom Reason / Notes (Optional)")
                        final_reason = f"{reason} - {custom_reason}" if custom_reason else reason
                        
                        submitted = st.form_submit_button("Confirm Adjustment")
                        if submitted:
                            if adj_qty == 0:
                                st.error("Adjustment quantity cannot be 0.")
                            else:
                                try:
                                    record_stock_adjustment(p_code, int(adj_qty), final_reason, "Warehouse Staff")
                                    st.success(f"Successfully adjusted stock of {p_code} by {adj_qty} units!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                                    
                    elif op_type == "Mark Damaged":
                        st.markdown("### ⚠️ Mark Stock as Damaged")
                        qty = st.number_input("Quantity", min_value=1, value=1, step=1)
                        reason = st.text_input("Damage Description", placeholder="e.g. Broken packaging, Water damage")
                        
                        submitted = st.form_submit_button("Mark as Damaged")
                        if submitted:
                            if not reason.strip():
                                st.error("Damage description is required.")
                            else:
                                try:
                                    record_damaged_stock(p_code, int(qty), reason.strip(), "Warehouse Staff")
                                    st.success(f"Successfully marked {qty} units of {p_code} as damaged!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

        with tab_history:
            st.subheader("📋 Inventory Transaction History")
            txns = get_inventory_transactions()
            if txns:
                txn_df = pd.DataFrame(txns, columns=[
                    "Transaction ID",
                    "Product Code",
                    "Transaction Type",
                    "Quantity",
                    "Previous Stock",
                    "New Stock",
                    "Reference",
                    "Reason",
                    "Performed By",
                    "Created At"
                ])
                txn_df = add_product_names(txn_df, products)
                st.dataframe(txn_df, use_container_width=True, hide_index=True)
            else:
                st.info("No stock transactions logged yet.")

    # 🛒 ORDER MANAGEMENT VIEW
    elif page == "🛒 Order Management":
        st.header("🛒 Order Management")
        st.write("Register new customer demand, inspect catalog details, and check priority scores.")
        st.divider()

        if products.empty:
            st.error("No products registered in the system. Add products first.")
        else:
            st.subheader("➕ Create New Customer Order")
            selected_prod_name = st.selectbox("Select Product", products["name"].tolist())
            selected_prod = products[products["name"] == selected_prod_name].iloc[0]
            
            # Product Details Lookup panel on selection (16 fields)
            st.markdown("### 🔍 Selected Product Catalog Information")
            det_col1, det_col2, det_col3, det_col4 = st.columns(4)
            det_col1.markdown(f"**Product Name**: `{selected_prod['name']}`")
            det_col2.markdown(f"**Product Code**: `{selected_prod['product_code']}`")
            det_col3.markdown(f"**Category**: `{selected_prod['category']}`")
            det_col4.markdown(f"**Warehouse Location**: `{selected_prod['location']}`")
            
            det_col5, det_col6, det_col7, det_col8 = st.columns(4)
            det_col5.markdown(f"**Total Stock**: `{selected_prod['total_stock']} units`")
            det_col6.markdown(f"**Reserved Stock**: `{selected_prod['reserved_stock']} units`")
            det_col7.markdown(f"**Damaged Stock**: `{selected_prod['damaged_stock']} units`")
            det_col8.markdown(f"**Available Stock**: `{selected_prod['available_stock']} units`")
            
            det_col9, det_col10, det_col11, det_col12 = st.columns(4)
            det_col9.markdown(f"**Reorder Threshold**: `{selected_prod['reorder_level']} units`")
            det_col10.markdown(f"**Reorder Qty**: `{selected_prod['reorder_quantity']} units`")
            det_col11.markdown(f"**Unit Cost Price**: `{format_inr(selected_prod['unit_cost'])}`")
            det_col12.markdown(f"**Unit Selling Price**: `{format_inr(selected_prod['selling_price'])}`")
            
            det_col13, det_col14, det_col15, det_col16 = st.columns(4)
            det_col13.markdown(f"**Inventory Asset Value**: `{format_inr(selected_prod['inventory_value'])}`")
            det_col14.markdown(f"**Potential Sales Value**: `{format_inr(selected_prod['potential_sales_value'])}`")
            det_col15.markdown(f"**Potential Profit Margin**: `{format_inr(selected_prod['potential_profit'])}`")
            stock_risk_class = get_stock_status(selected_prod['total_stock'], selected_prod['reserved_stock'], selected_prod['damaged_stock'], selected_prod['reorder_level'])
            det_col16.markdown(f"**Stock Risk Classification**: `{stock_risk_class}`")
            
            st.divider()
            
            with st.form("new_order_form"):
                col1, col2 = st.columns(2)
                with col1:
                    customer_name = st.text_input("Customer Name", "")
                with col2:
                    order_qty = st.number_input("Order Quantity Required", min_value=1, value=1, step=1)
                    cust_urgency = st.slider("Order Urgency Rating (1-10)", min_value=1, max_value=10, value=5)
                    
                submitted = st.form_submit_button("🚀 Evaluate & Register Order")
                
                if submitted:
                    if not customer_name.strip():
                        st.error("Invalid Input: Customer name cannot be empty.")
                    elif order_qty <= 0:
                        st.error("Invalid Input: Quantity must be greater than zero.")
                    else:
                        avail_stock = selected_prod["available_stock"]
                        cost = selected_prod["unit_cost"]
                        price = selected_prod["selling_price"]
                        
                        priority_class, score, reason, action = calculate_priority_score(
                            urgency=cust_urgency,
                            quantity=order_qty,
                            available_stock=avail_stock,
                            existing_priority="Medium",
                            order_status="Pending",
                            selling_price=price,
                            unit_cost=cost
                        )
                        
                        try:
                            new_code = create_order(
                                customer=customer_name.strip(),
                                product_code=selected_prod["product_code"],
                                quantity=int(order_qty),
                                priority=priority_class,
                                priority_score=score
                            )
                            st.success(f"✅ Order Registered! Code: **{new_code}** | Priority Score: **{score}/100** ({priority_class})")
                            st.info(f"🤖 **Decision Score Breakdown**: {reason}\n\n**Recommended Action**: {action}")
                            
                            o_val = order_qty * price
                            o_cost = order_qty * cost
                            o_profit = o_val - o_cost
                            shortage = max(0, int(order_qty) - avail_stock)
                            
                            st.markdown("### 📊 Order Financial Projections")
                            f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
                            f_col1.metric("Required Qty", f"{order_qty} units")
                            f_col2.metric("Available Stock", f"{avail_stock} units")
                            f_col3.metric("Stock Shortage", f"{shortage} units")
                            f_col4.metric("Unit Cost", format_inr(cost))
                            f_col5.metric("Selling Price", format_inr(price))
                            
                            f_col6, f_col7, f_col8 = st.columns(3)
                            f_col6.metric("Gross Order Value", format_inr(o_val))
                            f_col7.metric("Estimated Cost Basis", format_inr(o_cost))
                            f_col8.metric("Estimated Profit Margin", format_inr(o_profit))
                            
                            if shortage > 0:
                                st.warning(f"⚠️ Stock Shortage detected: {shortage} units will be backordered (Revenue at risk: {format_inr(shortage * price)}).")
                            else:
                                st.success("✅ Full quantity is available in stock for this order.")
                                
                            st.balloons()
                            orders = get_orders()
                        except Exception as e:
                            st.error(f"Database write failure: {e}")

            st.divider()

            # Existing Orders Table
            st.subheader("📋 Order Tracking Board")
            fo1, fo2, fo3 = st.columns(3)
            with fo1:
                search_ord = st.text_input("Search Order ID / Customer", "")
            with fo2:
                status_filter = st.selectbox("Filter Status", ["All", "Pending", "Allocated", "Picking", "Picked", "Packed", "Ready for Dispatch", "Dispatched"])
            with fo3:
                priority_filter = st.selectbox("Filter Priority", ["All", "Critical", "High", "Medium", "Low"])
                
            filtered_orders = orders.copy()
            if search_ord:
                filtered_orders = filtered_orders[
                    filtered_orders["order_code"].str.contains(search_ord, case=False) |
                    filtered_orders["customer"].str.contains(search_ord, case=False)
                ]
            if status_filter != "All":
                filtered_orders = filtered_orders[filtered_orders["status"] == status_filter]
            if priority_filter != "All":
                filtered_orders = filtered_orders[filtered_orders["priority"] == priority_filter]
                
            if not filtered_orders.empty:
                disp_orders = add_product_names(filtered_orders, products)
                
                def get_order_financials(row):
                    p_code = row["product_code"]
                    qty = row["quantity"]
                    if p_code in product_financials:
                        c, p = product_financials[p_code]
                        return format_inr(p), format_inr(qty * p), format_inr(qty * c), format_inr(qty * (p - c))
                    return "₹0", "₹0", "₹0", "₹0"
                
                financials_mapped = disp_orders.apply(get_order_financials, axis=1)
                disp_orders["Selling Price"] = [f[0] for f in financials_mapped]
                disp_orders["Order Value"] = [f[1] for f in financials_mapped]
                disp_orders["Order Cost"] = [f[2] for f in financials_mapped]
                disp_orders["Estimated Profit"] = [f[3] for f in financials_mapped]
                
                st.dataframe(
                    disp_orders[[
                        "order_code", "customer", "product_code", "product_name", "quantity", 
                        "priority", "priority_score", "status", "Selling Price", "Order Value", "Order Cost", "Estimated Profit"
                    ]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No orders found matching filters.")

    # 💳 ORDER TRANSACTIONS VIEW
    elif page == "💳 Order Transactions":
        st.header("💳 Order Transactions & Financial Lifecycle")
        st.write("Track the payment states, payment methods, cancel transactions, and reconcile financial parameters.")
        st.divider()
        
        # Calculations / metrics for transactions page
        t_col1, t_col2, t_col3 = st.columns(3)
        t_col1.metric("Total Order Value", format_inr(txn_total_val))
        t_col2.metric("Paid Transactions Value", format_inr(paid_total_val))
        t_col3.metric("Pending Payments Value", format_inr(pending_pay_val))
        st.divider()
        
        # Display transactions table
        st.subheader("📋 Order Transactions Ledger")
        txns_list = get_order_transactions()
        if txns_list:
            txn_df = pd.DataFrame(txns_list, columns=[
                "Transaction ID", "Order Code", "Customer", "Product Code", "Quantity", 
                "Unit Selling Price", "Subtotal", "Discount", "Tax", "Shipping Fee", 
                "Total Amount", "Payment Method", "Payment Status", "Transaction Type", 
                "Transaction Reference", "Created At", "Updated At"
            ])
            txn_df = add_product_names(txn_df, products)
            
            disp_txn_df = txn_df.copy()
            disp_txn_df["Unit Selling Price"] = disp_txn_df["Unit Selling Price"].apply(format_inr)
            disp_txn_df["Subtotal"] = disp_txn_df["Subtotal"].apply(format_inr)
            disp_txn_df["Total Amount"] = disp_txn_df["Total Amount"].apply(format_inr)
            
            st.dataframe(
                disp_txn_df[[
                    "Transaction ID", "Order Code", "Customer", "product_name", "Quantity",
                    "Unit Selling Price", "Total Amount", "Payment Method", "Payment Status", "Created At"
                ]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No order transactions in the ledger.")
            
        st.divider()
        
        # Transactions Actions
        st.subheader("⚙️ Transaction Operations")
        act_col1, act_col2 = st.columns(2)
        
        with act_col1:
            st.markdown("### 💳 Confirm Demo Payment")
            pending_txns = [t for t in txns_list if t[12] == "Pending Payment"] if txns_list else []
            if not pending_txns:
                st.success("✅ No pending payments to confirm!")
            else:
                pending_options = {f"Order {t[1]} - Cust: {t[2]} ({format_inr(t[10])})": t[1] for t in pending_txns}
                selected_pay_order = st.selectbox("Select Pending Order to Pay", list(pending_options.keys()))
                order_code_to_pay = pending_options[selected_pay_order]
                
                pay_method = st.selectbox("Select Payment Method", [
                    "UPI",
                    "Credit Card",
                    "Debit Card",
                    "Net Banking",
                    "Cash on Delivery"
                ])
                
                if st.button("Confirm Demo Payment", use_container_width=True):
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        
                        # Check duplicate
                        cursor.execute("SELECT total_amount, payment_status FROM order_transactions WHERE order_code = ?", (order_code_to_pay,))
                        txn_row = cursor.fetchone()
                        
                        if txn_row:
                            amount, payment_status = txn_row
                            if payment_status == "Paid":
                                st.info("ℹ️ This order is already paid.")
                                cursor.close()
                                conn.close()
                                st.stop()
                                
                            cursor.execute("""
                                UPDATE order_transactions
                                SET payment_status = 'Paid',
                                    payment_method = ?,
                                    transaction_type = 'Payment',
                                    transaction_reference = ?,
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE order_code = ?
                            """, (pay_method, f"TXN-{order_code_to_pay}", order_code_to_pay))
                        else:
                            cursor.execute("SELECT customer, product_code, quantity FROM orders WHERE order_code = ?", (order_code_to_pay,))
                            ord_row = cursor.fetchone()
                            if not ord_row:
                                raise ValueError("Order not found.")
                            customer, product_code, quantity = ord_row
                            
                            cursor.execute("SELECT selling_price FROM products WHERE product_code = ?", (product_code,))
                            p_row = cursor.fetchone()
                            price = p_row[0] if p_row else 0.0
                            
                            subtotal = quantity * price
                            discount = 0.0
                            tax = round(subtotal * 0.18, 2)
                            shipping_fee = 100.0 if subtotal < 1000.0 else 0.0
                            amount = subtotal - discount + tax + shipping_fee
                            
                            cursor.execute("""
                                INSERT INTO order_transactions
                                (order_code, customer, product_code, quantity, unit_selling_price, subtotal, discount, tax, shipping_fee, total_amount, payment_method, payment_status, transaction_type, transaction_reference, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Paid', 'Payment', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            """, (order_code_to_pay, customer, product_code, quantity, price, subtotal, discount, tax, shipping_fee, amount, pay_method, f"TXN-{order_code_to_pay}"))
                            
                        conn.commit()
                        cursor.close()
                        conn.close()
                        
                        st.success(f"✅ Payment Successful\n\nOrder: {order_code_to_pay}\nAmount: {format_inr(amount)}\nPayment Method: {pay_method}\nPayment Status: Paid")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
        with act_col2:
            st.markdown("### 🚫 Cancel Order & Transaction")
            active_orders_to_cancel = []
            if txns_list:
                for t in txns_list:
                    o_code = t[1]
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT status FROM orders WHERE order_code = ?", (o_code,))
                    status_row = cursor.fetchone()
                    conn.close()
                    if status_row and status_row[0] not in ["Cancelled", "Dispatched"]:
                        active_orders_to_cancel.append(t)
            
            if not active_orders_to_cancel:
                st.info("No active orders available for cancellation.")
            else:
                cancel_options = {f"Order {t[1]} - Cust: {t[2]} ({format_inr(t[10])})": t[1] for t in active_orders_to_cancel}
                selected_cancel_order = st.selectbox("Select Order to Cancel", list(cancel_options.keys()))
                order_code_to_cancel = cancel_options[selected_cancel_order]
                
                cancel_reason = st.text_input("Reason for Cancellation", placeholder="e.g. Customer requested, Stockout")
                
                if st.button("Cancel Order & Transaction", use_container_width=True):
                    if not cancel_reason.strip():
                        st.error("Please enter a reason for cancellation.")
                    else:
                        try:
                            cancel_order_db(order_code_to_cancel, "Warehouse Staff")
                            st.success(f"Successfully cancelled Order {order_code_to_cancel}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    # 🔄 RETURN MANAGEMENT VIEW
    elif page == "🔄 Return Management":
        st.header("🔄 Customer Returns Management")
        st.write("Process returns, inspect returned items, execute restocks, and authorize customer refunds.")
        st.divider()
        
        # Display return orders list
        st.subheader("📋 Active Returns Registry")
        returns_list = get_return_orders()
        
        if returns_list:
            ret_df = pd.DataFrame(returns_list, columns=[
                "Return ID", "Order Code", "Customer", "Product Code", "Quantity", 
                "Reason", "Description", "Status", "Rejection Reason", 
                "Inspection Condition", "Refund Amount", "Requested At", "Updated At"
            ])
            ret_df = add_product_names(ret_df, products)
            
            disp_ret_df = ret_df.copy()
            disp_ret_df["Refund Amount"] = disp_ret_df["Refund Amount"].apply(format_inr)
            
            st.dataframe(
                disp_ret_df[[
                    "Return ID", "Order Code", "Customer", "product_name", "Quantity", 
                    "Reason", "Status", "Inspection Condition", "Refund Amount", "Requested At"
                ]],
                use_container_width=True,
                hide_index=True
            )
            
            st.divider()
            
            # Select return to inspect/process
            st.subheader("⚙️ Process Return Request")
            ret_options = {f"Return #{r[0]} - Order {r[1]} ({r[2]})": r[0] for r in returns_list}
            selected_ret_str = st.selectbox("Select Return Case to Manage", list(ret_options.keys()))
            selected_ret_id = ret_options[selected_ret_str]
            
            # Find selected return item details
            ret_details = [r for r in returns_list if r[0] == selected_ret_id][0]
            ret_id, order_code, customer, product_code, quantity, reason, description, status, rej_reason, inspect_cond, refund_amt, req_at, upd_at = ret_details
            
            st.markdown(f"### Return #{ret_id} Details (Status: `{status}`)")
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                st.write(f"• **Order Code**: `{order_code}`")
                st.write(f"• **Customer**: `{customer}`")
                st.write(f"• **Product**: `{product_code}`")
                st.write(f"• **Quantity**: `{quantity}`")
            with r_col2:
                st.write(f"• **Return Reason**: `{reason}`")
                st.write(f"• **Description**: `{description}`")
                st.write(f"• **Estimated Refund Amount**: `{format_inr(refund_amt)}`")
                if rej_reason:
                    st.error(f"• **Rejection Reason**: {rej_reason}")
                if inspect_cond:
                    st.info(f"• **Inspection Condition**: {inspect_cond}")
                    
            st.markdown("#### Progress Actions:")
            
            if status == "Requested":
                rej_text = st.text_input("Rejection Reason (Required if Rejecting)")
                btn_app, btn_rej = st.columns(2)
                with btn_app:
                    if st.button("Approve Return Request", use_container_width=True):
                        try:
                            update_return_order_status(ret_id, "Pickup Scheduled")
                            st.success("Return approved! Scheduled for pickup.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                with btn_rej:
                    if st.button("Reject Return Request", use_container_width=True):
                        if not rej_text.strip():
                            st.error("Please enter a rejection reason.")
                        else:
                            try:
                                update_return_order_status(ret_id, "Rejected", rejection_reason=rej_text.strip())
                                st.success("Return request rejected.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                                
            elif status == "Pickup Scheduled":
                if st.button("🚚 Mark Product Received", use_container_width=True):
                    try:
                        update_return_order_status(ret_id, "Received")
                        update_return_order_status(ret_id, "Under Inspection")
                        st.success("Product marked as Received. Placed under inspection.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
            elif status == "Under Inspection":
                cond = st.radio("Select Inspected Product Condition", [
                    "Good Condition (Eligible for Restock)",
                    "Damaged (Not restocked - added to damaged inventory)",
                    "Partial Damage (Not restocked - added to damaged inventory)"
                ])
                cond_val = "Good Condition" if "Good Condition" in cond else "Damaged" if "Damaged" in cond else "Partial Damage"
                
                if st.button("Complete Inspection Check", use_container_width=True):
                    try:
                        update_return_order_status(ret_id, "Approved for Refund", inspection_condition=cond_val)
                        st.success(f"Inspection complete. Condition recorded as {cond_val}. Refund Approved.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
            elif status == "Approved for Refund":
                if inspect_cond == "Good Condition":
                    btn_restock, btn_ref = st.columns(2)
                    with btn_restock:
                        if st.button("📦 Restock Good Product to Catalog", use_container_width=True):
                            try:
                                update_return_order_status(ret_id, "Restocked")
                                st.success("Good product restocked successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    with btn_ref:
                        if st.button("💰 Complete Cash Refund Process", use_container_width=True):
                            try:
                                update_return_order_status(ret_id, "Refunded")
                                st.success("Refund processed successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                else:
                    st.warning("Product condition is Damaged/Partial Damage. Restocking is bypassed. Proceed straight to refund.")
                    if st.button("💰 Complete Cash Refund Process", use_container_width=True):
                        try:
                            update_return_order_status(ret_id, "Refunded")
                            st.success("Refund processed successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                            
            elif status == "Restocked":
                st.success("Inventory restock completed. Now authorize customer refund.")
                if st.button("💰 Complete Cash Refund Process", use_container_width=True):
                    try:
                        update_return_order_status(ret_id, "Refunded")
                        st.success("Refund processed successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
            elif status == "Refunded":
                st.success("🎉 This return case is fully resolved, and refund has been disbursed.")
                
            elif status == "Rejected":
                st.error("❌ This return request was rejected.")
        else:
            st.info("No returns logged in the database yet.")

    # 🧠 SMART ALLOCATION VIEW
    elif page == "🧠 Smart Allocation":
        st.header("🧠 Smart Allocation Decision Engine")
        st.write("Run inventory reservation checks, resolve stock assignments, and evaluate financial revenue splits.")
        st.divider()

        pending_allocations = orders[orders["status"] == "Pending"]
        
        if pending_allocations.empty:
            st.success("✅ No pending orders requiring allocation. All orders have been assigned or completed.")
        else:
            st.subheader("Pending Allocation List")
            selected_code = st.selectbox("Select Order to Allocate", pending_allocations["order_code"].tolist())
            
            selected_ord = pending_allocations[pending_allocations["order_code"] == selected_code].iloc[0]
            prod_code = selected_ord["product_code"]
            matching_prod = products[products["product_code"] == prod_code].iloc[0]
            
            req_qty = int(selected_ord["quantity"])
            avail_qty = int(matching_prod["available_stock"])
            priority = selected_ord["priority"]
            cost = matching_prod["unit_cost"]
            price = matching_prod["selling_price"]
            
            st.markdown("### Order Details Evaluation")
            ao1, ao2, ao3, ao4 = st.columns(4)
            ao1.metric("Selected Order", selected_code)
            ao2.metric("Product Requested", f"{matching_prod['name']} ({prod_code})")
            ao3.metric("Quantity Requested", req_qty)
            ao4.metric("Inventory Available", avail_qty)
            
            st.info(f"Priority Level: **{priority}** (Decision Score: **{selected_ord['priority_score']}/100**)")
            
            decision_details = allocate_inventory(req_qty, avail_qty, priority)
            
            st.subheader("🤖 Rule-based Intelligent Allocation Plan")
            st.markdown(f"**Allocation Decision**: `{decision_details['decision']}`")
            st.markdown(f"**Allocated Quantity**: `{decision_details['allocated']} units`")
            st.markdown(f"**Shortage/Backorder Quantity**: `{decision_details['shortage']} units`")
            st.markdown(f"**Recommended Fulfillment Steps**: {decision_details['action']}")
            st.info(f"**Decision Logic Explanation**: {decision_details['reason']}")
            
            alloc_qty = decision_details["allocated"]
            short_qty = decision_details["shortage"]
            
            alloc_val = alloc_qty * price
            alloc_cost = alloc_qty * cost
            alloc_profit = alloc_val - alloc_cost
            
            rev_at_risk = short_qty * price
            prof_at_risk = short_qty * (price - cost)
            
            st.markdown("### 💰 Allocation Financial Impact Analysis")
            ia1, ia2, ia3, ia4, ia5 = st.columns(5)
            ia1.metric("Required Quantity", f"{req_qty} units")
            ia2.metric("Available Stock", f"{avail_qty} units")
            ia3.metric("Allocated Quantity", f"{alloc_qty} units")
            ia4.metric("Shortage Quantity", f"{short_qty} units")
            ia5.metric("Product Unit Cost", format_inr(cost))
            
            fia1, fia2, fia3 = st.columns(3)
            fia1.metric("Allocated Revenue Value", format_inr(alloc_val))
            fia2.metric("Allocated Stock Cost", format_inr(alloc_cost))
            fia3.metric("Allocated Profit Margin", format_inr(alloc_profit))
            
            fib1, fib2 = st.columns(2)
            fib1.metric("Shortage Revenue at Risk", format_inr(rev_at_risk), delta_color="inverse")
            fib2.metric("Shortage Potential Profit at Risk", format_inr(prof_at_risk), delta_color="inverse")
            
            allocations_log = get_allocations()
            has_allocation = not allocations_log.empty and (allocations_log["order_code"] == selected_code).any()
            
            if has_allocation:
                st.warning(f"⚠️ Order {selected_code} has already had an allocation record processed in the system. Duplicate allocation prevented.")
            else:
                if st.button("⚡ EXECUTE ALLOCATION", use_container_width=True):
                    try:
                        result = execute_allocation(
                            order_code=selected_code,
                            product_code=prod_code,
                            requested_quantity=req_qty,
                            allocated_quantity=alloc_qty,
                            shortage_quantity=short_qty,
                            decision=decision_details["decision"]
                        )
                        st.success(f"Allocation executed successfully! Order updated to status: **{result['status']}**")
                        if alloc_qty > 0:
                            st.info("Fulfillment Release: Picking task has been generated in SQLite database.")
                        if short_qty > 0:
                            st.warning(f"Fulfillment Warning: Backorder logged for {short_qty} shortage units.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Execution Error: {e}")

        # Allocation History Log
        st.divider()
        st.subheader("📋 Allocation Decision History Log")
        hist = get_allocations()
        if not hist.empty:
            hist_df = hist.copy()
            hist_df["Unit Cost"] = hist_df["product_code"].apply(lambda p: format_inr(product_financials[p][0]) if p in product_financials else "₹0")
            hist_df["Order Value"] = hist_df.apply(lambda r: format_inr(r["requested_quantity"] * product_financials[r["product_code"]][1]) if r["product_code"] in product_financials else "₹0", axis=1)
            hist_df["Allocated Profit"] = hist_df.apply(lambda r: format_inr(r["allocated_quantity"] * (product_financials[r["product_code"]][1] - product_financials[r["product_code"]][0])) if r["product_code"] in product_financials else "₹0", axis=1)
            st.dataframe(add_product_names(hist_df, products), use_container_width=True, hide_index=True)
        else:
            st.info("No prior allocations executed.")

    # 👷 PICKING WORKFLOW VIEW
    elif page == "👷 Picking Workflow":
        st.header("👷 Picking Routing & Operations")
        st.write("Review active warehouse picking tasks, optimize collection routes, and confirm item pickups.")
        st.divider()

        tasks = get_picking_tasks()
        if not tasks:
            st.success("✅ No active picking tasks. All picking is completed or pending allocations.")
        else:
            tasks_df = pd.DataFrame(tasks, columns=["ID", "Order Code", "Product Code", "Quantity", "Location", "Status", "Created At"])
            tasks_df = add_product_names(tasks_df, products)
            
            # Ensure product_name exists safely
            if "product_name" not in tasks_df.columns:
                if "name" in tasks_df.columns:
                    tasks_df["product_name"] = tasks_df["name"]
                elif "Name" in tasks_df.columns:
                    tasks_df["product_name"] = tasks_df["Name"]
                elif "product_code" in tasks_df.columns:
                    product_names = products.set_index("product_code")["name"].to_dict()
                    tasks_df["product_name"] = tasks_df["product_code"].map(product_names)
                elif "Product Code" in tasks_df.columns:
                    product_names = products.set_index("product_code")["name"].to_dict()
                    tasks_df["product_name"] = tasks_df["Product Code"].map(product_names)
                else:
                    tasks_df["product_name"] = "Unknown Product"

            st.subheader("🧠 Location-Grouped Route Optimization")
            active_locations = tasks_df[tasks_df["Status"].isin(["Pending", "Picking"])]["Location"].tolist()
            
            if active_locations:
                unsorted_dist, sorted_dist, savings_pct = calculate_picking_route_savings(active_locations)
                
                p_opt1, p_opt2, p_opt3 = st.columns(3)
                p_opt1.metric("Standard Path Distance", f"{int(unsorted_dist)} units")
                p_opt2.metric("Optimized Path Distance", f"{int(sorted_dist)} units")
                p_opt3.metric("Picker Travel Distance Saved", f"{savings_pct:.1f}%")
                
                st.info(f"💡 **Routing Guidance**: Picking tasks are organized alphabetically by warehouse location code (Zone-Aisle-Shelf). Travel saving calculation is based on Manhattan travel weights between zone segments.")
                
                sorted_tasks = tasks_df[tasks_df["Status"].isin(["Pending", "Picking"])].sort_values(by="Location")
                st.markdown("**Recommended Picking Sequence (Optimized Aisle Route)**")
                
                # Make column selection completely safe for both capitalized and lowercase schemas
                display_columns = [
                    "location", "Location",
                    "order_code", "Order Code",
                    "product_code", "Product Code",
                    "product_name", "Product Name", "name", "Name",
                    "quantity", "Quantity",
                    "status", "Status"
                ]
                display_columns = [col for col in display_columns if col in sorted_tasks.columns]
                
                st.dataframe(sorted_tasks[display_columns], use_container_width=True, hide_index=True)
            else:
                st.info("All picking tasks are already completed.")

            st.divider()

            st.subheader("⚙️ Picking Tasks Execution Board")
            incomplete_tasks = tasks_df[~tasks_df["Status"].isin(["Packed", "Completed"])]
            
            if incomplete_tasks.empty:
                st.success("All picking queue tasks are completed.")
            else:
                task_options = {
                    f"Task #{row['ID']} - Order: {row['Order Code']} - Prod: {row['Product Code']} - Location: {row['Location']} (Qty: {row['Quantity']}) [{row['Status']}]": row["ID"]
                    for _, row in incomplete_tasks.iterrows()
                }
                selected_task_label = st.selectbox("Select Task to Advance", list(task_options.keys()))
                selected_task_id = task_options[selected_task_label]
                selected_task = tasks_df[tasks_df["ID"] == selected_task_id].iloc[0]
                
                st.write(f"Current Task State: **{selected_task['Status']}**")
                
                action_col1, action_col2 = st.columns(2)
                with action_col1:
                    start_disabled = selected_task["Status"] != "Pending"
                    if st.button("👷 START PICKING", disabled=start_disabled, use_container_width=True):
                        try:
                            update_picking_task_status(selected_task_id, "Picking")
                            st.success(f"Task #{selected_task_id} status updated to Picking.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Status update failed: {e}")
                with action_col2:
                    complete_disabled = selected_task["Status"] != "Picking"
                    if st.button("✅ COMPLETE PICKING", disabled=complete_disabled, use_container_width=True):
                        try:
                            update_picking_task_status(selected_task_id, "Picked")
                            st.success(f"Task #{selected_task_id} completed. Order updated to Picked.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Status update failed: {e}")

            st.divider()
            st.subheader("📋 Complete Picking Tasks Log")
            st.dataframe(tasks_df, use_container_width=True, hide_index=True)

    # 📦 PACKING WORKFLOW VIEW
    elif page == "📦 Packing Workflow":
        st.header("📦 Packing Operations Station")
        st.write("Process completed picks into secure shipments, prepare packaging, and check requirements.")
        st.divider()

        # Database-level query for orders ready for packing (Picked or QC Failed)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT
                o.order_code, 
                o.customer, 
                p.name AS product_name, 
                o.quantity, 
                o.priority, 
                coalesce(pt.status, 'Completed') AS picking_status,
                coalesce(po.status, 'Pending') AS packing_status,
                p.location,
                o.status AS order_status
            FROM orders o
            JOIN products p ON o.product_code = p.product_code
            LEFT JOIN picking_tasks pt ON o.order_code = pt.order_code
            LEFT JOIN packing_operations po ON o.order_code = po.order_code
            WHERE (o.status = 'Picked' OR pt.status = 'Picked' OR (o.status = 'QC Failed' AND coalesce(po.status, '') != 'Packed'))
              AND o.status NOT IN ('Packing', 'Packed', 'Ready for Dispatch', 'Dispatched')
              AND (po.status IS NULL OR po.status NOT IN ('Packing', 'Packed'))
            ORDER BY o.priority_score DESC, o.id DESC
        """)
        packing_rows = cursor.fetchall()
        
        # Build the list of selectable order codes (both ready and in-progress packing)
        cursor.execute("""
            SELECT DISTINCT o.order_code
            FROM orders o
            LEFT JOIN picking_tasks pt ON o.order_code = pt.order_code
            LEFT JOIN packing_operations po ON o.order_code = po.order_code
            WHERE (o.status IN ('Picked', 'Packing', 'QC Failed') OR pt.status = 'Picked')
              AND o.status NOT IN ('Packed', 'Ready for Dispatch', 'Dispatched')
              AND (po.status IS NULL OR po.status != 'Packed')
        """)
        selectable_order_codes = [row[0] for row in cursor.fetchall()]
        conn.close()

        if not selectable_order_codes:
            st.success("✅ No shipments are waiting at the packing station.")
        else:
            if packing_rows:
                queue_df = pd.DataFrame(packing_rows, columns=[
                    "Order ID", "Customer", "Product", "Quantity", "Priority", 
                    "Picking Status", "Packing Status", "Location", "Order Status"
                ])
                
                st.subheader("📋 Orders Ready for Packing")
                
                # Make display column selection safe for both capitalized and lowercase schemas
                display_columns = [
                    "Order ID", "Customer", "Product", "Quantity", "Priority", 
                    "Picking Status", "Packing Status", "Location"
                ]
                display_columns = [col for col in display_columns if col in queue_df.columns]
                st.dataframe(queue_df[display_columns], use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ No new orders waiting to start packing (active packing operations are listed below).")
            
            st.divider()
            st.subheader("📋 Select Order")
            selected_pack_code = st.selectbox("Select Order ID to Pack", selectable_order_codes)
            
            # Fetch fresh database details for the selected order
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    o.order_code, 
                    o.customer, 
                    p.name, 
                    o.quantity, 
                    o.priority, 
                    p.location, 
                    (p.total_stock - p.reserved_stock - p.damaged_stock) AS available_stock,
                    coalesce(pt.status, 'Completed') AS picking_status,
                    o.product_code,
                    o.status,
                    p.selling_price,
                    p.unit_cost
                FROM orders o
                JOIN products p ON o.product_code = p.product_code
                LEFT JOIN picking_tasks pt ON o.order_code = pt.order_code
                WHERE o.order_code = ?
            """, (selected_pack_code,))
            order_details = cursor.fetchone()
            conn.close()
            
            if order_details:
                ord_id, customer_name, prod_name, qty, priority, location, avail_stock, pick_status, p_code, ord_status, selling_price, unit_cost = order_details
                
                # Display details
                d_col1, d_col2, d_col3, d_col4 = st.columns(4)
                d_col1.metric("Order ID", ord_id)
                d_col2.metric("Customer", customer_name)
                d_col3.metric("Product", f"{prod_name} ({p_code})")
                d_col4.metric("Quantity", f"{qty} units")
                
                d_col5, d_col6, d_col7, d_col8 = st.columns(4)
                d_col5.metric("Priority", priority)
                d_col6.metric("Warehouse Location", location)
                d_col7.metric("Available Stock", f"{avail_stock} units")
                d_col8.metric("Picking Status", pick_status)
                
                st.divider()
                
                # Packaging selection
                st.subheader("📦 Packaging Selection")
                packaging_prices = {
                    "Small Box": 20.0,
                    "Medium Box": 35.0,
                    "Large Box": 50.0,
                    "Poly Mailer": 15.0,
                    "Bubble Wrap": 10.0,
                    "Custom Packaging": 75.0
                }
                selected_pkg = st.selectbox("Select Packaging Type", list(packaging_prices.keys()))
                pkg_cost = packaging_prices[selected_pkg]
                handling_cost = 10.0
                total_packing_cost = pkg_cost + handling_cost
                
                st.markdown("#### 💰 Packing Cost Analysis")
                pc_col1, pc_col2, pc_col3 = st.columns(3)
                pc_col1.metric("Packaging Cost", format_inr(pkg_cost))
                pc_col2.metric("Handling Cost", format_inr(handling_cost))
                pc_col3.metric("Total Packing Cost", format_inr(total_packing_cost))
                
                # Financial Integration analysis
                est_revenue = qty * selling_price
                est_profit = est_revenue - (qty * unit_cost) - total_packing_cost
                
                st.markdown("#### 📊 Financial Performance Projection")
                fp_col1, fp_col2, fp_col3, fp_col4 = st.columns(4)
                fp_col1.metric("Product Selling Price", format_inr(selling_price))
                fp_col2.metric("Total Order Cost Basis", format_inr(qty * unit_cost))
                fp_col3.metric("Estimated Revenue", format_inr(est_revenue))
                fp_col4.metric("Projected Profit Margin", format_inr(est_profit))
                
                st.divider()
                
                # Checklist
                st.subheader("☑️ Packing Checklist")
                st.write("Please confirm all checks are completed before starting or completing packing:")
                chk_prod = st.checkbox("Correct product verified", value=False)
                chk_qty = st.checkbox("Correct quantity verified", value=False)
                chk_insp = st.checkbox("Product inspected and undamaged", value=False)
                chk_pkg = st.checkbox("Packaging selected and verified", value=False)
                chk_label = st.checkbox("Shipping label printed and ready", value=False)
                chk_invoice = st.checkbox("Invoice generated and ready", value=False)
                
                all_checked = chk_prod and chk_qty and chk_insp and chk_pkg and chk_label and chk_invoice
                
                st.write("")
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    start_disabled = not all_checked or ord_status in ["Packing", "Packed"]
                    if st.button("📦 START PACKING", disabled=start_disabled, use_container_width=True):
                        try:
                            # Update order status
                            update_order_status(ord_id, "Packing")
                            # Create database record in packing_operations
                            create_packing_operation(
                                order_code=ord_id,
                                packaging_type=selected_pkg,
                                packaging_cost=pkg_cost,
                                handling_cost=handling_cost,
                                total_cost=total_packing_cost,
                                status="Packing",
                                packed_by="Staff-Packer"
                            )
                            st.success(f"Packing operation started for Order {ord_id}.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to start packing: {e}")
                            
                with btn_col2:
                    complete_disabled = not all_checked or ord_status != "Packing"
                    if st.button("✅ COMPLETE PACKING", disabled=complete_disabled, use_container_width=True):
                        try:
                            # Update order status
                            update_order_status(ord_id, "Packed")
                            # Update database record in packing_operations
                            update_packing_operation(ord_id, "Packed")
                            st.success(f"Packing completed for Order {ord_id}. Released to Quality Check.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to complete packing: {e}")

        # Packing History
        st.divider()
        st.subheader("📋 Packing History")
        history_rows = get_packing_history()
        if history_rows:
            # Map customer and product from orders for complete historical logs
            history_data = []
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.order_code, o.customer, p.name 
                FROM orders o 
                JOIN products p ON o.product_code = p.product_code
            """)
            order_mapping = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
            conn.close()
            
            for row in history_rows:
                ord_code = row[0]
                cust_name, prod_name = order_mapping.get(ord_code, ("Unknown", "Unknown"))
                history_data.append([
                    ord_code,
                    cust_name,
                    prod_name,
                    row[1], # packaging_type
                    row[2], # packaging_cost
                    row[3], # handling_cost
                    row[4], # total_cost
                    row[6], # packed_by
                    row[7], # packed_at
                    row[5]  # status
                ])
                
            history_df = pd.DataFrame(history_data, columns=[
                "Order ID", "Customer", "Product", "Packaging Type", "Packaging Cost", "Handling Cost", "Total Cost", "Packed By", "Packed At", "Status"
            ])
            # Format currency values
            history_df["Packaging Cost"] = history_df["Packaging Cost"].apply(format_inr)
            history_df["Handling Cost"] = history_df["Handling Cost"].apply(format_inr)
            history_df["Total Cost"] = history_df["Total Cost"].apply(format_inr)
            st.dataframe(history_df, use_container_width=True, hide_index=True)
        else:
            st.info("No packing operations logged yet.")

    # 🔍 QUALITY CHECK VIEW
    elif page == "🔍 Quality Check":
        st.header("🔍 Quality Check Operations")
        st.write("Inspect packed cargo before shipping releases. Enforce fail-safe dispatch blocks.")
        st.divider()

        st.subheader("Shipments Queued for Inspection")
        qc_orders = orders[orders["status"] == "Packed"]
        
        if qc_orders.empty:
            st.success("✅ No shipments waiting for quality inspection.")
        else:
            qc_options = {
                f"Order {row['order_code']} - Cust: {row['customer']} (Qty: {row['quantity']})": row["order_code"]
                for _, row in qc_orders.iterrows()
            }
            selected_qc_code = st.selectbox("Select Order to Inspect", list(qc_options.keys()))
            selected_qc_ord = qc_orders[qc_orders["order_code"] == qc_options[selected_qc_code]].iloc[0]
            
            st.markdown("### Quality Audit Checks")
            st.write(f"• **Item Code**: `{selected_qc_ord['product_code']}`")
            st.write(f"• **Fulfillment Quantity**: `{selected_qc_ord['quantity']} units`")
            st.write(f"• **Destination Customer**: `{selected_qc_ord['customer']}`")
            
            st.divider()
            
            q_act1, q_act2 = st.columns(2)
            with q_act1:
                if st.button("🟢 PASS INSPECTION", use_container_width=True):
                    try:
                        update_order_status(selected_qc_ord["order_code"], "Ready for Dispatch")
                        st.success(f"Order {selected_qc_ord['order_code']} passed inspection and is ready for dispatch.")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"QC pass failed: {e}")
            with q_act2:
                if st.button("🔴 FAIL INSPECTION (FLAG EXCEPTION)", use_container_width=True):
                    try:
                        update_order_status(selected_qc_ord["order_code"], "QC Failed")
                        desc = f"Order {selected_qc_ord['order_code']} failed physical quality check: Packaging tear on watch carton."
                        recom = resolve_exception("Quality Failure")
                        create_exception(
                            order_code=selected_qc_ord["order_code"],
                            exception_type="Quality Failure",
                            description=desc,
                            recommendation=recom
                        )
                        st.error(f"Order {selected_qc_ord['order_code']} has failed quality control. Exception created automatically.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"QC fail recording failed: {e}")

    # 🚨 EXCEPTION MANAGEMENT VIEW
    elif page == "🚨 Exception Management":
        st.header("🚨 Exception Management Center")
        st.write("Log operational irregularities, track open warehouse exception cards, and execute resolutions.")
        st.divider()

        es1, es2, es3, es4 = st.columns(4)
        es1.metric("Total Exceptions Logged", total_exceptions_count)
        es2.metric("Open Warnings", sum(1 for r in exceptions_rows if r[5] == "Open"))
        es3.metric("In Progress Investigations", sum(1 for r in exceptions_rows if r[5] == "In Progress"))
        es4.metric("Resolved Cases", sum(1 for r in exceptions_rows if r[5] in ["Closed", "Resolved"]))

        st.divider()

        st.subheader("➕ Record Manual Warehouse Exception")
        with st.expander("Record Exception Details"):
            with st.form("manual_exception_form"):
                man_order_code = st.selectbox("Related Order", ["None"] + orders["order_code"].tolist() if not orders.empty else ["None"])
                man_exc_type = st.selectbox("Exception Type", [
                    "Stock Shortage", "Damaged Item", "Missing Item", 
                    "Wrong Item Picked", "Quality Failure", "Inventory Mismatch", 
                    "Packing Error", "Dispatch Delay"
                ])
                man_desc = st.text_area("Irregularity Description", "")
                
                sub_exc = st.form_submit_button("🚨 Submit Exception Card")
                if sub_exc:
                    if not man_desc.strip():
                        st.error("Description cannot be empty.")
                    else:
                        rec_recom = resolve_exception(man_exc_type)
                        create_exception(
                            order_code=None if man_order_code == "None" else man_order_code,
                            exception_type=man_exc_type,
                            description=man_desc.strip(),
                            recommendation=rec_recom
                        )
                        st.success("Exception card filed successfully.")
                        st.rerun()

        st.divider()

        st.subheader("📋 Active Exception Board")
        if not exceptions_rows:
            st.success("✅ No exceptions registered.")
        else:
            exc_df = pd.DataFrame(exceptions_rows, columns=["ID", "Order Code", "Type", "Description", "Recommendation", "Status", "Created At"])
            
            status_sel = st.selectbox("Filter Exceptions", ["All Open/In Progress", "Open", "In Progress", "Closed", "Resolved"])
            if status_sel == "All Open/In Progress":
                disp_exc = exc_df[exc_df["Status"].isin(["Open", "In Progress"])]
            else:
                disp_exc = exc_df[exc_df["Status"] == status_sel]

            critical_order_codes = orders[orders["priority"].isin(["Critical", "High"])]["order_code"].tolist() if not orders.empty else []
            
            def flag_crit(row):
                if row["Status"] in ["Open", "In Progress"] and row["Order Code"] in critical_order_codes:
                    return "🔥 CRITICAL"
                return "NORMAL"
            
            if not disp_exc.empty:
                disp_exc = disp_exc.copy()
                disp_exc["Risk Rating"] = disp_exc.apply(flag_crit, axis=1)
                st.dataframe(disp_exc, use_container_width=True, hide_index=True)
                
                st.divider()
                
                st.subheader("⚙️ Update Exception Investigated State")
                active_exc_rows = exc_df[~exc_df["Status"].isin(["Closed", "Resolved"])]
                
                if not active_exc_rows.empty:
                    exc_options = {
                        f"#{row['ID']} - {row['Type']} on Order {row['Order Code']}": row['ID']
                        for _, row in active_exc_rows.iterrows()
                    }
                    selected_exc_lbl = st.selectbox("Select Active Case", list(exc_options.keys()))
                    selected_exc_id = exc_options[selected_exc_lbl]
                    selected_exc_data = exc_df[exc_df["ID"] == selected_exc_id].iloc[0]
                    
                    state_options = ["Open", "In Progress", "Resolved", "Closed"]
                    current_state_idx = state_options.index(selected_exc_data["Status"]) if selected_exc_data["Status"] in state_options else 0
                    new_state = st.selectbox("Update Case Status", state_options, index=current_state_idx)
                    
                    if st.button("💾 SAVE CASE UPDATE", use_container_width=True):
                        try:
                            update_exception_status(selected_exc_id, new_state)
                            st.success(f"Case #{selected_exc_id} updated to {new_state}.")
                            
                            if new_state in ["Resolved", "Closed"] and selected_exc_data["Type"] == "Quality Failure":
                                ord_code_rec = selected_exc_data["Order Code"]
                                if ord_code_rec:
                                    update_order_status(ord_code_rec, "Packed")
                                    st.info(f"Fulfillment Release: Order {ord_code_rec} status reset to Packed for QC re-evaluation.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failing saving updates: {e}")
                else:
                    st.success("All exceptions are closed.")
            else:
                st.info("No exceptions found matching selection.")

    # 📦 BACKORDER VIEW
    elif page == "📦 Backorder Management":
        st.header("📦 Backorder Operations Queue")
        st.write("Review shortage quantities, track backordered demand, and trigger fulfillment once stock replenishes.")
        st.divider()

        backorders = get_backorders()
        if backorders.empty:
            st.success("✅ No backorders in system.")
        else:
            st.subheader("Backordered Item Queue")
            disp_b = backorders.copy()
            def map_backorder_financials(row):
                p_code = row["product_code"]
                qty = row["quantity"]
                if p_code in product_financials:
                    cost, price = product_financials[p_code]
                    return format_inr(price), format_inr(price * qty), format_inr((price - cost) * qty)
                return "₹0", "₹0", "₹0"
                
            b_mapped = disp_b.apply(map_backorder_financials, axis=1)
            disp_b["Selling Price"] = [m[0] for m in b_mapped]
            disp_b["Revenue at Risk"] = [m[1] for m in b_mapped]
            disp_b["Profit at Risk"] = [m[2] for m in b_mapped]
            
            st.dataframe(add_product_names(disp_b, products), use_container_width=True, hide_index=True)

            st.divider()

            st.subheader("💡 Intelligent Backorder Fulfillment Advisor")
            open_backorders = backorders[backorders["status"] == "Open"]
            
            if open_backorders.empty:
                st.success("All backorders are resolved.")
            else:
                recommendations = []
                for _, row in open_backorders.iterrows():
                    p_code = row["product_code"]
                    match_prod = products[products["product_code"] == p_code].iloc[0]
                    avail = match_prod["available_stock"]
                    
                    if avail > 0:
                        fulfillable = min(avail, int(row["quantity"]))
                        cost, price = product_financials[p_code]
                        recommendations.append({
                            "Backorder ID": row["id"],
                            "Order Code": row["order_code"],
                            "Product Code": p_code,
                            "Product Name": match_prod["name"],
                            "Shortage Qty": row["quantity"],
                            "Available Stock": avail,
                            "Fulfillable Qty": fulfillable,
                            "Selling Price": format_inr(price),
                            "Fulfillable Revenue": format_inr(fulfillable * price),
                            "Status": "⚡ READY TO Fulfill"
                        })
                        
                if recommendations:
                    st.write("The following items have stock available in the warehouse and can be allocated:")
                    rec_df = pd.DataFrame(recommendations)
                    st.dataframe(rec_df, use_container_width=True, hide_index=True)
                    
                    st.markdown("### Fulfill Backorder Action")
                    rec_options = {
                        f"Fulfill ID #{r['Backorder ID']} - Order {r['Order Code']} (Allocate {r['Fulfillable Qty']} of {r['Product Name']})": (r['Backorder ID'], r['Fulfillable Qty'])
                        for r in recommendations
                    }
                    selected_rec_lbl = st.selectbox("Choose Backorder to Fulfill", list(rec_options.keys()))
                    selected_bid, selected_fq = rec_options[selected_rec_lbl]
                    
                    if st.button("⚡ ALLOCATE STOCK & RELEASE BACKORDER", use_container_width=True):
                        try:
                            allocated_amt = fulfill_backorder_db(selected_bid, selected_fq)
                            st.success(f"Allocated {allocated_amt} units to fulfill backorder. Picking task has been queued.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Fulfillment failed: {e}")
                else:
                    st.warning("⚠️ Insufficient warehouse stock to fulfill any backorder queue items. Replenishment is required.")

    # 🚚 DISPATCH & TIMELINE VIEW
    elif page == "🚚 Dispatch & Timeline":
        st.header("🚚 Shipping & Dispatch Controls")
        st.write("Run release validation rules, sign off dispatch approvals, and check fulfillment timelines.")
        st.divider()

        dispatch_orders = orders[orders["status"] == "Ready for Dispatch"]
        
        if dispatch_orders.empty:
            st.success("✅ No shipments are waiting dispatch clearance. Complete picking, packing, and Quality Check first.")
        else:
            st.subheader("Clearance Approval Queue")
            disp_options = {
                f"Order {row['order_code']} - Cust: {row['customer']}": row["order_code"]
                for _, row in dispatch_orders.iterrows()
            }
            selected_disp_code = disp_options[st.selectbox("Select Order to Review", list(disp_options.keys()))]
            selected_disp_ord = orders[orders["order_code"] == selected_disp_code].iloc[0]
            
            order_exceptions = [e for e in exceptions_rows if e[1] == selected_disp_code and e[5] in ["Open", "In Progress"]]
            
            st.write(f"Customer Destination: **{selected_disp_ord['customer']}**")
            st.write(f"Product Cargo: **{selected_disp_ord['product_code']}** (Qty: **{selected_disp_ord['quantity']}**)")
            
            val_exceptions = len(order_exceptions) == 0
            
            st.markdown("### Dispatch Prerequisites Audit")
            st.write("🟢 Picking Completed")
            st.write("🟢 Packing Verified")
            st.write("🟢 Quality Check Passed")
            if val_exceptions:
                st.write("🟢 No Unresolved Exceptions")
            else:
                st.write(f"🔴 Unresolved Exceptions Detected ({len(order_exceptions)} open case(s))")
                for e in order_exceptions:
                    st.error(f"Case ID #{e[0]} - Type: {e[2]} | {e[3]}")
                    
            all_passed = val_exceptions
            
            p_code = selected_disp_ord["product_code"]
            qty = selected_disp_ord["quantity"]
            cost, price = product_financials[p_code]
            o_val = qty * price
            o_cost = qty * cost
            o_profit = o_val - o_cost
            
            st.markdown("### 📊 Shipment Financial Release Details")
            df_col1, df_col2, df_col3 = st.columns(3)
            df_col1.metric("Order Sales Value", format_inr(o_val))
            df_col2.metric("Order Cost Basis", format_inr(o_cost))
            df_col3.metric("Estimated Dispatch Profit", format_inr(o_profit))
            
            if all_passed:
                st.success("✅ All fulfillment checkpoints passed. Shipment released for departure.")
                if st.button("🚚 DISPATCH SHIPMENT FROM WAREHOUSE", use_container_width=True):
                    try:
                        update_order_status(selected_disp_code, "Dispatched")
                        st.success("Shipment dispatched. Departure logged.")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Dispatch execution failed: {e}")
            else:
                st.error("⛔ Dispatch blocked. Resolve open exception cards before dispatching.")
                
        st.divider()
        
        st.subheader("📈 Live Fulfillment Tracker & Stage Timeline")
        all_ord_codes = orders["order_code"].tolist() if not orders.empty else []
        
        if all_ord_codes:
            selected_track_code = st.selectbox("Select Order to Track Timeline", all_ord_codes)
            selected_track_ord = orders[orders["order_code"] == selected_track_code].iloc[0]
            
            track_status = selected_track_ord["status"]
            stages = ["Pending", "Allocated", "Picking", "Picked", "Packing", "Packed", "Ready for Dispatch", "Dispatched"]
            
            stage_emojis = {
                "Order Created": "🛒",
                "Inventory Allocated": "📦",
                "Picking": "👷",
                "Picked": "📦",
                "Packing": "📦",
                "Packed": "📦",
                "Quality Check": "🔍",
                "Ready for Dispatch": "🚚",
                "Dispatched": "🚚",
                # Support old/alternative stage names safely
                "Pending": "🛒 Order Created",
                "Allocated": "📦 Allocated"
            }
            
            if track_status in stages:
                idx = stages.index(track_status)
            elif track_status == "QC Failed":
                idx = 4
            else:
                idx = 0
                
            progress_pct = (idx + 1) / len(stages)
            st.progress(progress_pct)
            st.write(f"Fulfillment Progress: **{int(progress_pct * 100)}%** (Stage {idx+1}/{len(stages)})")
            
            for i, stage in enumerate(stages):
                if i < idx:
                    st.success(f"✅ {stage_emojis.get(stage, '📦')} — Completed")
                elif i == idx:
                    if track_status == "QC Failed":
                        st.error(f"❌ {stage_emojis.get(stage, '📦')} — Inspection Failed (Exception Open)")
                    else:
                        st.warning(f"🟡 {stage_emojis.get(stage, '📦')} — Current Active Stage")
                else:
                    st.info(f"⏳ {stage_emojis.get(stage, '📦')} — Pending Stage")
        else:
            st.info("No orders registered.")

    # 📊 ANALYTICS VIEW
    elif page == "📊 Analytics & Insights":
        st.header("📊 Warehouse Intelligence & Analytics")
        st.write("Examine warehouse bottlenecks, system risk score diagnostics, and financial business reports.")
        st.divider()

        st.subheader("🚨 System Risk Diagnostics Evaluation")
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            st.markdown(f"**Risk Severity Score**: `{risk_score}/100`")
            st.markdown(f"**Risk Level Status**: `{risk_status}`")
        with r_col2:
            st.write(f"**Engine Narrative Explanation**: {risk_reason}")
            
        st.divider()

        st.subheader("⚠️ Operational Bottleneck Detector")
        st.write(f"**Current Identified Bottleneck Area**: `{bottleneck}`")
        st.write(f"**Affected Queue Load**: `{bottleneck_count} orders`")
        
        b_recom = ""
        if bottleneck == "Order Processing":
            b_recom = "Pending allocations are clogging the pipeline. Run allocations for pending orders immediately."
        elif bottleneck == "Picking Queue":
            b_recom = "Picking tasks are accumulating. Utilize Aisle route optimization grouping."
        elif bottleneck == "Packing Station":
            b_recom = "Sealing stations are packed. Check picker-packer flow balance."
        elif bottleneck == "Quality Check":
            b_recom = "Packed shipments await inspection release. Run quality checks on Packed items."
        elif bottleneck == "Dispatch Release":
            b_recom = "Shipments are locked ready for departure. Resolve exceptions and dispatch."
            
        st.info(f"💡 **Bottleneck Counter-Action Recommendation**: {b_recom}")

        st.divider()

        st.subheader("💰 Dedicated Financial Intelligence Section")
        dfa1, dfa2, dfa3 = st.columns(3)
        dfa1.metric("Total Warehouse Inventory Value", format_inr(total_inventory_value))
        dfa2.metric("Warehouse Potential Sales Value", format_inr(potential_sales_value))
        dfa3.metric("Warehouse Potential Profit Margin", format_inr(potential_profit))

        dfb1, dfb2, dfb3 = st.columns(3)
        dfb1.metric("Registered Orders Gross Value", format_inr(total_order_value))
        dfb2.metric("Registered Orders Cost Basis", format_inr(total_order_cost))
        dfb3.metric("Net Projected Orders Profit", format_inr(estimated_order_profit))

        st.markdown("#### Key Valuation Performance Indicators")
        avg_cost = products["unit_cost"].mean() if not products.empty else 0.0
        avg_price = products["selling_price"].mean() if not products.empty else 0.0
        highest_val_prod = products.loc[products["inventory_value"].idxmax()]["name"] if not products.empty and not products[products["inventory_value"] > 0].empty else "None"
        highest_prof_prod = products.loc[products["potential_profit"].idxmax()]["name"] if not products.empty and not products[products["potential_profit"] > 0].empty else "None"

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Average Product Cost", format_inr(avg_cost))
        kpi2.metric("Average Selling Price", format_inr(avg_price))
        kpi3.metric("Highest-Value Inventory Item", highest_val_prod)
        kpi4.metric("Highest-Profit Potential Item", highest_prof_prod)

        st.divider()

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.subheader("📦 Potential Sales Value by Product")
            if not products.empty:
                st.bar_chart(products.set_index("name")["potential_sales_value"])
            else:
                st.info("No items to plot.")
        with chart_col2:
            st.subheader("💵 Inventory Value by Product")
            if not products.empty:
                st.bar_chart(products.set_index("name")["inventory_value"])
            else:
                st.info("No items to plot.")

        st.divider()

        st.subheader("🚨 Financial Risk Analysis")
        damaged_stock_value = float((products["damaged_stock"] * products["unit_cost"]).sum()) if not products.empty else 0.0
        delayed_dispatch_val = 0.0
        if not orders.empty:
            for _, row in orders[orders["status"] == "Ready for Dispatch"].iterrows():
                p_code = row["product_code"]
                qty = row["quantity"]
                if p_code in product_financials:
                    delayed_dispatch_val += qty * product_financials[p_code][1]
                    
        fr1, fr2, fr3 = st.columns(3)
        fr1.metric("Revenue Blocked by Shortages (At Risk)", format_inr(revenue_at_risk), delta=f"-{format_inr(profit_at_risk)} Profit at Risk", delta_color="inverse")
        fr2.metric("Inventory Asset Write-off (Damaged Stock)", format_inr(damaged_stock_value), delta_color="inverse")
        fr3.metric("Departure Delayed Sales Value", format_inr(delayed_dispatch_val))
        
        st.divider()
        
        st.subheader("📊 Order Transactions & Returns Analytics")
        an_col1, an_col2, an_col3, an_col4 = st.columns(4)
        an_col1.metric("Inventory Turnover", f"{inventory_turnover:.2f}x")
        an_col2.metric("Order Return Rate", f"{return_rate:.1f}%")
        an_col3.metric("Returned Quantity", f"{returned_quantity_sum} units")
        an_col4.metric("Restocked Quantity", f"{restocked_quantity_sum} units")
        
        an_col5, an_col6, an_col7, an_col8 = st.columns(4)
        an_col5.metric("Stock In Total Qty", f"{stock_in_qty} units")
        an_col6.metric("Stock Out Total Qty", f"{stock_out_qty} units")
        an_col7.metric("Inventory Adjustments Qty", f"{stock_adj_qty} units")
        an_col8.metric("Order Revenue (Paid)", format_inr(paid_total_val))

        an_col9, an_col10, an_col11 = st.columns(3)
        an_col9.metric("Paid Orders", paid_count)
        an_col10.metric("Pending Payment Orders", pending_pay_count)
        an_col11.metric("Refunds Amount Paid", format_inr(refund_amount_sum))

        high_val_exc = []
        for row in exceptions_rows:
            if row[5] in ["Open", "In Progress"] and row[1]:
                ord_code = row[1]
                match_o = orders[orders["order_code"] == ord_code]
                if not match_o.empty:
                    qty = match_o.iloc[0]["quantity"]
                    p_code = match_o.iloc[0]["product_code"]
                    if p_code in product_financials:
                        v = qty * product_financials[p_code][1]
                        if v >= 20000.0:
                            high_val_exc.append(f"• **Exception ID #{row[0]}** on Order `{ord_code}` is holding cargo worth **{format_inr(v)}**.")
                            
        if high_val_exc:
            st.error("⚠️ **High-Value Exceptions Blocking Dispatch**:")
            for exc_msg in high_val_exc:
                st.write(exc_msg)
 
        st.divider()
 
        st.subheader("🧠 Decision Advisor Recommendations")
        recs = []
        if critical_orders_count > 0:
            recs.append("🔥 **HIGH URGENCY**: Process Critical orders in the queue first. *Note: Critical operational priority takes precedence over financial value.*")
        if low_stock_count > 0:
            recs.append(f"🟡 **REPLENISHMENT**: {low_stock_count} products are below reorder level. Review Smart Reorder recommendations.")
        if out_of_stock_count > 0:
            recs.append("🔴 **STOCKOUT WARNING**: Out of stock products exist. Place purchase orders.")
        if open_exceptions_count > 0:
            recs.append("🚨 **EXCEPTION HOLDS**: Active exception holds exist. Resolve open exception cards.")
        if open_backorders_count > 0:
            recs.append(f"📦 **BACKORDER RELEASE**: Open backorders detected. Fulfill backorders using available inventory. Revenue at Risk is **{format_inr(revenue_at_risk)}**.")
            
        # Smart Intelligent Insights Recommendations
        if pending_pay_count > 0:
            recs.append(f"💳 **PENDING PAYMENTS**: {pending_pay_count} orders have pending payment. Contact customers for payment confirmation.")
        if category_return_trend_msg:
            recs.append(f"📈 **RETURN WARNING**: {category_return_trend_msg}")
        if avail_restock_count > 0:
            recs.append(f"📦 **RESTOCK RECOMMENDATION**: {avail_restock_count} returned products are approved for restocking and waiting in the warehouse.")
        if high_value_refunds_pending:
            for r_code, r_amt in high_value_refunds_pending:
                recs.append(f"🚨 **HIGH VALUE REFUND**: Order {r_code} has a refund of {format_inr(r_amt)} pending that requires warehouse review.")

        if recs:
            for r in recs:
                st.write(r)
        else:
            st.success("🟢 Operations running at peak efficiency. No action recommendations flagged.")

    # 🚀 HACKATHON DEMO MODE VIEW
    elif page == "🚀 Hackathon Demo Mode":
        st.header("🚀 Hackathon Interactive Demo Mode")
        st.write("Demonstrate the complete warehouse lifecycle from order entry to final dispatch in a single interactive walkthrough.")
        st.divider()

        if "demo_step" not in st.session_state:
            st.session_state.demo_step = 1
        if "demo_order_code" not in st.session_state:
            st.session_state.demo_order_code = ""
        if "demo_exception_id" not in st.session_state:
            st.session_state.demo_exception_id = None

        st.subheader(f"Current Demo Step: {st.session_state.demo_step} of 10")
        st.progress(st.session_state.demo_step / 10)
        
        if st.session_state.demo_step == 1:
            st.markdown("### Step 1: Initialize System & Seed Demo Stock")
            st.write("We will reset and seed the warehouse database with default demo products, stock levels, and financial values.")
            if st.button("🚀 Seed Warehouse Database", use_container_width=True):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DROP TABLE IF EXISTS products")
                cursor.execute("DROP TABLE IF EXISTS orders")
                cursor.execute("DROP TABLE IF EXISTS picking_tasks")
                cursor.execute("DROP TABLE IF EXISTS exceptions")
                cursor.execute("DROP TABLE IF EXISTS allocations")
                cursor.execute("DROP TABLE IF EXISTS backorders")
                cursor.execute("DROP TABLE IF EXISTS inventory_transactions")
                cursor.execute("DROP TABLE IF EXISTS order_transactions")
                cursor.execute("DROP TABLE IF EXISTS return_orders")
                conn.commit()
                conn.close()
                initialize_database()
                st.session_state.demo_step = 2
                st.success("Warehouse database seeded. Ready for Order Creation!")
                st.rerun()

        elif st.session_state.demo_step == 2:
            st.markdown("### Step 2: Select Smart Watch (P006)")
            st.write("Display the catalog details of the **Smart Watch (P006)**. We see that the warehouse currently holds **6 units** of available stock.")
            st.write("• Product Code: `P006` | Cost Price: **₹2,500** | Selling Price: **₹3,999**")
            st.write("• Total Stock: **6** | Reorder Level: **8** (Marks as Low Stock Risk)")
            
            if st.button("👁️ Inspect Smart Watch Catalog Profile", use_container_width=True):
                st.session_state.demo_step = 3
                st.rerun()

        elif st.session_state.demo_step == 3:
            st.markdown("### Step 3: Create Customer Demand (10 Smart Watches)")
            st.write("Create a critical order for **10 Smart Watches** for Customer **Apex Enterprises**.")
            st.write("Note: The warehouse only has **6 Smart Watches** in stock. This will trigger partial stock allocation and backordering.")
            
            if st.button("🛒 Generate Apex Smart Watch Order", use_container_width=True):
                try:
                    priority_class, score, reason, action = calculate_priority_score(
                        urgency=9,
                        quantity=10,
                        available_stock=6,
                        existing_priority="Critical",
                        order_status="Pending",
                        selling_price=3999.0,
                        unit_cost=2500.0
                    )
                    ord_code = create_order(
                        customer="Apex Enterprises",
                        product_code="P006",
                        quantity=10,
                        priority=priority_class,
                        priority_score=score
                    )
                    st.session_state.demo_order_code = ord_code
                    st.session_state.demo_step = 4
                    st.success(f"Order created successfully! Code: **{ord_code}** | Priority: **{priority_class}**")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed creating order: {e}")

        elif st.session_state.demo_step == 4:
            st.markdown("### Step 4: Run Intelligent Priority Engine")
            st.write(f"Order **{st.session_state.demo_order_code}** is awaiting evaluation by our priority scoring engine.")
            st.write(f"• Raw Customer Urgency: **9/10**")
            st.write(f"• Required Qty: **10** | Available Stock: **6**")
            st.write(f"• Total Order Value: **₹39,990** | Projected Profit: **₹14,990**")
            
            priority_class, score, reason, action = calculate_priority_score(
                urgency=9,
                quantity=10,
                available_stock=6,
                existing_priority="Critical",
                order_status="Pending",
                selling_price=3999.0,
                unit_cost=2500.0
            )
            
            st.info(f"🤖 **Engine Output Score**: **{score}/100** ({priority_class})\n\n**Logic Narrative**: {reason}\n\n**Action Recommendation**: {action}")
            
            if st.button("🧠 Accept Evaluation & Move to Allocation", use_container_width=True):
                st.session_state.demo_step = 5
                st.rerun()

        elif st.session_state.demo_step == 5:
            st.markdown("### Step 5: Execute Smart Allocation Engine")
            st.write(f"We will check warehouse stocks and run the allocation logic on **{st.session_state.demo_order_code}**.")
            st.write("The system should allocate the 6 available Smart Watches to picking and reserve them, and backorder the remaining 4 units.")
            
            alloc_val = 6 * 3999.0
            alloc_profit = 6 * (3999.0 - 2500.0)
            risk_val = 4 * 3999.0
            risk_profit = 4 * (3999.0 - 2500.0)
            
            st.markdown("#### Projected Financial Impact of Allocation Decision")
            fa1, fa2 = st.columns(2)
            fa1.metric("Allocated Sales Value", format_inr(alloc_val), delta=f"{format_inr(alloc_profit)} profit released")
            fa2.metric("Shortage Revenue at Risk", format_inr(risk_val), delta=f"-{format_inr(risk_profit)} profit at risk", delta_color="inverse")
            
            if st.button("⚡ Execute Allocation Allocation Check", use_container_width=True):
                try:
                    result = execute_allocation(
                        order_code=st.session_state.demo_order_code,
                        product_code="P006",
                        requested_quantity=10,
                        allocated_quantity=6,
                        shortage_quantity=4,
                        decision="PARTIAL ALLOCATION"
                    )
                    st.success("Allocation executed successfully!")
                    st.info("🟢 6 Smart Watches allocated for picking (Reserved).\n\n🟡 4 Smart Watches registered as an Open Backorder.")
                    st.session_state.demo_step = 6
                    st.rerun()
                except Exception as e:
                    st.error(f"Allocation execution failed: {e}")

        elif st.session_state.demo_step == 6:
            st.markdown("### Step 6: Start & Complete Aisle Picking Task")
            st.write("A picking task has been generated in the database for the 6 allocated Smart Watches at warehouse location `A-01-01`.")
            
            p_tasks = get_picking_tasks(order_code=st.session_state.demo_order_code)
            if p_tasks:
                t_id = p_tasks[0][0]
                t_status = p_tasks[0][5]
                st.write(f"• Picking Task ID: `#{t_id}` | Location: `A-01-01` | Status: `{t_status}`")
                
                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    if st.button("👷 Start Aisle Picker Route", disabled=(t_status != "Pending"), use_container_width=True):
                        update_picking_task_status(t_id, "Picking")
                        st.success("Picker travel path initialized.")
                        st.rerun()
                with p_col2:
                    if st.button("✅ Confirm Aisle Item Collection", disabled=(t_status != "Picking"), use_container_width=True):
                        update_picking_task_status(t_id, "Picked")
                        st.success("Items picked and brought to packaging bay. Order status set to Picked.")
                        st.session_state.demo_step = 7
                        st.rerun()
            else:
                st.error("No picking tasks found for this order. Did you complete Step 5?")

        elif st.session_state.demo_step == 7:
            st.markdown("### Step 7: Package Sealing Station")
            st.write("Order has arrived at the packaging station. We will pack and seal the 6 picked units.")
            if st.button("📦 Complete Packaging & Labeling", use_container_width=True):
                update_order_status(st.session_state.demo_order_code, "Packed")
                st.success("Shipment packed and labeled. Ready for Quality Check.")
                st.session_state.demo_step = 8
                st.rerun()

        elif st.session_state.demo_step == 8:
            st.markdown("### Step 8: Quality Inspection Fail-safe Demonstration")
            st.write("Before dispatching, let's demonstrate the Quality check. We will simulate a QC Failure to show the automatic exception logging and dispatch block.")
            
            if st.button("🔴 Fail Quality Inspection (Simulation)", use_container_width=True):
                update_order_status(st.session_state.demo_order_code, "QC Failed")
                desc = f"Order {st.session_state.demo_order_code} failed physical quality check: Packaging tear on watch carton."
                recom = resolve_exception("Quality Failure")
                create_exception(
                    order_code=st.session_state.demo_order_code,
                    exception_type="Quality Failure",
                    description=desc,
                    recommendation=recom
                )
                exc_list = get_exceptions()
                if exc_list:
                    st.session_state.demo_exception_id = exc_list[0][0]
                st.error("Inspection Failed! A 'Quality Failure' exception card was automatically created in the database, blocking dispatch.")
                st.session_state.demo_step = 9
                st.rerun()

        elif st.session_state.demo_step == 9:
            st.markdown("### Step 9: Resolve Exception & Pass QC")
            st.write(f"We see that Order **{st.session_state.demo_order_code}** has a QC Exception ID `#{st.session_state.demo_exception_id}` in progress.")
            st.write("The supervisor replaces the package box, files the resolution, and releases the exception block.")
            
            if st.button("✅ Resolve Quality Exception", use_container_width=True):
                if st.session_state.demo_exception_id:
                    update_exception_status(st.session_state.demo_exception_id, "Closed")
                    update_order_status(st.session_state.demo_order_code, "Packed")
                update_order_status(st.session_state.demo_order_code, "Ready for Dispatch")
                st.success("Exception resolved and closed. Quality Check passed. Order cleared for departure!")
                st.session_state.demo_step = 10
                st.rerun()

        elif st.session_state.demo_step == 10:
            st.markdown("### Step 10: Demo Completed successfully!")
            st.success("🎉 You have successfully demonstrated the end-to-end Intelligent Fulfillment and Financial flow!")
            
            st.markdown("#### Final Operations & Risk Summary")
            ds1, ds2, ds3, ds4 = st.columns(4)
            ds1.metric("Order Gross Value", format_inr(10 * 3999.0))
            ds2.metric("Dispatched Value (6 units)", format_inr(6 * 3999.0))
            ds3.metric("Revenue at Risk (4 units)", format_inr(4 * 3999.0))
            ds4.metric("Operations Risk Score", f"{risk_score}/100")
            
            if st.button("🔄 Restart Interactive Demo", use_container_width=True):
                st.session_state.demo_step = 1
                st.session_state.demo_order_code = ""
                st.session_state.demo_exception_id = None
                st.rerun()

# ============================================================
# PERSPECTIVE 2: 👤 CUSTOMER VIEW (CUSTOMER PORTAL)
# ============================================================
elif perspective == "👤 Customer":
    st.sidebar.divider()
    
    # Initialize Customer Session States
    if "customer_session" not in st.session_state:
        st.session_state.customer_session = False
        st.session_state.customer_login_name = ""
        st.session_state.customer_login_order_code = None
        st.session_state.customer_active_order_code = None

    # Access Form in Sidebar if not logged in
    if not st.session_state.customer_session:
        st.sidebar.markdown("### 🔑 Customer Authentication")
        st.sidebar.write("Access your order status dashboard using your Customer Name AND Order ID.")
        
        login_name = st.sidebar.text_input("Customer Name", value="", placeholder="e.g. Apex Enterprises")
        login_order = st.sidebar.text_input("Order ID", value="", placeholder="e.g. ORD005")
        
        if st.sidebar.button("🔓 ACCESS CUSTOMER PORTAL", use_container_width=True):
            if not login_name.strip() or not login_order.strip():
                st.sidebar.error("❌ Both Customer Name AND Order ID are required to verify ownership.")
            else:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Verify Name AND Order ID together
                cursor.execute(
                    "SELECT customer, order_code FROM orders WHERE UPPER(order_code) = UPPER(?) AND UPPER(customer) = UPPER(?)",
                    (login_order.strip(), login_name.strip())
                )
                row = cursor.fetchone()
                if row:
                    st.session_state.customer_session = True
                    st.session_state.customer_login_name = row[0]
                    st.session_state.customer_login_order_code = row[1]
                    st.session_state.customer_active_order_code = row[1]
                    st.sidebar.success("Access Granted!")
                    st.rerun()
                else:
                    st.sidebar.error("❌ Order not found or customer information does not match.")
                conn.close()
                
        # Main Welcome panel for Customer Portal before Login
        st.header("👤 Customer Operations Tracking Portal")
        st.write("Welcome to the SmartFulfill Customer Portal. Please utilize the authentication console in the sidebar on the left to review your order schedules, check cargo allocation states, and monitor real-time shipment dispatch departures.")
        st.info("💡 **Demo Authentication Credentials**: You can access using Customer Name: `Apex Enterprises` AND Order ID: `ORD005` (after initializing the demo).")
        
    else:
        # Logged In customer menu options
        st.sidebar.markdown(f"👤 Account: **{st.session_state.customer_login_name}**")
        cust_menu = st.sidebar.radio("Navigation", [
            "👤 Customer Dashboard",
            "🧾 My Orders",
            "💳 Payments & Transactions",
            "🔄 Return Requests",
            "📦 Order Details & Tracking"
        ])
        
        if st.sidebar.button("🔒 EXIT CUSTOMER PORTAL", use_container_width=True):
            st.session_state.customer_session = False
            st.session_state.customer_login_name = ""
            st.session_state.customer_login_order_code = None
            st.session_state.customer_active_order_code = None
            st.rerun()

        # Database-level query for Customer orders
        cust_name_key = st.session_state.customer_login_name
        c_orders = get_customer_orders_db(cust_name_key)
        
        # --------------------------------------------------------
        # 👤 CUSTOMER DASHBOARD SUB-VIEW
        # --------------------------------------------------------
        if cust_menu == "👤 Customer Dashboard":
            st.header(f"👤 Customer Dashboard")
            st.subheader(f"Welcome, {st.session_state.customer_login_name}!")
            st.write("Monitor real-time fulfillment status counters and shipment values.")
            st.divider()
            
            # Calculations
            cust_total_orders = len(c_orders)
            cust_active = int(c_orders[c_orders["status"] != "Dispatched"].shape[0])
            cust_dispatched = int(c_orders[c_orders["status"] == "Dispatched"].shape[0])
            
            # Query backordered count at DB level
            cust_backorders_count = get_customer_backorders_count_db(cust_name_key)
            
            c_col1, c_col2, c_col3, c_col4 = st.columns(4)
            c_col1.metric("Total Orders Registered", cust_total_orders)
            c_col2.metric("Active Shipments", cust_active)
            c_col3.metric("Dispatched Shipments", cust_dispatched)
            c_col4.metric("Backordered Orders", cust_backorders_count)
            
            st.divider()
            st.subheader("📋 Order Tracking Summary")
            
            if not c_orders.empty:
                for _, row in c_orders.iterrows():
                    o_code = row["order_code"]
                    p_code = row["product_code"]
                    qty = row["quantity"]
                    status = row["status"]
                    
                    price = product_financials[p_code][1] if p_code in product_financials else 0.0
                    p_name = products[products["product_code"] == p_code].iloc[0]["name"] if not products[products["product_code"] == p_code].empty else p_code
                    o_value = qty * price
                    
                    # Status progress mapping
                    stages_map = ["Pending", "Allocated", "Picking", "Picked", "Packing", "Packed", "Ready for Dispatch", "Dispatched"]
                    if status in stages_map:
                        prog_idx = stages_map.index(status)
                    elif status == "QC Failed":
                        prog_idx = 4
                    else:
                        prog_idx = 0
                    prog_pct = int(((prog_idx + 1) / len(stages_map)) * 100)
                    
                    st.markdown(f"""
                    <div class="customer-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #e2e8f0; padding-bottom:0.5rem; margin-bottom:0.75rem;">
                            <span class="customer-header">🧾 Order ID: {o_code}</span>
                            <span style="background-color:#e0f2fe; color:#0369a1; padding:0.2rem 0.5rem; border-radius:0.25rem; font-size:0.8rem; font-weight:600;">Status: {status}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between;">
                            <div>
                                <p style="margin:0; font-size:0.9rem; color:#475569;"><b>Product</b>: {p_name} ({p_code})</p>
                                <p style="margin:0.25rem 0 0 0; font-size:0.9rem; color:#475569;"><b>Quantity</b>: {qty} units</p>
                                <p style="margin:0.25rem 0 0 0; font-size:0.9rem; color:#475569;"><b>Selling Price</b>: {format_inr(price)}</p>
                            </div>
                            <div style="text-align:right;">
                                <p style="margin:0; font-size:0.95rem; font-weight:700; color:#0f172a;">Order Total: {format_inr(o_value)}</p>
                                <p style="margin:0.25rem 0 0 0; font-size:0.85rem; color:#64748b;">Fulfillment: {prog_pct}%</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No orders currently logged in your history.")

        # --------------------------------------------------------
        # 🧾 MY ORDERS SUB-VIEW (CATEGORIZED INTO ACTIVE, DISPATCHED, BACKORDERED)
        # --------------------------------------------------------
        elif cust_menu == "🧾 My Orders":
            st.header("🧾 My Orders Board")
            st.write("Browse details of all past and pending orders.")
            st.divider()
            
            if c_orders.empty:
                st.info("No order history found.")
            else:
                # Add product details and calculate Order Total
                disp_c = add_product_names(c_orders, products)
                disp_c["Selling Price"] = disp_c["product_code"].apply(lambda p: format_inr(product_financials[p][1]) if p in product_financials else "₹0")
                disp_c["Order Total"] = disp_c.apply(lambda r: format_inr(r["quantity"] * product_financials[r["product_code"]][1]) if r["product_code"] in product_financials else "₹0", axis=1)
                
                # Fetch backorder records for these orders
                bo_list = get_backorders()
                bo_order_codes = bo_list[bo_list["status"] == "Open"]["order_code"].tolist() if not bo_list.empty else []
                
                # Categorization
                active_orders_df = disp_c[
                    (disp_c["status"] != "Dispatched") & 
                    (disp_c["status"] != "Backordered") & 
                    (~disp_c["order_code"].isin(bo_order_codes))
                ]
                dispatched_orders_df = disp_c[disp_c["status"] == "Dispatched"]
                backordered_orders_df = disp_c[
                    (disp_c["status"] == "Backordered") | 
                    (disp_c["order_code"].isin(bo_order_codes))
                ]
                
                tab1, tab2, tab3 = st.tabs(["⏳ Active Orders", "🚚 Dispatched Orders", "⚠️ Backordered Orders"])
                
                # Dynamic rendering helper for tabs
                def render_orders_tab(df, tab_name):
                    if df.empty:
                        st.info(f"No orders currently in {tab_name}.")
                    else:
                        # 1. Cards Layout
                        for _, row in df.iterrows():
                            o_code = row["order_code"]
                            p_code = row["product_code"]
                            qty = row["quantity"]
                            status = row["status"]
                            price = product_financials[p_code][1] if p_code in product_financials else 0.0
                            o_value = qty * price
                            
                            stages_map = ["Pending", "Allocated", "Picking", "Picked", "Packing", "Packed", "Ready for Dispatch", "Dispatched"]
                            prog_idx = stages_map.index(status) if status in stages_map else 4 if status == "QC Failed" else 0
                            prog_pct = int(((prog_idx + 1) / len(stages_map)) * 100)
                            
                            card_col1, card_col2 = st.columns([4, 1])
                            with card_col1:
                                st.markdown(f"""
                                <div class="customer-card" style="margin-bottom: 0px;">
                                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #e2e8f0; padding-bottom:0.3rem; margin-bottom:0.5rem;">
                                        <span style="font-weight:700; color:#0f172a;">🧾 Order: {o_code}</span>
                                        <span style="background-color:#f1f5f9; color:#475569; padding:0.15rem 0.4rem; border-radius:0.25rem; font-size:0.75rem; font-weight:600;">{status}</span>
                                    </div>
                                    <p style="margin:0; font-size:0.85rem; color:#475569;"><b>Product</b>: {row['product_name']} ({p_code}) | <b>Quantity</b>: {qty} units</p>
                                    <p style="margin:0.15rem 0 0 0; font-size:0.85rem; color:#475569;"><b>Selling Price</b>: {format_inr(price)} | <b>Order Total</b>: {format_inr(o_value)}</p>
                                    <p style="margin:0.15rem 0 0 0; font-size:0.8rem; color:#64748b;">Fulfillment Progress: {prog_pct}%</p>
                                </div>
                                """, unsafe_allow_html=True)
                            with card_col2:
                                st.write("")
                                st.write("")
                                if st.button("🔎 Track Details", key=f"btn_track_{o_code}", use_container_width=True):
                                    st.session_state.customer_active_order_code = o_code
                                    st.info(f"Target selected: ORD {o_code}. Navigate to 'Order Details & Tracking' to view.")
                                    st.rerun()
                            st.write("")
                            
                        # 2. Detailed Data Table
                        st.markdown("#### Detailed Reference Table")
                        st.dataframe(
                            df[[
                                "order_code", "product_code", "product_name", "quantity", 
                                "Selling Price", "Order Total", "status", "created_at"
                            ]],
                            use_container_width=True,
                            hide_index=True
                        )
                
                with tab1:
                    render_orders_tab(active_orders_df, "Active Queue")
                with tab2:
                    render_orders_tab(dispatched_orders_df, "Dispatched Queue")
                with tab3:
                    render_orders_tab(backordered_orders_df, "Backorders Queue")
                
                st.divider()
                st.subheader("🔍 Quick Order Tracking Selection")
                selected_track = st.selectbox("Select Order ID to review detailed timeline", disp_c["order_code"].tolist())
                if selected_track:
                    st.session_state.customer_active_order_code = selected_track

        # --------------------------------------------------------
        # 💳 PAYMENTS & TRANSACTIONS SUB-VIEW
        # --------------------------------------------------------
        elif cust_menu == "💳 Payments & Transactions":
            st.header("💳 My Payments & Transactions")
            st.write("Monitor order pricing details, check invoice payment status, and make mock payments.")
            st.divider()
            
            # Fetch all order transactions
            all_txns = get_order_transactions()
            cust_txns = [t for t in all_txns if t[2].upper() == cust_name_key.upper()] if all_txns else []
            
            if not cust_txns:
                st.info("No transaction records found in your payment ledger.")
            else:
                st.subheader("📋 Invoice Transaction Records")
                cust_txn_df = pd.DataFrame(cust_txns, columns=[
                    "Transaction ID", "Order Code", "Customer", "Product Code", "Quantity", 
                    "Unit Selling Price", "Subtotal", "Discount", "Tax", "Shipping Fee", 
                    "Total Amount", "Payment Method", "Payment Status", "Transaction Type", 
                    "Transaction Reference", "Created At", "Updated At"
                ])
                cust_txn_df = add_product_names(cust_txn_df, products)
                
                # Format for display (Privacy: No Unit Cost, Warehouse Cost, Profit, Profit Margin)
                disp_cust_txn = cust_txn_df.copy()
                disp_cust_txn["Total Amount"] = disp_cust_txn["Total Amount"].apply(format_inr)
                
                st.dataframe(
                    disp_cust_txn[[
                        "Transaction ID", "Order Code", "product_name", "Quantity",
                        "Total Amount", "Payment Method", "Payment Status", "Created At"
                    ]],
                    use_container_width=True,
                    hide_index=True
                )
                
                st.divider()
                st.subheader("💳 Make a Payment")
                pending_cust_txns = [t for t in cust_txns if t[12] == "Pending Payment"]
                
                if not pending_cust_txns:
                    st.success("✅ All of your registered invoices are fully paid!")
                else:
                    pay_options = {f"Order {t[1]} - Total: {format_inr(t[10])}": t[1] for t in pending_cust_txns}
                    selected_pay_order = st.selectbox("Select Pending Order to Pay Now", list(pay_options.keys()), key="cust_select_pay")
                    order_code_to_pay = pay_options[selected_pay_order]
                    
                    method = st.selectbox("Choose Payment Method", [
                        "UPI",
                        "Credit Card",
                        "Debit Card",
                        "Net Banking",
                        "Cash on Delivery"
                    ], key="cust_pay_method")
                    
                    if st.button("💳 Confirm Payment", use_container_width=True):
                        try:
                            conn = get_connection()
                            cursor = conn.cursor()
                            
                            # Check duplicate
                            cursor.execute("SELECT total_amount, payment_status FROM order_transactions WHERE order_code = ?", (order_code_to_pay,))
                            txn_row = cursor.fetchone()
                            
                            if txn_row:
                                amount, payment_status = txn_row
                                if payment_status == "Paid":
                                    st.info("ℹ️ This order is already paid.")
                                    cursor.close()
                                    conn.close()
                                    st.stop()
                                    
                                cursor.execute("""
                                    UPDATE order_transactions
                                    SET payment_status = 'Paid',
                                        payment_method = ?,
                                        transaction_type = 'Payment',
                                        transaction_reference = ?,
                                        updated_at = CURRENT_TIMESTAMP
                                    WHERE order_code = ?
                                """, (method, f"TXN-{order_code_to_pay}", order_code_to_pay))
                            else:
                                cursor.execute("SELECT customer, product_code, quantity FROM orders WHERE order_code = ?", (order_code_to_pay,))
                                ord_row = cursor.fetchone()
                                if not ord_row:
                                    raise ValueError("Order not found.")
                                customer, product_code, quantity = ord_row
                                
                                cursor.execute("SELECT selling_price FROM products WHERE product_code = ?", (product_code,))
                                p_row = cursor.fetchone()
                                price = p_row[0] if p_row else 0.0
                                
                                subtotal = quantity * price
                                discount = 0.0
                                tax = round(subtotal * 0.18, 2)
                                shipping_fee = 100.0 if subtotal < 1000.0 else 0.0
                                amount = subtotal - discount + tax + shipping_fee
                                
                                cursor.execute("""
                                    INSERT INTO order_transactions
                                    (order_code, customer, product_code, quantity, unit_selling_price, subtotal, discount, tax, shipping_fee, total_amount, payment_method, payment_status, transaction_type, transaction_reference, created_at, updated_at)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Paid', 'Payment', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                                """, (order_code_to_pay, customer, product_code, quantity, price, subtotal, discount, tax, shipping_fee, amount, method, f"TXN-{order_code_to_pay}"))
                                
                            conn.commit()
                            cursor.close()
                            conn.close()
                            
                            st.success(f"✅ Payment Successful\n\nOrder: {order_code_to_pay}\nAmount: {format_inr(amount)}\nPayment Method: {method}\nPayment Status: Paid")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error executing payment: {e}")

        # --------------------------------------------------------
        # 🔄 RETURN REQUESTS SUB-VIEW
        # --------------------------------------------------------
        elif cust_menu == "🔄 Return Requests":
            st.header("🔄 Order Returns & Restock Pipeline")
            st.write("File return requests for dispatched shipments and track returned packages.")
            st.divider()
            
            # Tab 1: Request Return, Tab 2: Track Returns
            tab_req, tab_track = st.tabs(["🔄 File a Return Request", "📦 Track My Returns"])
            
            with tab_req:
                st.subheader("➕ Request Return for Dispatched Order")
                # Find dispatched orders for this customer
                dispatched_orders = c_orders[c_orders["status"] == "Dispatched"]
                
                if dispatched_orders.empty:
                    st.info("You do not have any dispatched/delivered orders eligible for return.")
                else:
                    order_codes_list = dispatched_orders["order_code"].unique().tolist()
                    selected_order_code = st.selectbox("Select Dispatched Order ID", order_codes_list)
                    
                    # Fetch products in that order
                    order_items = dispatched_orders[dispatched_orders["order_code"] == selected_order_code]
                    product_options = {f"{row['product_code']} - {products[products['product_code'] == row['product_code']].iloc[0]['name'] if not products[products['product_code'] == row['product_code']].empty else row['product_code']}": row['product_code'] for _, row in order_items.iterrows()}
                    selected_item_str = st.selectbox("Select Product to Return", list(product_options.keys()))
                    product_code_to_return = product_options[selected_item_str]
                    
                    # Fetch purchased quantity
                    purchased_qty = int(order_items[order_items["product_code"] == product_code_to_return].iloc[0]["quantity"])
                    
                    return_qty = st.number_input("Return Quantity", min_value=1, max_value=purchased_qty, value=1, step=1)
                    
                    reason = st.selectbox("Return Reason", [
                        "Damaged Product",
                        "Wrong Product",
                        "Defective Product",
                        "Missing Parts",
                        "Product Not as Expected",
                        "Other"
                    ])
                    description = st.text_area("Return Description & Comments (Please explain details)")
                    
                    # Calculate refund amount based on order transactions total_amount and quantity
                    all_order_txns = get_order_transactions()
                    matching_txn = [t for t in all_order_txns if t[1] == selected_order_code and t[3] == product_code_to_return]
                    if matching_txn:
                        txn_total = matching_txn[0][10]
                        txn_qty = matching_txn[0][4]
                        # Proportionate refund amount
                        est_refund = round((txn_total / txn_qty) * return_qty, 2)
                    else:
                        est_refund = 0.0
                        
                    st.write(f"Estimated Refund Amount: **{format_inr(est_refund)}**")
                    
                    if st.button("🔄 REQUEST RETURN", use_container_width=True):
                        # Val 1: Return Qty
                        if return_qty > purchased_qty:
                            st.error(f"Cannot return more than the purchased quantity of {purchased_qty} units.")
                        else:
                            try:
                                create_return_order(
                                    order_code=selected_order_code,
                                    customer=cust_name_key,
                                    product_code=product_code_to_return,
                                    quantity=return_qty,
                                    reason=reason,
                                    description=description.strip(),
                                    refund_amount=est_refund
                                )
                                st.success("Return request submitted successfully! Go to 'Track My Returns' to view progress.")
                                st.rerun()
                            except ValueError as ve:
                                st.error(str(ve))
                            except Exception as e:
                                st.error(f"Failed to file return request: {e}")
                                
            with tab_track:
                st.subheader("📦 My Returns Timeline Tracking")
                all_returns = get_return_orders()
                cust_returns = [r for r in all_returns if r[2].upper() == cust_name_key.upper()] if all_returns else []
                
                if not cust_returns:
                    st.info("You have not requested any returns yet.")
                else:
                    return_track_options = {f"Return #{r[0]} - Order {r[1]} ({r[3]})": r[0] for r in cust_returns}
                    selected_track_return = st.selectbox("Select Return to Track", list(return_track_options.keys()))
                    
                    ret_data = [r for r in cust_returns if r[0] == selected_track_return][0]
                    ret_id, order_code, customer, product_code, quantity, reason, description, status, rej_reason, inspect_cond, refund_amt, req_at, upd_at = ret_data
                    
                    p_name = products[products["product_code"] == product_code].iloc[0]["name"] if not products[products["product_code"] == product_code].empty else product_code
                    
                    st.markdown(f"### Return #{ret_id} Tracking Console")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"• **Order Code**: `{order_code}`")
                        st.write(f"• **Product**: `{p_name}`")
                        st.write(f"• **Quantity**: `{quantity}`")
                        st.write(f"• **Return Reason**: `{reason}`")
                    with c2:
                        st.write(f"• **Refund Status**: `Refund Pending` (if Approved) or `Refunded` (if Refund complete)")
                        st.write(f"• **Refund Amount**: `{format_inr(refund_amt)}`")
                        if inspect_cond:
                            st.write(f"• **Inspection Condition**: `{inspect_cond}`")
                        if rej_reason:
                            st.error(f"• **Rejection Reason**: {rej_reason}")
                            
                    st.divider()
                    
                    # Return tracking timeline
                    st.markdown("#### Return Progress Timeline")
                    
                    # Timeline list: Requested, Approved, Pickup Scheduled, Received, Under Inspection, Approved for Refund, Refunded, Restocked
                    stages = ["Requested", "Approved", "Pickup Scheduled", "Received", "Under Inspection", "Approved for Refund", "Refunded"]
                    labels = {
                        "Requested": "🔄 Return Requested",
                        "Approved": "✅ Approved",
                        "Pickup Scheduled": "🚚 Pickup",
                        "Received": "📦 Received",
                        "Under Inspection": "🔍 Inspection",
                        "Approved for Refund": "💰 Refund Approved",
                        "Refunded": "💰 Refund Processed"
                    }
                    
                    # Determine current timeline stage
                    curr_idx = 0
                    if status == "Requested":
                        curr_idx = 0
                    elif status == "Rejected":
                        curr_idx = -1
                    elif status == "Pickup Scheduled":
                        curr_idx = 2
                    elif status == "Received":
                        curr_idx = 3
                    elif status == "Under Inspection":
                        curr_idx = 4
                    elif status == "Approved for Refund":
                        curr_idx = 5
                    elif status in ["Refunded", "Restocked", "Closed"]:
                        curr_idx = 6
                        
                    if curr_idx == -1:
                        st.error("❌ Return Request Rejected.")
                    else:
                        progress_pct = (curr_idx + 1) / len(stages)
                        st.progress(progress_pct)
                        st.write(f"📈 **Timeline Status**: {int(progress_pct*100)}%")
                        
                        for i, stg in enumerate(stages):
                            if i < curr_idx:
                                st.success(f"✅ {labels[stg]} — Completed")
                            elif i == curr_idx:
                                st.warning(f"🔄 {labels[stg]} — In Progress")
                            else:
                                st.info(f"⏳ {labels[stg]} — Pending Stage")
                                
                        if status == "Restocked":
                            st.success("📦 Restocked — Product restocked into warehouse inventory")

        # --------------------------------------------------------
        # 📦 ORDER DETAILS & TRACKING SUB-VIEW
        # --------------------------------------------------------
        elif cust_menu == "📦 Order Details & Tracking":
            st.header("📦 Order Details & Fulfillment Tracking")
            st.write("Review chronological milestones, friendly notices, and shipping departure logs.")
            st.divider()
            
            # Select Active Order
            active_list = c_orders["order_code"].tolist()
            if not active_list:
                st.info("No orders registered.")
            else:
                default_idx = 0
                if st.session_state.customer_active_order_code in active_list:
                    default_idx = active_list.index(st.session_state.customer_active_order_code)
                    
                selected_ord_code = st.selectbox("Select Order to View Track Details", active_list, index=default_idx)
                
                # Fetch fresh values from database for the active order code
                active_ord_df = get_customer_order_db(selected_ord_code, cust_name_key)
                if active_ord_df.empty:
                    st.error("❌ Order could not be accessed.")
                else:
                    active_ord = active_ord_df.iloc[0]
                    
                    # Order properties
                    p_code = active_ord["product_code"]
                    qty = active_ord["quantity"]
                    status = active_ord["status"]
                    price = product_financials[p_code][1] if p_code in product_financials else 0.0
                    p_name = products[products["product_code"] == p_code].iloc[0]["name"] if not products[products["product_code"] == p_code].empty else p_code
                    
                    # Details Header
                    st.subheader("🧾 Customer Order Verification Card")
                    cs1, cs2, cs3 = st.columns(3)
                    cs1.markdown(f"**Order ID**: `{selected_ord_code}`")
                    cs2.markdown(f"**Customer Name**: `{active_ord['customer']}`")
                    cs3.markdown(f"**Order Date**: `{active_ord['created_at']}`")
                    
                    cs4, cs5, cs6 = st.columns(3)
                    cs4.markdown(f"**Product Requested**: `{p_name} ({p_code})`")
                    cs5.markdown(f"**Quantity**: `{qty} units`")
                    cs6.markdown(f"**Unit Price**: `{format_inr(price)}`")
                    
                    # Calculated Order Total
                    o_total = qty * price
                    st.markdown(f"**💵 Order Total**: `{format_inr(o_total)}`")
                    
                    # Retrieve packing status dynamically
                    conn = get_connection()
                    cursor = conn.cursor()
                    try:
                        cursor.execute("SELECT status FROM packing_operations WHERE order_code = ?", (selected_ord_code,))
                        po_row = cursor.fetchone()
                        packing_status = po_row[0] if po_row else ("Pending" if status in ["Pending", "Allocated", "Picking", "Picked"] else "Completed")
                    except Exception:
                        packing_status = "Pending"
                    conn.close()
                    
                    # Derive quality check and dispatch statuses
                    qc_status = "In Progress" if status == "Packed" else "Failed" if status == "QC Failed" else "Passed" if status in ["Ready for Dispatch", "Dispatched"] else "Pending"
                    disp_status = "Dispatched" if status == "Dispatched" else "Ready for Dispatch" if status == "Ready for Dispatch" else "Pending"
                    
                    st.markdown("#### 📋 Order Lifecycle Status")
                    ls1, ls2, ls3, ls4 = st.columns(4)
                    ls1.markdown(f"**Order Status**: `{status}`")
                    ls2.markdown(f"**Packing Status**: `{packing_status}`")
                    ls3.markdown(f"**Quality Check**: `{qc_status}`")
                    ls4.markdown(f"**Dispatch Status**: `{disp_status}`")
                    
                    st.divider()
                    
                    # Progress timeline stages
                    stages = [
                        "Pending",
                        "Allocated",
                        "Picking",
                        "Packing",
                        "Quality Check",
                        "Ready for Dispatch",
                        "Dispatched"
                    ]
                    
                    stage_labels = {
                        "Pending": "🛒 Order Created",
                        "Allocated": "📦 Inventory Allocated",
                        "Picking": "👷 Picking",
                        "Packing": "📦 Packing",
                        "Quality Check": "🔍 Quality Check",
                        "Ready for Dispatch": "🚚 Ready for Dispatch",
                        "Dispatched": "🚚 Dispatched"
                    }
                    
                    if status in ["Pending", "Backordered"]:
                        curr_idx = 0
                    elif status == "Allocated":
                        curr_idx = 1
                    elif status in ["Picking", "Picked"]:
                        curr_idx = 2
                    elif status in ["Packing", "Packed"]:
                        curr_idx = 3
                    elif status == "QC Failed":
                        curr_idx = 4
                    elif status == "Ready for Dispatch":
                        curr_idx = 5
                    elif status == "Dispatched":
                        curr_idx = 6
                    else:
                        curr_idx = 0
                        
                    progress_pct = (curr_idx + 1) / len(stages)
                    st.progress(progress_pct)
                    st.write(f"📈 **Fulfillment Progress**: {int(progress_pct * 100)}%")
                    
                    st.write("#### Fulfillment Timeline Progress Checkpoints")
                    for i, stage in enumerate(stages):
                        if i < curr_idx:
                            st.success(f"✅ {stage_labels.get(stage, '📦')} — Completed")
                        elif i == curr_idx:
                            if status == "QC Failed":
                                st.error(f"❌ {stage_labels.get(stage, '📦')} — Inspection Failed (Warning Delay)")
                            else:
                                st.warning(f"🔄 {stage_labels.get(stage, '📦')} — In Progress")
                        else:
                            st.info(f"⏳ {stage_labels.get(stage, '📦')} — Pending Stage")
                            
                    st.divider()
                    
                    # Customer-friendly status notices
                    st.subheader("📢 Order Status Notice")
                    if status in ["Pending", "Backordered"]:
                        st.info("🟡 Your order has been received and is waiting for processing.")
                    elif status == "Allocated":
                        st.info("📦 Your order has been allocated stocks and is waiting in the picking queue.")
                    elif status == "Picking":
                        st.info("👷 Your order is currently being picked from the warehouse.")
                    elif status in ["Picked", "Packing"]:
                        st.info("📦 Your order has been picked and is currently undergoing packaging.")
                    elif status == "Packed":
                        st.info("📦 Your order has been packed.")
                    elif status == "QC Failed":
                        st.info("🔍 Your order is undergoing final quality inspection.")
                    elif status == "Ready for Dispatch":
                        st.success("🚚 Your order is ready for dispatch.")
                    elif status == "Dispatched":
                        st.success("🎉 Your order has been dispatched successfully.")
                        
                    # Backorder & Shortage check (customer-safe)
                    allocs = get_allocations()
                    if not allocs.empty:
                        order_alloc = allocs[allocs["order_code"] == selected_ord_code]
                        if not order_alloc.empty:
                            alloc_row = order_alloc.iloc[0]
                            shortage_qty = int(alloc_row["shortage_quantity"])
                            
                            if shortage_qty > 0:
                                st.warning(f"### ⚠️ Partial Fulfillment Notice")
                                st.write("Some items are currently unavailable. The remaining quantity has been placed on backorder.")
                                
                                sa1, sa2, sa3 = st.columns(3)
                                sa1.metric("Requested Quantity", int(alloc_row["requested_quantity"]))
                                sa2.metric("Allocated Quantity", int(alloc_row["allocated_quantity"]))
                                sa3.metric("Remaining Quantity (Backordered)", shortage_qty)
                                
                                bo_list = get_backorders()
                                if not bo_list.empty:
                                    order_bo = bo_list[bo_list["order_code"] == selected_ord_code]
                                    if not order_bo.empty:
                                        bo_status = order_bo.iloc[0]["status"]
                                        # Customer friendly status mapping
                                        cust_bo_status = "Awaiting Replenishment" if bo_status == "Open" else "Processing" if bo_status in ["Replenishment Pending", "Processing"] else "Fulfilled"
                                        
                                        st.write(f"• **Backorder Status**: `{cust_bo_status}`")
                                        st.write(f"• **Backordered Quantity**: `{shortage_qty} units`")
                                        
                    # Dispatch Status Notice
                    if status == "Dispatched":
                        st.success("### 🚚 Dispatch Departure Clearance")
                        st.write("Your order has been dispatched successfully.")
                        
                        # Real tracking number check (if database order has tracking data, otherwise show simple message)
                        # The SQLite database does not contain a tracking_number column, so we show the required template:
                        st.info("ℹ️ Tracking information will be available after dispatch.")
                        
                    # Exception delay warnings
                    exc_records = get_exceptions()
                    order_exc = [e for e in exc_records if e[1] == selected_ord_code]
                    if order_exc:
                        st.subheader("🔔 Operations Updates")
                        open_exc = [e for e in order_exc if e[5] in ["Open", "In Progress"]]
                        if open_exc:
                            st.error("⚠️ There is a delay with your order. Our warehouse team is working to resolve it.")
                        else:
                            st.success("✅ The issue affecting your order has been resolved.")