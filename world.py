from collections import defaultdict, Counter
from copy import deepcopy
from random import sample
import pickle
from time import time
import os
from datetime import datetime, timedelta
from glob import glob

from models import *

BACKUPDIR = "backups"

class World:
	def __init__(self):
		self.startdate = datetime(1200,1,1)
		self.ticks = 0
		self.options = {
			"backupinterval" : 60
		}
		self.pid = 0
		self.oid = 0
		self.players = []
		self.tradehistory = []

	def new_player(self, name):
		"""must be called through getOrCreatePlayer for name check!"""

		player = deepcopy(playerj)
		player["id"] = self.pid
		self.pid += 1

		player["name"] = name

		player["capacity"] = self.getWeightCapacity(player)
		for city in cities:
			name = city["name"]
			player["storage"][name] = {}
			player["buys"][name] = []
			player["sells"][name] = []
		self.players.append(player)
		return player

	def new_oid(self):
		self.oid += 1
		return self.oid

	def getOrCreatePlayer(self, name):
		for player in self.players:
			if player["name"] == name:
				return player

		return self.new_player(name)

	def getRandomName(self):
		# TODO: avoid DOS
		while True:
			name = generateRandomName()
			for other in self.players:
				if other["name"] == name:
					break
			else:
				return name

	def getLastStat(self, name):
		for i in range(len(self.stats)-1, -1, -1):
			if name in self.stats[i]:
				return self.stats[i][name]

	def getSumStat(self, name, lastn):
		total = 0
		for i in range(len(self.stats)-1, max(0, len(self.stats)-1-lastn), -1):
			if name in self.stats[i]:
				total += self.stats[i][name]
		return total

	def requireStorage(self, player, d, city=None):
		if city is None:
			city = player["location"]
		return all([self.getStorage(player, city, item) >= count for item, count in d.items()])

	def requireInventory(self, player, d):
		return all([self.getInventory(player, item) >= count for item, count in d.items()])

	def require(self, player, d):
		city = player["location"]
		return all([self.getInventory(player, item)+self.getStorage(player, city, item) >= count for item, count in d.items()])

	def deduct(self, player, d):
		if self.require(player, d):
			city = player["location"]
			for item, count in d.items():
				delta = min(self.getStorage(player, city, item), count)

				if delta > 0:
					self.addStorage(player, city, item, -delta)
					count -= delta

				if count > 0:
					self.addInventory(player, item, -count)

			return True

		return False

	def trade(self, player, d):

		# or d["price"]*d["volume"] > player["inventory"][TIME]:
		if d["volume"] <= 0 or (d["type"] == "limit" and d["price"] <= 0):
			return "Volume and Price must be positive"

		if int(d["volume"]) != d["volume"] or (d["type"] == "limit" and d["volume"]*d["price"] != int(d["volume"]*d["price"])):
			return "Volume and Cost must be whole numbers"

		city = player["location"]

		initialvolume = d["volume"]

		if d["bos"] == "sell":
			market = self.getMarket(city, d["item"], "buys", "highest")
		else:
			market = self.getMarket(city, d["item"], "sells", "lowest")

		if d["type"] in ["market", "limit"]:
			for trader, order in market:

				if d["type"] == "limit" and ((d["bos"] == "buy" and order["price"] > d["price"]) or (d["bos"] == "sell" and order["price"] < d["price"])):
					break

				volumedelta = min(order["volume"], d["volume"])

				if d["bos"] == "buy":
					buyer = player
					seller = trader
				else:
					buyer = trader
					seller = player

				if self.exchange(city, buyer, seller, d["item"], volumedelta, order["price"]):
					order["volume"] -= volumedelta
					d["volume"] -= volumedelta

					if order["volume"] == 0:
						trader["sells" if d["bos"] == "buy" else "buys"][city].remove(order)

					if d["volume"] == 0:
						break

		if d["type"] == "market":
			return f"{initialvolume-d['volume']}/{initialvolume} filled"

		if d["type"] == "limit" and d["volume"] > 0:

			if d["bos"] == "buy":
				#buy/sell only in clicks? works in eve, but there credits arent mined
				outstanding_buys = sum([order["price"]*order["volume"] for order in player["buys"].get(city, [])])
				cost = d["price"]*d["volume"]

				# kinda doesnt work if money lost in the meantime, but hey
				if cost + outstanding_buys <= self.getStorage(player, city, CURRENCY):
					#pre-deduct?
					#(successful?) order and tx costs
					d["oid"] = self.new_oid()
					player["buys"][city] = player["buys"].get(city, []) + [d]
					return "Volume remaining, created buy order"
				else:
					return f"Insufficient {CURRENCY} in storage or too many outstanding buys"

			else:
				outstanding_sells = sum([order["volume"] for order in player["sells"].get(city, []) if order["item"] == d["item"]])

				if d["volume"] + outstanding_sells <= self.getStorage(player, city, d["item"]):
					d["oid"] = self.new_oid()
					player["sells"][city] = player["sells"].get(city, []) + [d]
					return "Volume remaining, created sell order"
				else:
					return f"Insufficient {d['item']} in storage or too many outstanding sells"

		return f"{initialvolume-d['volume']}/{initialvolume} filled"

	def getMarket(self, city, item, bos="buy", sort="lowest"):
		market = []
		for player in self.players:
			for order in player[bos].get(city, []):
				if order["item"] == item:
					 market.append([player, order])

		# TODO: sort same-price orders by longest standing
		return sorted(market, key=lambda op: op[1]["price"], reverse=sort=="highest")

	def exchange(self, city, a, b, item, volume, price):
		"""a gets items, b gets money"""
		# Check a==b? -> can currently hit own orders
		# TODO: avoid exchanging fractional camels
		cost = volume*price

		if cost <= 0:
			return False

		# All or nothing
		if self.getStorage(a, city, CURRENCY) >= cost and self.getStorage(b, city, item) >= volume:
			self.addStorage(a, city, CURRENCY, -cost)
			self.addStorage(b, city, CURRENCY, cost)
			self.addStorage(b, city, item, -volume)
			self.addStorage(a, city, item, volume)

			self.tradehistory.append([self.ticks, city, item, volume, price, cost])

			return True

		return False

	def getTradeHistory(self, city, item, stat="volume", nticks=1):
		dataindex = {
			"volume": 3,
			"cost": 5
		}[stat]

		history = []

		lastindex = -1
		for trade in self.tradehistory:
			if trade[1] == city and trade[2] == item:
				index = datetime.timestamp(self.startdate + timedelta(seconds=(trade[0] // nticks)*nticks))
				if index != lastindex:
					if len(history) > 0:
						history[-1]["value"] = sum(history[-1]["value"])
					history.append({"time":index, "value":[]})
					lastindex = index
				history[-1]["value"].append(trade[dataindex])

		if len(history) > 0:
			history[-1]["value"] = sum(history[-1]["value"])

		return history

	def getVolumeHistory(self, city, item, nticks=1):
		return self.getTradeHistory(city, item, "volume", nticks)

	def getCostHistory(self, city, item, nticks=1):
		return self.getTradeHistory(city, item, "cost", nticks)

	def getPriceHistory(self, city, item, nticks=1):
		volumehistory = self.getTradeHistory(city, item, "volume", nticks)
		costhistory = self.getTradeHistory(city, item, "cost", nticks)

		pricehistory = []
		for i in range(len(volumehistory)):
			pricehistory.append({"time":volumehistory[i]["time"], "value":costhistory[i]["value"]/volumehistory[i]["value"]})

		return pricehistory

	def clearOldOrders(self):
		for player in self.players:
			for bos in ["buys", "sells"]:
				for city in list(player[bos]):
					for order in city:
						if order.get("ticks", None) is not None and order["ticks"] <= 0:
							player[bos].remove(order)

	def craft(self, player, item, count=1):
		craft = getCity(player["location"])["craftable"][item]

		"""
		capacity = self.getWeightCapacity(player)
		player["capacity"] = capacity

		weight = self.getInventoryWeight(player) + self.getItemWeight(item, count)
		if weight <= capacity:#Doesn't count capacity of added camels!
		"""

		if self.deduct(player, rmultiply(craft[0], count)):
			#player["inventory"][item] = self.getInventory(player, item) + count
			self.addStorage(player, player["location"], item, count)
			#player["weight"] = weight
		else:
			pass
			#print("insufficient resources")
		"""
		else:
			#TODO
			pass
		"""

	def cancelOrder(self, player, city, bos, oid):
		for index, order in enumerate(list(player[bos].get(city, []))):
			if order["oid"] == oid:
				player[bos][city].pop(index)
				break

	def ranking(self):
		return sorted(self.players, key=lambda player:player["inventory"][CURRENCY], reverse=True)#clicks

	def getStorage(self, player, city, item):
		if city not in player["storage"]:
			return 0

		return player["storage"][city].get(item, 0)

	def getItemWeight(self, item, count):
		if item == TIME:
			return 0
		return tradeable[item].get("weight", 0)*count

	def getInventoryWeight(self, player):
		weight = 0
		for item, count in player["inventory"].items():
			weight += self.getItemWeight(item, count)
		return weight

	def getInventory(self, player, item):
		return player["inventory"].get(item, 0)

	def getItemWeightCapacity(self, item, count):
		if item == TIME:
			return 0
		if "capacity" in tradeable[item]:
			return tradeable[item]["capacity"]*count
		else:
			return 0

	def getWeightCapacity(self, player):
		capacity = player["baseweightcapacity"]
		for item, count in player["inventory"].items():
			capacity += self.getItemWeightCapacity(item, count)
		return capacity

	def store(self, player, item, count):
		# TODO storing camel, decrease capacity!!!
		has = min(self.getInventory(player, item), count)
		city = player["location"]
		if has > 0:
			if city not in player["storage"]:
				player["storage"][city] = {}

			weightAfter = self.getInventoryWeight(player) - self.getItemWeight(item, has)
			capacityAfter = self.getWeightCapacity(player) - self.getItemWeightCapacity(item, has)

			if weightAfter <= capacityAfter:
				self.addStorage(player, city, item, has)
				self.addInventory(player, item, -has)

				player["weight"] = weightAfter
				player["capacity"] = capacityAfter


	def unstore(self, player, item, count):
		city = player["location"]
		has = min(self.getStorage(player, city, item), count)
		if has > 0:

			weightAfter = self.getInventoryWeight(player) + self.getItemWeight(item, has)
			capacityAfter = self.getWeightCapacity(player) + self.getItemWeightCapacity(item, has)
			if weightAfter <= capacityAfter:
				self.addStorage(player, city, item, -has)
				self.addInventory(player, item, has)

				player["weight"] = weightAfter
				player["capacity"] = capacityAfter

	def travel(self, player, city, mode):
		route = getRoute(player["location"], city)

		cost = self.getTravelCost(player, city, mode)

		if self.deduct(player, cost):
			player["location"] = city
			return True

		return False

	# TODO allow multi-city routes?
	def getTravelCost(self, player, city, mode):
		# differ by carried weight?

		# TODO travelling without own boat either impossible or need to pay gold (depending on weight)!

		route = getRoute(player["location"], city)

		length = route[2][mode]

		camels = self.getInventory(player, "camel")

		costs = {"wheat": camels * 3 * length, "gold": (camels//5) * length, TIME: length}

		hasboat = self.requireInventory(player, {"boat": 1}) or self.requireInventory(player, {"ship": 1})
		if mode == "ship" and not hasboat:
			costs["gold"] = costs.get("gold", 0) + 1 * length

		return costs

	def getTravelInfo(self, player, city):
		info = {
			"city": city,
			"costs": {}
		}
		route = getRoute(player["location"], city)

		if route is None:
			# No connection
			return None

		for mode in route[2]:
			info["costs"][mode] = self.getTravelCost(player, city, mode)

		return info

	def addInventory(self, player, item, count):
		player["inventory"][item] = self.getInventory(player, item) + count
		if self.getInventory(player, item) == 0:
			del player["inventory"][item]

	def addStorage(self, player, city, item, count):
		player["storage"][city][item] = self.getStorage(player, city, item) + count
		if self.getStorage(player, city, item) == 0:
			del player["storage"][city][item]

	def tick(self):

		if self.ticks > 0 and self.ticks % self.options["backupinterval"] == 0:
			self.save()

		print("TICK", self.ticks)

		for player in sample(self.players, len(self.players)):
			self.addInventory(player, TIME, 1)

		self.ticks += 1

	def load(self, path):
		print("Loading", path)
		with open(path, "rb") as f:
			tmp = pickle.load(f)
		self.__dict__.update(tmp)

	def save(self, path=None):

		if path is None:
			path = os.path.join(BACKUPDIR, f"{int(time()*1000)}_{self.ticks}.pickle")

		os.makedirs(BACKUPDIR, exist_ok=True)

		print("Saving", path)

		data = deepcopy(self.__dict__)

		data.pop("options", None)

		with open(path, "wb+") as f:
			pickle.dump(data, f)

	def loadlatest(self):
		backups = sorted(glob(os.path.join(BACKUPDIR, "*.pickle")), key=lambda path:int(path.split(os.path.sep)[-1].split("_")[0]))
		if len(backups) > 0:
			self.load(backups[-1])
		else:
			print("No save found, starting new")
