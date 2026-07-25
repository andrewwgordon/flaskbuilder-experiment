import enum
from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime, Enum, Table
from sqlalchemy.orm import relationship


class Project(Model, AuditMixin):
    """Top-level container for scoped requirements."""
    __tablename__ = "project"
    id = Column(Integer, primary_key=True)
    project_code = Column(String(30), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)

    requirements = relationship("Requirement", back_populates="project", cascade="all, delete-orphan")
    baselines = relationship("ProjectBaseline", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"[{self.project_code}] {self.name}"


class PartyType(str, enum.Enum):
    PERSON = "Person"
    ORGANIZATION = "Organization"


class PersonOrganizationSelect(Model, AuditMixin):
    """Represents individuals or organizational entities owning or asserting requirements."""
    __tablename__ = "person_organization_select"
    id = Column(Integer, primary_key=True)
    party_type = Column(Enum(PartyType), nullable=False)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True)
    organization_name = Column(String(150), nullable=True)

    def __repr__(self):
        return f"{self.name} ({self.party_type.value if hasattr(self.party_type, 'value') else self.party_type})"


class VersionStatus(str, enum.Enum):
    DRAFT = "Draft"
    IN_REVIEW = "In Review"
    CHANGES_REQUESTED = "Changes Requested"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    BASELINED = "Baselined"
    SUPERSEDED = "Superseded"


