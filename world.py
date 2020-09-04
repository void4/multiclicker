from collections import defaultdict, Counter

from models import *

class World:
	def __init__(self):
		self.players = []
		self.stats = []

	def require(self, player, d):
		if all([player["inventory"][key] >= value for key, value in d.items()]):
			for key, value in d.items():
				player["inventory"][key] -= value
			return True

		return False

	def buy(self, player, d):

		if d["volume"] <= 0:# or d["price"]*d["volume"] > player["inventory"]["clicks"]:
			return

		if d["type"] in ["market", "limit"]:
			for trader, order in self.getMarket(d["item"], "sells", "lowest"):

				if d["type"] == "limit" and order["price"] > d["price"]:
					break

				volumedelta = min(order["volume"], d["volume"])

				if self.exchange(player, trader, d["item"], volumedelta, order["price"]):
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

			self.stats[-1]["tradevolume"] += cost
			self.stats[-1]["price"] = price

			return True

		return False

	def sell(self, player, d):

		if d["volume"] <= 0:
			return

		if d["type"] in ["market", "limit"]:
			for trader, order in self.getMarket(d["item"], "buys", "highest"):

				if d["type"] == "limit" and order["price"] < d["price"]:
					break

				volumedelta = min(order["volume"], d["volume"])

				if self.exchange(trader, player, d["item"], volumedelta, order["price"]):
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
