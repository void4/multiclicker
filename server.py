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
                sendjall("player", player, room=player["sid"])


world = World()

def sendjall(typ, j, *args, **kwargs):
    #for player in world.players:
    #   sendj(typ, j, room=player["sid"], *args, **kwargs)
    socketio.send({"type":typ, "data":j}, json=True, *args, **kwargs)

def sendj(typ, j, *args, **kwargs):
    room = session["player"]["sid"]
    socketio.send({"type":typ, "data":j}, json=True, room=room, *args, **kwargs)

@socketio.on('connect')
def handle_connect():
    print('connected', request.sid)
    sendjall("randomname", world.getRandomName(), room=request.sid)


@socketio.on('disconnect')
def handle_disconnect():
    print("disconnected", request.sid)
    player = session["player"]#getPlayer(request.sid)
    if player:
        player["online"] = False
    #TODO set offline

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

from random import randint
def sendMarket(player, item):

    city = player["location"]

    buys = world.getMarket(city, item, "buys", "highest")
    buys = [{**order, **{"own":trader==player}} for trader, order in buys]

    sells = world.getMarket(city, item, "sells", "highest")
    sells = [{**order, **{"own":trader==player}} for trader, order in sells]

    pricehistory = []
    volumehistory = []
    for i in range(1, 30):
        pricehistory.append({ "time": f"2020-04-{i}", "value": randint(0,100) })
        volumehistory.append({ "time": f"2020-04-{i}", "value": randint(0,25) })

    response = {
        "item":item,
        "buys":buys,
        "sells":sells,
        "lastprice": world.getLastStat("price"+item),
        "currency": CURRENCY,
        "pricehistory": pricehistory,
        "volumehistory": volumehistory,
    }
    print(response)

    for player in world.players:
        if player["online"] and player["market"] == item:
            sendjall("market", response, room=player["sid"])

@socketio.on('json')
def handle_json(j):
    global world
    print('received json: ' + str(j))
    typ = j["type"]
    data = j.get("data")

    if typ == "randomname":
        sendjall("randomname", world.getRandomName(), room=request.sid)

    elif typ == "savelogin":

        if len(data["username"]) == 0:
            return

        if session.get("player") is None:
            session["player"] = world.getOrCreatePlayer(data["username"])

        if session["player"] is not None and session["player"]["password"] in [None, data["password"]]:

            if session["player"]["password"] is None and len(data["password"])>0:
                session["player"]["name"] = data["username"]
                session["player"]["password"] = data["password"]

            session["player"]["sid"] = request.sid
            session["player"]["online"] = True
            sendj("login", "successful")
            sendj("items", tradeable)
            markets = list(tradeable.keys())
            markets.remove(CURRENCY)
            sendj("markets", markets)
            sendj("cities", cities)
            sendj("routes", routes)
        else:
            sendj("login", "failed")



    player = session.get("player")

    if player is None:
        return

    if typ == "decision":

        if session["player"] is None:
            return

        player["decision"] = data["decision"]
        player["data"] = data["data"]

    elif typ == "market":
        player["market"] = data
        sendMarket(player, data)

    elif typ == "order":
        world.trade(player, data)
        sendMarket(player, data["item"])

    elif typ == "craft":
        world.craft(player, data["item"], data["count"])

    elif typ == "getTravelInfo":
        sendj("travelinfo", world.getTravelInfo(player, data))

    elif typ == "travel":
        if world.travel(player, data["city"], data["mode"]):
            sendj("city", None)
            sendMarket(player, player["market"])

    elif typ == "store":
        world.store(player, data["item"], data["count"])
        sendj("player", player)

    elif typ == "unstore":
        world.unstore(player, data["item"], data["count"])
        sendj("player", player)

    elif typ == "cancelOrder":
        world.cancelOrder(player, player["location"], data["bos"], data["oid"])
        sendMarket(player, player["market"])



    elif typ == "logout":
        session["player"]["online"] = False
        session["player"] = None

if __name__ == '__main__':
    socketio.start_background_task(world_tick)
    socketio.run(app, host="0.0.0.0", port=9999)
