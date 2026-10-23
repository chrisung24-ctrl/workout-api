import datetime as dt
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select

engine = create_engine(
    "sqlite:///workouts.db", connect_args={"check_same_thread": False}
)


class LogBase(SQLModel):
    exercise: str = Field(index=True)
    reps: int = Field(gt=0)
    weight_kg: float = Field(ge=0)
    performed_on: dt.date = Field(default_factory=dt.date.today)


class Log(LogBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class LogRead(LogBase):
    id: int


def get_session():
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Workout Log API", lifespan=lifespan)


@app.post("/logs", response_model=LogRead, status_code=201)
def add_log(data: LogBase, session: Session = Depends(get_session)):
    log = Log.model_validate(data)
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


@app.get("/logs", response_model=list[LogRead])
def list_logs(exercise: str | None = None, session: Session = Depends(get_session)):
    stmt = select(Log).order_by(Log.performed_on.desc())
    if exercise:
        stmt = stmt.where(Log.exercise == exercise)
    return session.exec(stmt).all()


@app.delete("/logs/{log_id}", status_code=204)
def delete_log(log_id: int, session: Session = Depends(get_session)):
    log = session.get(Log, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    session.delete(log)
    session.commit()


@app.get("/stats/{exercise}")
def stats(exercise: str, session: Session = Depends(get_session)):
    logs = session.exec(select(Log).where(Log.exercise == exercise)).all()
    if not logs:
        raise HTTPException(status_code=404, detail="No logs for that exercise")
    return {
        "exercise": exercise,
        "sets_logged": len(logs),
        "max_weight_kg": max(l.weight_kg for l in logs),
        "total_volume_kg": sum(l.reps * l.weight_kg for l in logs),
    }