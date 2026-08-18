# SmartFulfill – Smart Warehouse Operations & Financial Intelligence Platform

SmartFulfill is a modern, responsive single-page web dashboard designed for intelligent warehouse management and real-time order fulfillment processing. It is engineered entirely with HTML, CSS, and Vanilla JavaScript, allowing it to run fully client-side directly in any web browser without requiring a backend database or Python environment.

This project was converted from a Python + Streamlit + SQLite app to a client-side web application for rapid presentation during hackathons and demonstrations. All state changes persist automatically in browser `localStorage`.

---

## 🚀 Key Features & Modules

The application features a complete 15-module system accessible via a modern left-hand sidebar navigation:

1. **Dashboard**: Comprehensive SaaS-style visual analytics including operational KPI metrics (stock states, orders queues), financial KPIs (inventory value, potential profit, revenue at risk), warehouse risk assessment gauges, and real-time system alerts.
2. **Smart Inventory**: A fully searchable, categorizable directory featuring a complete log of 30 seeded products. Real-time operations include *Stock Check In*, *Stock Check Out*, *Audit Adjustments*, and *Damage Registrations*, alongside automated reorder recommendation reports and stock movement ledgers.
3. **Order Management**: Order initialization with a live, real-time preview of the *Intelligent Priority Engine* which calculates priority scores (0-100) and levels (Critical, High, Medium, Low) using customer urgency, shortage volume, complexity margins, and financial margins.
4. **Order Transactions**: Complete invoicing ledgers tracking paid and pending payments (Accounts Receivable) with confirmation actions that shift statuses and allocate transaction reference codes.
5. **Return Management**: A dedicated RMA (Return Merchandise Authorization) portal where returns can be filed, pickup schedules set, items inspected, refunds processed, and returned goods restocked directly back into sellable inventory.
6. **Smart Allocation**: Intelligent inventory reservations recommendation board suggesting full/partial/hold status allocations.
7. **Picking Workflow**: Shows pick tasks and integrates a *Manhattan Picking Route Optimizer* showcasing standard travel distances vs optimized location-grouped sequence path savings.
8. **Packing Workflow**: A packing station queue enabling box packaging classification (Small Box, Medium Box, Pallets) with associated shipping cost calculations.
9. **Quality Check**: Quality control station to pass or fail picked items.
10. **Exception ManagementLog**: Displays discrepancies (e.g. shortages or damages) with AI-powered recommended resolutions.
11. **Backorder Management**: Registers order shortages on hold awaiting restocks, offering manually triggered fulfillments as stock recovers.
12. **Dispatch & Timeline**: An 8-stage visual stepper tracing individual order fulfillment progress (Created &rarr; Allocated &rarr; Picking &rarr; Packing &rarr; QC &rarr; Ready &rarr; Dispatched &rarr; Completed).
13. **Analytics & Insights**: Chart.js integration graphing sales revenue, category values, and line trends of stock movements.
14. **Hackathon Demo Mode**: Dedicated testing console offering quick buttons to simulate order requests, payments, returns, stock shortages, or direct dispatches with live logging.

---

## 🛠️ Technology Stack

* **Frontend Structure**: HTML5 Semantic markup
* **Styling**: Vanilla CSS3 custom dark design system (featuring CSS custom variables, custom animations, transitions, and fully responsive layouts)
* **Logic & Engine**: Client-side Vanilla JavaScript (ES6+)
* **Data Storage**: Browser `localStorage` (state-persistent across reloads)
* **Libraries (CDN)**:
  * Chart.js (Interactive charting and data-visualization)
  * FontAwesome 6 (Vector iconography)

---

## ⚡ Quick Start

1. **Run Locally**:
   Double-click the `index.html` file to open the dashboard directly in any browser (Chrome, Firefox, Edge, Safari). Or run it using the VS Code **Live Server** extension.
2. **First Launch Seeding**:
   The dashboard will automatically seed default database configurations (30 products, orders, transactions, andRMAs) on first load.
3. **Hackathon Demonstrations**:
   Navigate to the **Hackathon Demo Mode** tab in the sidebar and trigger the simulation actions to showcase real-time calculations. Wiping and resetting the database is possible at any time.
