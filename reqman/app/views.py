from flask import flash, redirect, render_template
from flask_appbuilder import (
    BaseView,
    IndexView,
    MasterDetailView,
    ModelView,
    action,
    expose,
    has_access,
)
from flask_appbuilder.models.sqla.interface import SQLAInterface
from markupsafe import Markup

from .models import (
    DomainTarget,
    PersonOrganizationSelect,
    Project,
    ProjectBaseline,
    Requirement,
    RequirementReview,
    RequirementSatisfactionAssertion,
    RequirementVersion,
    RequirementView,
    StringValue,
    ValueWithUnit,
    VersionStatus,
)


def status_badge_formatter(value):
    """Formats VersionStatus enums with visually distinct Bootstrap badges."""
    status_str = value.value if hasattr(value, "value") else str(value)
    badge_class = {
        "Draft": "default",
        "In Review": "warning",
        "Changes Requested": "danger",
        "Approved": "success",
        "Rejected": "danger",
        "Baselined": "primary",
        "Superseded": "info",
        "DRAFT": "default",
        "IN_REVIEW": "warning",
        "CHANGES_REQUESTED": "danger",
        "APPROVED": "success",
        "REJECTED": "danger",
        "BASELINED": "primary",
        "SUPERSEDED": "info",
    }.get(status_str, "default")
    return Markup(f'<span class="label label-{badge_class}">{status_str}</span>')


class DashboardIndexView(IndexView):
    index_template = "dashboard.html"

    @expose("/")
    def index(self):
        session = self.appbuilder.session
        projects = session.query(Project).all()
        total_projects = len(projects)
        total_requirements = session.query(Requirement).count()
        pending_reviews_count = session.query(RequirementVersion).filter_by(
            status=VersionStatus.IN_REVIEW).count()
        total_baselines = session.query(ProjectBaseline).count()

        project_summaries = []
        for proj in projects:
            req_count = session.query(Requirement).filter_by(
                project_id=proj.id).count()
            baseline_count = session.query(
                ProjectBaseline).filter_by(project_id=proj.id).count()
            project_summaries.append({
                "project": proj,
                "req_count": req_count,
                "baseline_count": baseline_count
            })

        return self.render_template(
            self.index_template,
            appbuilder=self.appbuilder,
            projects=projects,
            project_summaries=project_summaries,
            total_projects=total_projects,
            total_requirements=total_requirements,
            pending_reviews_count=pending_reviews_count,
            total_baselines=total_baselines,
        )


class PersonOrganizationSelectView(ModelView):
    datamodel = SQLAInterface(PersonOrganizationSelect)
    list_columns = ["name", "party_type", "email", "organization_name"]
    show_columns = ["name", "party_type", "email", "organization_name"]
    add_columns = ["name", "party_type", "email", "organization_name"]
    edit_columns = ["name", "party_type", "email", "organization_name"]
    search_columns = ["name", "party_type", "organization_name"]


class DomainTargetView(ModelView):
    datamodel = SQLAInterface(DomainTarget)
    list_columns = ["identifier", "name", "target_type"]
    show_columns = ["identifier", "name", "target_type"]
    add_columns = ["identifier", "name", "target_type"]
    edit_columns = ["identifier", "name", "target_type"]
    search_columns = ["identifier", "name", "target_type"]


class RequirementInlineView(ModelView):
    datamodel = SQLAInterface(Requirement)
    list_columns = ["req_key", "title", "owner"]
    add_columns = ["req_key", "title", "owner", "project"]
    edit_columns = ["req_key", "title", "owner"]


class ProjectMasterView(MasterDetailView):
    datamodel = SQLAInterface(Project)
    related_views = [RequirementInlineView]
    list_columns = ["project_code", "name"]
    show_columns = ["project_code", "name", "description"]
    add_columns = ["project_code", "name", "description"]
    edit_columns = ["project_code", "name", "description"]
    add_fieldsets = [
        ("Project Details", {"fields": [
         "project_code", "name", "description"]})
    ]
    edit_fieldsets = [
        ("Project Details", {"fields": [
         "project_code", "name", "description"]})
    ]


class RequirementViewView(ModelView):
    datamodel = SQLAInterface(RequirementView)
    list_columns = ["version", "view_name"]
    show_columns = ["version", "view_name",
                    "properties", "satisfaction_assertions"]
    add_columns = ["version", "view_name"]
    edit_columns = ["view_name"]


