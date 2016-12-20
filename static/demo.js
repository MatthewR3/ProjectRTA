$(document).ready(function() {

	console.log("jQuery Loaded");

});

function get_trip() {
	point_a = $("#point_a").val().replace(/ /g,'').replace(" ", "");
	point_b = $("#point_b").val().replace(/ /g,'').replace(" ", "");
	// console.log(point_a);
	// console.log(point_b);
	$("#gmaps_container").html('<iframe id="iframe" width="100%" height="100%" frameborder="0" style="border:0" src="" allowfullscreen></iframe>');
	$.ajax({
		url: "http://127.0.0.1:5000/trip/" + point_a + "/" + point_b + "/",
		crossDomain: true,
		xhrFields: {
			withCredentials: true
		},
		success: function(data){
			// console.log(data);
			// console.log(data["path"])
			// console.log(data[""])
			$("#gmaps_container").html('<iframe width="100%" height="100%" frameborder="0" style="border:0" src="' + data["path"] + '" allowfullscreen></iframe>');
			if (data["debug"] == true) {
				initMap(data["coordsList"]);
			}
		},
		failure: function(){
			alert("Failure to receive data");
		},
	});
}


function initMap(coordsList) {

	console.log("COORDSLIST:");
	console.log(coordsList);
	console.log(coordsList[0]);
	center = {"lat": coordsList[0][0], "lng": coordsList[0][1]};
	console.log(center);

	var map = new google.maps.Map(document.getElementById('gmaps_markers'), {
		zoom: 4,
		center: center,
	});

	for (i in coordsList) {
		coords = coordsList[i];
		console.log("COORDS:");
		console.log(coords);
		coord = {"lat": coords[0], "lng": coords[1]};
		console.log(coord);
		var marker = new google.maps.Marker({
			position: coord,
			map: map,
			title: "Region Point"
		});
	}

	for (i in coordsList) {
		console.log(coordsList);
		coords = coordsList[i];
		console.log(coords);
		// hiLat = max(coords[0], coords[0])
		var regionCoords = [
		    {lat: 25.774, lng: -80.190},
		    {lat: 18.466, lng: -66.118},
		    {lat: 32.321, lng: -64.757},
		    {lat: 25.774, lng: -80.190}
		];

	  // Construct the polygon.
		var region = new google.maps.Polygon({
			paths: regionCoords,
			strokeColor: '#FF0000',
			strokeOpacity: 0.8,
			strokeWeight: 2,
			fillColor: '#FF0000',
			fillOpacity: 0.35
		});
		region.setMap(map);
		}

}