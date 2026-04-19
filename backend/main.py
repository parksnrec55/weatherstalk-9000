from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime, timedelta, timezone


class WeatherDataBase(SQLModel):
    location: str
    time: datetime
    temp: float
    humidity: float

class WeatherData(WeatherDataBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

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

@app.get("/favicon.svg")
def serve_favicon():
    return FileResponse("./src/favicon.svg", media_type="image/svg+xml")

# API Endpoints
# GET LATEST WEATHER DATA ENTRY
@app.get("/weatherdata/latest", response_model=WeatherData)
def get_latest_weather(session: Session = Depends(get_session)):
    latest = session.exec(
        select(WeatherData).order_by(WeatherData.id.desc())
    ).first()  # largest id = last inserted

    if not latest:
        raise HTTPException(status_code=404, detail="No weather data found")
    
    return latest

# GET WEATHER STATS
class WeatherStats(SQLModel):
    temp_high: float
    temp_high_time: datetime
    temp_low: float
    temp_low_time: datetime
    humidity_high: float
    humidity_high_time: datetime
    humidity_low: float
    humidity_low_time: datetime

@app.get("/weatherdata/24-hr_stats", response_model=WeatherStats)
def get_weather_stats(session: Session = Depends(get_session)):
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    rows = session.exec(
        select(WeatherData).where(WeatherData.time >= since)
    ).all()

    if not rows:
        raise HTTPException(status_code=404, detail="No weather data in the last 24 hours")

    temp_high_row   = max(rows, key=lambda r: r.temp)
    temp_low_row    = min(rows, key=lambda r: r.temp)
    humid_high_row  = max(rows, key=lambda r: r.humidity)
    humid_low_row   = min(rows, key=lambda r: r.humidity)

    return WeatherStats(
        temp_high=temp_high_row.temp,
        temp_high_time=temp_high_row.time,
        temp_low=temp_low_row.temp,
        temp_low_time=temp_low_row.time,
        humidity_high=humid_high_row.humidity,
        humidity_high_time=humid_high_row.time,
        humidity_low=humid_low_row.humidity,
        humidity_low_time=humid_low_row.time,
    )


# CREATE NEW DATA ENTRY
@app.post("/weatherdata/")
def create_weatherdata(
    weatherdata: WeatherDataBase,
    session: Session = Depends(get_session)
) -> WeatherData:
    db_item = WeatherData(**weatherdata.model_dump())
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


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
