import asyncio
from  pyfabapi import fabapi
import pyfabapi.fabapi.user_system

from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

from zenroom import zencode_exec

import json

import os
from dotenv import load_dotenv 

load_dotenv()

class Config:
    fab_host: string
    fab_port: int
    fab_user: string
    fab_pass: string

    def __init__(self):
        self.fab_host = os.getenv("FAB_HOST")
        self.fab_port = int(os.getenv("FAB_PORT"))
        self.fab_user = os.getenv("FAB_USER")
        self.fab_pass = os.getenv("FAB_PASS")

with open('zenflows-crypto/src/verify_fabaccess_open.zen','r') as file:
        zen_verify_open = file.read()

with open('zenflows-crypto/src/verify_fabaccess_cmd.zen','r') as file:
        zen_verify_cmd = file.read()

class NewSession(BaseModel):
    timestamp: str
    command: str
    eddsa_public_key: str
    eddsa_signature: str

class Command(BaseModel):
    timestamp: str
    token: str
    service: str
    command: str
    eddsa_public_key: str
    eddsa_signature: str

app = FastAPI()
conf = Config()

# Maybe the session is useless
@app.post("/new-session")
async def new_session(cmd: NewSession):
    zen_result = zencode_exec(zen_verify_open, keys=cmd.json())

    if zen_result.output == '':
        raise HTTPException(status_code=500, detail="Invalid signature")

    res = json.loads(zen_result.output)

    if res["output"][0] != 'ok':
        raise HTTPException(status_code=500, detail="Invalid signature")

    return {"token": "todo"}

@app.get("/command")
async def read_root(cmd: Command):
    zen_result = zencode_exec(zen_verify_cmd, keys=cmd.json())

    if zen_result.output == '':
        raise HTTPException(status_code=500, detail="Invalid signature")

    res = json.loads(zen_result.output)

    if res["output"][0] != 'ok':
        raise HTTPException(status_code=500, detail="Invalid signature")


    # a service "urn:fabaccess:resource:Another"

    session = await fabapi.connect(conf.fab_host, conf.fab_port, conf.fab_user, conf.fab_pass)
    info = session.machineSystem.info
    ma = await info.getMachineURN(cmd.service).a_wait()

    if ma.just:
        print(ma)
        print(ma.just)
        await ma.just.use.use().a_wait()
    else:
        raise HTTPException(status_code=500, detail="No such resource")