playerj = {
	"id": None,
	"name": "???",
	"password": None,

	"last_online": None,
	"online": None,

	"baseweightcapacity": 25,
	"weight": 0,
	"capacity": 0,

	"inventory": {
		"clicks": 0,
	},

	"storage": {},

	"location": "Cairo",
	"market": "wheat",

	"decision": None,
	"default_action": "click",
	"data": None,

	"buys": {},

	"sells": {},

	"log": []
}


cities = [

	{"name": "Port Said", "coords": [210,23],
	"craftable": {
		"fish": [{"clicks":10}],
		"ship": [{"clicks":2000}],
	}},

	{"name": "Al Arish", "coords": [310,43],
	"craftable": {
		"fish": [{"clicks":10}],
		"ship": [{"clicks":2000}],
	}},

	{"name": "Al Ismailiyyah", "coords": [210,53],
	"craftable": {
		"fish": [{"clicks":10}],
		"ship": [{"clicks":2000}],
	}},

	{"name": "Alexandria", "coords": [40,23],
	"craftable": {
		"fish": [{"clicks":10}],
		"ship": [{"clicks":2000}],
	}},

	{"name": "Tanta", "coords": [112,50],
	"craftable": {
		"meat": [{"clicks":30}],
		"copper": [{"clicks":5}],
		"lapis lazuli": [{"clicks":200}],
	}},

    {"name": "Cairo", "coords": [142,80],
	"craftable": {
		"camel": [{"clicks":10}],
		"wheat": [{"clicks":1}],
		"beer": [{"clicks":25}],
		"knife": [{"clicks":10, "copper":5}],
		"linen": [{"clicks":150}],
		"papyrus": [{"clicks":250}],
		"pouch": [{"clicks":10}],
		"factory": [{"clicks":1000}],
	}},


]

tradeable = set()
for city in cities:
	for item in city["craftable"]:
		tradeable.add(item)

#tradeable = sorted(list(tradeable))
#for item in tradeable:
#	print("\""+item+"\": {\"weight\":},")

tradeable = {
"beer": {"weight":1},
"camel": {"weight":0, "capacity":250},
"copper": {"weight":5},
"factory": {"weight":10},
"fish": {"weight":1},
"gold": {"weight":1},
"iron": {"weight":5},
"knife": {"weight":1},
"lapis lazuli": {"weight":1},
"linen": {"weight":5},
"meat": {"weight":3},
"papyrus": {"weight":5},
"pouch": {"weight":5, "capacity": 20},
"ship": {"weight":10},
"silver": {"weight":1},
"wheat": {"weight":1},

}

def getCity(name):
	for city in cities:
		if city["name"] == name:
			return city

routes = [
	["Alexandria", "Cairo", {"camel": 10, "boat":5}],
	["Tanta", "Cairo", {"camel": 10, "boat": 1}],
	["Tanta", "Port Said", {"camel": 15, "boat": 10}],
	["Alexandria", "Port Said", {"boat": 10}],
	["Tanta", "Al Ismailiyyah", {"camel": 15, "boat":8}],
	["Suez", "Al Ismailiyyah", {"camel": 10, "boat":3}],
	["Cairo", "Al Fayyum", {"camel": 10}],
]

def getRoute(a, b):
	for route in routes:
		if (route[0] == a and route[1] == b) or (route[0] == b and route[1] == a):
			return route

def rmultiply(req, factor):
	return {key:value*factor for key, value in req.items()}
