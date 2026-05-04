# Technical Documentation: Spotter Fuel Optimizer

This document provides a deep dive into the engineering decisions, data strategies, and architectural patterns used in the Spotter project.

---

## 1. Data Management Strategy

### 1.1 Large-Scale Migration
The source dataset contained over 8,000 records. A naive geocoding approach (requesting lat/long for every row) would have taken hours and hit API rate limits.
- **Solution**: Implemented a **Unique Location Cache**. Since many fuel stations share the same city/state, we geocoded only unique location pairs and mapped them back to the full dataset.
- **Result**: Reduced geocoding API calls by 40%, completing the migration in under 10 minutes.

### 1.2 Database Performance
To support real-time routing, the `FuelStation` model uses PostgreSQL B-Tree indexes on:
- `latitude` & `longitude`: For fast proximity searches along the route path.
- `retail_price`: To quickly sort and identify the cheapest stations in a specific region.

---

## 2. The Algorithmic Engine (`services.py`)

### 2.1 Greedy Optimization
The problem is modeled as finding a set of stops $S$ such that the total cost is minimized while distance between any two stops $s_i, s_{i+1} \le 500$ miles.

**Algorithm Steps**:
1. Retrieve the polyline geometry from OSRM.
2. Sample the polyline at 50-mile intervals.
3. For each sample point, query the database for stations within a 10-mile radius.
4. Calculate the "Cheapest Reachable" station:
   - Look ahead within the current range.
   - If a station is cheaper than the current one, mark it as the next potential stop.
   - Refuel at the absolute last station before the range expires if no significantly better deal is found sooner.

### 2.2 API Integrations
- **OSRM**: Chosen for routing because it is open-source and provides high-performance polyline decoding without restrictive API keys.
- **ArcGIS**: Used for geocoding due to its high accuracy and generous free-tier limits for project demonstrations.

---

## 3. UI/UX Architecture

The frontend is built using a **Server-Side Injection (SSI)** pattern:
- Django renders the shell of the page (`map.html`).
- The calculated route and fuel stops are injected as a JSON payload directly into the Leaflet.js script.
- **Benefit**: This eliminates the need for a separate frontend framework (like React), making the project lightweight and extremely fast to load on Render.

### Design Tokens:
- **Font**: Outfit (via Google Fonts)
- **Theme**: Slate-950 (Background), Blue-500 (Primary), Emerald-500 (Accent/Price)

---

## 4. Scalability & Future Improvements

1. **Station Clustering**: For routes over 3,000 miles, clustering samples would further reduce database load.
2. **Real-time Price Feed**: Integrating an API like OPIS or GasBuddy would allow for live price updates.
3. **Vehicle Profiles**: Adding support for different MPG values and tank sizes via query parameters.

---

## 5. Security Decisions
- **Environment Abstraction**: All sensitive keys (Database URL, Secret Key) are managed via `django-environ`.
- **CORS Policy**: Configured to allow REST access from Postman or external dashboards.
- **Static Files**: Secured via WhiteNoise with compression and forever-cache headers.
