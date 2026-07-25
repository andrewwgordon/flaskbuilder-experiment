---
name: flask-appbuilder
description: Comprehensive expert rules, architectural patterns, code templates, security guidelines, and domain-driven UI/UX design workflows for building web applications and REST APIs using the Flask-AppBuilder framework. Use when writing, reviewing, or refactoring Flask-AppBuilder (FAB) models, views, security handlers, REST APIs, or user interfaces.
---

# Flask-AppBuilder (FAB) Expert Skill

Flask-AppBuilder (FAB) is a rapid application development framework built on top of Flask and SQLAlchemy. It provides automated database-driven CRUD views, role-based security (RBAC), security audit logs, built-in REST APIs, internationalization, and Bootstrap integration.

When developing Flask-AppBuilder applications, strictly follow the architectural conventions, security protocols, code patterns, and domain-driven UI/UX design workflows detailed below.

---

## 1. Core Architecture & Project Structure

Organize Flask-AppBuilder applications using the Application Factory pattern with clean separation of concerns:

```
my_fab_app/
├── app/
│   ├── __init__.py          # App initialization & AppBuilder instance
│   ├── models.py            # SQLAlchemy models & FAB Mixins
│   ├── views.py             # ModelViews, BaseViews, & MasterDetailViews
│   ├── api.py               # ModelRestApi endpoints
│   ├── index.py             # Custom IndexView (optional)
│   ├── sec.py               # Custom SecurityManager & User Model (optional)
│   └── templates/           # Custom Jinja2 templates overriding FAB defaults
├── config.py                # FAB & Flask configuration
├── run.py                   # Entry point for development server
└── requirements.txt
```

---

## 2. Configuration (`config.py`)

Always configure database settings, authentication type, security settings, and FAB UI parameters in `config.py`:

```python
import os
from flask_appbuilder.security.manager import (
    AUTH_DB,
    AUTH_LDAP,
    AUTH_OAUTH,
    AUTH_OID,
    AUTH_REMOTE_USER,
)

basedir = os.path.abspath(os.path.dirname(__file__))

# --- Database Configuration ---
SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'app.db')}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# --- Security & Secret Keys ---
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-super-secret-key")
CSRF_ENABLED = True

# --- FAB Authentication Configuration ---
AUTH_TYPE = AUTH_DB  # Options: AUTH_DB, AUTH_LDAP, AUTH_OAUTH, AUTH_OID, AUTH_REMOTE_USER
AUTH_ROLE_ADMIN = "Admin"
AUTH_ROLE_PUBLIC = "Public"
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Public"

# --- Theme & Branding ---
APP_NAME = "Enterprise Portal"
APP_THEME = "bootstrap-flatly.css"  # Options: cerulean, cosmo, cyborg, flatly, journal, lumen, paper, etc.
FAB_ADD_SECURITY_VIEWS = True
```

---

## 3. Database Models & SQLAlchemy (`app/models.py`)

Models **must** inherit from FAB's `Model` base class (which provides metadata tracking and string representation utility) rather than raw `db.Model`. Use FAB audit mixins where tracking record changes is needed.

```python
from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Numeric
from sqlalchemy.orm import relationship

class Department(Model):
    __tablename__ = "department"

    id = Column(Integer, primary_order=True, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Employee(AuditMixin, Model):
    """
    AuditMixin automatically adds created_on, changed_on, created_by_fk, changed_by_fk
    and links them to the logged-in FAB user.
    """
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    hire_date = Column(Date, nullable=False)
    salary = Column(Numeric(10, 2), nullable=False)
    
    department_id = Column(Integer, ForeignKey("department.id"), nullable=False)
    department = relationship("Department", backref="employees")

    def __repr__(self):
        return f"{self.full_name} ({self.email})"
```

---

## 4. Model Views & UI (`app/views.py`)

FAB auto-generates CRUD forms and tables using `ModelView` wrapped around a `SQLAInterface`.

