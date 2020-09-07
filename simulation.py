from copy import deepcopy
from random import randint, shuffle, choice, random, sample
from collections import defaultdict, Counter
from math import log
import json

from world import World
from models import *

world = World()

for i in range(100):
	player = deepcopy(playerj)
	player["id"] = i
	player["inventory"][TIME] = 0#randint(0,1000)
	world.players.append(player)

ids = Counter()

def randomItem():
	return choice(list(craftable.keys()))

def randomInventoryItem(player):
	inventory = [key for key, value in player["inventory"].items() if value > 0]
	if not inventory:
		return

	return choice(inventory)



for step in range(1000):

	ids[world.ranking()[0]["id"]] += 1

	world.stats.append(Counter())

	stat = world.stats[-1]

	for player in sample(world.players, len(world.players)):
		stat["p"+str(player["id"])] = player["inventory"][TIME]

		r = random() * 5

		if r < 0.05:
			item = randomItem()
			cost = craftable[item][0][TIME]
			price = randint(cost//2, int(cost*1.5))
			world.trade(player, {"bos":"buy", "type":"limit", "item":item, "volume":randint(1, 5), "price":price})
		elif r < 0.1:
			item = randomInventoryItem(player)
			if item:
				world.trade(player, {"bos":"sell", "type":"limit", "item":item, "volume":randint(1, 5), "price": randint(10, 20)})
		elif r < 0.11:
			item = randomItem()
			world.trade(player, {"bos":"buy", "type":"market", "item":item, "volume":randint(1,5)})
		elif r < 0.12:
			item = randomInventoryItem(player)
			if item:
				world.trade(player, {"bos":"sell", "type":"market", "item":item, "volume":randint(1,5)})
		elif r < 0.4:
			bos = choice(["buys", "sells"])
			numorders = len(player[bos])
			if numorders > 0:
				index = randint(0, numorders-1)
				world.cancelOrder(player, bos, index)
		elif r < 0.8:
			item = choice(list(craftable.keys()))
			lastprice = world.getLastStat("price"+item)
			if (lastprice is not None and lastprice > craftable[item][0][TIME]) or world.getSumStat("tradevolume", 100) < 1:
				world.craft(player, item, randint(1,5))
		else:
			decision = player["default_action"]
			if decision == "click":
				player["inventory"][TIME] += 1

	stat["totalclicks"] = sum([player["inventory"][TIME] for player in world.players])
	for item in craftable:
		stat["total"+item] = sum([player["inventory"].get(item, 0) for player in world.players])

	# use volume or cost?
	#stat["sells"] = getMarket("factory", "sells", "highest")
	#stat["buys"] =  getMarket("factory", "sells", "highest")

"""
for player in world.players:
	#print(json.dumps(player, indent=4))
	print(len(player["buys"]), player["inventory"])
"""

import matplotlib.pyplot as plt
#print(stats)

query1 = []
query2 = []
query3 = ["totalclicks"]
for item in craftable:
	query1.extend(["price"+item])
	query2.append("tradevolume"+item)
	query3.append("total"+item)

#for player in world.players:
#	query.append("p"+str(player["id"]))

def removeY0(xs, ys):
	for i in range(len(ys)-1, -1, -1):
		if ys[i] == 0:
			xs.pop(i)
			ys.pop(i)

def plot(plt, query, y0=False):

	for name in query:
		print(name)
		xs = list(range(len(world.stats)))
		ys = [world.stats[i][name] for i in range(len(world.stats))]

		if not y0:
			removeY0(xs, ys)

		plt.plot(xs, ys, label=name)
		plt.legend()

fig, axes = plt.subplots(nrows=3, ncols=1)

plot(axes[0], query1)
plot(axes[1], query2, y0=True)
plot(axes[2], query3)

#plt.plot(list(range(len(ids))), list([x[1] for x in ids.most_common()]))

print(ids)

plt.show()
