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

def rmultiply(req, factor):
	return {key:value*factor for key, value in req.items()}