class RequirementVersionView(ModelView):
    datamodel = SQLAInterface(RequirementVersion)
    list_columns = ["requirement.req_key", "version_label",
                    "status", "changed_on", "changed_by"]
    show_columns = ["requirement", "version_label",
                    "status", "revision_date", "views", "reviews"]
    add_columns = ["requirement", "version_label", "status", "revision_date"]
    edit_columns = ["version_label", "status", "revision_date"]
    search_columns = ["status", "version_label"]
    formatters_columns = {"status": status_badge_formatter}

    add_fieldsets = [
        ("Version Info", {"fields": [
         "requirement", "version_label", "status", "revision_date"]})
    ]
    edit_fieldsets = [
        ("Version Revision", {"fields": [
         "version_label", "status", "revision_date"]})
    ]

    def pre_update(self, item):
        if item.status in [VersionStatus.APPROVED, VersionStatus.BASELINED]:
            raise ValueError(
                "Approved or Baselined requirement versions are read-only. Create a new revision.")

    @action("submit_for_review", "Submit for Review", "Submit selected draft(s) for formal review?", "fa-paper-plane", single=True)
    def submit_for_review(self, items):
        for item in items:
            if item.status == VersionStatus.DRAFT:
                item.status = VersionStatus.IN_REVIEW
                self.datamodel.edit(item)
                flash(f"{item} submitted for review.", "info")
            else:
                flash(
                    f"Cannot submit {item}: Only Drafts can be submitted.", "warning")
        return redirect(self.get_redirect())

    @action("approve_version", "Approve Requirement", "Approve selected requirement version(s)?", "fa-check-circle", single=True)
    def approve_version(self, items):
        for item in items:
            if item.status == VersionStatus.IN_REVIEW:
                item.status = VersionStatus.APPROVED
                self.datamodel.edit(item)
                flash(f"{item} successfully approved.", "success")
            else:
                flash(
                    f"Cannot approve {item}: Must be 'In Review'.", "warning")
        return redirect(self.get_redirect())

    @action("request_changes", "Request Revisions", "Request revisions on selected version?", "fa-undo", single=True)
    def request_changes(self, items):
        for item in items:
            if item.status == VersionStatus.IN_REVIEW:
                item.status = VersionStatus.CHANGES_REQUESTED
                self.datamodel.edit(item)
                flash(f"Revisions requested for {item}.", "warning")
        return redirect(self.get_redirect())


class RequirementCRUDView(ModelView):
    datamodel = SQLAInterface(Requirement)
    list_columns = ["project", "req_key", "title", "owner"]
    show_columns = ["project", "req_key", "title", "owner", "versions"]
    add_columns = ["project", "req_key", "title", "owner"]
    edit_columns = ["project", "req_key", "title", "owner"]
    search_columns = ["req_key", "title", "project"]


class StringValueView(ModelView):
    datamodel = SQLAInterface(StringValue)
    list_columns = ["requirement_view", "name", "text_content"]
    add_columns = ["requirement_view", "name", "text_content"]
    edit_columns = ["name", "text_content"]


class ValueWithUnitView(ModelView):
    datamodel = SQLAInterface(ValueWithUnit)
    list_columns = ["requirement_view", "name", "numeric_value", "unit"]
    add_columns = ["requirement_view", "name", "numeric_value", "unit"]
    edit_columns = ["name", "numeric_value", "unit"]


class RequirementSatisfactionAssertionView(ModelView):
    datamodel = SQLAInterface(RequirementSatisfactionAssertion)
    list_columns = ["requirement_view", "target",
                    "assertion_statement", "asserted_by", "asserted_at"]
    add_columns = ["requirement_view", "target",
                   "assertion_statement", "asserted_by", "asserted_at"]
    edit_columns = ["assertion_statement", "asserted_by", "asserted_at"]


class RequirementReviewView(ModelView):
    datamodel = SQLAInterface(RequirementReview)
    list_columns = ["version", "reviewer", "recommended_status", "comments"]
    add_columns = ["version", "reviewer", "recommended_status", "comments"]
    edit_columns = ["recommended_status", "comments"]


class BaselineInlineView(ModelView):
    datamodel = SQLAInterface(RequirementVersion)
    list_columns = ["requirement.req_key", "version_label", "status"]
    formatters_columns = {"status": status_badge_formatter}


class ProjectBaselineMasterView(MasterDetailView):
    datamodel = SQLAInterface(ProjectBaseline)
    related_views = [BaselineInlineView]
    list_columns = ["project", "baseline_name", "release_date"]
    show_columns = ["project", "baseline_name", "release_date", "versions"]
    add_columns = ["project", "baseline_name", "release_date", "versions"]
    edit_columns = ["baseline_name", "release_date", "versions"]
    add_fieldsets = [
        ("Baseline Identification", {"fields": [
         "project", "baseline_name", "release_date"]}),
        ("Included Requirements", {"fields": ["versions"], "expanded": True}),
    ]
    edit_fieldsets = [
        ("Baseline Identification", {
         "fields": ["baseline_name", "release_date"]}),
        ("Included Requirements", {"fields": ["versions"], "expanded": True}),
    ]


class ReviewerDashboardView(BaseView):
    default_view = "pending_reviews"

    @expose("/pending/")
    @has_access
    def pending_reviews(self):
        in_review_versions = (
            self.appbuilder.session
            .query(RequirementVersion)
            .filter_by(status=VersionStatus.IN_REVIEW)
            .all()
        )
        return self.render_template(
            "reviewer_dashboard.html",
            base_template=self.appbuilder.base_template,
            appbuilder=self.appbuilder,
            pending_reviews=in_review_versions
        )


def page_not_found(e):
    from .extensions import appbuilder
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )
