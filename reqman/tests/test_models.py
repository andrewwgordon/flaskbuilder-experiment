from app.models import (
    Project,
    ProjectBaseline,
    PropertyValue,
    Requirement,
    RequirementDecompositionRelationship,
    RequirementRelationship,
    RequirementTracingRelationship,
    RequirementVersion,
    RequirementView,
    StringValue,
    ValueWithUnit,
    VersionStatus,
)


def test_project_model_and_repr(sample_data):
    project = sample_data["project"]
    assert project.id is not None
    assert str(project) == "[PRJ-101] Avionics Flight System"


def test_person_organization_model_and_repr(sample_data):
    owner = sample_data["owner"]
    assert owner.id is not None
    assert str(owner) == "Dr. Jane Doe (Person)"


def test_requirement_model_and_repr(sample_data):
    req = sample_data["requirement"]
    assert req.id is not None
    assert str(req) == "[REQ-SYS-001] Emergency Power Supply"
    assert req.project.project_code == "PRJ-101"
    assert req.owner.name == "Dr. Jane Doe"


def test_requirement_version_model_and_repr(sample_data):
    ver_approved = sample_data["ver_approved"]
    assert ver_approved.id is not None
    assert "REQ-SYS-001 v1.0 (Approved)" in str(ver_approved)


def test_requirement_view_model_and_repr(sample_data):
    req_view = sample_data["req_view"]
    assert req_view.id is not None
    assert "Electrical Performance View" in str(req_view)


def test_polymorphic_property_values(db_session, sample_data):
    req_view = sample_data["req_view"]

    str_val = sample_data["prop_string"]
    unit_val = sample_data["prop_unit"]

    assert str_val.value_type == "string"
    assert unit_val.value_type == "unit"

    assert str(str_val) == f"{str_val.name}: {str_val.text_content[:30]}..."
    assert str(unit_val) == f"{unit_val.name}: {unit_val.numeric_value} {unit_val.unit}"

    # Query polymorphism via base class
    all_props = db_session.query(PropertyValue).filter_by(requirement_view_id=req_view.id).all()
    assert len(all_props) == 2
    types = {type(p) for p in all_props}
    assert StringValue in types
    assert ValueWithUnit in types


def test_domain_target_and_assertion(sample_data):
    target = sample_data["target"]
    assertion = sample_data["assertion"]

    assert target.id is not None
    assert str(target) == "[Part] Main Power Management Unit (HW-PMU-200)"
    assert assertion.id is not None
    assert assertion.requirement_view.view_name == "Electrical Performance View"
    assert assertion.target.identifier == "HW-PMU-200"


def test_requirement_review_model(sample_data):
    review = sample_data["review"]
    assert review.id is not None
    assert review.recommended_status == VersionStatus.APPROVED
    assert review.reviewer.name == "Dr. Jane Doe"


def test_project_baseline_m2m_repr(sample_data):
    baseline = sample_data["baseline"]
    ver_approved = sample_data["ver_approved"]

    assert baseline.id is not None
    assert str(baseline) == "PRJ-101 - PDR Baseline v1"
    assert len(baseline.versions) == 1
    assert baseline.versions[0] == ver_approved


def test_requirement_relationships(db_session, sample_data, admin_user):
    req1 = sample_data["requirement"]

    req2 = Requirement(
        project_id=sample_data["project"].id,
        req_key="REQ-SYS-002",
        title="Secondary Battery Backup",
        created_by=admin_user,
        changed_by=admin_user,
    )
    db_session.add(req2)
    db_session.commit()

    rel = RequirementRelationship(
        source_id=req1.id,
        target_id=req2.id,
        relationship_type="Depends On",
        created_by=admin_user,
        changed_by=admin_user,
    )
    db_session.add(rel)
    db_session.commit()

    assert rel.id is not None
    assert "Depends On" in str(rel)
    assert rel.source == req1
    assert rel.target == req2


def test_tracing_and_decomposition_relationships(db_session, sample_data, admin_user):
    req_view = sample_data["req_view"]

    req_view_child = RequirementView(
        version_id=sample_data["ver_draft"].id,
        view_name="Low Level Thermal View",
        created_by=admin_user,
        changed_by=admin_user,
    )
    db_session.add(req_view_child)
    db_session.commit()

    trace_rel = RequirementTracingRelationship(
        source_view_id=req_view.id,
        target_view_id=req_view_child.id,
        trace_type="Traces To",
        created_by=admin_user,
        changed_by=admin_user,
    )
    decomp_rel = RequirementDecompositionRelationship(
        parent_view_id=req_view.id,
        child_view_id=req_view_child.id,
        created_by=admin_user,
        changed_by=admin_user,
    )
    db_session.add_all([trace_rel, decomp_rel])
    db_session.commit()

    assert trace_rel.id is not None
    assert decomp_rel.id is not None
    assert trace_rel.source_view == req_view
    assert decomp_rel.parent_view == req_view


def test_cascade_deletion(db_session, sample_data):
    project = sample_data["project"]
    proj_id = project.id
    req_id = sample_data["requirement"].id
    ver_id = sample_data["ver_approved"].id

    # Delete project and verify cascade to requirement and baseline
    db_session.delete(project)
    db_session.commit()

    assert db_session.query(Project).get(proj_id) is None
    assert db_session.query(Requirement).get(req_id) is None
    assert db_session.query(RequirementVersion).get(ver_id) is None
    assert db_session.query(ProjectBaseline).filter_by(project_id=proj_id).first() is None
