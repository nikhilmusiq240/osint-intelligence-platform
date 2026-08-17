from app.db import SessionLocal
from app.models import EntityRecord, EvidenceRecord, Investigation


def test_entity_and_evidence_can_be_created_in_memory() -> None:
    session = SessionLocal()
    try:
        investigation = Investigation(
            title="Evidence model",
            description="Verify provenance storage",
            status="draft",
        )
        session.add(investigation)
        session.flush()

        entity = EntityRecord(
            investigation_id=investigation.id,
            entity_type="domain",
            value="example.com",
            normalized_value="example.com",
            confidence=0.91,
            attributes={"source": "unit-test"},
        )
        session.add(entity)
        session.flush()

        evidence = EvidenceRecord(
            investigation_id=investigation.id,
            entity_id=entity.id,
            source_name="example-source",
            source_url="https://example.com",
            title="Example evidence",
            content="Publicly visible reference",
            content_type="text",
            provenance={"captured_by": "unit-test", "method": "http"},
            is_verified=False,
        )
        session.add(evidence)
        session.commit()

        persisted = (
            session.query(EvidenceRecord).filter(EvidenceRecord.id == evidence.id).one()
        )
        assert persisted.source_name == "example-source"
        assert persisted.provenance["method"] == "http"
        assert persisted.entity_id == entity.id
    finally:
        session.close()
