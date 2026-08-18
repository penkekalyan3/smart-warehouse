def format_inr(val):
    """
    Format values using the Indian Numbering System (e.g. ₹1,25,000 or ₹45,000).
    """
    if val is None:
        return "₹0"
    try:
        val = float(val)
    except ValueError:
        return f"₹{val}"
    
    is_negative = val < 0
    val = abs(val)
    
    # Check if we should display decimals
    if val - int(val) > 0.005:
        s = f"{val:.2f}"
        parts = s.split(".")
        num = parts[0]
        dec = "." + parts[1]
    else:
        num = f"{val:.0f}"
        dec = ""
        
    if len(num) <= 3:
        res = num
    else:
        last3 = num[-3:]
        remaining = num[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        res = ",".join(groups) + "," + last3
        
    formatted = f"₹{res}{dec}"
    return f"-{formatted}" if is_negative else formatted


def calculate_priority(urgency, order_age, customer_value, stock_criticality):
    """
    Calculate an order priority score from 0 to 100.
    For backward compatibility.
    """

    score = (
        urgency * 25
        + order_age * 20
        + customer_value * 20
        + stock_criticality * 35
    )

    score = min(100, score)

    if score >= 80:
        priority = "Critical"
    elif score >= 60:
        priority = "High"
    elif score >= 40:
        priority = "Medium"
    else:
        priority = "Low"

    return priority, score


def calculate_priority_score(urgency, quantity, available_stock, existing_priority=None, order_status=None, selling_price=0.0, unit_cost=0.0):
    """
    Rules-based intelligent priority scoring system.
    Operational priority ALWAYS takes precedence. Profit value is used as a tie-breaker.
    """
    # 1. Base urgency score from customer (1-10) -> maps to 0-35 points
    urgency_val = min(10, max(1, urgency))
    urgency_points = urgency_val * 3.5

    # 2. Quantity weight: larger volumes represent higher complexity -> maps to 0-15 points
    qty_points = min(15.0, quantity * 0.3)

    # 3. Shortage weight: critical orders with shortage are flagged to prompt fast replenishment -> maps to 0-20 points
    shortage = max(0, quantity - available_stock)
    if shortage > 0 and quantity > 0:
        shortage_points = min(20.0, (shortage / quantity) * 20.0)
    else:
        shortage_points = 0.0

    # 4. Existing priority weight -> maps to 0-15 points
    priority_map = {"Critical": 15.0, "High": 11.0, "Medium": 7.0, "Low": 2.0}
    existing_points = priority_map.get(existing_priority, 7.0)

    # 5. Order status weight -> maps to 0-10 points
    status_points = 0.0
    if order_status in ["Backordered", "Pending"]:
        status_points = 10.0

    # Base operational score (max 95)
    base_operational_score = urgency_points + qty_points + shortage_points + existing_points + status_points

    # 6. Financial Tie-Breaker (max 5 points)
    # Applied as minor bump for high profit values to resolve scheduling conflicts
    profit_margin = selling_price - unit_cost
    estimated_profit = quantity * profit_margin
    financial_bonus = min(5.0, (max(0.0, estimated_profit) / 10000.0) * 5.0)

    total_score = base_operational_score + financial_bonus
    total_score = int(min(100.0, max(0.0, total_score)))

    # Determine priority category
    if total_score >= 80:
        priority = "Critical"
        action = "Prioritize immediate allocation, dispatch pickers. Escalate low stock immediately."
    elif total_score >= 60:
        priority = "High"
        action = "Run allocation check and place in picking queue. Monitor packing progress."
    elif total_score >= 40:
        priority = "Medium"
        action = "Process in standard queue. Release for picking once stock is verified."
    else:
        priority = "Low"
        action = "Consolidate dispatch or process during off-peak operational windows."

    # Explanatory text
    reasons = []
    reasons.append(f"Customer urgency is rated {urgency_val}/10 (+{urgency_points:.1f} pts).")
    reasons.append(f"Order quantity is {quantity} units (+{qty_points:.1f} pts).")
    if shortage > 0:
        reasons.append(f"Inventory shortage of {shortage} units detected (+{shortage_points:.1f} pts).")
    else:
        reasons.append("Inventory is fully available for this product (0 pts shortage penalty).")
    if existing_priority:
        reasons.append(f"Prior categorization is '{existing_priority}' (+{existing_points:.1f} pts).")
    if order_status:
        reasons.append(f"Order status is '{order_status}' (+{status_points:.1f} pts).")
    
    if financial_bonus > 0:
        reasons.append(f"Financial tie-breaker applied for estimated profit of {format_inr(estimated_profit)} (+{financial_bonus:.1f} pts).")
    else:
        reasons.append("No financial tie-breaker bonus applied.")

    reason_text = " ".join(reasons) + f" Total score: {total_score}/100. (Note: Critical operational priority takes precedence over financial value)."

    return priority, total_score, reason_text, action


def get_available_stock(total_stock, reserved_stock, damaged_stock):
    """
    Calculate usable warehouse stock.
    """

    return max(
        0,
        total_stock - reserved_stock - damaged_stock
    )


def get_stock_status(
    total_stock,
    reserved_stock,
    damaged_stock,
    reorder_level
):
    """
    Determine inventory health.
    """

    available = get_available_stock(
        total_stock,
        reserved_stock,
        damaged_stock
    )

    if available == 0:
        return "OUT OF STOCK"

    if available <= reorder_level:
        return "LOW STOCK"

    return "HEALTHY"


def allocate_inventory(
    required_quantity,
    available_quantity,
    priority
):
    """
    Smart inventory allocation decision.
    """

    if available_quantity >= required_quantity:

        return {
            "decision": "FULL ALLOCATION",
            "allocated": required_quantity,
            "shortage": 0,
            "action": "Generate picking task and release order.",
            "reason": (
                "Enough inventory is available "
                "to completely fulfill the order."
            )
        }

    shortage = required_quantity - available_quantity

    if priority == "Critical" or priority == "High":

        return {
            "decision": "PARTIAL ALLOCATION",
            "allocated": available_quantity,
            "shortage": shortage,
            "action": (
                "Allocate available stock, generate picking task "
                "for available units, and create a backorder."
            ),
            "reason": (
                f"The order priority is {priority}, so available "
                "inventory is released. A backorder is registered for shortage."
            )
        }

    return {
        "decision": "HOLD ORDER",
        "allocated": 0,
        "shortage": required_quantity,
        "action": (
            "Wait for stock replenishment. "
            "Order is placed in backorder queue."
        ),
        "reason": (
            "Insufficient inventory is available and order priority "
            "is not high enough to permit partial fulfillment."
        )
    }


def get_reorder_recommendation(
    available_quantity,
    reorder_level,
    reorder_quantity
):
    """
    Recommend replenishment when stock is low.
    """

    if available_quantity <= 0:

        return {
            "reorder": True,
            "urgency": "URGENT",
            "quantity": reorder_quantity,
            "message": (
                "Stock is completely unavailable. "
                "Immediate replenishment is recommended."
            )
        }

    if available_quantity <= reorder_level:

        return {
            "reorder": True,
            "urgency": "HIGH",
            "quantity": reorder_quantity,
            "message": (
                "Stock is below the reorder level. "
                "Replenishment is recommended."
            )
        }

    return {
        "reorder": False,
        "urgency": "NORMAL",
        "quantity": 0,
        "message": "Stock level is healthy."
    }


def resolve_exception(exception_type):
    """
    Recommend a resolution for warehouse exceptions.
    """

    resolutions = {

        "Stock Shortage": (
            "Check priority → "
            "Partial allocation → "
            "Create backorder → "
            "Trigger reorder"
        ),

        "Damaged Item": (
            "Remove damaged quantity → "
            "Check replacement stock → "
            "Allocate replacement if available"
        ),

        "Missing Item": (
            "Recheck picking location → "
            "Verify inventory → "
            "Create investigation task"
        ),

        "Quality Failure": (
            "Hold order → "
            "Perform quality inspection → "
            "Replace failed items"
        ),

        "Wrong Item Picked": (
            "Return incorrect item to shelf → "
            "Re-pick correct product code from location"
        ),

        "Inventory Mismatch": (
            "Perform physical count → "
            "Reconcile system stock counts → "
            "Update SQLite db"
        ),

        "Packing Error": (
            "Re-pack shipment → "
            "Verify package contents against packing slip"
        ),

        "Dispatch Delay": (
            "Escalate to logistics partner → "
            "Reschedule pick-up time slot"
        )
    }

    return resolutions.get(
        exception_type,
        "Escalate to warehouse supervisor."
    )


def optimize_picking_route(locations):
    """
    Simple picking optimization.
    Groups warehouse locations to reduce movement.
    """

    return sorted(locations)


def calculate_picking_route_savings(locations):
    """
    Calculate travel distance savings when using location-grouped routing.
    Locations are strings like 'A-01-03', 'B-02-01', etc.
    """
    if not locations or len(locations) < 2:
        return 0.0, 0.0, 0.0  # Unsorted distance, sorted distance, savings %

    # Parse location coordinates: Zone (A=1, B=2, C=3), Aisle (int), Shelf (int)
    def parse_loc(loc):
        if not isinstance(loc, str):
            return 1, 1, 1
        parts = loc.split("-")
        if len(parts) < 3:
            return 1, 1, 1
        zone_char = parts[0].upper()
        zone = ord(zone_char) - ord('A') + 1 if zone_char.isalpha() else 1
        try:
            aisle = int(parts[1])
        except ValueError:
            aisle = 1
        try:
            shelf = int(parts[2])
        except ValueError:
            shelf = 1
        return zone, aisle, shelf

    coords = [parse_loc(loc) for loc in locations]

    # Calculate distance between two coordinate tuples: Manhattan-style distance
    # Zone has weight 20, Aisle has weight 10, Shelf has weight 2
    def dist(c1, c2):
        return abs(c1[0] - c2[0]) * 20 + abs(c1[1] - c2[1]) * 10 + abs(c1[2] - c2[2]) * 2

    # Unsorted distance (order of input locations)
    unsorted_dist = 0.0
    for i in range(len(coords) - 1):
        unsorted_dist += dist(coords[i], coords[i+1])

    # Sorted distance (grouped by location, which is sorted alphabetical order)
    sorted_locations = sorted(locations)
    sorted_coords = [parse_loc(loc) for loc in sorted_locations]
    
    sorted_dist = 0.0
    for i in range(len(sorted_coords) - 1):
        sorted_dist += dist(sorted_coords[i], sorted_coords[i+1])

    # Calculate savings
    savings = max(0.0, unsorted_dist - sorted_dist)
    savings_pct = (savings / unsorted_dist * 100) if unsorted_dist > 0 else 0.0
    
    return unsorted_dist, sorted_dist, savings_pct


def explain_decision(
    required,
    available,
    priority,
    decision
):
    """
    Generate a human-readable explanation.
    """

    shortage = max(
        0,
        required - available
    )

    if decision == "FULL ALLOCATION":

        return (
            f"Order priority is {priority}. "
            f"{available} units are available and "
            f"{required} units are required. "
            f"The order can be completely fulfilled."
        )

    if decision == "PARTIAL ALLOCATION":

        return (
            f"Order priority is {priority}. "
            f"Only {available} of {required} units "
            f"are available. "
            f"{available} units should be allocated "
            f"and {shortage} units should be backordered."
        )

    return (
        f"Order priority is {priority}. "
        f"Only {available} of {required} units "
        f"are available. "
        f"The order should wait for replenishment."
    )