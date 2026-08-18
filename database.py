import sqlite3


DATABASE_NAME = "warehouse.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE_NAME)


# ============================================================
# CREATE TABLES AND MIGRATE
# ============================================================

def create_tables():

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # PRODUCTS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_code TEXT UNIQUE,
            name TEXT NOT NULL,
            category TEXT,
            location TEXT,
            total_stock INTEGER DEFAULT 0,
            reserved_stock INTEGER DEFAULT 0,
            damaged_stock INTEGER DEFAULT 0,
            reorder_level INTEGER DEFAULT 10,
            reorder_quantity INTEGER DEFAULT 20,
            unit_cost REAL DEFAULT 0.0,
            selling_price REAL DEFAULT 0.0
        )
    """)

    # --------------------------------------------------------
    # ORDERS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_code TEXT UNIQUE,
            customer TEXT,
            product_code TEXT,
            quantity INTEGER,
            priority TEXT,
            priority_score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # PICKING TASKS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS picking_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_code TEXT,
            product_code TEXT,
            quantity INTEGER,
            location TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # EXCEPTIONS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exceptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_code TEXT,
            exception_type TEXT,
            description TEXT,
            recommendation TEXT,
            status TEXT DEFAULT 'Open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # ALLOCATIONS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_code TEXT,
            product_code TEXT,
            requested_quantity INTEGER,
            allocated_quantity INTEGER,
            shortage_quantity INTEGER,
            decision TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # BACKORDERS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backorders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_code TEXT,
            product_code TEXT,
            quantity INTEGER,
            status TEXT DEFAULT 'Open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # PACKING OPERATIONS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS packing_operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_code TEXT UNIQUE,
            packaging_type TEXT,
            packaging_cost REAL,
            handling_cost REAL,
            total_cost REAL,
            status TEXT DEFAULT 'Pending',
            packed_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            packed_at TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # SCHEMA MIGRATIONS (SAFE COLUMNS MIGRATION)
    # --------------------------------------------------------

    # Add unit_cost to products if missing
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN unit_cost REAL DEFAULT 0.0")
    except sqlite3.OperationalError:
        pass

    # Add selling_price to products if missing
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN selling_price REAL DEFAULT 0.0")
    except sqlite3.OperationalError:
        pass

    # Add created_at to orders if missing
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN created_at TIMESTAMP")
        cursor.execute("UPDATE orders SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    except sqlite3.OperationalError:
        pass

    # Add created_at to picking_tasks if missing
    try:
        cursor.execute("ALTER TABLE picking_tasks ADD COLUMN created_at TIMESTAMP")
        cursor.execute("UPDATE picking_tasks SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    except sqlite3.OperationalError:
        pass

    # Add created_at to exceptions if missing
    try:
        cursor.execute("ALTER TABLE exceptions ADD COLUMN created_at TIMESTAMP")
        cursor.execute("UPDATE exceptions SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    except sqlite3.OperationalError:
        pass

    # --------------------------------------------------------
    # INVENTORY TRANSACTIONS
    # --------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_code TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            previous_stock INTEGER,
            new_stock INTEGER,
            reference TEXT,
            reason TEXT,
            performed_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # ORDER TRANSACTIONS
    # --------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_code TEXT UNIQUE NOT NULL,
            customer TEXT,
            product_code TEXT,
            quantity INTEGER,
            unit_selling_price REAL,
            subtotal REAL,
            discount REAL DEFAULT 0.0,
            tax REAL DEFAULT 0.0,
            shipping_fee REAL DEFAULT 0.0,
            total_amount REAL,
            payment_method TEXT,
            payment_status TEXT DEFAULT 'Pending Payment',
            transaction_type TEXT,
            transaction_reference TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # RETURN ORDERS
    # --------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS return_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_code TEXT NOT NULL,
            customer TEXT NOT NULL,
            product_code TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            reason TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Requested',
            rejection_reason TEXT,
            inspection_condition TEXT,
            refund_amount REAL DEFAULT 0.0,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # SEED MISSING FINANCIAL TRANSACTIONS FOR EXISTING ORDERS
    # --------------------------------------------------------
    try:
        cursor.execute("SELECT order_code, customer, product_code, quantity, status, created_at FROM orders")
        existing_orders = cursor.fetchall()
        for row in existing_orders:
            o_code, customer, p_code, qty, status, created_at = row
            cursor.execute("SELECT COUNT(*) FROM order_transactions WHERE order_code = ?", (o_code,))
            if cursor.fetchone()[0] == 0:
                # Fetch product price
                cursor.execute("SELECT selling_price FROM products WHERE product_code = ?", (p_code,))
                p_row = cursor.fetchone()
                price = p_row[0] if p_row else 0.0
                
                subtotal = qty * price
                discount = 0.0
                tax = round(subtotal * 0.18, 2)
                shipping_fee = 100.0 if subtotal < 1000.0 else 0.0
                total_amount = subtotal - discount + tax + shipping_fee
                
                # Determine statuses based on current order status
                p_status = 'Pending Payment' if status in ['Pending', 'Backordered'] else 'Paid'
                p_method = 'UPI' if p_status == 'Paid' else 'Cash on Delivery'
                t_type = 'DEBIT' if p_status == 'Paid' else 'PENDING'
                
                cursor.execute("""
                    INSERT INTO order_transactions
                    (order_code, customer, product_code, quantity, unit_selling_price, subtotal, discount, tax, shipping_fee, total_amount, payment_method, payment_status, transaction_type, transaction_reference, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (o_code, customer, p_code, qty, price, subtotal, discount, tax, shipping_fee, total_amount, p_method, p_status, t_type, f"TXN-{o_code}", created_at, created_at))
    except Exception as e:
        print(f"Error migrating order transactions: {e}")

    connection.commit()
    connection.close()


