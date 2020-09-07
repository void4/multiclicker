from collections import defaultdict, Counter
from copy import deepcopy
from random import sample

from models import *

class World:
	def __init__(self):
		self.ticks = 0
		self.pid = 0
		self.oid = 0
		self.players = []
		self.stats = []

	def new_player(self):
		player = deepcopy(playerj)
		player["id"] = self.pid
		self.pid += 1
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

		return self.new_player()

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

	def require(self, player, d):
		city = player["location"]
		if all([self.getInventory(player, item)+self.getStorage(player, city, item) >= count for item, count in d.items()]):
			for item, count in d.items():
				delta = min(self.getStorage(player, city, item), count)

				if delta > 0:
					player["storage"][city][item] -= delta
					count -= delta

				if count > 0:
					player["inventory"][item] -= count

			return True

		return False

	def trade(self, player, d):

		if d["volume"] <= 0 or (d["type"] == "limit" and d["price"] <= 0):# or d["price"]*d["volume"] > player["inventory"]["clicks"]:
			return

		city = player["location"]

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

		if d["type"] == "limit" and d["volume"] > 0:

			if d["bos"] == "buy":
				#buy/sell only in clicks? works in eve, but there credits arent mined
				outstanding_buys = sum([order["price"]*order["volume"] for order in player["buys"].get(city, [])])
				cost = d["price"]*d["volume"]

				# kinda doesnt work if money lost in the meantime, but hey
				if cost + outstanding_buys <= self.getStorage(player, city, "clicks"):
					#pre-deduct?
					#(successful?) order and tx costs
					d["oid"] = self.new_oid()
					player["buys"][city] = player["buys"].get(city, []) + [d]

			else:
				outstanding_sells = sum([order["volume"] for order in player["buys"].get(city, []) if order["item"] == d["item"]])

				if d["volume"] + outstanding_sells <= self.getStorage(player, city, d["item"]):
					d["oid"] = self.new_oid()
					player["sells"][city] = player["sells"].get(city, []) + [d]

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
		cost = volume*price

		if cost <= 0:
			return False

		# All or nothing
		if self.getStorage(a, city, "clicks") >= cost and self.getStorage(b, city, item) >= volume:
			a["storage"][city]["clicks"] -= cost
			b["storage"][city]["clicks"] = self.getStorage(b, city, "clicks") + cost
			b["storage"][city][item] = b["storage"][city].get(item, 0) - volume
			a["storage"][city][item] = a["storage"][city].get(item, 0) + volume

			self.stats[-1]["tradevolume"+item] += cost
			self.stats[-1]["price"+item] = price

			return True

		return False


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

		if self.require(player, rmultiply(craft[0], count)):
			#player["inventory"][item] = self.getInventory(player, item) + count
			player["storage"][player["location"]][item] = self.getStorage(player, player["location"], item) + count
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
		return sorted(self.players, key=lambda player:player["inventory"]["clicks"], reverse=True)

	def getStorage(self, player, city, item):
		if city not in player["storage"]:
			return 0

		return player["storage"][city].get(item, 0)

	def getItemWeight(self, item, count):
		if item == "clicks":
			return 0
		return tradeable[item]["weight"]*count

	def getInventoryWeight(self, player):
		weight = 0
		for item, count in player["inventory"].items():
			if item == "clicks":
				continue
			weight += tradeable[item]["weight"]*count
		return weight

	def getInventory(self, player, item):
		return player["inventory"].get(item, 0)

	def getItemWeightCapacity(self, item, count):
		if item == "clicks":
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
				player["storage"][city][item] = self.getStorage(player, city, item) + has
				player["inventory"][item] -= has
				if player["inventory"][item] == 0:
					del player["inventory"][item]

				player["weight"] = weightAfter
				player["capacity"] = capacityAfter


	def unstore(self, player, item, count):
		city = player["location"]
		has = min(self.getStorage(player, city, item), count)
		if has > 0:

			weightAfter = self.getInventoryWeight(player) + self.getItemWeight(item, has)
			capacityAfter = self.getWeightCapacity(player) + self.getItemWeightCapacity(item, has)
			if weightAfter <= capacityAfter:
				player["storage"][city][item] -= has
				player["inventory"][item] = self.getInventory(player, item) + has
				player["weight"] = weightAfter
				player["capacity"] = capacityAfter

				if player["storage"][city][item] == 0:
					del player["storage"][city][item]

	def travel(self, player, city, mode):
		route = getRoute(player["location"], city)

		cost = self.getTravelCost(player, city, mode)

		if self.require(player, cost):
			player["location"] = city
			return True

		return False

	# TODO allow multi-city routes?
	def getTravelCost(self, player, city, mode):
		# differ by carried weight?

		route = getRoute(player["location"], city)

		length = route[2][mode]

		camels = self.getInventory(player, "camels")

		return {"wheat": camels * 5 * length, "gold": (camels//5) * length, "clicks": length}

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

	def tick(self):

		self.stats.append(Counter())

		#print("TICK")

		for player in sample(self.players, len(self.players)):

			decision = player["decision"] if player["decision"] is not None else player["default_action"]
			data = player["data"]

			if decision == "click":
				player["inventory"]["clicks"] += 1
			elif decision in ["buy", "sell"]:
				self.trade(player, data)
			elif decision == "craft":
				self.craft(player, data["item"], data["count"])

			player["decision"] = None

		self.ticks += 1
