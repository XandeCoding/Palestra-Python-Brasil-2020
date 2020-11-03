import aiohttp
import asyncio
import socket
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

conn = aiohttp.TCPConnector(
        family=socket.AF_INET,
        ssl=False,
    )

@app.on_event('startup')
async def startup_event():
    global session
    session = aiohttp.ClientSession(connector=conn)

@app.on_event('shutdown')
async def shutdown_event():
    await session.close()

class ChuckJoke(BaseModel):
    """
    classe que mantém as informações das piadas.

    atributos: id, joke, categories.
    """

    id: int
    joke: str
    categories: Optional[List[str]]

async def getChuckJokes(quantity: int) -> List[ChuckJoke]:
    async with session.get(f'http://api.icndb.com/jokes/random/{quantity}') as response:
        jokes = await response.json()

        if (jokes['type'] != 'success'):
            return []

        return [ChuckJoke.parse_obj(joke) for joke in jokes['value']]

async def getChuckJoke(id: int) -> ChuckJoke:
    async with session.get(f'http://api.icndb.com/jokes/{id}') as response:
        joke = await response.json()

        if (joke['type'] != 'success'):
            return []

        return joke['value']


async def getSooMuchJokes():
    tasks = []

    for page in range(1, 10):
        task = asyncio.create_task(getChuckJokes(page * 100))
        tasks.append(task)

        unflattedJokes = await asyncio.gather(*tasks)
        return sum(unflattedJokes, [])

@app.get('/', response_model=List[ChuckJoke])
async def getAll():
    """
    Retorna as piadas de Chuck Norris de forma paginada.
    """
    return await getSooMuchJokes()

@app.get('/{id}', response_model=ChuckJoke)
async def getById(id: int):
    """
    Busca e retorna uma piada pelo id.
    """

    return await getChuckJoke(id)