# ============================================================
# SAMPLE DATA
# ============================================================

def add_sample_data():

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # PRODUCTS (EXPANDED TO 30 PRODUCTS WITH FINANCIALS & REAL STOCK MARGINS)
    # --------------------------------------------------------

    products = [
        ("P001", "Wireless Mouse", "Electronics", "A-01-03", 100, 20, 5, 25, 50, 400.0, 650.0),
        ("P002", "Keyboard", "Electronics", "A-01-05", 50, 15, 2, 15, 30, 800.0, 1200.0),
        ("P003", "USB Cable", "Accessories", "B-02-01", 30, 20, 3, 10, 25, 150.0, 300.0),
        ("P004", "Laptop", "Electronics", "C-01-01", 15, 0, 0, 10, 20, 45000.0, 55000.0),
        ("P005", "Headphones", "Audio", "B-03-02", 5, 2, 1, 8, 15, 1000.0, 1800.0),
        ("P006", "Smart Watch", "Wearables", "A-01-01", 6, 0, 0, 8, 15, 2500.0, 3999.0),
        ("P007", "Bluetooth Speaker", "Audio", "A-01-02", 45, 5, 1, 10, 20, 1500.0, 2499.0),
        ("P008", "Power Bank", "Accessories", "A-01-04", 80, 10, 2, 15, 30, 900.0, 1499.0),
        ("P009", "Smartphone", "Electronics", "B-01-01", 0, 0, 0, 5, 10, 18000.0, 22999.0),
        ("P010", "Tablet", "Electronics", "B-01-02", 25, 2, 0, 5, 10, 15000.0, 19999.0),
        ("P011", "Webcam", "Electronics", "B-01-03", 40, 4, 1, 8, 15, 1200.0, 1999.0),
        ("P012", "Gaming Mouse", "Gaming", "B-01-04", 60, 8, 2, 12, 25, 1000.0, 1799.0),
        ("P013", "Gaming Keyboard", "Gaming", "B-01-05", 35, 5, 0, 8, 15, 2000.0, 3499.0),
        ("P014", "T-Shirt", "Clothing", "C-01-02", 200, 20, 5, 15, 50, 400.0, 799.0),
        ("P015", "Jeans", "Clothing", "C-01-03", 120, 10, 2, 10, 25, 900.0, 1599.0),
        ("P016", "Backpack", "Bags", "C-01-04", 75, 6, 1, 10, 20, 700.0, 1299.0),
        ("P017", "Running Shoes", "Footwear", "C-01-05", 55, 5, 1, 8, 15, 1500.0, 2499.0),
        ("P018", "Water Bottle", "Home & Lifestyle", "A-01-01", 110, 10, 0, 15, 30, 250.0, 499.0),
        ("P019", "LED Bulb", "Home & Electrical", "A-01-02", 150, 0, 3, 20, 50, 120.0, 249.0),
        ("P020", "Calculator", "Stationery", "A-01-03", 90, 5, 1, 10, 20, 200.0, 399.0),
        ("P021", "Notebook", "Stationery", "A-01-04", 300, 0, 0, 30, 100, 60.0, 120.0),
        ("P022", "Pen Pack", "Stationery", "A-01-05", 500, 20, 0, 50, 150, 50.0, 100.0),
        ("P023", "Desk Lamp", "Home & Electrical", "B-01-01", 65, 5, 2, 10, 20, 500.0, 899.0),
        ("P024", "Earbuds", "Audio", "B-01-02", 85, 8, 1, 12, 25, 1200.0, 1999.0),
        ("P025", "Smartphone Charger", "Accessories", "B-01-03", 120, 15, 4, 15, 30, 350.0, 699.0),
        ("P026", "HDMI Cable", "Accessories", "B-01-04", 140, 10, 2, 10, 25, 250.0, 499.0),
        ("P027", "SSD 1TB", "Computer Hardware", "B-01-05", 45, 4, 0, 5, 10, 5000.0, 6999.0),
        ("P028", "RAM 16GB", "Computer Hardware", "C-01-01", 60, 6, 1, 8, 15, 3500.0, 4999.0),
        ("P029", "Monitor", "Computer Hardware", "C-01-02", 0, 0, 0, 2, 5, 8000.0, 11999.0),
        ("P030", "Printer", "Office Equipment", "C-01-03", 12, 2, 0, 3, 5, 9000.0, 12999.0)
    ]

    for product in products:

        cursor.execute("""
            INSERT OR IGNORE INTO products
            (
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
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, product)

    # Force update details for all 30 products to ensure costs/prices/categories are seeded correctly on existing DB
    for product in products:
        p_code = product[0]
        name = product[1]
        cat = product[2]
        loc = product[3]
        tot = product[4]
        res = product[5]
        dmg = product[6]
        lvl = product[7]
        qty = product[8]
        cost = product[9]
        price = product[10]
        
        cursor.execute("""
            UPDATE products
            SET name = ?,
                category = ?,
                location = ?,
                unit_cost = ?,
                selling_price = ?,
                reorder_level = ?,
                reorder_quantity = ?
            WHERE product_code = ?
        """, (name, cat, loc, cost, price, lvl, qty, p_code))
        
        cursor.execute("""
            UPDATE products
            SET total_stock = ?,
                reserved_stock = ?,
                damaged_stock = ?
            WHERE product_code = ? AND total_stock = 0 AND reserved_stock = 0 AND damaged_stock = 0 AND product_code != 'P009' AND product_code != 'P029'
        """, (tot, res, dmg, p_code))

    # --------------------------------------------------------
    # ORDERS
    # --------------------------------------------------------

    orders = [

        (
            "ORD001",
            "ABC Technologies",
            "P004",
            10,
            "Critical",
            95,
            "Pending"
        ),

        (
            "ORD002",
            "Retail Store",
            "P001",
            15,
            "High",
            78,
            "Pending"
        ),

        (
            "ORD003",
            "College Store",
            "P002",
            5,
            "Medium",
            55,
            "Picking"
        ),

        (
            "ORD004",
            "Online Customer",
            "P003",
            8,
            "Low",
            30,
            "Packed"
        )
    ]

    for order in orders:

        cursor.execute("""
            INSERT OR IGNORE INTO orders
            (
                order_code,
                customer,
                product_code,
                quantity,
                priority,
                priority_score,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, order)

    # Seed matching picking task for ORD003 (status: Picking) and ORD004 (status: Picked)
    cursor.execute("SELECT COUNT(*) FROM picking_tasks")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO picking_tasks (order_code, product_code, quantity, location, status)
            VALUES ('ORD003', 'P002', 5, 'A-01-05', 'Picking')
        """)
        cursor.execute("""
            INSERT INTO picking_tasks (order_code, product_code, quantity, location, status)
            VALUES ('ORD004', 'P003', 8, 'B-02-01', 'Picked')
        """)

    # Seed matching packing operation for ORD004 (status: Packed)
    cursor.execute("SELECT COUNT(*) FROM packing_operations")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT OR IGNORE INTO packing_operations (order_code, packaging_type, packaging_cost, handling_cost, total_cost, status, packed_by, packed_at)
            VALUES ('ORD004', 'Medium Box', 35.0, 10.0, 45.0, 'Packed', 'System', CURRENT_TIMESTAMP)
        """)

    connection.commit()
    connection.close()


