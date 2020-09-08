var socket = window.location.hostname == "qewasd.com" ? io({path:"/multisocket/socket.io/"}) : io(":9999");

function send(type, data) {
  socket.emit("json", {"type":type, "data":data})
}

socket.on('connect', function(){
  var username = getCookie("username");
  var password = getCookie("password");

  if (username != "" && password != "") {
    send("savelogin", {"username":username, "password":password})
  }
  //var name = "" + new Date().getTime();
  //send("login", {"name":name})
});

socket.on('event', function(data){
  console.log(data)
});

socket.on('json', function(message){
  var username = document.querySelector("#username")
  var password = document.querySelector("#password")
  //console.log(message)
  var type = message["type"]
  var data = message["data"]
  console.log(type, data)
  if (type == "login") {
    console.log("LOGIN:", data)
    app.online = true;
    setCookie("username", username.value)
    setCookie("password", password.value)
  } else if (type == "randomname") {
    var cookie_username = getCookie("username");
    var cookie_password = getCookie("password");
    if (cookie_username=="" && username.value=="") {
      console.log(data)
      username.value = data;
      app.saveLogin()
    }
    //}
  } else if (type == "player") {
    app.player = data;
  } else if (type == "markets") {
    app.markets = data;
    if (Object.keys(app.market).length == 0) {
      app.getMarket(app.markets[0])
    }
  } else if (type == "market") {
    app.market = data;
    app.order.price = data["lastprice"]
    app.order.estprice = data["lastprice"]
    app.order.item = data["item"]
  } else if (type == "cities") {
    app.cities = data;
  } else if (type == "routes") {
    app.routes = data;
  } else if (type == "items") {
    app.items = data;
  } else if (type == "travelinfo") {
    app.travelinfo = data;
  } else if (type == "city") {
    app.city = data;
    app.travelinfo = null;
  }
});

socket.on('message', function(data){
  console.log(data)
});

socket.on('disconnect', function(){

});

window.addEventListener("beforeunload", function() {
  console.log("Disconnecting...")
  socket.disconnect();
});

function joinDict(object, glue, separator) {

  if (glue == undefined)
    glue = ' ';

  if (separator == undefined)
    separator = ',';

  var result = "";

  for (const [ key, value ] of Object.entries(object)) {
    result += value + glue + key + separator
  }

  return result.slice(0, -1)
}

function indexOfSmallest(a) {
 return a.indexOf(Math.min.apply(Math, a));
}

function count(array, el) {
  var count = 0;
  for(var i = 0; i < array.length; ++i){
      if(array[i] == el)
          count++;
  }
  return count;
}


var darkTheme = {
	chart: {
		layout: {
			backgroundColor: "rgba(219, 209, 140, 0.55)",//'#2B2B43',
			lineColor: '#2B2B43',
			textColor: 'rgb(0,0,0)',
		},
		watermark: {
			color: 'rgba(0, 0, 0, 0)',
		},
		crosshair: {
			color: '#758696',
		},
		grid: {
			vertLines: {
				color: '#2B2B43',
			},
			horzLines: {
				color: '#363C4E',
			},
		},
	},
	series: {
			topColor: 'rgba(32, 226, 47, 0.56)',
			bottomColor: 'rgba(32, 226, 47, 0.04)',
			lineColor: 'rgba(32, 226, 47, 1)',
	},
  volume: {
    lineColor: 'rgba(255,0,0,1)'
  }
};

Vue.component("marketchart", {
  template: `<div ref="chart"></div>`,
  mounted: function() {
    //console.log("CHART MOUNTED")
      const chart = LightweightCharts.createChart(this.$refs.chart, { width: 600, height: 300 });
      const lineSeries = chart.addLineSeries();
      lineSeries.setData(app.market.pricehistory);
      const volumeSeries = chart.addHistogramSeries({
        priceFormat: "volume",
        color: "rgba(200,150,10,1)",
        priceScaleId: '',
        scaleMargins: {
          top: 0.8,
          bottom: 0,
        },
      })

      volumeSeries.setData(app.market.volumehistory)
      chart.applyOptions(darkTheme.chart);
      //volumeSeries.applyOptions(darkTheme.volume)
  },
  updated: function() {
    console.log("UPDATED")
  },
  activated: function() {
    console.log("ACTIVATED")
  }
})

