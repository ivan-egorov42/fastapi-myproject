from fastapi import FastAPI

from app.routes import auth, games, players, stats, utils
from app.db import init_database

# from contextlib import asynccontextmanager  # Uncomment if you need to create tables on app start >>>
#
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#    init_database()
#    yield                                   # <<< Uncomment if you need to create tables on app start


app = FastAPI(
    # lifespan=lifespan,  # Uncomment if you need to create tables on app start
    title="Спортивная статистика клуба NBA Dallas Mavericks",
    description="Система управления статистикой, игроками и играми, основанная на " "фреймворке FastAPI.",
    version="0.0.1",
    contact={
        "name": "Егоров Иван",
        "email": "egorov.im@phystech.edu",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

app.include_router(auth.router)
app.include_router(games.router)
app.include_router(players.router)
app.include_router(stats.router)
app.include_router(utils.router)
