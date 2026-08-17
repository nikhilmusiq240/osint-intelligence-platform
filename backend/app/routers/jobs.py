from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db_session
from app.models import InvestigationJob
from app.schemas import JobCreate, JobRead

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobRead])
def list_jobs(
    session: Annotated[Session, Depends(get_db_session)],
) -> list[InvestigationJob]:
    return (
        session.query(InvestigationJob)
        .order_by(InvestigationJob.created_at.desc())
        .all()
    )


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    session: Annotated[Session, Depends(get_db_session)],
) -> InvestigationJob:
    job = InvestigationJob(
        investigation_id=payload.investigation_id,
        connector_name=payload.connector_name,
        query=payload.query,
        job_metadata=payload.job_metadata,
        status="queued",
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


@router.get("/{job_id}", response_model=JobRead)
def get_job(
    job_id: int, session: Annotated[Session, Depends(get_db_session)]
) -> InvestigationJob:
    job = (
        session.query(InvestigationJob)
        .filter(InvestigationJob.id == job_id)
        .one_or_none()
    )
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    return job