var app = new Vue({
  el: '#app',
  data: {
    online: false,
    player: {},
    bos: "buy",
    orders: [],
    order: {bos: "buy", type: "limit"},
    markets: [],
    market: {},
    loc: [0, 0, 0],
    cities: [],
    routes: [],
    storeamount: 1,
    items: {},
    travelinfo: null,
    city: null,
  },
  /*
  watch: {
      market: function() {
        console.log("CHANGED!")

      }
  },
  */
  methods: {
    decide(name) {
      socket.emit("json", {"type":"decision", "data":name})
    },
    getMarket(name) {
      send("market", name)
    },
    submitOrder() {
      send("order", app.order)
    },
    orderChange(index) {
      if (app.order.type=="limit") {
        app.loc[index] = new Date().getTime();

        if (count([app.order.volume, app.order.price, app.order.cost], null) < 2) {
          var smol = indexOfSmallest(app.loc)

          if (smol == 0) {
            app.order.volume = app.order.cost/app.order.price
          } else if (smol == 1) {
            app.order.price = app.order.cost/app.order.volume
          } else if (smol == 2) {
            app.order.cost = app.order.volume*app.order.price
          }
        }
      } else {
        if (app.order.estprice != null) {
          app.order.estcost = app.order.volume * app.order.estprice;
        }
      }
    },
    craft(item) {
      send("craft", {"item":item, "count": parseInt(app.storeamount)})
    },
    getTravelInfo(city) {
      send("getTravelInfo", city)
    },
    travel(city, mode) {
      send("travel", {"city":city, "mode":mode})
    },
    getCity(name) {
      for (var city of app.cities) {
        if (city.name == name) {
          return city
        }
      }
    },
    getCurrentCity() {
      return app.getCity(app.player.location)
    },
    store(key) {
      send("store", {"item":key, "count":parseInt(app.storeamount)})
    },
    unstore(key) {
      send("unstore", {"item":key, "count":parseInt(app.storeamount)})
    },
    cancelOrder(bos, oid) {
      send("cancelOrder", {"bos":bos, "oid":oid})
    },
    acceptOrder(bos, oid) {
      send("acceptOrder", {"bos":bos, "oid":oid})
    },
    saveLogin() {
      var username = document.querySelector("#username").value
      var password = document.querySelector("#password").value
      send("savelogin", {"username":username, "password":password})
    },
    logout() {
      send("logout", null)
      app.player = {};
      app.market = [];
      app.markets = [];
      app.orders = [];
      app.routes = [];
      app.online = false;
      setCookie("username", "")
      setCookie("password", "")
    },
    randomName() {
      send('randomname', null)
    }
  }
});



var canvas = document.querySelector('canvas')
var ctx = canvas.getContext("2d")

function draw() {

  if (app.player == null) {
    return;
  }

  var map = document.getElementById("map")

  if (!map) {
    return;
  }

  var rect = map.getBoundingClientRect();

  canvas.style.left = rect.left + "px";
  canvas.style.top = rect.top + "px";

  ctx.canvas.width  = rect.width;
  ctx.canvas.height = rect.height;

  ctx.drawImage(map, 0, 0)

  var city = app.getCurrentCity()

  if (city) {
    for (var route of app.routes) {
      var other = null;
      if (route[0]==city.name) {
        other = app.getCity(route[1])
      } else if (route[1]==city.name) {
        other = app.getCity(route[0])
      }

      if (other!=null) {
        for (const [mode, length] of Object.entries(route[2])) {
          ctx.beginPath();

          if (mode == "ship") {
            ctx.lineWidth = "4";
            ctx.strokeStyle = `rgb(0,0,${200-length})`;
          } else if (mode == "camel") {
            ctx.lineWidth = "8";
            ctx.strokeStyle = `rgb(${200-length},0,0)`;
          }
          ctx.moveTo(city.coords[0], city.coords[1])
          ctx.lineTo(other.coords[0], other.coords[1]);
          ctx.stroke();
        }
      }
    }

    ctx.beginPath();
    ctx.lineWidth = "6";
    ctx.strokeStyle = "red";
    ctx.rect(city.coords[0], city.coords[1], city.coords[2], city.coords[3]);
    ctx.stroke();
  }


}

document.addEventListener('readystatechange', event => {
    if (event.target.readyState === "interactive") {
        setInterval(draw, 25)
    }
})

function getCursorPosition(canvas, event) {
    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    console.log("x: " + x + " y: " + y)
}

canvas.addEventListener('mousemove', function(e) {
    //getCursorPosition(canvas, e)
})


function setCookie(cname, cvalue, exdays) {
  if (exdays==undefined) {
    exdays = 7;
  }
  var d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
  var expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}