class Requirement(Model, AuditMixin):
    __tablename__ = "requirement"
    id = Column(Integer, primary_key=True)

    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    project = relationship("Project", back_populates="requirements")

    req_key = Column(String(50), unique=True, nullable=False)
    title = Column(String(200), nullable=False)

    owner_id = Column(Integer, ForeignKey("person_organization_select.id"), nullable=True)
    owner = relationship("PersonOrganizationSelect")

    versions = relationship("RequirementVersion", back_populates="requirement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"[{self.req_key}] {self.title}"


class RequirementVersion(Model, AuditMixin):
    __tablename__ = "requirement_version"
    id = Column(Integer, primary_key=True)
    requirement_id = Column(Integer, ForeignKey("requirement.id"), nullable=False)
    version_label = Column(String(20), nullable=False)
    status = Column(Enum(VersionStatus), default=VersionStatus.DRAFT, nullable=False)
    revision_date = Column(DateTime)

    requirement = relationship("Requirement", back_populates="versions")
    views = relationship("RequirementView", back_populates="version", cascade="all, delete-orphan")
    reviews = relationship("RequirementReview", back_populates="version", cascade="all, delete-orphan")

    def __repr__(self):
        status_val = self.status.value if hasattr(self.status, "value") else self.status
        return f"{self.requirement.req_key if self.requirement else 'REQ'} v{self.version_label} ({status_val})"


class RequirementView(Model, AuditMixin):
    __tablename__ = "requirement_view"
    id = Column(Integer, primary_key=True)
    version_id = Column(Integer, ForeignKey("requirement_version.id"), nullable=False)
    view_name = Column(String(100), nullable=False)

    version = relationship("RequirementVersion", back_populates="views")
    properties = relationship("PropertyValue", back_populates="requirement_view", cascade="all, delete-orphan")
    satisfaction_assertions = relationship("RequirementSatisfactionAssertion", back_populates="requirement_view", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.version} - {self.view_name}"


class RequirementRelationship(Model, AuditMixin):
    __tablename__ = "requirement_relationship"
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("requirement.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("requirement.id"), nullable=False)
    relationship_type = Column(String(50), nullable=False)

    source = relationship("Requirement", foreign_keys=[source_id])
    target = relationship("Requirement", foreign_keys=[target_id])

    def __repr__(self):
        return f"{self.source} -> {self.relationship_type} -> {self.target}"


class RequirementTracingRelationship(Model, AuditMixin):
    __tablename__ = "requirement_tracing_relationship"
    id = Column(Integer, primary_key=True)
    source_view_id = Column(Integer, ForeignKey("requirement_view.id"), nullable=False)
    target_view_id = Column(Integer, ForeignKey("requirement_view.id"), nullable=False)
    trace_type = Column(String(50), default="Traces To")

    source_view = relationship("RequirementView", foreign_keys=[source_view_id])
    target_view = relationship("RequirementView", foreign_keys=[target_view_id])


class RequirementDecompositionRelationship(Model, AuditMixin):
    __tablename__ = "requirement_decomposition_relationship"
    id = Column(Integer, primary_key=True)
    parent_view_id = Column(Integer, ForeignKey("requirement_view.id"), nullable=False)
    child_view_id = Column(Integer, ForeignKey("requirement_view.id"), nullable=False)

    parent_view = relationship("RequirementView", foreign_keys=[parent_view_id])
    child_view = relationship("RequirementView", foreign_keys=[child_view_id])


class PropertyValue(Model, AuditMixin):
    __tablename__ = "property_value"
    id = Column(Integer, primary_key=True)
    requirement_view_id = Column(Integer, ForeignKey("requirement_view.id"), nullable=False)
    name = Column(String(100), nullable=False)
    value_type = Column(String(50))

    requirement_view = relationship("RequirementView", back_populates="properties")

    __mapper_args__ = {
        "polymorphic_identity": "property_value",
        "polymorphic_on": value_type,
    }

    def __repr__(self):
        return f"{self.name} ({self.value_type})"


class StringValue(PropertyValue):
    __tablename__ = "string_value"
    id = Column(Integer, ForeignKey("property_value.id"), primary_key=True)
    text_content = Column(Text, nullable=False)

    __mapper_args__ = {"polymorphic_identity": "string"}

    def __repr__(self):
        return f"{self.name}: {self.text_content[:30]}..."


class ValueWithUnit(PropertyValue):
    __tablename__ = "value_with_unit"
    id = Column(Integer, ForeignKey("property_value.id"), primary_key=True)
    numeric_value = Column(Float, nullable=False)
    unit = Column(String(30), nullable=False)

    __mapper_args__ = {"polymorphic_identity": "unit"}

    def __repr__(self):
        return f"{self.name}: {self.numeric_value} {self.unit}"


class TargetType(str, enum.Enum):
    PART = "Part"
    INDIVIDUAL_PART = "Individual Part"
    BREAKDOWN = "Breakdown"
    DOCUMENT = "Document"


class DomainTarget(Model, AuditMixin):
    """Represents external/system targets (Part, Individual Part, Breakdown, Document)."""
    __tablename__ = "domain_target"
    id = Column(Integer, primary_key=True)
    target_type = Column(Enum(TargetType), nullable=False)
    name = Column(String(150), nullable=False)
    identifier = Column(String(100), nullable=False)

    def __repr__(self):
        type_val = self.target_type.value if hasattr(self.target_type, 'value') else self.target_type
        return f"[{type_val}] {self.name} ({self.identifier})"


class RequirementSatisfactionAssertion(Model, AuditMixin):
    __tablename__ = "requirement_satisfaction_assertion"
    id = Column(Integer, primary_key=True)
    requirement_view_id = Column(Integer, ForeignKey("requirement_view.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("domain_target.id"), nullable=False)
    assertion_statement = Column(Text, nullable=False)

    asserted_by_id = Column(Integer, ForeignKey("person_organization_select.id"), nullable=False)
    asserted_at = Column(DateTime, nullable=False)

    requirement_view = relationship("RequirementView", back_populates="satisfaction_assertions")
    target = relationship("DomainTarget")
    asserted_by = relationship("PersonOrganizationSelect")


class RequirementReview(Model, AuditMixin):
    """Review feedback log for a requirement version."""
    __tablename__ = "requirement_review"
    id = Column(Integer, primary_key=True)
    version_id = Column(Integer, ForeignKey("requirement_version.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("person_organization_select.id"), nullable=False)
    comments = Column(Text, nullable=False)
    recommended_status = Column(Enum(VersionStatus), nullable=False)

    version = relationship("RequirementVersion", back_populates="reviews")
    reviewer = relationship("PersonOrganizationSelect")


baseline_version_association = Table(
    "baseline_version_association",
    Model.metadata,
    Column("baseline_id", Integer, ForeignKey("project_baseline.id"), primary_key=True),
    Column("version_id", Integer, ForeignKey("requirement_version.id"), primary_key=True),
)


class ProjectBaseline(Model, AuditMixin):
    """Formal release snapshot bundling approved requirement versions."""
    __tablename__ = "project_baseline"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    baseline_name = Column(String(100), nullable=False)
    release_date = Column(DateTime, nullable=False)

    project = relationship("Project", back_populates="baselines")
    versions = relationship("RequirementVersion", secondary=baseline_version_association)

    def __repr__(self):
        return f"{self.project.project_code if self.project else 'PRJ'} - {self.baseline_name}"


"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""
