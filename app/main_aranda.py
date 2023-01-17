from genericpath import isfile
import os
import yaml
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.routes.api import router as api_router
from app.src.classes.aranda import Aranda
from app.src.libs.logger import custom_log

VERSION="0.0.1"

config_file_path = "app/config/config.yaml" if os.getenv("API_ENV") != "DEV" else "app/config/examples/config.yaml"

if not os.path.isfile(config_file_path):
    custom_log(f"[ERROR] Configuration file not found", "red")
    exit(1)

with open(config_file_path,"r") as config_file:
    try:
        config = yaml.safe_load(config_file)
    except yaml.YAMLError as e:
        custom_log(f"[ERROR] Error loading configuration file - ${e}", "red")

app = FastAPI(
    title="IAS",
    version=VERSION,
    description="Infrastructure APIs Services - Aranda Authenticator API",
    root_path=os.getenv("API_PATH")
)

app.aranda = Aranda(config, renew_auth_interval=config["app"]["renew_auth_interval"])

@app.on_event("startup")
async def startup_event():
    custom_log(f"[INFO] Infrastructure APIs Services - Aranda Authenticator API", "green")
    custom_log(f"[INFO] Version: {VERSION}", "green")
    custom_log(f"[INFO] API Path: {os.getenv('API_PATH')}", "green")
    custom_log(f"[INFO] Renewing authentication token every {config['app']['renew_auth_interval']} seconds", "green")



@app.on_event("shutdown")
def shutdown_event():
    custom_log(f"[WARN] Exiting the main program", "yellow")

"""
origins = ["http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""

app.include_router(api_router)

"""
if __name__ == "app.main":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("API_PORT")),
        log_level=config["app"]["log_level"],
        reload=config["app"]["reload"]
        )
"""