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
	player["inventory"]["clicks"] = 0#randint(0,1000)
	world.players.append(player)

ids = Counter()

for step in range(1000):

	ids[world.ranking()[0]["id"]] += 1

	world.stats.append(Counter())

	stat = world.stats[-1]

	for player in sample(world.players, len(world.players)):
		stat["p"+str(player["id"])] = player["inventory"]["clicks"]

		r = random() * 5

		if r < 0.05:
			world.buy(player, {"type":"limit", "item":"factory", "volume":randint(1, 5), "price": randint(5, 15)})
		elif r < 0.1:
			world.sell(player, {"type":"limit", "item":"factory", "volume":randint(1, 5), "price": randint(10, 20)})
		elif r < 0.15:
			world.buy(player, {"type":"market", "item":"factory", "volume":randint(1,5)})
		elif r < 0.2:
			world.sell(player, {"type":"market", "item":"factory", "volume":randint(1,5)})
		elif r < 0.4:
			bos = choice(["buys", "sells"])
			numorders = len(player[bos])
			if numorders > 0:
				index = randint(0, numorders-1)
				world.cancelOrder(player, bos, index)
		elif r < 0.8:
			if step > 0 and stat["price"] > 10 or stat["tradevolume"] < 1:
				world.craft(player, choice(list(craftable.keys())), randint(1,5))
		else:
			decision = player["default_action"]
			if decision == "click":
				player["inventory"]["clicks"] += 1

	stat["totalclicks"] = sum([player["inventory"]["clicks"] for player in world.players])
	stat["totalfactory"] = sum([player["inventory"].get("factory", 0) for player in world.players])

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

for name in "totalclicks tradevolume price totalfactory".split() + ["p"+str(player["id"]) for player in world.players]:#stats[-1].keys():
	print(name)
	xs = list(range(len(world.stats)))
	ys = [world.stats[i][name] for i in range(len(world.stats))]
	for i in range(len(ys)-1, -1, -1):
		if ys[i] == 0:
			xs.pop(i)
			ys.pop(i)
	plt.plot(xs, ys, label=name)

#plt.plot(list(range(len(ids))), list([x[1] for x in ids.most_common()]))

print(ids)

plt.legend()
plt.show()
