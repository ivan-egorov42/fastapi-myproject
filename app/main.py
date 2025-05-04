from fastapi import FastAPI
from app.db import init_database
from app.routes import players, games, auth, stats
#from contextlib import asynccontextmanager  # Uncomment if you need to create tables on app start >>>
#
#@asynccontextmanager
#async def lifespan(app: FastAPI):
#    init_database()
#    yield                                   # <<< Uncomment if you need to create tables on app start


app = FastAPI(
    #lifespan=lifespan,  # Uncomment if you need to create tables on app start
    title="Спортивной статистика клуба NBA Dallas Mavericks",
    description="Система управления задачами, основанная на "
                "фреймворке FastAPI.",
    version="0.0.1",
    contact={
        "name": "Егоров Иван",
        "email": "egorov.im@phystech.edu",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

app.include_router(auth.router)
app.include_router(games.router)
app.include_router(players.router)
app.include_router(stats.router)