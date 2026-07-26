import sys
from datetime import datetime, timezone
from os import environ

from flask import g
from sqlalchemy.exc import SQLAlchemyError

from app import appbuilder, create_app, db, models

app = create_app()

with app.app_context():

    print("Establishing user context...")
    try:
        user_name = environ["SEED_USER"]
    except KeyError as ex:
        print(
            f"Set SEED_USER environemnt variable to application user name: {ex.message}")
        sys.exit(1)
    user = appbuilder.sm.find_user(environ["SEED_USER"])
    if not user:
        print*"set SEED_USER environment variable."
        sys.exit()

    g.user = user

    print("Seeding sample data...")

    try:
        # 1. Create Parties
        alice = models.PersonOrganizationSelect(
            party_type=models.PartyType.PERSON,
            name="Alice Engineer",
            email="alice@example.com",
            organization_name="Avionics Division",
        )
        acme_corp = models.PersonOrganizationSelect(
            party_type=models.PartyType.ORGANIZATION,
            name="Acme Aerospace",
            email="contact@acmeaerospace.com",
            organization_name="Acme Aerospace Inc.",
        )
        db.session.add_all([alice, acme_corp])
        db.session.commit()

        # 2. Create Project
        project = models.Project(
            project_code="PRJ-AVIONICS",
            name="Next-Gen Flight Control Avionics",
            description="Requirement specification for Flight Control Computer (FCC) & Software System.",
        )
        db.session.add(project)
        db.session.commit()

        # 3. Create Requirement & Version
        req1 = models.Requirement(
            project_id=project.id,
            req_key="REQ-FCC-001",
            title="Flight Control Computer Maximum Latency",
            owner_id=alice.id,
        )
        db.session.add(req1)
        db.session.commit()

        v1 = models.RequirementVersion(
            requirement_id=req1.id,
            version_label="1.0.0",
            status=models.VersionStatus.IN_REVIEW,
            revision_date=datetime.now(timezone.utc),
        )
        db.session.add(v1)
        db.session.commit()

        # 4. Create Requirement Views & Properties
        sys_view = models.RequirementView(
            version_id=v1.id,
            view_name="Systems Engineering View",
        )
        db.session.add(sys_view)
        db.session.commit()

        prop_desc = models.StringValue(
            requirement_view_id=sys_view.id,
            name="Requirement Text",
            text_content="The Flight Control Computer shall process control surface commands with end-to-end response latency not exceeding 10 milliseconds.",
        )
        prop_unit = models.ValueWithUnit(
            requirement_view_id=sys_view.id,
            name="Maximum Acceptable Latency",
            numeric_value=10.0,
            unit="ms",
        )
        db.session.add_all([prop_desc, prop_unit])

        # 5. Create System Target & Satisfaction Assertion
        fcc_part = models.DomainTarget(
            target_type=models.TargetType.PART,
            name="Flight Control Processor Board Subsystem",
            identifier="PART-FCC-BD-01",
        )
        db.session.add(fcc_part)
        db.session.commit()

        assertion = models.RequirementSatisfactionAssertion(
            requirement_view_id=sys_view.id,
            target_id=fcc_part.id,
            assertion_statement="Satisfied by hardware interrupt benchmark test suite v2.1.",
            asserted_by_id=alice.id,
            asserted_at=datetime.now(timezone.utc),
        )
        db.session.add(assertion)

        # 6. Create Review Log
        review = models.RequirementReview(
            version_id=v1.id,
            reviewer_id=alice.id,
            comments="Latency budget verified against system architecture. Recommended for approval.",
            recommended_status=models.VersionStatus.APPROVED,
        )
        db.session.add(review)

        # 7. Create Baseline
        baseline = models.ProjectBaseline(
            project_id=project.id,
            baseline_name="Baseline 1.0 - System Requirements Review (SRR)",
            release_date=datetime.now(timezone.utc),
            versions=[v1],
        )
        db.session.add(baseline)

        db.session.commit()
        print("Seed data successfully populated!")

    except SQLAlchemyError as exc:
        db.session.rollback()
        print(f"Error seeding database: {exc._message}", file=sys.stderr)
        sys.exit(1)
