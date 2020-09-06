from collections import defaultdict, Counter
import json
from time import time
import os

from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, send, emit

from world import World
from models import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")#, asyncmode="threading"

# TODO: Redis
#sessions = {}

def world_tick():
    while True:
        socketio.sleep(1)
        world.tick()
        for player in world.players:
            if player["online"]:
                sendj("player", player, room=player["sid"])


world = World()

def sendjall(typ, j, *args, **kwargs):
    for player in world.players:
        sendj(typ, j, room=player["sid"], *args, **kwargs)

def sendj(typ, j, *args, **kwargs):
    socketio.send({"type":typ, "data":j}, json=True, *args, **kwargs)

@socketio.on('connect')
def handle_connect():
    print('connected', request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print("disconnected", request.sid)
    player = session["player"]#getPlayer(request.sid)
    player["online"] = False
    #TODO set offline

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

def sendMarket(player, item):
    buys = world.getMarket(item, "buys", "highest")
    buys = [{**order, **{"own":trader==player}} for trader, order in buys]

    sells = world.getMarket(item, "sells", "lowest")
    sells = [{**order, **{"own":trader==player}} for trader, order in sells]
    response = {
        "item":item,
        "buys":buys,
        "sells":sells,
        "lastprice": world.getLastStat("price"+item)
    }
    print(response)
    sendj("market", response)

@socketio.on('json')
def handle_json(j):
    global world
    print('received json: ' + str(j))
    typ = j["type"]
    data = j.get("data")

    if typ == "login":
        session["player"] = world.getOrCreatePlayer(data["name"])
        if session["player"] is not None:
            sendj("login", "successful")
            session["player"]["sid"] = request.sid
            session["player"]["online"] = True
            sendj("markets", list(craftable.keys()), room=session["player"]["sid"])
            sendj("craftable", craftable, room=session["player"]["sid"])
            sendj("cities", cities, room=session["player"]["sid"])
        else:
            sendj("login", "failed")

    player = session["player"]

    if player is None:
        return

    if typ == "decision":

        if session["player"] is None:
            return

        player["decision"] = data["decision"]
        player["data"] = data["data"]

    elif typ == "market":
        sendMarket(player, data)

    elif typ == "order":
        world.trade(player, data)
        sendMarket(player, data["item"])

    elif typ == "craft":
        world.craft(player, data["item"], data["count"])

if __name__ == '__main__':
    socketio.start_background_task(world_tick)
    socketio.run(app, host="0.0.0.0", port=9999)