# ============================================================
# GENERATE ORDER CODE
# ============================================================

def generate_order_code():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT MAX(id) FROM orders
    """)
    val = cursor.fetchone()[0]
    count = val if val is not None else 0

    connection.close()

    return f"ORD{count + 1:03d}"


# ============================================================
# CREATE NEW ORDER
# ============================================================

def create_order(
    customer,
    product_code,
    quantity,
    priority,
    priority_score
):

    connection = get_connection()
    cursor = connection.cursor()

    order_code = generate_order_code()

    cursor.execute("""
        INSERT INTO orders
        (
            order_code,
            customer,
            product_code,
            quantity,
            priority,
            priority_score,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        order_code,
        customer,
        product_code,
        quantity,
        priority,
        priority_score,
        "Pending"
    ))

    # Fetch product price to calculate order value
    cursor.execute("SELECT selling_price FROM products WHERE product_code = ?", (product_code,))
    p_row = cursor.fetchone()
    price = p_row[0] if p_row else 0.0
    
    subtotal = quantity * price
    discount = 0.0
    tax = round(subtotal * 0.18, 2)
    shipping_fee = 100.0 if subtotal < 1000.0 else 0.0
    total_amount = subtotal - discount + tax + shipping_fee
    
    cursor.execute("""
        INSERT INTO order_transactions
        (order_code, customer, product_code, quantity, unit_selling_price, subtotal, discount, tax, shipping_fee, total_amount, payment_method, payment_status, transaction_type, transaction_reference, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Cash on Delivery', 'Pending Payment', 'PENDING', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (order_code, customer, product_code, quantity, price, subtotal, discount, tax, shipping_fee, total_amount, f"TXN-{order_code}"))

    connection.commit()
    connection.close()

    return order_code


# ============================================================
# SAVE ALLOCATION
# ============================================================

def save_allocation(
    order_code,
    product_code,
    requested_quantity,
    allocated_quantity,
    shortage_quantity,
    decision
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO allocations
        (
            order_code,
            product_code,
            requested_quantity,
            allocated_quantity,
            shortage_quantity,
            decision
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        order_code,
        product_code,
        requested_quantity,
        allocated_quantity,
        shortage_quantity,
        decision
    ))

    connection.commit()
    connection.close()


# ============================================================
# SMART ALLOCATION
# ============================================================

def execute_allocation(
    order_code,
    product_code,
    requested_quantity,
    allocated_quantity,
    shortage_quantity,
    decision
):

    connection = get_connection()
    cursor = connection.cursor()

    # Prevent duplicate allocation for the same order
    cursor.execute("SELECT COUNT(*) FROM allocations WHERE order_code = ?", (order_code,))
    if cursor.fetchone()[0] > 0:
        connection.close()
        raise ValueError(f"Allocation already executed for order {order_code}")

    # Fetch product warehouse location
    cursor.execute("SELECT location FROM products WHERE product_code = ?", (product_code,))
    row = cursor.fetchone()
    location = row[0] if row else "Unknown"

    # --------------------------------------------------------
    # UPDATE RESERVED STOCK
    # --------------------------------------------------------

    cursor.execute("""
        UPDATE products
        SET reserved_stock = reserved_stock + ?
        WHERE product_code = ?
    """, (
        allocated_quantity,
        product_code
    ))

    # Log reservation transaction
    if allocated_quantity > 0:
        cursor.execute("SELECT total_stock FROM products WHERE product_code = ?", (product_code,))
        tot_row = cursor.fetchone()
        tot = tot_row[0] if tot_row else 0
        cursor.execute("""
            INSERT INTO inventory_transactions (product_code, transaction_type, quantity, previous_stock, new_stock, reference, reason, performed_by)
            VALUES (?, 'RESERVATION', ?, ?, ?, ?, 'Stock Allocated to Order', 'System')
        """, (product_code, allocated_quantity, tot, tot, order_code))

    # --------------------------------------------------------
    # UPDATE ORDER STATUS
    # --------------------------------------------------------

    if allocated_quantity > 0:
        new_status = "Allocated"
    else:
        new_status = "Pending"

    cursor.execute("""
        UPDATE orders
        SET status = ?
        WHERE order_code = ?
    """, (
        new_status,
        order_code
    ))

    # --------------------------------------------------------
    # SAVE ALLOCATION RECORD
    # --------------------------------------------------------

    cursor.execute("""
        INSERT INTO allocations
        (
            order_code,
            product_code,
            requested_quantity,
            allocated_quantity,
            shortage_quantity,
            decision
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        order_code,
        product_code,
        requested_quantity,
        allocated_quantity,
        shortage_quantity,
        decision
    ))

    # --------------------------------------------------------
    # CREATE PICKING TASK FOR ALLOCATED QUANTITY
    # --------------------------------------------------------
    if allocated_quantity > 0:
        cursor.execute("""
            INSERT INTO picking_tasks (order_code, product_code, quantity, location, status, created_at)
            VALUES (?, ?, ?, ?, 'Pending', CURRENT_TIMESTAMP)
        """, (order_code, product_code, allocated_quantity, location))

    # --------------------------------------------------------
    # CREATE BACKORDER FOR SHORTAGE
    # --------------------------------------------------------

    if shortage_quantity > 0:

        cursor.execute("""
            INSERT INTO backorders
            (
                order_code,
                product_code,
                quantity,
                status
            )
            VALUES (?, ?, ?, ?)
        """, (
            order_code,
            product_code,
            shortage_quantity,
            "Open"
        ))

    connection.commit()
    connection.close()

    return {
        "order_code": order_code,
        "allocated": allocated_quantity,
        "shortage": shortage_quantity,
        "decision": decision,
        "status": new_status
    }


