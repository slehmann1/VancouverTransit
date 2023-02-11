
var colors = ['#1a9850', '#91cf60', '#d9ef8b', '#ffffbf', '#fee08b', '#fc8d59', '#d73027']
var naColor = '#ccb0c2'
var leg_vals = [30, 60, 90, 120, 150, 180]

map = L.map('map').setView([49.2827, -123.1207], 12);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, <a href="https://www.translink.ca/">Data From Translink</a>'
}).addTo(map);


data = JSON.parse(raw_data);


for (let i = 0; i < data.length; i++) {
    let circle = L.circle([data[i].Lat, data[i].Lon], {
        color: getColor(data[i].Value),
        fillOpacity: 0.5,
        radius: 15
    }).addTo(map);

    circle.bindPopup(data[i].Name + "<br/> Mean Delay: " + Math.round(data[i].Value) + " Seconds")

}

var legend = L.control({ position: 'bottomright' });
legend.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'), labels = [];

    // Fill the text in the legend
    div.innerHTML +=
        'Mean Delay In Seconds: <br> <i style="background:' +  getColor(leg_vals[0]) + '"></i> ≤ ' + leg_vals[0] + ' <br>';

    for (var i = 0; i < leg_vals.length - 1; i++) {
        div.innerHTML +=
            '<i style="background:' + getColor(leg_vals[i] + 1) + '"></i> ' +
            leg_vals[i] + '&ndash;' + leg_vals[i + 1] + '<br>';
    }

    div.innerHTML +=
        '<i style="background:' + getColor(leg_vals[leg_vals.length]) + '"></i> ≥ ' + leg_vals[leg_vals.length - 1] + ' <br>';

    div.innerHTML +=
        '<i style="background:' + naColor + '"></i> No Data';

    return div;
};

legend.addTo(map);

function getColor(d) {

    if (d == "None") {
        return naColor;
    }

    for (let i = 0; i < leg_vals.length; i++) {
        if (d <= leg_vals[i]) {
            return colors[i]
        }
    }

    return colors[colors.length - 1];
}
