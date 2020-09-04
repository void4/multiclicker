from copy import deepcopy
from random import randint, shuffle, choice, random, sample
from collections import defaultdict, Counter
from math import log
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

			if d["type"] == "limit" and order["price"] > d["price"]:
				break

			volumedelta = min(order["volume"], d["volume"])

			if exchange(player, trader, d["item"], volumedelta, order["price"]):
				order["volume"] -= volumedelta
				d["volume"] -= volumedelta

				if order["volume"] == 0:
					trader["sells"].remove(order)

				if d["volume"] == 0:
					break

	if d["type"] == "limit" and d["volume"] > 0:

		#buy/sell only in clicks? works in eve, but there credits arent mined
		outstanding_buys = sum([order["price"]*order["volume"] for order in player["buys"]])
		cost = d["price"]*d["volume"]

		# kinda doesnt work if money lost in the meantime, but hey

		if cost + outstanding_buys <= player["inventory"].get("clicks", 0):
			#print("BUY ORDER")
			#pre-deduct?
			#inventory["clicks"] -= cost

			player["buys"].append(d)

def getMarket(item, bos="buy", sort="lowest"):
	market = []
	for player in players:
		for order in player[bos]:
			if order["item"] == item:
				 market.append([player, order])

	# TODO: sort same-price orders by longest standing
	return sorted(market, key=lambda op: op[1]["price"], reverse=sort=="highest")

def exchange(a, b, item, volume, price):
	"""a gets items, b gets money"""
	global stat
	# Check a==b? -> can currently hit own orders
	cost = volume*price

	if cost <= 0:
		return False

	# All or nothing
	if a["inventory"].get("clicks", 0) >= cost and b["inventory"].get(item, 0) >= volume:
		a["inventory"]["clicks"] -= cost
		b["inventory"]["clicks"] += cost
		b["inventory"][item] = b["inventory"].get(item, 0) - volume
		a["inventory"][item] = a["inventory"].get(item, 0) + volume

		stat["tradevolume"] += cost
		stat["price"] = price

		return True

	return False

def sell(player, d):

	if d["volume"] <= 0:
		return

	if d["type"] in ["market", "limit"]:
		for trader, order in getMarket(d["item"], "buys", "highest"):

			if d["type"] == "limit" and order["price"] < d["price"]:
				break

			volumedelta = min(order["volume"], d["volume"])

			if exchange(trader, player, d["item"], volumedelta, order["price"]):
				order["volume"] -= volumedelta
				d["volume"] -= volumedelta

				if order["volume"] == 0:
					trader["buys"].remove(order)

				if d["volume"] == 0:
					break

	if d["type"] == "limit" and d["volume"] > 0:

		outstanding_sells = sum([order["volume"] for order in player["buys"] if order["item"] == d["item"]])

		if d["volume"] + outstanding_sells <= player["inventory"].get(d["item"], 0):
			#print("SELL ORDER")
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
		pass
		#print("insufficient resources")

def cancelOrder(player, bos, index):
	player[bos].pop(index)

for i in range(10):
	player = deepcopy(playerj)
	player["id"] = i
	player["inventory"]["clicks"] = 0#randint(0,1000)
	players.append(player)

stats = defaultdict(Counter)

for step in range(1000):

	stat = stats[step]

	for player in sample(players, len(players)):
		stat["p"+str(player["id"])] = player["inventory"]["clicks"]

		r = random() * 5

		if r < 0.05:
			buy(player, {"type":"limit", "item":"factory", "volume":randint(1, 5), "price": randint(5, 15)})
		elif r < 0.1:
			sell(player, {"type":"limit", "item":"factory", "volume":randint(1, 5), "price": randint(10, 20)})
		elif r < 0.15:
			buy(player, {"type":"market", "item":"factory", "volume":randint(1,5)})
		elif r < 0.2:
			sell(player, {"type":"market", "item":"factory", "volume":randint(1,5)})
		elif r < 0.4:
			bos = choice(["buys", "sells"])
			numorders = len(player[bos])
			if numorders > 0:
				index = randint(0, numorders-1)
				cancelOrder(player, bos, index)
		elif r < 0.8:
			if step > 0 and stats[step-1]["price"] > 10 or stats[step-1]["tradevolume"] < 1:
				craft(player, choice(list(craftable.keys())), randint(1,5))
		else:
			decision = player["default_action"]
			if decision == "click":
				player["inventory"]["clicks"] += 1

	stat["totalclicks"] = sum([player["inventory"]["clicks"] for player in players])
	stat["totalfactory"] = sum([player["inventory"].get("factory", 0) for player in players])

	# use volume or cost?
	#stat["sells"] = getMarket("factory", "sells", "highest")
	#stat["buys"] =  getMarket("factory", "sells", "highest")

"""
for player in players:
	#print(json.dumps(player, indent=4))
	print(len(player["buys"]), player["inventory"])
"""

import matplotlib.pyplot as plt
#print(stats)
#
for name in "totalclicks tradevolume price totalfactory".split():# + ["p"+str(player["id"]) for player in players]:#stats[-1].keys():
	print(name)
	xs = list(range(len(stats)))
	ys = [stats[i][name] for i in range(len(stats))]
	for i in range(len(ys)-1, -1, -1):
		if ys[i] == 0:
			xs.pop(i)
			ys.pop(i)
	plt.plot(xs, ys, label=name)

plt.legend()
plt.show()
