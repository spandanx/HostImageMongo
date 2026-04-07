# from datetime import timedelta
from typing import List
from fastapi import FastAPI, Request, HTTPException, status, Depends
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.components.ImageStorage.ImageStore import ImageStore

from fastapi.responses import StreamingResponse
from io import BytesIO
import logging

###------------- Config Parser
from configparser import ConfigParser

parser = ConfigParser()
config_file_path = 'config.properties'

with open(config_file_path) as f:
    file_content = f.read()

parser.read_string(file_content)
###------------- Config Parser


origins = [
    # props["origin"]["frontend"],
    "*"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

imageStorage = ImageStore(username=parser['MONGODB']['mongodb_username'],
                  password=parser['MONGODB']['mongodb_password'],
                  hostname=parser['MONGODB']['mongodb_hostname'],
                  database=parser['MONGODB']['mongodb_image_database'],
                  port=parser['MONGODB']['mongodb_port']
                  )

@app.get("/healthcheck-public")
async def healthcheck_public():
    return {"message": "I am Alive - Public Healthcheck!"}

@app.get("/image/{image_path}")
async def get_image(image_path: str):
    logging.info("Called /image/{image_path} endpoint")
    print("Called /image/{image_path} endpoint")
    image_data = imageStorage.get_image(target_image_path=image_path)
    if image_data!=None:
        image_stream = BytesIO(image_data.read())
        logging.info("Image Data")
        print("Image Data")
        logging.info(image_stream)
        print(image_stream)
        return StreamingResponse(image_stream, media_type=image_data.content_type)
    else:
        return {"error": "Image not found!"}