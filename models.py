from copy import deepcopy
from random import randint, shuffle, choice, random, sample
import json

players = []

playerj = {
	"id": None,
	"name": "???",
	"password": None,

	"last_online": None,
	"online": None,

	"inventory": {
		"clicks": 0,
	},

	"decision": None,
	"default_action": "click",

	"buys": [],

	"sells": [],

	"log": []
}

craftable = {
	"factory": [{"clicks":10}, "clicks += 1", ""],
}

actions = {
	"click": [None, "clicks += 1"],
	"craft": [None, "craft(data)"],
	"buy": [None, "buy(data)"],
	"sell": [None, "sell(data)"],
}

def require(player, d):
	if all([player["inventory"][key] >= value for key, value in d.items()]):
		for key, value in d.items():
			player["inventory"][key] -= value
		return True

	return False

def buy(player, d):

	if d["volume"] <= 0:# or d["price"]*d["volume"] > player["inventory"]["clicks"]:
		return

	if d["type"] in ["market", "limit"]:
		for trader, order in getMarket(d["item"], "sells", "lowest"):

			volumedelta = min(order["volume"], d["volume"])

			if exchange(player, trader, d["item"], volumedelta, order["price"]):
				order["volume"] -= volumedelta
				d["volume"] -= volumedelta

				if order["volume"] == 0:
					trader["sells"].remove(order)

	if d["type"] == "limit":

		#buy/sell only in clicks? works in eve, but there credits arent mined
		outstanding_buys = sum([order["price"]*order["volume"] for order in player["buys"]])
		cost = d["price"]*d["volume"]

		# kinda doesnt work if money lost in the meantime, but hey

		if cost + outstanding_buys <= player["inventory"].get("clicks", 0):
			#pre-deduct?
			#inventory["clicks"] -= cost

			player["buys"].append(d)

def getMarket(item, bos="buy", sort="lowest"):
	market = []
	for player in players:
		for order in player[bos]:
			if order["item"] == item:
				 market.append([player, order])

	return sorted(market, key=lambda op: op[1]["price"], reverse=sort=="highest")

def exchange(a, b, item, volume, price):
	"""a gets items, b gets money"""
	# Check a==b? -> can currently hit own orders
	cost = volume*price
	if a["inventory"].get("clicks", 0) >= cost and b["inventory"][item] >= volume:
		a["inventory"]["clicks"] -= cost
		b["inventory"]["clicks"] += cost
		b["inventory"][item] = b["inventory"].get(item, 0) - volume
		a["inventory"][item] = a["inventory"].get(item, 0) + volume

		return True

	return False

def sell(player, d):

	if d["volume"] <= 0:
		return

	if d["type"] in ["market", "limit"]:
		for trader, order in getMarket(d["item"], "buys", "highest"):

			volumedelta = min(order["volume"], d["volume"])

			if exchange(trader, player, d["item"], volumedelta, order["price"]):
				order["volume"] -= volumedelta
				d["volume"] -= volumedelta

				if order["volume"] == 0:
					trader["buys"].remove(order)

	if d["type"] == "limit":

		outstanding_sells = sum([order["volume"] for order in player["buys"] if order["item"] == d["item"]])

		if d["volume"] + outstanding_sells <= player["inventory"].get(d["item"], 0):
			player["sells"].append(d)

def clearOldOrders():
	for player in players:
		for bos in ["buys", "sells"]:
			for order in list(player[bos]):
				if order.get("ticks", None) is not None and order["ticks"] <= 0:
					player[bos].remove(order)

def rmultiply(req, factor):
	return {key:value*factor for key, value in req.items()}

def craft(player, item, number=1):
	craft = craftable[item]
	if require(player, rmultiply(craft[0], number)):
		player["inventory"][item] = player["inventory"].get(item, 0) + number
	else:
		print("insufficient resources")

def cancelOrder(player, bos, index):
	player[bos].pop(index)

for i in range(2):
	player = deepcopy(playerj)
	player["inventory"]["clicks"] = randint(0,1000)
	players.append(player)

for i in range(100):

	for player in sample(players, len(players)):
		craft(player, "factory", 5)

		r = random()

		if r < 0.1:
			buy(player, {"type":"limit", "item":"factory", "volume":randint(1, 5), "price": randint(10, 20)})
		if r < 0.2:
			sell(player, {"type":"limit", "item":"factory", "volume":randint(1, 5), "price": randint(5, 15)})
		elif r < 0.3:
			buy(player, {"type":"market", "item":"factory", "volume":randint(1,5)})
		elif r < 0.4:
			sell(player, {"type":"market", "item":"factory", "volume":randint(1,5)})
		elif r < 0.6:
			bos = choice(["buys", "sells"])
			numorders = len(player[bos])
			if numorders > 0:
				index = randint(0, numorders-1)
				cancelOrder(player, bos, index)
		else:
			decision = player["default_action"]
			if decision == "click":
				player["inventory"]["clicks"] += 1

#sell(players[0], {"type":"market", "item":"factory", "volume":5})

for player in players:
	print(json.dumps(player, indent=4))
