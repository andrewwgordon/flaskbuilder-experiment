import os
import sys

# Ensure CODESPACES is false during testing so SERVER_NAME isn't set to external domain
os.environ["CODESPACES"] = "false"

import pytest

# Ensure the app package is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.pool import StaticPool

from app import create_app
from app.extensions import appbuilder, db
from app.models import (
    DomainTarget,
    PartyType,
    PersonOrganizationSelect,
    Project,
    ProjectBaseline,
    Requirement,
    RequirementReview,
    RequirementSatisfactionAssertion,
    RequirementVersion,
    RequirementView,
    StringValue,
    TargetType,
    ValueWithUnit,
    VersionStatus,
)


@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app instance for testing."""
    test_app = create_app()
    test_app.config.update(
        {
            "TESTING": True,
            "SERVER_NAME": None,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "poolclass": StaticPool,
                "connect_args": {"check_same_thread": False},
            },
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key-for-pytest",
            "PRESERVE_CONTEXT_ON_EXCEPTION": False,
        }
    )
    yield test_app


from flask_appbuilder import Model


@pytest.fixture
def db_session(app):
    """Provide a clean database session for each test."""
    with app.app_context():
        db.session.remove()
        Model.metadata.drop_all(bind=db.engine)
        Model.metadata.create_all(bind=db.engine)

        # Initialize FAB security manager database schema and default roles
        appbuilder.sm.create_db()
        appbuilder.add_permissions(update_perms=True)

        yield db.session

        db.session.rollback()
        db.session.remove()
        Model.metadata.drop_all(bind=db.engine)


@pytest.fixture
def client(app, db_session):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def admin_user(app, db_session):
    """Create a default admin user for authentication tests."""
    role_admin = appbuilder.sm.find_role(appbuilder.sm.auth_role_admin)
    user = appbuilder.sm.find_user(username="test_admin")
    if not user:
        user = appbuilder.sm.add_user(
            username="test_admin",
            first_name="Test",
            last_name="Admin",
            email="admin@test.com",
            role=role_admin,
            password="password123",
        )
    return user



@pytest.fixture
def auth_client(client, admin_user):
    """Flask test client authenticated as admin user for web views."""
    client.post(
        "/login/",
        data={"username": "test_admin", "password": "password123"},
        follow_redirects=True,
    )
    return client


@pytest.fixture
def api_client(client, admin_user):
    """Flask test client with JWT authorization header for FAB REST API endpoints."""
    login_payload = {
        "username": "test_admin",
        "password": "password123",
        "provider": "db",
    }
    response = client.post(
        "/api/v1/security/login",
        json=login_payload,
    )
    if response.status_code == 200:
        token = response.get_json().get("access_token")
        client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    return client


@pytest.fixture
def sample_data(app, db_session, admin_user):
    """Create sample domain model entities for testing."""
    from flask import g
    with app.test_request_context():
        g.user = admin_user

        project = Project(
            project_code="PRJ-101",
            name="Avionics Flight System",
            description="Flight control system specification",
            created_by=admin_user,
            changed_by=admin_user,
        )
        db_session.add(project)

        owner = PersonOrganizationSelect(
            name="Dr. Jane Doe",
            party_type=PartyType.PERSON,
            email="jane.doe@example.com",
            organization_name="Systems Engineering Dept",
            created_by=admin_user,
            changed_by=admin_user,
        )
        db_session.add(owner)
        db_session.commit()

        req = Requirement(
            project_id=project.id,
            req_key="REQ-SYS-001",
            title="Emergency Power Supply",
            owner_id=owner.id,
            created_by=admin_user,
            changed_by=admin_user,
        )
        db_session.add(req)
        db_session.commit()

        ver_draft = RequirementVersion(
            requirement_id=req.id,
            version_label="1.0-DRAFT",
            status=VersionStatus.DRAFT,
            created_by=admin_user,
            changed_by=admin_user,
        )
        ver_in_review = RequirementVersion(
            requirement_id=req.id,
            version_label="1.0-REVIEW",
            status=VersionStatus.IN_REVIEW,
            created_by=admin_user,
            changed_by=admin_user,
        )
        ver_approved = RequirementVersion(
            requirement_id=req.id,
            version_label="1.0",
            status=VersionStatus.APPROVED,
            created_by=admin_user,
            changed_by=admin_user,
        )
        db_session.add_all([ver_draft, ver_in_review, ver_approved])
        db_session.commit()

        req_view = RequirementView(
            version_id=ver_approved.id,
            view_name="Electrical Performance View",
            created_by=admin_user,
            changed_by=admin_user,
        )
        db_session.add(req_view)
        db_session.commit()

        prop_string = StringValue(
            requirement_view_id=req_view.id,
            name="Functional Description",
            text_content="Power supply must switch to battery backup within 10ms of primary failure.",
            created_by=admin_user,
            changed_by=admin_user,
        )
        prop_unit = ValueWithUnit(
            requirement_view_id=req_view.id,
            name="Backup Runtime",
            numeric_value=30.0,
            unit="minutes",
            created_by=admin_user,
            changed_by=admin_user,
        )
        db_session.add_all([prop_string, prop_unit])

        target = DomainTarget(
            target_type=TargetType.PART,
            name="Main Power Management Unit",
            identifier="HW-PMU-200",
            created_by=admin_user,
            changed_by=admin_user,
        )
        db_session.add(target)
        db_session.commit()

        assertion = RequirementSatisfactionAssertion(
            requirement_view_id=req_view.id,
            target_id=target.id,
            assertion_statement="Tested via hardware-in-the-loop bench test #402",
            asserted_by_id=owner.id,
            asserted_at=ver_approved.created_on or None,
            created_by=admin_user,
            changed_by=admin_user,
        )
        review = RequirementReview(
            version_id=ver_in_review.id,
            reviewer_id=owner.id,
            comments="Looks good, pending thermal validation.",
            recommended_status=VersionStatus.APPROVED,
            created_by=admin_user,
            changed_by=admin_user,
        )
        db_session.add_all([assertion, review])

        baseline = ProjectBaseline(
            project_id=project.id,
            baseline_name="PDR Baseline v1",
            release_date=ver_approved.created_on or None,
            created_by=admin_user,
            changed_by=admin_user,
        )
        baseline.versions.append(ver_approved)
        db_session.add(baseline)
        db_session.commit()

        return {
            "project": project,
            "owner": owner,
            "requirement": req,
            "ver_draft": ver_draft,
            "ver_in_review": ver_in_review,
            "ver_approved": ver_approved,
            "req_view": req_view,
            "prop_string": prop_string,
            "prop_unit": prop_unit,
            "target": target,
            "assertion": assertion,
            "review": review,
            "baseline": baseline,
        }
