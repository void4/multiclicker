from collections import defaultdict, Counter
from copy import deepcopy
from random import sample

from models import *

class World:
	def __init__(self):
		self.ticks = 0
		self.pid = 0
		self.players = []
		self.stats = []

	def new_player(self):
		player = deepcopy(playerj)
		player["id"] = self.pid
		self.pid += 1
		self.players.append(player)
		return player

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
		if all([player["inventory"][key] >= value for key, value in d.items()]):
			for key, value in d.items():
				player["inventory"][key] -= value
			return True

		return False

	def trade(self, player, d):

		if d["volume"] <= 0:# or d["price"]*d["volume"] > player["inventory"]["clicks"]:
			return

		if d["bos"] == "sell":
			market = self.getMarket(d["item"], "buys", "highest")
		else:
			market = self.getMarket(d["item"], "sells", "lowest")

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

				if self.exchange(buyer, seller, d["item"], volumedelta, order["price"]):
					order["volume"] -= volumedelta
					d["volume"] -= volumedelta

					if order["volume"] == 0:
						trader["sells" if d["bos"] == "buy" else "buys"].remove(order)

					if d["volume"] == 0:
						break

		if d["type"] == "limit" and d["volume"] > 0:

			if d["bos"] == "buy":
				#buy/sell only in clicks? works in eve, but there credits arent mined
				outstanding_buys = sum([order["price"]*order["volume"] for order in player["buys"]])
				cost = d["price"]*d["volume"]

				# kinda doesnt work if money lost in the meantime, but hey
				if cost + outstanding_buys <= player["inventory"].get("clicks", 0):
					#pre-deduct?
					#(successful?) order and tx costs
					player["buys"].append(d)

			else:
				outstanding_sells = sum([order["volume"] for order in player["buys"] if order["item"] == d["item"]])

				if d["volume"] + outstanding_sells <= player["inventory"].get(d["item"], 0):
					player["sells"].append(d)

	def getMarket(self, item, bos="buy", sort="lowest"):
		market = []
		for player in self.players:
			for order in player[bos]:
				if order["item"] == item:
					 market.append([player, order])

		# TODO: sort same-price orders by longest standing
		return sorted(market, key=lambda op: op[1]["price"], reverse=sort=="highest")

	def exchange(self, a, b, item, volume, price):
		"""a gets items, b gets money"""
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

			self.stats[-1]["tradevolume"+item] += cost
			self.stats[-1]["price"+item] = price

			return True

		return False


	def clearOldOrders(self):
		for player in self.players:
			for bos in ["buys", "sells"]:
				for order in list(player[bos]):
					if order.get("ticks", None) is not None and order["ticks"] <= 0:
						player[bos].remove(order)

	def craft(self, player, item, number=1):
		craft = craftable[item]
		if self.require(player, rmultiply(craft[0], number)):
			player["inventory"][item] = player["inventory"].get(item, 0) + number
		else:
			pass
			#print("insufficient resources")

	def cancelOrder(self, player, bos, index):
		player[bos].pop(index)

	def ranking(self):
		return sorted(self.players, key=lambda player:player["inventory"]["clicks"], reverse=True)

	def tick(self):

		print("TICK")

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