# ============================================================
# UPDATE ORDER STATUS
# ============================================================

def update_order_status(
    order_code,
    new_status
):

    connection = get_connection()
    cursor = connection.cursor()

    # Get old status first to prevent double-dispatch actions
    cursor.execute("SELECT status FROM orders WHERE order_code = ?", (order_code,))
    old_row = cursor.fetchone()
    old_status = old_row[0] if old_row else None

    cursor.execute("""
        UPDATE orders
        SET status = ?
        WHERE order_code = ?
    """, (
        new_status,
        order_code
    ))

    # Sync picking tasks status if relevant
    if new_status == "Picking":
        cursor.execute("UPDATE picking_tasks SET status = 'Picking' WHERE order_code = ?", (order_code,))
    elif new_status == "Packed":
        cursor.execute("UPDATE picking_tasks SET status = 'Packed' WHERE order_code = ?", (order_code,))
    elif new_status == "Dispatched":
        cursor.execute("UPDATE picking_tasks SET status = 'Completed' WHERE order_code = ?", (order_code,))

    # If dispatched, decrease total_stock and reserved_stock
    if old_status != "Dispatched" and new_status == "Dispatched":
        cursor.execute("SELECT allocated_quantity, product_code FROM allocations WHERE order_code = ?", (order_code,))
        alloc = cursor.fetchone()
        if alloc:
            allocated_quantity, product_code = alloc
            cursor.execute("SELECT total_stock, reserved_stock FROM products WHERE product_code = ?", (product_code,))
            p_row = cursor.fetchone()
            if p_row:
                total_stock, reserved_stock = p_row
                new_total = max(0, total_stock - allocated_quantity)
                new_reserved = max(0, reserved_stock - allocated_quantity)
                cursor.execute("""
                    UPDATE products
                    SET total_stock = ?, reserved_stock = ?
                    WHERE product_code = ?
                """, (new_total, new_reserved, product_code))
                
                # Log RELEASE transaction
                cursor.execute("""
                    INSERT INTO inventory_transactions
                    (product_code, transaction_type, quantity, previous_stock, new_stock, reference, reason, performed_by)
                    VALUES (?, 'RELEASE', ?, ?, ?, ?, 'Order Dispatched', 'System')
                """, (product_code, allocated_quantity, total_stock, new_total, order_code))

    connection.commit()
    connection.close()


