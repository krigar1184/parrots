from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
# from kafka import KafkaProducer
# from kafka.errors import KafkaError
from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

from tasks.models import tasks_table
from tasks.db import database
from tasks.settings import KAFKA_BOOTSTRAP_SERVERS


class Task(BaseModel):
    """
    Write model
    """
    name: str
    description: str


app = FastAPI()

producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='http://localhost:8000/token')


@app.get('/')
async def index(_ = Depends(oauth2_scheme)):
    return {'message': 'I am index'}


@app.post('/tasks')
async def create_task(payload: Task, _ = Depends(oauth2_scheme)):
    await producer.start()

    try:
        await producer.send_and_wait('tasks-stream', value=payload.json().encode())
    finally:
        await producer.stop()

    return payload.json()


@app.get('/tasks')
async def get_tasks(_ = Depends(oauth2_scheme)):
    query = tasks_table.select()
    data = await database.fetch_all(query)
    return data