### Basic `ModelView` Setup
```python
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.sqla.filters import FilterStartsWith
from .models import Department, Employee

class DepartmentView(ModelView):
    datamodel = SQLAInterface(Department)
    
    # UI Customizations
    list_columns = ["name"]
    show_columns = ["name", "employees"]
    add_columns = ["name"]
    edit_columns = ["name"]
    
    search_columns = ["name"]


class EmployeeView(ModelView):
    datamodel = SQLAInterface(Employee)
    
    # Grid & Display Columns
    list_columns = ["full_name", "email", "department", "hire_date", "salary"]
    show_columns = [
        "full_name", "email", "department", "hire_date", "salary",
        "created_on", "created_by", "changed_on", "changed_by"
    ]
    
    # Order & Sorting
    base_order = ("full_name", "asc")
    
    # Form Layout & Exclusions
    add_columns = ["full_name", "email", "department", "hire_date", "salary"]
    edit_columns = ["full_name", "email", "department", "salary"]
    
    # Labels & Help Texts
    label_columns = {
        "full_name": "Employee Name",
        "department": "Assigned Department",
    }
    description_columns = {
        "salary": "Annual gross salary in USD."
    }
```

### Master-Detail & Multi-View Relations
To display parent-child views (e.g., Department and its list of Employees) on a single page:

```python
from flask_appbuilder import MasterDetailView, MultipleView

class EmployeeInlineView(ModelView):
    datamodel = SQLAInterface(Employee)
    list_columns = ["full_name", "email", "hire_date"]

class DepartmentMasterView(MasterDetailView):
    datamodel = SQLAInterface(Department)
    related_views = [EmployeeInlineView]
```

### Custom `BaseView` for Arbitrary Pages
Use `BaseView` with `@expose` and `@has_access` decorators to build non-CRUD custom dashboards:

```python
from flask_appbuilder import BaseView, expose, has_access

class AnalyticsView(BaseView):
    default_view = "summary"

    @expose("/summary/")
    @has_access
    def summary(self):
        # Business logic / data fetching
        metrics = {"total_revenue": 105000, "active_users": 1420}
        return self.render_template("analytics_summary.html", metrics=metrics)
```

---

## 5. REST APIs (`app/api.py`)

FAB provides OpenAPI/Swagger documented REST APIs out of the box using `ModelRestApi`.

```python
from flask_appbuilder.api import ModelRestApi, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from .models import Employee

class EmployeeApi(ModelRestApi):
    datamodel = SQLAInterface(Employee)
    resource_name = "employee"
    
    # Control accessible API fields
    list_columns = ["id", "full_name", "email", "department.name"]
    show_columns = ["id", "full_name", "email", "hire_date", "salary", "department_id"]
    add_columns = ["full_name", "email", "hire_date", "salary", "department_id"]
    edit_columns = ["full_name", "email", "salary", "department_id"]
    
    # Enable search filtering on endpoints
    search_columns = ["full_name", "email", "department_id"]
```

---

## 6. App Initialization (`app/__init__.py`)

Construct the app using the Application Factory pattern and register views with categories/menus:

```python
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_appbuilder import AppBuilder, SQLA

db = SQLA()
appbuilder = AppBuilder()

def create_app(config_object="config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)

    with app.app_context():
        # Register AppBuilder
        appbuilder.init_app(app, db.session)

        # Import Views & APIs after DB init
        from .views import DepartmentView, EmployeeView, DepartmentMasterView, AnalyticsView
        from .api import EmployeeApi

        # Add Views to Navigation Menu
        appbuilder.add_view(
            DepartmentView,
            "Departments",
            icon="fa-folder-open",
            category="Organization",
            category_icon="fa-sitemap"
        )
        appbuilder.add_view(
            EmployeeView,
            "Employees",
            icon="fa-users",
            category="Organization"
        )
        appbuilder.add_view(
            DepartmentMasterView,
            "Master-Detail View",
            icon="fa-layer-group",
            category="Organization"
        )
        appbuilder.add_view(
            AnalyticsView,
            "Dashboard",
            icon="fa-chart-line",
            category="Analytics"
        )

        # Add REST API endpoints
        appbuilder.add_api(EmployeeApi)

    return app
```

---

