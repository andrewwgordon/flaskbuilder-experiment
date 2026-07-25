import pytest

from app.extensions import appbuilder
from app.models import RequirementVersion, VersionStatus
from app.views import RequirementVersionView, status_badge_formatter


def test_status_badge_formatter():
    badge_draft = status_badge_formatter(VersionStatus.DRAFT)
    assert "label-default" in str(badge_draft)
    assert "DRAFT" in str(badge_draft) or "Draft" in str(badge_draft)

    badge_review = status_badge_formatter(VersionStatus.IN_REVIEW)
    assert "label-warning" in str(badge_review)

    badge_approved = status_badge_formatter(VersionStatus.APPROVED)
    assert "label-success" in str(badge_approved)

    badge_rejected = status_badge_formatter(VersionStatus.REJECTED)
    assert "label-danger" in str(badge_rejected)

    badge_baselined = status_badge_formatter(VersionStatus.BASELINED)
    assert "label-primary" in str(badge_baselined)

    badge_superseded = status_badge_formatter(VersionStatus.SUPERSEDED)
    assert "label-info" in str(badge_superseded)


def test_dashboard_index_view(auth_client, sample_data):
    response = auth_client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Avionics Flight System" in html
    assert "PRJ-101" in html


def test_reviewer_dashboard_view_authenticated(auth_client, sample_data):
    response = auth_client.get("/reviewerdashboardview/pending/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    # The sample_data fixture contains one version in IN_REVIEW status: "1.0-REVIEW"
    assert "1.0-REVIEW" in html


def test_reviewer_dashboard_view_unauthenticated(client):
    response = client.get("/reviewerdashboardview/pending/")
    # Unauthenticated user should be redirected to login
    assert response.status_code == 302
    assert "/login/" in response.location


def test_version_pre_update_immutability(sample_data, admin_user):
    view = RequirementVersionView()

    # APPROVED or BASELINED versions must raise an exception on update
    ver_approved = sample_data["ver_approved"]
    with pytest.raises(Exception) as exc_info:
        view.pre_update(ver_approved)
    assert "read-only" in str(exc_info.value)

    ver_baselined = RequirementVersion(
        requirement_id=sample_data["requirement"].id,
        version_label="0.9-BASELINED",
        status=VersionStatus.BASELINED,
        created_by=admin_user,
        changed_by=admin_user,
    )
    with pytest.raises(Exception) as exc_info:
        view.pre_update(ver_baselined)
    assert "read-only" in str(exc_info.value)

    # DRAFT or IN_REVIEW versions pass pre_update without raising
    ver_draft = sample_data["ver_draft"]
    view.pre_update(ver_draft)  # Should not raise exception


def test_action_submit_for_review(app, db_session, sample_data):
    with app.test_request_context("/"):
        view = RequirementVersionView()
        view.appbuilder = appbuilder

        ver_draft = sample_data["ver_draft"]
        assert ver_draft.status == VersionStatus.DRAFT

        view.submit_for_review([ver_draft])
        assert ver_draft.status == VersionStatus.IN_REVIEW


def test_action_approve_version(app, db_session, sample_data):
    with app.test_request_context("/"):
        view = RequirementVersionView()
        view.appbuilder = appbuilder

        ver_in_review = sample_data["ver_in_review"]
        assert ver_in_review.status == VersionStatus.IN_REVIEW

        view.approve_version([ver_in_review])
        assert ver_in_review.status == VersionStatus.APPROVED


def test_action_request_changes(app, db_session, sample_data):
    with app.test_request_context("/"):
        view = RequirementVersionView()
        view.appbuilder = appbuilder

        ver_in_review = sample_data["ver_in_review"]
        assert ver_in_review.status == VersionStatus.IN_REVIEW

        view.request_changes([ver_in_review])
        assert ver_in_review.status == VersionStatus.CHANGES_REQUESTED


def test_invalid_state_transition_actions(app, db_session, sample_data):
    with app.test_request_context("/"):
        view = RequirementVersionView()
        view.appbuilder = appbuilder

        ver_approved = sample_data["ver_approved"]

        # Attempting submit_for_review on an APPROVED version should not change status
        view.submit_for_review([ver_approved])
        assert ver_approved.status == VersionStatus.APPROVED

        # Attempting approve_version on a DRAFT version should not change status
        ver_draft = sample_data["ver_draft"]
        view.approve_version([ver_draft])
        assert ver_draft.status == VersionStatus.DRAFT


def test_model_views_list_access(auth_client, sample_data):
    endpoints = [
        "/projectmasterview/list/",
        "/requirementcrudview/list/",
        "/requirementversionview/list/",
        "/personorganizationselectview/list/",
        "/domaintargetview/list/",
        "/projectbaselinemasterview/list/",
    ]
    for endpoint in endpoints:
        response = auth_client.get(endpoint)
        assert response.status_code == 200, f"Failed accessing {endpoint}"
