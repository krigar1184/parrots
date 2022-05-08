from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from kafka import KafkaProducer
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='http://localhost:8000/token')


@app.get('/')
async def index(_ = Depends(oauth2_scheme)):
    return {'message': 'I am index'}


@app.post('/tasks')
async def create_task(payload: Task, _ = Depends(oauth2_scheme)):
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

    if not producer.bootstrap_connected():
        raise HTTPException(401, 'cannot connect to broker')

    try:
        for i in range(100):
            producer.send('tasks', f'pewpew{str(i)}'.encode())
    finally:
        producer.close()

    return payload.json()


@app.get('/tasks')
async def get_tasks(_ = Depends(oauth2_scheme)):
    query = tasks_table.select()
    data = await database.fetch_all(query)
    return data
