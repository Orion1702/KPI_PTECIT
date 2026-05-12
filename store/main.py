import asyncio
import json
from typing import Set, Dict, List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    insert,
    update,
    delete,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from datetime import datetime
from pydantic import BaseModel, field_validator
from config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
)

# FastAPI app setup
app = FastAPI()

# SQLAlchemy setup [cite: 73-80]
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the ProcessedAgentData table [cite: 82-106]
processed_agent_data = Table(
    "processed_agent_data",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("road_state", String),
    Column("user_id", Integer),
    Column("x", Float),
    Column("y", Float),
    Column("z", Float),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("timestamp", DateTime),
)

SessionLocal = sessionmaker(bind=engine)

# Pydantic models [cite: 108-184]
class ProcessedAgentDataInDB(BaseModel):
    id: int
    road_state: str
    user_id: int
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime

class AccelerometerData(BaseModel):
    x: float
    y: float
    z: float

class GpsData(BaseModel):
    latitude: float
    longitude: float

class AgentData(BaseModel):
    user_id: int
    accelerometer: AccelerometerData
    gps: GpsData
    timestamp: datetime

    @classmethod
    @field_validator("timestamp", mode="before")
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            )

class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: AgentData

# WebSocket subscriptions [cite: 192-194]
subscriptions: Dict[int, Set[WebSocket]] = {}

# FastAPI WebSocket endpoint [cite: 198-216]
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    if user_id not in subscriptions:
        subscriptions[user_id] = set()
    subscriptions[user_id].add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions[user_id].remove(websocket)

# Function to send data to subscribed users [cite: 220-226]
async def send_data_to_subscribers(user_id: int, data):
    if user_id in subscriptions:
        for websocket in subscriptions[user_id]:
            # Дані вже мають бути словником, dumps робимо всередині send_json
            await websocket.send_json(data)

# FastAPI CRUDL endpoints [cite: 227-294]

@app.post("/processed_agent_data/")
async def create_processed_agent_data(data: List[ProcessedAgentData]):
    with engine.connect() as connection:
        for item in data:
            # 1. Вставка в БД
            stmt = insert(processed_agent_data).values(
                road_state=item.road_state,
                user_id=item.agent_data.user_id,
                x=item.agent_data.accelerometer.x,
                y=item.agent_data.accelerometer.y,
                z=item.agent_data.accelerometer.z,
                latitude=item.agent_data.gps.latitude,
                longitude=item.agent_data.gps.longitude,
                timestamp=item.agent_data.timestamp,
            )
            connection.execute(stmt)
            
            # 2. Підготовка даних для WebSocket
            ws_data = {
                "road_state": item.road_state,
                "user_id": item.agent_data.user_id,
                "x": item.agent_data.accelerometer.x,
                "y": item.agent_data.accelerometer.y,
                "z": item.agent_data.accelerometer.z,
                "latitude": item.agent_data.gps.latitude,
                "longitude": item.agent_data.gps.longitude,
                "timestamp": item.agent_data.timestamp.isoformat(),
            }
            # 3. Відправка підписникам
            await send_data_to_subscribers(item.agent_data.user_id, ws_data)
        
        connection.commit()
    return {"status": "ok"}

@app.get(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataInDB,
)
def read_processed_agent_data(processed_agent_data_id: int):
    with engine.connect() as connection:
        stmt = select(processed_agent_data).where(processed_agent_data.c.id == processed_agent_data_id)
        result = connection.execute(stmt).first()
        if result:
            return result
        raise HTTPException(status_code=404, detail="Data not found")

@app.get("/processed_agent_data/", response_model=List[ProcessedAgentDataInDB])
def list_processed_agent_data():
    with engine.connect() as connection:
        stmt = select(processed_agent_data)
        results = connection.execute(stmt).fetchall()
        return results

@app.put(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataInDB,
)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):
    with engine.connect() as connection:
        stmt = (
            update(processed_agent_data)
            .where(processed_agent_data.c.id == processed_agent_data_id)
            .values(
                road_state=data.road_state,
                user_id=data.agent_data.user_id,
                x=data.agent_data.accelerometer.x,
                y=data.agent_data.accelerometer.y,
                z=data.agent_data.accelerometer.z,
                latitude=data.agent_data.gps.latitude,
                longitude=data.agent_data.gps.longitude,
                timestamp=data.agent_data.timestamp,
            )
            .returning(processed_agent_data)
        )
        result = connection.execute(stmt).first()
        connection.commit()
        if result:
            return result
        raise HTTPException(status_code=404, detail="Data not found")

@app.delete(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataInDB,
)
def delete_processed_agent_data(processed_agent_data_id: int):
    with engine.connect() as connection:
        stmt = (
            delete(processed_agent_data)
            .where(processed_agent_data.c.id == processed_agent_data_id)
            .returning(processed_agent_data)
        )
        result = connection.execute(stmt).first()
        connection.commit()
        if result:
            return result
        raise HTTPException(status_code=404, detail="Data not found")

if __name__ == "__main__":
    import uvicorn
    # Запуск на 0.0.0.0 для доступності в Docker 
    uvicorn.run(app, host="0.0.0.0", port=8000)