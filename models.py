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
		"clicks": 1000,
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

	{"name": "Port Said", "coords": [201, 41],
	"craftable": {
		"fish": [{"clicks":10}],
		"ship": [{"clicks":2000}],
	}},

	{"name": "Al Arish", "coords": [264, 47],
	"craftable": {
		"fish": [{"clicks":10}],
		"ship": [{"clicks":2000}],
	}},

	{"name": "Al Ismailiyyah", "coords": [201, 71],
	"craftable": {
		"fish": [{"clicks":10}],
		"ship": [{"clicks":2000}],
	}},

	{"name": "Alexandria", "coords": [99, 46],
	"craftable": {
		"fish": [{"clicks":10}],
		"ship": [{"clicks":2000}],
	}},

	{"name": "Tanta", "coords": [145, 62],
	"craftable": {
		"meat": [{"clicks":30}],
		"copper": [{"clicks":5}],
		"lapis lazuli": [{"clicks":200}],
	}},

    {"name": "Cairo", "coords": [159, 98],
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

	{"name": "Suez", "coords": [212, 101],
	"craftable": {
	  "lapis lazuli": [{"clicks":200}],
	  "silver": [{"clicks":250}],
	  "gold": [{"clicks":500}],
	}},

	{"name": "Al Fayyum", "coords": [137, 135],
	"craftable": {
	  "lapis lazuli": [{"clicks":200}],
	  "silver": [{"clicks":250}],
	  "gold": [{"clicks":500}],
	}},

	{"name": "Bani Suwayf", "coords": [148, 148],
	"craftable": {
	  "lapis lazuli": [{"clicks":200}],
	  "silver": [{"clicks":250}],
	  "gold": [{"clicks":500}],
	}},

	{"name": "At Tur", "coords": [261, 186],
	"craftable": {
	  "iron": [{"clicks":30}],
	  "copper": [{"clicks":5}],
	}},

	{"name": "Al Minya", "coords": [131, 196],
	"craftable": {
	  "lapis lazuli": [{"clicks":200}],
	  "silver": [{"clicks":250}],
	  "gold": [{"clicks":500}],
	}},

	{"name": "Sharm el-Sheikh", "coords": [290, 204],
	"craftable": {
	  "lapis lazuli": [{"clicks":200}],
	  "silver": [{"clicks":250}],
	  "gold": [{"clicks":500}],
	}},

	{"name": "Hurghada", "coords": [267, 236],
	"craftable": {
	  "lapis lazuli": [{"clicks":200}],
	  "silver": [{"clicks":250}],
	  "gold": [{"clicks":500}],
	}},

	{"name": "Asyut", "coords": [153, 240],
	"craftable": {
	  "lapis lazuli": [{"clicks":200}],
	  "silver": [{"clicks":250}],
	  "gold": [{"clicks":500}],
	}},

	{"name": "Suhaj", "coords": [175, 271],
	"craftable": {
	  "lapis lazuli": [{"clicks":200}],
	  "silver": [{"clicks":250}],
	  "gold": [{"clicks":500}],
	}},

	{"name": "Qina", "coords": [221, 286],
	"craftable": {
	  "lapis lazuli": [{"clicks":200}],
	  "silver": [{"clicks":250}],
	  "gold": [{"clicks":500}],
	}},

	{"name": "Luxor", "coords": [221, 311],
	"craftable": {
	  "lapis lazuli": [{"clicks":200}],
	  "silver": [{"clicks":250}],
	  "gold": [{"clicks":500}],
	}},

	{"name": "Mut", "coords": [57, 324],
	"craftable": {
	  "lapis lazuli": [{"clicks":200}],
	  "silver": [{"clicks":250}],
	  "gold": [{"clicks":500}],
	}},

	{"name": "Al Kharjah", "coords": [125, 324],
	"craftable": {
	  "lapis lazuli": [{"clicks":200}],
	  "silver": [{"clicks":250}],
	  "gold": [{"clicks":500}],
	}},

	{"name": "Idfu", "coords": [231, 348],
	"craftable": {
	  "lapis lazuli": [{"clicks":200}],
	  "silver": [{"clicks":250}],
	  "gold": [{"clicks":500}],
	}},

	{"name": "Aswan", "coords": [231, 391],
	"craftable": {
	  "lapis lazuli": [{"clicks":200}],
	  "silver": [{"clicks":250}],
	  "gold": [{"clicks":500}],
	}},

]

tradeable = set()
for city in cities:

	city["craftable"] = dict(sorted(city["craftable"].items()))

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
	["Alexandria", "Cairo", {"camel": 10, "ship":5}],
	["Tanta", "Cairo", {"camel": 10, "ship": 5}],
	["Tanta", "Alexandria", {"camel": 10, "ship": 5}],
	["Tanta", "Port Said", {"camel": 15, "ship": 10}],
	["Alexandria", "Port Said", {"ship": 10}],
	["Port Said", "Al Arish", {"camel": 10, "ship": 5}],
	["Port Said", "Al Ismailiyyah", {"camel": 10, "ship": 5}],
	["Tanta", "Al Ismailiyyah", {"camel": 15, "ship":8}],
	["Suez", "Al Ismailiyyah", {"camel": 10, "ship":3}],
	["Cairo", "Al Fayyum", {"camel": 10}],
	["Cairo", "Suez", {"camel": 15}],
	["Cairo", "Al Ismailiyyah", {"camel": 10, "ship":5}],
	["Cairo", "Port Said", {"camel": 15, "ship":10}],
	["Al Ismailiyyah", "Al Arish", {"camel": 20}],

	["Cairo", "Bani Suwayf", {"camel": 10, "ship":5}],
	["Bani Suwayf", "Al Minya", {"camel": 10, "ship":5}],
	["Bani Suwayf", "Al Fayyum", {"camel": 10}],
	["Al Minya", "Asyut", {"camel": 10, "ship":5}],
	["Asyut", "Suhaj", {"camel": 10, "ship":5}],
	["Suhaj", "Qina", {"camel": 10, "ship":5}],
	["Qina", "Luxor", {"camel": 10, "ship":5}],
	["Luxor", "Idfu", {"camel": 10, "ship":5}],
	["Idfu", "Aswan", {"camel": 10, "ship":5}],

	["Asyut", "Hurghada", {"camel": 25}],
	["Suhaj", "Hurghada", {"camel": 20}],
	["Qina", "Hurghada", {"camel": 20}],

	["Hurghada", "Sharm el-Sheikh", {"ship": 10}],
	["Hurghada", "At Tur", {"ship": 10}],

	["Sharm el-Sheikh", "At Tur", {"camel": 15, "ship": 10}],
	["At Tur", "Suez", {"camel": 60, "ship": 15}],

	["Suez", "Al Ismailiyyah", {"camel": 15, "ship": 5}],
	["Suez", "Al Arish", {"camel": 30}],

	["Luxor", "Al Kharjah", {"camel": 30}],
	["Idfu", "Al Kharjah", {"camel": 35}],
	["Suhaj", "Al Kharjah", {"camel": 50}],

	["Suhaj", "Mut", {"camel": 90}],
	["Al Kharjah", "Mut", {"camel": 25}],

]

def getRoute(a, b):
	for route in routes:
		if (route[0] == a and route[1] == b) or (route[0] == b and route[1] == a):
			return route

def rmultiply(req, factor):
	return {key:value*factor for key, value in req.items()}