# ============================================================
# CREATE EXCEPTION
# ============================================================

def create_exception(
    order_code,
    exception_type,
    description,
    recommendation
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO exceptions
        (
            order_code,
            exception_type,
            description,
            recommendation,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        order_code,
        exception_type,
        description,
        recommendation,
        "Open"
    ))

    connection.commit()
    connection.close()


# ============================================================
# GET EXCEPTIONS
# ============================================================

def get_exceptions():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            order_code,
            exception_type,
            description,
            recommendation,
            status,
            created_at
        FROM exceptions
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


# ============================================================
# CLOSE EXCEPTION
# ============================================================

def close_exception(
    exception_id
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE exceptions
        SET status = 'Closed'
        WHERE id = ?
    """, (
        exception_id
    ))

    connection.commit()
    connection.close()


# ============================================================
# UPDATE EXCEPTION STATUS
# ============================================================

def update_exception_status(exception_id, status):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE exceptions
        SET status = ?
        WHERE id = ?
    """, (
        status,
        exception_id
    ))

    connection.commit()
    connection.close()


# ============================================================
# GET BACKORDERS
# ============================================================

def get_backorders():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            order_code,
            product_code,
            quantity,
            status,
            created_at
        FROM backorders
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


# ============================================================
# UPDATE BACKORDER STATUS
# ============================================================

def update_backorder_status(backorder_id, status):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE backorders
        SET status = ?
        WHERE id = ?
    """, (
        status,
        backorder_id
    ))

    connection.commit()
    connection.close()


# ============================================================
# FULFILL BACKORDER
# ============================================================

def fulfill_backorder_db(backorder_id, quantity_to_fulfill):
    connection = get_connection()
    cursor = connection.cursor()

    # Fetch backorder details
    cursor.execute("SELECT order_code, product_code, quantity FROM backorders WHERE id = ?", (backorder_id,))
    backorder = cursor.fetchone()
    if not backorder:
        connection.close()
        raise ValueError("Backorder not found.")

    order_code, product_code, shortage_qty = backorder

    # Check product availability
    cursor.execute("SELECT total_stock, reserved_stock, damaged_stock, location FROM products WHERE product_code = ?", (product_code,))
    prod = cursor.fetchone()
    if not prod:
        connection.close()
        raise ValueError("Product not found.")

    total_stock, reserved_stock, damaged_stock, location = prod
    available_stock = max(0, total_stock - reserved_stock - damaged_stock)

    allocated = min(available_stock, shortage_qty, quantity_to_fulfill)
    if allocated <= 0:
        connection.close()
        raise ValueError("No available stock to fulfill this backorder.")

    # Update reserved stock
    cursor.execute("""
        UPDATE products
        SET reserved_stock = reserved_stock + ?
        WHERE product_code = ?
    """, (allocated, product_code))

    # Log reservation transaction
    if allocated > 0:
        cursor.execute("SELECT total_stock FROM products WHERE product_code = ?", (product_code,))
        tot_row = cursor.fetchone()
        tot = tot_row[0] if tot_row else 0
        cursor.execute("""
            INSERT INTO inventory_transactions (product_code, transaction_type, quantity, previous_stock, new_stock, reference, reason, performed_by)
            VALUES (?, 'RESERVATION', ?, ?, ?, ?, 'Backorder Stock Allocated', 'System')
        """, (product_code, allocated, tot, tot, order_code))

    # Create picking task for allocated quantity
    cursor.execute("""
        INSERT INTO picking_tasks (order_code, product_code, quantity, location, status, created_at)
        VALUES (?, ?, ?, ?, 'Pending', CURRENT_TIMESTAMP)
    """, (order_code, product_code, allocated, location))

    # Update backorder quantity
    new_shortage = shortage_qty - allocated
    if new_shortage <= 0:
        cursor.execute("UPDATE backorders SET quantity = 0, status = 'Fulfilled' WHERE id = ?", (backorder_id,))
    else:
        cursor.execute("UPDATE backorders SET quantity = ? WHERE id = ?", (new_shortage, backorder_id))

    # Check if the parent order is currently Pending, and update it to Allocated
    cursor.execute("SELECT status FROM orders WHERE order_code = ?", (order_code,))
    order_status_row = cursor.fetchone()
    if order_status_row and order_status_row[0] in ["Pending", "Backordered"]:
        cursor.execute("UPDATE orders SET status = 'Allocated' WHERE order_code = ?", (order_code,))

    connection.commit()
    connection.close()
    return allocated


# ============================================================
# PICKING TASK HELPERS
# ============================================================

def create_picking_task(order_code, product_code, quantity, location):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO picking_tasks (order_code, product_code, quantity, location, status, created_at)
        VALUES (?, ?, ?, ?, 'Pending', CURRENT_TIMESTAMP)
    """, (order_code, product_code, quantity, location))

    connection.commit()
    connection.close()