## 7. Security & Row-Level Security (RLS)

Flask-AppBuilder handles authentication, roles, view permissions, and action permissions.

### Restricting Access via Custom Filters
To restrict a logged-in user so they only view their own department's employees, override `base_filters` on `ModelView`:

```python
from flask import g
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.sqla.filters import BaseFilter
from .models import Employee

class FilterEmployeeByDepartment(BaseFilter):
    name = "Filter Employee by User Department"
    arg_name = "dept"

    def apply(self, query, value):
        # Assuming current user profile has department_id attribute
        user_dept_id = getattr(g.user, "department_id", None)
        if user_dept_id:
            return query.filter(Employee.department_id == user_dept_id)
        return query

class MyScopedEmployeeView(ModelView):
    datamodel = SQLAInterface(Employee)
    base_filters = [["department_id", FilterEmployeeByDepartment, None]]
```

### Custom Security Manager Overrides
When extending user registration or custom LDAP/OAuth payload mapping, create a custom `SecurityManager`:

```python
# app/sec.py
from flask_appbuilder.security.sqla.manager import SecurityManager

class CustomSecurityManager(SecurityManager):
    def create_user_profile(self, user_info):
        # Custom logic when user authenticates via OAuth/LDAP
        user = super().create_user_profile(user_info)
        # Custom post-creation logic here
        return user
```

In `config.py`:
```python
from app.sec import CustomSecurityManager

SECURITY_MANAGER_CLASS = CustomSecurityManager
```

---

## 8. Domain-Driven UI/UX, Layout & Workflow Design

The user interface, page hierarchy, layout constructs, and operational workflows in FAB must be directly derived from the underlying domain model structure (bounded contexts, aggregate roots, entities, relationships, and state transitions).

### A. Mapping Domain Concepts to FAB Views

| Domain Model Element | Structural UX Mapping | Recommended FAB Component | UI Pattern & Layout |
| :--- | :--- | :--- | :--- |
| **Aggregate Root** | Top-level business entity and entry point. | `ModelView` / `MasterDetailView` | Standard table view with search filters and detail panels. |
| **Child Entity / Value Object** | Secondary records dependent on an Aggregate Root (e.g., Order Items). | `CompactCRUDMixin` / `related_views` | Rendered as inline detail tables within the Aggregate Root's show page or tabbed layout. |
| **1-to-Many Relationships** | Parent-Child relationship requiring unified context navigation. | `MasterDetailView` or `MultipleView` | Split-view layout (Parent header on top, child list below) or tabbed child grids. |
| **Many-to-Many / Join Tables** | Cross-domain associations (e.g., User Roles, Tagging). | `ModelView` with `add_form_query_rel_fields` | Select2 multi-select widgets or inline table tags with quick search modal interfaces. |
| **Domain State Transitions** | Lifecycle status changes (e.g., Draft $\to$ Submitted $\to$ Approved). | `@action` methods in `ModelView` | Contextual action buttons on list/show views with security permission checks. |

---

### B. Designing Workflows & State Transitions

When domain entities follow state workflows (e.g., approving an expense report or processing an order):

1. **Contextual Actions:** Implement state transition methods using FAB `@action` decorators instead of exposing arbitrary edit forms.
2. **Visual Status Indicators:** Map domain state fields to badges or icons in `list_columns` using custom formatter functions.
3. **Form Layout Fieldsets:** Group fields logically based on domain sub-concepts using `fieldsets`.

