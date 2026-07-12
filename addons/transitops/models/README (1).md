# TransitOps - Smart Transport Operations Platform (Odoo Edition)

TransitOps is a centralized smart transport operations platform built as an Odoo module. It enables logistics companies to digitize vehicle registry, driver profiles, dispatch workflows, maintenance logs, and fuel/expense tracking while enforcing strict business rules and providing real-time KPI insights.

---

## 🚀 Getting Started (How to Run)

We have provided a complete Docker configuration to run Odoo and PostgreSQL locally with zero setup.

### Prerequisites
Make sure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

### Steps to Run
1. Navigate to the project root directory:
   ```bash
   cd projects/transitops_project
   ```
2. Start the services:
   ```bash
   docker compose up -d
   ```
3. Access Odoo in your browser:
   * URL: **`http://localhost:8069`**
   * Master Password: **`admin`** (if prompted to create a database)
   * Create a new database and make sure to check **"Demo data"** (though TransitOps will seed its own demo data too!).
4. Install the module:
   * Go to **Apps** in the Odoo dashboard.
   * Click **Update Apps List** in the top menu bar.
   * Search for **`TransitOps`**.
   * Click **Activate**.

---

## 👥 Team Task Division & Git Commit Workflow

To ensure that all **4 team members** contribute equally and push code individually, the project features are divided into 4 independent sub-tasks. Each member must run the command corresponding to their task on their own system, commit, and push.

### Git Branching Strategy
1. **Branch Names**: Each member should work on a dedicated branch (e.g. `feature/member1-vehicles`, `feature/member2-drivers`, etc.).
2. **Commit Message**: Use a clean prefix matching your feature (e.g. `feat(vehicles): ...`).
3. **Merging**: Open a Pull Request (PR) to the `main` branch to combine your work.

---

### 📋 Detailed Allocation of Tasks