def get_picking_tasks(order_code=None, status=None):
    connection = get_connection()
    cursor = connection.cursor()

    query = "SELECT id, order_code, product_code, quantity, location, status, created_at FROM picking_tasks"
    params = []
    conditions = []

    if order_code:
        conditions.append("order_code = ?")
        params.append(order_code)
    if status:
        conditions.append("status = ?")
        params.append(status)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY id DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    connection.close()

    return rows


def update_picking_task_status(task_id, status):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE picking_tasks
        SET status = ?
        WHERE id = ?
    """, (status, task_id))

    # Sync order status based on picking task progress
    cursor.execute("SELECT order_code FROM picking_tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if row:
        order_code = row[0]
        if status == "Picked":
            cursor.execute("UPDATE orders SET status = 'Picked' WHERE order_code = ?", (order_code,))
        elif status == "Picking":
            cursor.execute("UPDATE orders SET status = 'Picking' WHERE order_code = ?", (order_code,))
        elif status == "Packed":
            cursor.execute("UPDATE orders SET status = 'Packed' WHERE order_code = ?", (order_code,))

    connection.commit()
    connection.close()


def create_packing_operation(order_code, packaging_type, packaging_cost, handling_cost, total_cost, status, packed_by):
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO packing_operations (order_code, packaging_type, packaging_cost, handling_cost, total_cost, status, packed_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (order_code, packaging_type, packaging_cost, handling_cost, total_cost, status, packed_by))
    
    connection.commit()
    connection.close()

def update_packing_operation(order_code, status):
    connection = get_connection()
    cursor = connection.cursor()
    
    if status == "Packed":
        cursor.execute("""
            UPDATE packing_operations
            SET status = ?, packed_at = CURRENT_TIMESTAMP
            WHERE order_code = ?
        """, (status, order_code))
    else:
        cursor.execute("""
            UPDATE packing_operations
            SET status = ?
            WHERE order_code = ?
        """, (status, order_code))
        
    connection.commit()
    connection.close()

def get_packing_history():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT order_code, packaging_type, packaging_cost, handling_cost, total_cost, status, packed_by, packed_at
        FROM packing_operations
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    connection.close()
    return rows


# ============================================================
# INVENTORY OPERATIONS HELPERS
# ============================================================

def record_stock_in(product_code, quantity, supplier, reference, date, performed_by):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT total_stock FROM products WHERE product_code = ?", (product_code,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError("Product not found.")
    total_stock = row[0]
    new_stock = total_stock + quantity
    
    cursor.execute("UPDATE products SET total_stock = ? WHERE product_code = ?", (new_stock, product_code))
    
    # Log STOCK IN transaction
    cursor.execute("""
        INSERT INTO inventory_transactions (product_code, transaction_type, quantity, previous_stock, new_stock, reference, reason, performed_by)
        VALUES (?, 'STOCK IN', ?, ?, ?, ?, ?, ?)
    """, (product_code, quantity, total_stock, new_stock, reference, f"Supplier: {supplier}, Date: {date}", performed_by))
    
    conn.commit()
    conn.close()

def record_stock_out(product_code, quantity, reason, reference, performed_by):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT total_stock, reserved_stock, damaged_stock FROM products WHERE product_code = ?", (product_code,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError("Product not found.")
    total_stock, reserved_stock, damaged_stock = row
    available_stock = total_stock - reserved_stock - damaged_stock
    
    if available_stock < quantity:
        conn.close()
        raise ValueError(f"Insufficient stock. Available: {available_stock}, Requested: {quantity}")
        
    new_stock = total_stock - quantity
    cursor.execute("UPDATE products SET total_stock = ? WHERE product_code = ?", (new_stock, product_code))
    
    # Log STOCK OUT transaction
    cursor.execute("""
        INSERT INTO inventory_transactions (product_code, transaction_type, quantity, previous_stock, new_stock, reference, reason, performed_by)
        VALUES (?, 'STOCK OUT', ?, ?, ?, ?, ?, ?)
    """, (product_code, quantity, total_stock, new_stock, reference, reason, performed_by))
    
    conn.commit()
    conn.close()

def record_stock_adjustment(product_code, adjustment_qty, reason, performed_by):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT total_stock FROM products WHERE product_code = ?", (product_code,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError("Product not found.")
    total_stock = row[0]
    new_stock = total_stock + adjustment_qty
    
    if new_stock < 0:
        conn.close()
        raise ValueError(f"Adjustment would result in negative stock. Current: {total_stock}, Adjustment: {adjustment_qty}")
        
    cursor.execute("UPDATE products SET total_stock = ? WHERE product_code = ?", (new_stock, product_code))
    
    # Log ADJUSTMENT transaction
    cursor.execute("""
        INSERT INTO inventory_transactions (product_code, transaction_type, quantity, previous_stock, new_stock, reference, reason, performed_by)
        VALUES (?, 'ADJUSTMENT', ?, ?, ?, '', ?, ?)
    """, (product_code, abs(adjustment_qty), total_stock, new_stock, reason, performed_by))
    
    conn.commit()
    conn.close()

def record_damaged_stock(product_code, quantity, reason, performed_by):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT total_stock, reserved_stock, damaged_stock FROM products WHERE product_code = ?", (product_code,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError("Product not found.")
    total_stock, reserved_stock, damaged_stock = row
    available_stock = total_stock - reserved_stock - damaged_stock
    
    if available_stock < quantity:
        conn.close()
        raise ValueError(f"Insufficient available stock to mark as damaged. Available: {available_stock}, Requested: {quantity}")
        
    new_damaged = damaged_stock + quantity
    cursor.execute("UPDATE products SET damaged_stock = ? WHERE product_code = ?", (new_damaged, product_code))
    
    # Log DAMAGED transaction
    cursor.execute("""
        INSERT INTO inventory_transactions (product_code, transaction_type, quantity, previous_stock, new_stock, reference, reason, performed_by)
        VALUES (?, 'DAMAGED', ?, ?, ?, '', ?, ?)
    """, (product_code, quantity, total_stock, total_stock, reason, performed_by))
    
    conn.commit()
    conn.close()

def get_inventory_transactions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, product_code, transaction_type, quantity, previous_stock, new_stock, reference, reason, performed_by, created_at
        FROM inventory_transactions
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

# ============================================================
# ORDER TRANSACTIONS HELPERS
# ============================================================

def get_order_transactions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, order_code, customer, product_code, quantity, unit_selling_price, subtotal, discount, tax, shipping_fee, total_amount, payment_method, payment_status, transaction_type, transaction_reference, created_at, updated_at
        FROM order_transactions
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_order_transaction_payment_status(order_code, status, payment_method=None):
    conn = get_connection()
    cursor = conn.cursor()
    t_type = 'DEBIT' if status == 'Paid' else 'REFUND' if status == 'Refunded' else 'PENDING'
    if payment_method:
        cursor.execute("""
            UPDATE order_transactions
            SET payment_status = ?, payment_method = ?, transaction_type = ?, updated_at = CURRENT_TIMESTAMP
            WHERE order_code = ?
        """, (status, payment_method, t_type, order_code))
    else:
        cursor.execute("""
            UPDATE order_transactions
            SET payment_status = ?, transaction_type = ?, updated_at = CURRENT_TIMESTAMP
            WHERE order_code = ?
        """, (status, t_type, order_code))
    conn.commit()
    conn.close()

def cancel_order_db(order_code, performed_by="System"):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if order exists and is not already Cancelled or Dispatched
    cursor.execute("SELECT status, product_code, quantity FROM orders WHERE order_code = ?", (order_code,))
    ord_row = cursor.fetchone()
    if not ord_row:
        conn.close()
        raise ValueError("Order not found.")
        
    status, product_code, quantity = ord_row
    if status == "Cancelled":
        conn.close()
        return
        
    # Update order status to Cancelled
    cursor.execute("UPDATE orders SET status = 'Cancelled' WHERE order_code = ?", (order_code,))
    
    # Update transaction status to Cancelled
    cursor.execute("UPDATE order_transactions SET payment_status = 'Cancelled', transaction_type = 'CANCELLED', updated_at = CURRENT_TIMESTAMP WHERE order_code = ?", (order_code,))
    
    # If the order was allocated, we release the reserved stock
    cursor.execute("SELECT allocated_quantity FROM allocations WHERE order_code = ?", (order_code,))
    alloc_row = cursor.fetchone()
    allocated = alloc_row[0] if alloc_row else 0
    
    if allocated > 0:
        cursor.execute("SELECT total_stock, reserved_stock FROM products WHERE product_code = ?", (product_code,))
        p_row = cursor.fetchone()
        if p_row:
            total_stock, reserved_stock = p_row
            new_reserved = max(0, reserved_stock - allocated)
            cursor.execute("UPDATE products SET reserved_stock = ? WHERE product_code = ?", (new_reserved, product_code))
            
            # Log RELEASE transaction
            cursor.execute("""
                INSERT INTO inventory_transactions (product_code, transaction_type, quantity, previous_stock, new_stock, reference, reason, performed_by)
                VALUES (?, 'RELEASE', ?, ?, ?, ?, 'Order Cancelled', ?)
            """, (product_code, allocated, total_stock, total_stock, order_code, performed_by))
            
    conn.commit()
    conn.close()

# ============================================================
# RETURN ORDERS HELPERS
# ============================================================

def get_return_orders():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, order_code, customer, product_code, quantity, reason, description, status, rejection_reason, inspection_condition, refund_amount, requested_at, updated_at
        FROM return_orders
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def create_return_order(order_code, customer, product_code, quantity, reason, description, refund_amount):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if there is already an active return request for this product in this order
    cursor.execute("""
        SELECT COUNT(*) FROM return_orders 
        WHERE order_code = ? AND product_code = ? AND status NOT IN ('Rejected', 'Refunded', 'Restocked', 'Closed')
    """, (order_code, product_code))
    if cursor.fetchone()[0] > 0:
        conn.close()
        raise ValueError(f"An active return request already exists for product {product_code} in order {order_code}.")
        
    cursor.execute("""
        INSERT INTO return_orders (order_code, customer, product_code, quantity, reason, description, refund_amount, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Requested')
    """, (order_code, customer, product_code, quantity, reason, description, refund_amount))
    conn.commit()
    conn.close()

def update_return_order_status(return_id, new_status, rejection_reason=None, inspection_condition=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Fetch current return details
    cursor.execute("SELECT order_code, product_code, quantity, status, refund_amount FROM return_orders WHERE id = ?", (return_id,))
    ret_row = cursor.fetchone()
    if not ret_row:
        conn.close()
        raise ValueError("Return request not found.")
        
    order_code, product_code, quantity, old_status, refund_amount = ret_row
    
    # Update query
    if rejection_reason:
        cursor.execute("""
            UPDATE return_orders
            SET status = ?, rejection_reason = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_status, rejection_reason, return_id))
    elif inspection_condition:
        cursor.execute("""
            UPDATE return_orders
            SET status = ?, inspection_condition = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_status, inspection_condition, return_id))
    else:
        cursor.execute("""
            UPDATE return_orders
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_status, return_id))
        
    # Perform side effects based on transitions:
    
    # Transition 1: Under Inspection -> Approved for Refund
    if old_status == "Under Inspection" and new_status == "Approved for Refund":
        # Check inspection condition
        cursor.execute("SELECT inspection_condition FROM return_orders WHERE id = ?", (return_id,))
        cond_row = cursor.fetchone()
        cond = cond_row[0] if cond_row else "Good Condition"
        
        if cond == "Good Condition":
            # Eligible for restock. Restocking will be manual by clicking the button.
            # Move order transaction to Refund Pending
            cursor.execute("UPDATE order_transactions SET payment_status = 'Refund Pending' WHERE order_code = ?", (order_code,))
        else:
            # Damaged or Partial Damage:
            # "When returned product is damaged: increase damaged_stock. ... If return is damaged: Do not add to usable stock. Add to damaged_stock."
            cursor.execute("SELECT total_stock, damaged_stock FROM products WHERE product_code = ?", (product_code,))
            p_row = cursor.fetchone()
            if p_row:
                total_stock, damaged_stock = p_row
                new_total = total_stock + quantity
                new_damaged = damaged_stock + quantity
                cursor.execute("UPDATE products SET total_stock = ?, damaged_stock = ? WHERE product_code = ?", (new_total, new_damaged, product_code))
                
                # Log DAMAGED transaction in inventory_transactions
                cursor.execute("""
                    INSERT INTO inventory_transactions (product_code, transaction_type, quantity, previous_stock, new_stock, reference, reason, performed_by)
                    VALUES (?, 'DAMAGED', ?, ?, ?, ?, 'Damaged Return Item', 'System')
                """, (product_code, quantity, total_stock, new_total, f"RET-{return_id}"))
                
            # Move order transaction to Refund Pending
            cursor.execute("UPDATE order_transactions SET payment_status = 'Refund Pending' WHERE order_code = ?", (order_code,))
            
    # Transition 2: Approved for Refund -> Restocked (for Good Condition only)
    elif new_status == "Restocked":
        # Increase usable stock: total_stock increases (which increases available stock)
        cursor.execute("SELECT total_stock FROM products WHERE product_code = ?", (product_code,))
        p_row = cursor.fetchone()
        if p_row:
            total_stock = p_row[0]
            new_total = total_stock + quantity
            cursor.execute("UPDATE products SET total_stock = ? WHERE product_code = ?", (new_total, product_code))
            
            # Log RETURN transaction in inventory_transactions
            cursor.execute("""
                INSERT INTO inventory_transactions (product_code, transaction_type, quantity, previous_stock, new_stock, reference, reason, performed_by)
                VALUES (?, 'RETURN', ?, ?, ?, ?, 'Good Condition Restock', 'System')
            """, (product_code, quantity, total_stock, new_total, f"RET-{return_id}"))
            
    # Transition 3: Approved for Refund/Restocked -> Refunded
    elif new_status == "Refunded":
        # Update order transaction status to Refunded
        cursor.execute("UPDATE order_transactions SET payment_status = 'Refunded' WHERE order_code = ?", (order_code,))
        
    conn.commit()
    conn.close()


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    create_tables()
    add_sample_data()


# ============================================================
# TEST DATABASE
# ============================================================

if __name__ == "__main__":

    initialize_database()

    print(
        "SmartFulfill database initialized successfully!"
    )