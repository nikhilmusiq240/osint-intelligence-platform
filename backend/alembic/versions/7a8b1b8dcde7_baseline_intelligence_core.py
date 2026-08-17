"""baseline_intelligence_core

Revision ID: 7a8b1b8dcde7
Revises:
Create Date: 2026-08-17 03:01:22.094385
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "7a8b1b8dcde7"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "investigations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_investigations_id"), "investigations", ["id"], unique=False
    )

    op.create_table(
        "investigation_targets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("target_type", sa.String(length=100), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("normalized_value", sa.String(length=255), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("attributes", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_investigation_targets_id"),
        "investigation_targets",
        ["id"],
        unique=False,
    )

    op.create_table(
        "investigation_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("connector_name", sa.String(length=100), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("job_metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_investigation_jobs_id"), "investigation_jobs", ["id"], unique=False
    )

    op.create_table(
        "provenance_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_name", sa.String(length=150), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("provenance_metadata", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_provenance_records_id"), "provenance_records", ["id"], unique=False
    )

    op.create_table(
        "connectors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_connectors_id"), "connectors", ["id"], unique=False)

    op.create_table(
        "entities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=True),
        sa.Column("provenance_id", sa.Integer(), nullable=True),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("normalized_value", sa.String(length=255), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("attributes", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_observed", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"]),
        sa.ForeignKeyConstraint(["target_id"], ["investigation_targets.id"]),
        sa.ForeignKeyConstraint(["provenance_id"], ["provenance_records.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_entities_id"), "entities", ["id"], unique=False)

    op.create_table(
        "entity_relationships",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("source_entity_id", sa.Integer(), nullable=False),
        sa.Column("target_entity_id", sa.Integer(), nullable=False),
        sa.Column("provenance_id", sa.Integer(), nullable=True),
        sa.Column("relation_type", sa.String(length=100), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("attributes", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"]),
        sa.ForeignKeyConstraint(["source_entity_id"], ["entities.id"]),
        sa.ForeignKeyConstraint(["target_entity_id"], ["entities.id"]),
        sa.ForeignKeyConstraint(["provenance_id"], ["provenance_records.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_entity_relationships_id"), "entity_relationships", ["id"], unique=False
    )

    op.create_table(
        "evidence",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("provenance_id", sa.Integer(), nullable=True),
        sa.Column("provenance_metadata", sa.JSON(), nullable=True),
        sa.Column("source_name", sa.String(length=150), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("content_type", sa.String(length=50), nullable=False),
        sa.Column("hash_value", sa.String(length=128), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("connector_name", sa.String(length=150), nullable=True),
        sa.Column("connector_version", sa.String(length=50), nullable=True),
        sa.Column("raw_source_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_immutable", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"]),
        sa.ForeignKeyConstraint(["target_id"], ["investigation_targets.id"]),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"]),
        sa.ForeignKeyConstraint(["provenance_id"], ["provenance_records.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_evidence_id"), "evidence", ["id"], unique=False)

    op.create_table(
        "connector_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=True),
        sa.Column("connector_name", sa.String(length=100), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("run_metadata", sa.JSON(), nullable=True),
        sa.Column("result_summary", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"]),
        sa.ForeignKeyConstraint(["target_id"], ["investigation_targets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_connector_runs_id"), "connector_runs", ["id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_connector_runs_id"), table_name="connector_runs")
    op.drop_table("connector_runs")
    op.drop_index(op.f("ix_evidence_id"), table_name="evidence")
    op.drop_table("evidence")
    op.drop_index(op.f("ix_entity_relationships_id"), table_name="entity_relationships")
    op.drop_table("entity_relationships")
    op.drop_index(op.f("ix_entities_id"), table_name="entities")
    op.drop_table("entities")
    op.drop_index(op.f("ix_connectors_id"), table_name="connectors")
    op.drop_table("connectors")
    op.drop_index(op.f("ix_provenance_records_id"), table_name="provenance_records")
    op.drop_table("provenance_records")
    op.drop_index(op.f("ix_investigation_jobs_id"), table_name="investigation_jobs")
    op.drop_table("investigation_jobs")
    op.drop_index(
        op.f("ix_investigation_targets_id"), table_name="investigation_targets"
    )
    op.drop_table("investigation_targets")
    op.drop_index(op.f("ix_investigations_id"), table_name="investigations")
    op.drop_table("investigations")
