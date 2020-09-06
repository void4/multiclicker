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
    {"name": "Cairo", "coords": [142,80,50,50],
	"craftable": {
		"camel": [{"clicks":10}],
		"wheat": [{"clicks":1}],
		"beer": [{"clicks":25}],
		"knife": [{"clicks":10, "copper":5}],
		"linen": [{"clicks":150}],
		"papyrus": [{"clicks":250}],
		"pouch": [{"clicks":10}],
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
	["Alexandria", "Cairo", {"clicks": 10}],
]

def getRoute(a, b):
	for route in routes:
		if (route[0] == a and route[1] == b) or (route[0] == b and route[1] == a):
			return route

def rmultiply(req, factor):
	return {key:value*factor for key, value in req.items()}
