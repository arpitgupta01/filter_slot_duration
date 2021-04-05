import os,sys
import threading
import logging
logging.config.fileConfig("./app/logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.dbpool import dbHdlr
from app.api.routes import router as api_router

app = FastAPI()

if os.getenv("BYPASS_CORS","false").lower()=="true":
    logger.warn("[Potential security lapse] Bypass Cross origin resource sharing option is set to TRUE.. Please check if this can be turned OFF.")
    app.add_middleware(
        CORSMiddleware,
        #allow_origins=["*"],
        allow_origin_regex='https?://.*',
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api")