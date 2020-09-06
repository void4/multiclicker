playerj = {
	"id": None,
	"name": "???",
	"password": None,

	"last_online": None,
	"online": None,

	"inventory": {
		"clicks": 0,
	},

	"location": "Cairo",

	"decision": None,
	"default_action": "click",
	"data": None,

	"buys": [],

	"sells": [],

	"log": []
}


cities = [
    {"name": "Cairo", "coords": [142,80,190,130]},
	{"name": "Alexandria", "coords": [10,23,60,73]},
	{"name": "At Tur", "coords": [258,173,308,223]},
	{"name": "Aswan", "coords": [224,386,274,436]},
]

craftable = {
	"factory": [{"clicks":10}, "clicks += 1", ""],
	"ship": [{"clicks":20}, "clicks += 1", ""],
}

actions = {
	"click": [None, "clicks += 1"],
	"craft": [None, "craft(data)"],
	"buy": [None, "buy(data)"],
	"sell": [None, "sell(data)"],
}

def rmultiply(req, factor):
	return {key:value*factor for key, value in req.items()}