#### Domain Workflow Pattern Example:
```python
from flask import flash, redirect
from flask_appbuilder import ModelView, action
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.widgets import ListWidget
from markupsafe import Markup
from .models import Order

def status_formatter(view, value):
    """Formats domain state with visually distinct Bootstrap badges."""
    badge_class = {
        "DRAFT": "secondary",
        "PENDING": "warning",
        "APPROVED": "success",
        "REJECTED": "danger",
    }.get(value, "dark")
    return Markup(f'<span class="badge badge-{badge_class}">{value}</span>')


class OrderView(ModelView):
    datamodel = SQLAInterface(Order)

    # Layout & Navigation driven by Domain Model
    list_columns = ["order_number", "customer", "total_amount", "status"]
    formatters_columns = {"status": status_formatter}
    
    # Fieldsets group related domain properties visually on forms
    edit_fieldsets = [
        (
            "Order Header",
            {"fields": ["order_number", "customer", "order_date"]}
        ),
        (
            "Financial Details",
            {"fields": ["subtotal", "tax", "total_amount"], "expanded": True}
        ),
    ]

    # Domain Action: Submit Draft Order
    @action("submit_order", "Submit Order", "Submit selected draft orders?", "fa-paper-plane", single=True)
    def submit_order(self, item):
        if item.status != "DRAFT":
            flash("Only DRAFT orders can be submitted.", "warning")
            return redirect(self.get_redirect())

        item.status = "PENDING"
        self.datamodel.edit(item)
        flash(f"Order {item.order_number} submitted for approval.", "info")
        return redirect(self.get_redirect())

    # Domain Action: Batch Approve Orders
    @action("approve_orders", "Approve Orders", "Approve all selected pending orders?", "fa-check-circle", single=False)
    def approve_orders(self, items):
        approved_count = 0
        for order in items:
            if order.status == "PENDING":
                order.status = "APPROVED"
                self.datamodel.edit(order)
                approved_count += 1

        flash(f"Successfully approved {approved_count} orders.", "success")
        return redirect(self.get_redirect())
```

---

### C. Application Menu Structure & Navigation Hierarchy

Organize menu items using Domain-Driven Design (DDD) bounded contexts:

```python
# app/__init__.py navigation configuration grouped by domain context

# 1. Bounded Context: Sales & Procurement
appbuilder.add_view(
    CustomerView, "Customers", icon="fa-user-tie", category="Sales Domain"
)
appbuilder.add_view(
    OrderView, "Orders", icon="fa-shopping-cart", category="Sales Domain"
)

# 2. Bounded Context: Warehouse & Inventory
appbuilder.add_view(
    ProductView, "Products", icon="fa-box", category="Inventory Domain"
)
appbuilder.add_view(
    StockLevelView, "Stock Levels", icon="fa-warehouse", category="Inventory Domain"
)

# 3. Bounded Context: System & Administration
appbuilder.add_view(
    AuditLogView, "Audit Trail", icon="fa-history", category="System Settings"
)
```

---

## 9. Command Line Interface (CLI) Commands

Manage FAB applications using `flask fab` CLI tools:

* **Create Admin User:**
  ```bash
  flask fab create-admin
  ```
* **Reset User Password:**
  ```bash
  flask fab reset-password
  ```
* **List Registered Views & Permissions:**
  ```bash
  flask fab list-views
  flask fab list-user-perms
  ```
* **Create Custom App Template:**
  ```bash
  fabmanager create-app --name my_app --engine SQLAlchemy
  ```

---

## 10. Critical Anti-Patterns & Best Practices

| Do's | Don'ts |
| :--- | :--- |
| **Do** subclass `flask_appbuilder.Model` for all database models. | **Don't** subclass standard `db.Model` directly, as FAB views require `Model` metadata wrappers. |
| **Do** wrap model classes in `SQLAInterface(MyModel)` when binding to FAB views/APIs. | **Don't** pass raw SQLAlchemy model classes into `datamodel = MyModel`. |
| **Do** drive screen layouts (fieldsets, master-detail views, actions) based on domain bounded contexts. | **Don't** expose unstructured CRUD forms with all database columns exposed unconditionally. |
| **Do** use FAB `@action` decorators to model domain state transitions safely. | **Don't** allow users to manually edit workflow status fields in standard edit forms. |
| **Don't** import models inside `views.py` before `db` is initialized. | **Do** follow the app factory pattern to prevent circular imports. |
| **Do** use `@has_access` or `@has_access_api` on custom view endpoints. | **Don't** leave custom `@expose` endpoints unprotected without explicit security checks. |
| **Do** utilize `AuditMixin` for regulatory compliance and audit logs. | **Don't** write manual `created_by` / `updated_by` logic when FAB mixins automate it natively. |