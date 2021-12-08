#! /usr/bin/env python3

from bs4 import BeautifulSoup
from threading import Thread
from analyze import parse
from aiohttp import web
from datetime import datetime
from time import sleep
import requests
import json
import socketio
import asyncio
import os


# logging function
def consoleLog(log):
    print(f"- [{datetime.now()}]> {log}")


### variables ###
BASE_URL = "https://helli1.iranlms.org/"
SETTINGS = json.load(open("settings.json"))
session = requests.session()


### login process ###
moodel_credentials = SETTINGS["MOODLE_CREDENTIALS"]
r = session.get(f"{BASE_URL}/login/index.php")

# find the login token
soup = BeautifulSoup(r.text, "html.parser")
login_token = soup.select("input[name=logintoken]")[0]["value"]
payload = {"logintoken": login_token, **moodel_credentials}

# login to lms
r = session.post(r.url, data=payload)
consoleLog("login: 200")


### download results in xlsx ###
async def update():
    # update the SETTINGS
    SETTINGS = json.load(open("settings.json"))

    if SETTINGS["status"] == "freezing":
        consoleLog("status is freezing. send the old data")
        await sio.emit(json.load(open("data.json")))
        return

    r = session.get(
        f"https://helli1.iranlms.org/mod/choice/report.php?id={SETTINGS['electionRoomID']}"
    )

    # find sesskey
    soup = BeautifulSoup(r.text, "html.parser")
    sesskey = soup.select("input[name=sesskey]")[0]["value"]
    payload = {"id": SETTINGS["electionRoomID"], "download": "xls", "sesskey": sesskey}

    r = session.post(r.url, data=payload)

    # writing into file
    with open("data.xlsx", "wb") as file:
        file.write(r.content)

    consoleLog("data.xlsx downloaded")

    ### parse excel ###
    parsed_data = parse("data.xlsx")
    await sio.emit("information", parsed_data)
    consoleLog("new information has sent to the client")

    with open("data.json", "w") as file:
        file.write(json.dumps(parsed_data))


def main():
    while True:
        asyncio.run(update())
        sleep(5)


### send data via socket.io ###
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

td = Thread(target=main)
td.start()


async def index(request):
    with open("public/index.html") as f:
        return web.Response(text=f.read(), content_type="text/html")


@sio.event
async def connect(sid, environ):
    print(sid, "connected")
    if not os.path.exists("data.json"):
        print("data.json was not found")
        await update()

    data = json.load(open("data.json"))
    await sio.emit("information", data)


@sio.event
async def disconnect(sid):
    print(sid, "disconnected")


app.router.add_get("/", index)
app.router.add_static("/static", "public")

if __name__ == "__main__":
    web.run_app(app, port=SETTINGS["port"] if "port" in SETTINGS else 8080)
