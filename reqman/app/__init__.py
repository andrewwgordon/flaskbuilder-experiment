from flask import Flask, app
from werkzeug.middleware.proxy_fix import ProxyFix
from .extensions import db
from .extensions import appbuilder


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")
    # Tell Flask to trust the proxy headers forwarded by GitHub Codespaces
    # x_host=1 tells it to trust the dynamic *.app.github.dev host header
    app.wsgi_app = ProxyFix(
       app.wsgi_app, 
       x_for=1, 
       x_proto=1, 
       x_host=1, 
       x_port=1
   )
    with app.app_context():
        db.init_app(app)

        # Import Views & APIs after DB init to avoid circular imports
        from .views import (
            DashboardIndexView,
            ProjectMasterView,
            RequirementCRUDView,
            RequirementVersionView,
            RequirementViewView,
            StringValueView,
            ValueWithUnitView,
            RequirementSatisfactionAssertionView,
            RequirementReviewView,
            ProjectBaselineMasterView,
            ReviewerDashboardView,
            DomainTargetView,
            PersonOrganizationSelectView,
            page_not_found,
        )
        from .api import (
            ProjectApi,
            RequirementApi,
            RequirementVersionApi,
            RequirementViewApi,
            ProjectBaselineApi,
            DomainTargetApi,
        )

        # Initialize AppBuilder with Flask app and DB session
        appbuilder.init_app(app, db.session)

        # 1. Bounded Context: Requirements Domain
        appbuilder.add_view(
            ProjectMasterView,
            "Projects",
            icon="fa-cubes",
            category="Requirements Domain",
            category_icon="fa-tasks",
        )
        appbuilder.add_view(
            RequirementCRUDView,
            "All Requirements",
            icon="fa-list-alt",
            category="Requirements Domain",
        )
        appbuilder.add_view(
            RequirementVersionView,
            "Version History & Actions",
            icon="fa-history",
            category="Requirements Domain",
        )

        # 2. Bounded Context: Quality & Verification
        appbuilder.add_view(
            ReviewerDashboardView,
            "Reviewer Inbox",
            icon="fa-check-square-o",
            category="Quality & Verification",
            category_icon="fa-check-square-o",
        )
        appbuilder.add_view(
            ProjectBaselineMasterView,
            "Project Baselines",
            icon="fa-bookmark",
            category="Quality & Verification",
        )
        appbuilder.add_view(
            RequirementSatisfactionAssertionView,
            "Satisfaction Assertions",
            icon="fa-check-circle",
            category="Quality & Verification",
        )
        appbuilder.add_view(
            RequirementReviewView,
            "Review Log",
            icon="fa-comments",
            category="Quality & Verification",
        )

        # 3. Bounded Context: System Configuration
        appbuilder.add_view(
            RequirementViewView,
            "Requirement Views",
            icon="fa-eye",
            category="System Configuration",
            category_icon="fa-cogs",
        )
        appbuilder.add_view(
            StringValueView,
            "Text Properties",
            icon="fa-file-text-o",
            category="System Configuration",
        )
        appbuilder.add_view(
            ValueWithUnitView,
            "Numeric Properties",
            icon="fa-calculator",
            category="System Configuration",
        )
        appbuilder.add_view(
            DomainTargetView,
            "System Targets (Parts/Docs)",
            icon="fa-database",
            category="System Configuration",
        )
        appbuilder.add_view(
            PersonOrganizationSelectView,
            "Parties & Owners",
            icon="fa-id-card",
            category="System Configuration",
        )

        # 6. REST API Endpoints
        appbuilder.add_api(ProjectApi)
        appbuilder.add_api(RequirementApi)
        appbuilder.add_api(RequirementVersionApi)
        appbuilder.add_api(RequirementViewApi)
        appbuilder.add_api(ProjectBaselineApi)
        appbuilder.add_api(DomainTargetApi)

        from flask_appbuilder import Model
        Model.metadata.create_all(db.engine)

        app.register_error_handler(404, page_not_found)

    return app

