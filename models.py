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
    {"name": "Cairo", "coords": [142,80,50,50],
	"craftable": {
		"wheat": [{"clicks":1}],
		"beer": [{"clicks":25}],
		"knife": [{"clicks":10, "copper":5}],
		"linen": [{"clicks":150}],
		"papyrus": [{"clicks":250}],
		"factory": [{"clicks":1000}],
	}
	},

	{"name": "Tanta", "coords": [112,50,50,50],
	"craftable": {
		"meat": [{"clicks":30}],
		"copper": [{"clicks":5}],
		"lapis lazuli": [{"clicks":200}],
	}},

	{"name": "Alexandria", "coords": [10,23,50,50],
	"craftable": {
		"fish": [{"clicks":10}],
		"ship": [{"clicks":2000}],
	}},

	{"name": "At Tur", "coords": [258,173,50,50],
	"craftable": {
		"iron": [{"clicks":30}],
		"copper": [{"clicks":5}],
	}},

	{"name": "Aswan", "coords": [224,386,50,50],
	"craftable": {
		"lapis lazuli": [{"clicks":200}],
		"silver": [{"clicks":250}],
		"gold": [{"clicks":500}],
	}},
]

tradeable = set()
for city in cities:
	for item in city["craftable"]:
		tradeable.add(item)

tradeable = list(tradeable)

def getCity(name):
	for city in cities:
		if city["name"] == name:
			return city

routes = [
	["Alexandria", "Cairo", 5],
]

def rmultiply(req, factor):
	return {key:value*factor for key, value in req.items()}
