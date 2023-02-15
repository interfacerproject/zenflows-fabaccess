import asyncio
from  pyfabapi import fabapi
import pyfabapi.fabapi.user_system

from typing import Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from zenroom import zencode_exec

import json
import datetime

import os
import requests
from dotenv import load_dotenv 

load_dotenv()

class Config:
    fab_host: str
    fab_port: int
    fab_user: str
    fab_pass: str
    did_url: str
    delta_timestamp: str

    def __init__(self):
        self.fab_host = os.getenv("FAB_HOST")
        self.fab_port = int(os.getenv("FAB_PORT"))
        self.fab_user = os.getenv("FAB_USER")
        self.fab_pass = os.getenv("FAB_PASS")
        self.did_url = os.getenv("DID_URL")
        self.delta_timestamp = int(os.getenv("DELTA_TIMESTAMP"))

with open('zenflows-crypto/src/verify_fabaccess_open.zen','r') as file:
        zen_verify_open = file.read()

with open('zenflows-crypto/src/verify_fabaccess_cmd.zen','r') as file:
        zen_verify_cmd = file.read()

class Command(BaseModel):
    timestamp: str
    token: str
    service: str
    command: str
    eddsa_public_key: str
    eddsa_signature: str

# TODO: keep the same session across multiple calls
app = FastAPI()
conf = Config()

@app.post("/command")
async def command(cmd: Command):
    # Verify DID exits on DID controller

    did_request = requests.get(f"{conf.did_url}{cmd.eddsa_public_key}")
    if did_request.status_code != 200:
        raise HTTPException(status_code=500, detail="Could not fetch did")

    # Verify signature with zenroom

    zen_result = zencode_exec(zen_verify_cmd, keys=cmd.json())

    if zen_result.output == '':
        raise HTTPException(status_code=500, detail="Invalid signature")

    res = json.loads(zen_result.output)

    if res["output"][0] != 'ok':
        raise HTTPException(status_code=500, detail="Invalid signature")

    # Verify timestamp

    now_time = datetime.datetime.now()
    cmd_timestamp = int(cmd.timestamp)
    delta_t = int(datetime.datetime.timestamp(now_time)) - cmd_timestamp
    if delta_t < 0:
        raise HTTPException(status_code=500, detail="Command from the future...")

    if delta_t > conf.delta_timestamp:
        raise HTTPException(status_code=500, detail="Signature expired")

    # Connect to fabaccess and send command

    session = await fabapi.connect(conf.fab_host, conf.fab_port, conf.fab_user, conf.fab_pass)
    if session == None:
        raise HTTPException(status_code=500, detail="Fabaccess not available")
    info = session.machineSystem.info
    print(cmd.service)
    ma = await info.getMachineURN(cmd.service).a_wait()

    try:
        if ma.just:
            if cmd.command == "ON":
                await ma.just.use.use().a_wait()
            elif cmd.command == "OFF":
                await ma.just.inuse.giveBack().a_wait()
            else:
                raise HTTPException(status_code=500, detail="Fabaccess not available")
        else:
            raise HTTPException(status_code=500, detail="No such resource")
    except:
        raise HTTPException(status_code=500, detail="Could not complete command")


    return {"success": True}

@app.get("/state/{urn}")
async def state(urn: str):
    session = await fabapi.connect(conf.fab_host, conf.fab_port, conf.fab_user, conf.fab_pass)
    if session == None:
        raise HTTPException(status_code=500, detail="Fabaccess not available")
    info = session.machineSystem.info
    print(urn)
    ma = await info.getMachineURN(urn).a_wait()

    if ma.just:
        return {"state": str(ma.just.state)}
    else:
        raise HTTPException(status_code=500, detail="Fabaccess not available")