#### 🚗 Member 1: Core Framework, RBAC Security, and Vehicle Registry
* **Focus**: Base project configuration, permission models, and vehicle asset registry.
* **Files to Commit & Push**:
  * [addons/transitops/__init__.py](file:///home/vedant/projects/transitops_project/addons/transitops/__init__.py)
  * [addons/transitops/__manifest__.py](file:///home/vedant/projects/transitops_project/addons/transitops/__manifest__.py)
  * [addons/transitops/models/__init__.py](file:///home/vedant/projects/transitops_project/addons/transitops/models/__init__.py)
  * [addons/transitops/models/vehicle.py](file:///home/vedant/projects/transitops_project/addons/transitops/models/vehicle.py)
  * [addons/transitops/security/security.xml](file:///home/vedant/projects/transitops_project/addons/transitops/security/security.xml)
  * [addons/transitops/security/ir.model.access.csv](file:///home/vedant/projects/transitops_project/addons/transitops/security/ir.model.access.csv)
  * [addons/transitops/views/menus.xml](file:///home/vedant/projects/transitops_project/addons/transitops/views/menus.xml)
  * [addons/transitops/views/vehicle_views.xml](file:///home/vedant/projects/transitops_project/addons/transitops/views/vehicle_views.xml)
  * [docker-compose.yml](file:///home/vedant/projects/transitops_project/docker-compose.yml)
  * [config/odoo.conf](file:///home/vedant/projects/transitops_project/config/odoo.conf)
* **Git Commands (Run on Member 1's system)**:
  ```bash
  git checkout -b feature/member1-vehicles
  git add addons/transitops/__init__.py addons/transitops/__manifest__.py addons/transitops/models/__init__.py addons/transitops/models/vehicle.py addons/transitops/security/security.xml addons/transitops/security/ir.model.access.csv addons/transitops/views/menus.xml addons/transitops/views/vehicle_views.xml docker-compose.yml config/odoo.conf
  git commit -m "feat(vehicles): init module, implement base RBAC security and vehicle registry"
  git push origin feature/member1-vehicles
  ```

#### 👤 Member 2: Driver Management & Compliance
* **Focus**: Driver profile logs, safety scoring database, and license compliance checker.
* **Files to Commit & Push**:
  * [addons/transitops/models/driver.py](file:///home/vedant/projects/transitops_project/addons/transitops/models/driver.py)
  * [addons/transitops/views/driver_views.xml](file:///home/vedant/projects/transitops_project/addons/transitops/views/driver_views.xml)
  * [addons/transitops/data/data.xml](file:///home/vedant/projects/transitops_project/addons/transitops/data/data.xml) (Seed data for vehicles and drivers)
* **Git Commands (Run on Member 2's system)**:
  ```bash
  git checkout -b feature/member2-drivers
  git add addons/transitops/models/driver.py addons/transitops/views/driver_views.xml addons/transitops/data/data.xml
  git commit -m "feat(drivers): implement driver profiles, license expiry tracking, and demo seed data"
  git push origin feature/member2-drivers
  ```

#### 🗺️ Member 3: Trip Management & Workflow State Transitions
* **Focus**: Trip planning dispatch logs, cargo capacity constraints, driver/vehicle trip states, and sequence generator.
* **Files to Commit & Push**:
  * [addons/transitops/models/trip.py](file:///home/vedant/projects/transitops_project/addons/transitops/models/trip.py)
  * [addons/transitops/views/trip_views.xml](file:///home/vedant/projects/transitops_project/addons/transitops/views/trip_views.xml)
* **Git Commands (Run on Member 3's system)**:
  ```bash
  git checkout -b feature/member3-trips
  git add addons/transitops/models/trip.py addons/transitops/views/trip_views.xml
  git commit -m "feat(trips): implement trip dispatching logic, state transitions, and sequence generation"
  git push origin feature/member3-trips
  ```

#### 📊 Member 4: Maintenance, Expenses, QWeb Reports, & KPI Dashboards
* **Focus**: Maintenance status changes, fuel log entries, computed cost/ROI analytics, QWeb PDF report creation, and Graph/Pivot dashboards.
* **Files to Commit & Push**:
  * [addons/transitops/models/maintenance.py](file:///home/vedant/projects/transitops_project/addons/transitops/models/maintenance.py)
  * [addons/transitops/models/fuel_expense.py](file:///home/vedant/projects/transitops_project/addons/transitops/models/fuel_expense.py)
  * [addons/transitops/views/maintenance_views.xml](file:///home/vedant/projects/transitops_project/addons/transitops/views/maintenance_views.xml)
  * [addons/transitops/views/expense_views.xml](file:///home/vedant/projects/transitops_project/addons/transitops/views/expense_views.xml)
  * [addons/transitops/views/dashboard_views.xml](file:///home/vedant/projects/transitops_project/addons/transitops/views/dashboard_views.xml)
  * [addons/transitops/report/report_views.xml](file:///home/vedant/projects/transitops_project/addons/transitops/report/report_views.xml)
  * [addons/transitops/report/trip_report_templates.xml](file:///home/vedant/projects/transitops_project/addons/transitops/report/trip_report_templates.xml)
* **Git Commands (Run on Member 4's system)**:
  ```bash
  git checkout -b feature/member4-analytics
  git add addons/transitops/models/maintenance.py addons/transitops/models/fuel_expense.py addons/transitops/views/maintenance_views.xml addons/transitops/views/expense_views.xml addons/transitops/views/dashboard_views.xml addons/transitops/report/report_views.xml addons/transitops/report/trip_report_templates.xml
  git commit -m "feat(analytics): implement maintenance logic, fuel expenses, KPI dashboards, and PDF reports"
  git push origin feature/member4-analytics
  ```

---

## 🛠️ Verification & Demo Workflow

You can verify the entire setup step-by-step:
1. **Vehicle Entry**: Create a vehicle (e.g. `Van-05`) with a maximum capacity of `500 kg` (automatically seeded).
2. **Driver Entry**: Create a driver (e.g. `Alex`) with a valid license and safety score (automatically seeded).
3. **Trip Setup**: Create a trip with a cargo weight of `450 kg` using vehicle `Van-05` and driver `Alex`.
4. **Dispatch**: Click **Dispatch**. Verify that both the vehicle and driver status transition to **On Trip**.
5. **Complete Trip**: Click **Complete Trip**. Input a final odometer reading (e.g., `12150 km`) and fuel consumption details. Verify that:
   * Vehicle and driver statuses change back to **Available**.
   * A fuel log record is automatically generated for the vehicle.
6. **Maintenance**: Create a maintenance record. Start the maintenance, and observe that the vehicle status changes to **In Shop** (hiding it from the trip selection). Complete the maintenance and observe that its status transitions back to **Available**.
7. **Dashboard & Analytics**: Open the **Fleet Dashboard** to view real-time calculations of total operational costs, fuel efficiency, and ROI graphs. Print the **Trip Details** to generate a PDF invoice-like report.
