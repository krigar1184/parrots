import asyncio

from aiokafka import AIOKafkaConsumer
from tasks.settings import KAFKA_BOOTSTRAP_SERVERS


async def main():
    consumer = AIOKafkaConsumer(
        'tasks-stream',
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    )

    await consumer.start()
    print('consumer started')

    try:
        async for message in consumer:
            print(message)
    finally:
        await consumer.stop()

    print('stopped')


if __name__ == '__main__':
    asyncio.run(main())
