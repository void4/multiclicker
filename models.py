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
	"market": "wheat",

	"decision": None,
	"default_action": "click",
	"data": None,

	"buys": [],

	"sells": [],

	"log": []
}


cities = [
    {"name": "Cairo", "coords": [142,80,50,50]},
	{"name": "Tanta", "coords": [112,50,50,50]},
	{"name": "Alexandria", "coords": [10,23,50,50]},
	{"name": "At Tur", "coords": [258,173,50,50]},
	{"name": "Aswan", "coords": [224,386,50,50]},
]

routes = [
	["Alexandria", "Cairo", 5],
]

craftable = {
	"wheat": [{"clicks":1}],
	"iron": [{"clicks":30}],
	"copper": [{"clicks":5}],
	"fish": [{"clicks":10}],
	"beer": [{"clicks":25}],
	"meat": [{"clicks":30}],
	"knife": [{"clicks":10, "copper":5}],
	"linen": [{"clicks":150}],
	"lapis lazuli": [{"clicks":200}],
	"papyrus": [{"clicks":250}],
	"silver": [{"clicks":250}],
	"gold": [{"clicks":500}],
	"factory": [{"clicks":1000}, "clicks += 1", ""],
	"ship": [{"clicks":2000}, "clicks += 1", ""],
}

actions = {
	"click": [None, "clicks += 1"],
	"craft": [None, "craft(data)"],
	"buy": [None, "buy(data)"],
	"sell": [None, "sell(data)"],
}

def rmultiply(req, factor):
	return {key:value*factor for key, value in req.items()}
