import logging

from fastapi import FastAPI
from api import router

app = FastAPI()

app.include_router(router, prefix="/api/v1")

logging.basicConfig(level=logging.INFO, filename=f"py_log.log",
                    format="%(asctime)s %(levelname)s %(message)s")
