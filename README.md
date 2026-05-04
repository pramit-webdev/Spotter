# 🚛 Spotter: AI-Powered Fuel Route Optimizer

Spotter is a professional-grade Django REST API and Interactive Dashboard designed to calculate the most cost-efficient fuel stops for long-haul trucking routes across the USA.

[![Status: Live](https://img.shields.io/badge/Status-Live-success)](https://spotter-jmm5.onrender.com/)
[![Tech Stack: Django](https://img.shields.io/badge/Tech_Stack-Django_6.0-092e20)](https://www.djangoproject.com/)
[![Database: Supabase](https://img.shields.io/badge/Database-PostgreSQL-336791)](https://supabase.com/)

---

## 🌟 Key Features

- **Optimal Stop Discovery**: Uses a custom **Greedy Optimization Algorithm** to find the cheapest fuel stops within a 500-mile vehicle range.
- **Massive Dataset**: Efficiently processed and indexed **8,000+ fuel station records** from across the USA.
- **Interactive Map Dashboard**: A premium, dark-mode Leaflet.js visualization with glassmorphism UI.
- **Dual-Output API**: Supports both `JSON` for programmatic use and `HTML (ui=map)` for visual demonstrations.
- **Geocoding Cache Strategy**: High-performance location resolution using ArcGIS with internal caching to avoid API rate limits.
- **Production Ready**: Fully configured for Render with WhiteNoise static serving and PostgreSQL connection pooling.

---

## 🚀 Quick Start (Demo)

The easiest way to test Spotter is via the **Launchpad UI**:

1. **Visit**: [https://spotter-jmm5.onrender.com/](https://spotter-jmm5.onrender.com/)
2. **Enter Cities**: e.g., `Chicago, IL` to `St. Louis, MO`.
3. **Optimize**: View the calculated path and recommended cheap fuel stops.

### Example REST API Request:
```bash
curl "https://spotter-jmm5.onrender.com/api/route/?start=Chicago,IL&end=Dallas,TX"
```

---

## 🛠️ Technical Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Django 6.0, Django REST Framework |
| **Database** | PostgreSQL (Supabase) + pgvector/spatial indexes |
| **Routing** | OSRM (Open Source Routing Machine) |
| **Geocoding** | ArcGIS Geopy Integration |
| **Frontend** | Vanilla JS, Leaflet.js, Glassmorphism CSS |
| **Deployment** | Render, Gunicorn, WhiteNoise |

---

## 🧠 The Algorithm: Greedy Fuel Optimizer

The core logic resides in `fuel_route/services.py`. 

1. **Path Sampling**: The route geometry is divided into segments.
2. **Radius Search**: For each segment, the system performs a spatial query to find all stations within a 10-mile radius of the highway.
3. **Greedy Decision**: The algorithm projects the vehicle's remaining range (max 500 miles). If a cheaper station is found within range, the vehicle plans to refuel there just before the tank hits empty.
4. **Safety Buffer**: Ensures the truck never runs out of fuel while traversing remote areas.

---

## 📦 Installation & Local Setup

1. **Clone the repo**:
   ```bash
   git clone <repo-url>
   cd Spotter
   ```

2. **Setup Environment**: Create a `.env` file based on `.env.example`.
   ```bash
   DATABASE_URL=postgres://...
   DEBUG=True
   SECRET_KEY=your-secret
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Import Data**:
   ```bash
   python manage.py import_fuel fuel-prices-for-be-assessment.csv
   ```

6. **Start Server**:
   ```bash
   python manage.py runserver
   ```

---

## 🧪 Testing

The project includes an automated test suite covering geocoding, routing logic, and API status:

```bash
# Run local unit tests
python manage.py test

# Run live E2E production test
python live_test.py
```

---

## 🤝 Project Structure

```text
├── spotter_api/          # Project configuration & settings
├── fuel_route/           
│   ├── management/       # Data migration commands
│   ├── templates/        # Premium UI/UX (Landing + Map)
│   ├── services.py       # Algorithmic & API core logic
│   ├── models.py         # FuelStation schema with indexing
│   └── views.py          # Dual-output API handlers
├── requirements.txt      # Production dependencies
└── live_test.py          # E2E test script
```

---

Developed with ❤️ for the Spotter Engineering Assessment.
