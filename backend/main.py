from http.client import HTTPResponse
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime


class WeatherData(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    location: str
    time: str
    temp: float
    humidity: float


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# SERVE UP MAIN HTML PAGE
@app.get("/")
def serve_main_html_page():
    return FileResponse("./src/index.html")

# CREATE
@app.post("/weatherdata/")
def create_weatherdata(
    weatherdata: WeatherData,
    session: Session = Depends(get_session)
) -> WeatherData:
    session.add(weatherdata)
    session.commit()
    session.refresh(weatherdata)
    return weatherdata


# READ ALL
@app.get("/weatherdata/")
def read_weatherdata(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
) -> list[WeatherData]:
    data = session.exec(
        select(WeatherData).offset(offset).limit(limit)
    ).all()
    return data


# READ ONE
@app.get("/weatherdata/{data_id}")
def read_weatherdata_item(
    data_id: int,
    session: Session = Depends(get_session)
) -> WeatherData:
    item = session.get(WeatherData, data_id)
    if not item:
        raise HTTPException(status_code=404, detail="Data not found")
    return item


# DELETE
@app.delete("/weatherdata/{data_id}")
def delete_weatherdata(
    data_id: int,
    session: Session = Depends(get_session)
):
    item = session.get(WeatherData, data_id)
    if not item:
        raise HTTPException(status_code=404, detail="Data not found")
    session.delete(item)
    session.commit()
    return {"ok": True}
