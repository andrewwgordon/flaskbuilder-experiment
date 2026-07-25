from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface

from .models import (
    DomainTarget,
    Project,
    ProjectBaseline,
    Requirement,
    RequirementVersion,
    RequirementView,
)


class ProjectApi(ModelRestApi):
    datamodel = SQLAInterface(Project)
    resource_name = "project"
    list_columns = ["id", "project_code", "name", "description"]
    show_columns = ["id", "project_code", "name", "description"]
    add_columns = ["project_code", "name", "description"]
    edit_columns = ["project_code", "name", "description"]
    search_columns = ["project_code", "name"]


class RequirementApi(ModelRestApi):
    datamodel = SQLAInterface(Requirement)
    resource_name = "requirement"
    list_columns = ["id", "req_key", "title", "project.project_code", "owner.name"]
    show_columns = ["id", "req_key", "title", "project", "owner"]
    add_columns = ["req_key", "title", "project", "owner"]
    edit_columns = ["req_key", "title", "project", "owner"]
    search_columns = ["req_key", "title"]


class RequirementVersionApi(ModelRestApi):
    datamodel = SQLAInterface(RequirementVersion)
    resource_name = "requirement_version"
    list_columns = ["id", "requirement.req_key", "version_label", "status", "revision_date"]
    show_columns = ["id", "requirement", "version_label", "status", "revision_date"]
    add_columns = ["requirement", "version_label", "status", "revision_date"]
    edit_columns = ["version_label", "status", "revision_date"]
    search_columns = ["status"]


class RequirementViewApi(ModelRestApi):
    datamodel = SQLAInterface(RequirementView)
    resource_name = "requirement_view"
    list_columns = ["id", "version.version_label", "view_name"]
    show_columns = ["id", "version", "view_name"]
    add_columns = ["version", "view_name"]
    edit_columns = ["view_name"]


class ProjectBaselineApi(ModelRestApi):
    datamodel = SQLAInterface(ProjectBaseline)
    resource_name = "project_baseline"
    list_columns = ["id", "project.project_code", "baseline_name", "release_date"]
    show_columns = ["id", "project", "baseline_name", "release_date"]
    add_columns = ["project", "baseline_name", "release_date"]
    edit_columns = ["baseline_name", "release_date"]


class DomainTargetApi(ModelRestApi):
    datamodel = SQLAInterface(DomainTarget)
    resource_name = "domain_target"
    list_columns = ["id", "identifier", "name", "target_type"]
    show_columns = ["id", "identifier", "name", "target_type"]
    add_columns = ["identifier", "name", "target_type"]
    edit_columns = ["identifier", "name", "target_type"]

