# REQMan - Enterprise Systems Engineering Requirements Management System

REQMan is a web application and REST API built with **Flask-AppBuilder (FAB)** and **SQLAlchemy**. Designed following Domain-Driven Design (DDD) principles and Model-Driven UI/UX patterns, REQMan helps engineering teams track multi-project requirements, enforce lifecycle governance, manage multi-perspective views, capture traceability & decomposition, and release baselines.

---

## Key Features

* **Executive Dashboard**: Unified landing page with real-time KPI metrics (Active Projects, Requirements, Pending Reviews, Baselines) and project portfolio quick-access cards.
* **Domain-Driven Menu Structure**: Consolidated, intuitive navigation organized into 3 bounded contexts:
  * **Requirements Domain**: Projects portfolio, requirement master views, and version lifecycle management.
  * **Quality & Verification**: Reviewer Inbox dashboard for pending approvals, release baselines, review feedback logs, and satisfaction assertions.
  * **System Configuration**: Multi-perspective requirement views, polymorphic property values (Text & Value-With-Unit), system target entities (Parts, Documents), and parties/owners.
* **Lifecycle Governance & Immutability**:
  * Formal version state workflow: `Draft` $\rightarrow$ `In Review` $\rightarrow$ `Approved` / `Changes Requested` $\rightarrow$ `Baselined` / `Superseded`.
  * Enforced immutability on `Approved` and `Baselined` requirements.
  * Custom FAB `@action` handlers (`submit_for_review`, `approve_version`, `request_changes`).
* **Visual Status Formatting**: Status indicators rendered with color-coded Bootstrap badges across tables and inline lists.
* **Built-in OpenAPI/Swagger REST APIs**: Automated CRUD API endpoints (`/api/v1/project`, `/api/v1/requirement`, `/api/v1/requirementversion`, `/api/v1/projectbaseline`, `/api/v1/domaintarget`).
* **Role-Based Security (RBAC)**: Fine-grained user access control, authentication, and security audit logs provided natively by Flask-AppBuilder.

---

## Technology Stack

* **Core Framework**: [Flask-AppBuilder](https://flask-appbuilder.readthedocs.io/)
* **Backend Language**: Python 3.12+
* **Database & ORM**: SQLAlchemy with SQLite (configurable to PostgreSQL/MySQL)
* **Frontend / UI**: Bootstrap 3 (via FAB template engine), FontAwesome Icons, Jinja2 Templates
* **API Documentation**: OpenAPI / Swagger (integrated via Flask-AppBuilder REST APIs)
* **Internationalization**: Babel (English, Portuguese, Spanish, German, Polish support)

---

## Project Structure

```
flaskbuilder-experiment/
├── docs/
│   └── plan.md               # Domain architecture & specification
├── reqman/
│   ├── app/
│   │   ├── __init__.py       # Application factory & DDD menu registration
│   │   ├── api.py            # ModelRestApi endpoints
│   │   ├── extensions.py     # Database & AppBuilder extensions initialization
│   │   ├── models.py         # SQLAlchemy domain models & FAB AuditMixins
│   │   ├── views.py          # ModelViews, MasterDetailViews, & Dashboard views
│   │   └── templates/
│   │       ├── dashboard.html           # Executive KPI dashboard
│   │       └── reviewer_dashboard.html  # Reviewer inbox dashboard
│   ├── config.py             # Database, security, and FAB configuration
│   ├── run.py                # Development server entry point
│   └── seed.py               # Seed script for sample projects & requirements
└── README.md
```

---

## Getting Started

### Prerequisites

* Python 3.10+
* `pip` / `virtualenv`

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/andrewwgordon/flaskbuilder-experiment.git
   cd flaskbuilder-experiment
   ```

2. **Set up a virtual environment and install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Initialize database & seed sample data:**
   ```bash
   cd reqman
   python seed.py
   ```
   *Note: `seed.py` creates the SQLite database (`app.db`), builds tables, creates an initial admin user (`admin` / `admin`), and populates sample projects and requirements.*

4. **Run the development server:**
   ```bash
   python run.py
   ```
   Or using the Flask CLI:
   ```bash
   export FLASK_APP=./app/__init__.py
   flask run
   ```

5. **Access the application:**
   Open your browser and navigate to `http://localhost:5000/`. Log in with:
   * **Username**: `admin`
   * **Password**: `admin`

---

## License

Distributed under the MIT License. See `LICENSE` for details.
