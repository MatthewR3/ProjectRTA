from flask import Flask
from flask import render_template
import os
import pathRouter
from flask import jsonify

app = Flask(__name__)



# Default response; return empty string
@app.route("/")
def main():
	return "Main page"

# If user inputs two points, generates trip
# TODO: Find trip format from google maps API
# TODO: Calculate trip
# TODO: Add links to other parts
# This method will be the main method. We will specify rules with more arguments later like <gas_stations> or <attractions> for custom trips
@app.route("/trip/<pointA>/<pointB>/")
def trip(pointA, pointB):

	# https://developers.google.com/maps/documentation/directions/intro#DirectionsRequests
	# Google Maps Directions API general form
	# http://maps.googleapis.com/maps/api/directions/output?parameters

	debug = True
	if not debug:
		path = pathRouter.fullProcess(pointA, pointB, debug)
		response = {"debug": debug, "path": path}
		return jsonify(response)
	else:
		path, regionCoords = pathRouter.fullProcess(pointA, pointB, debug)
		response = { "debug": debug, "path": path, "coordsList": regionCoords}
		return jsonify(response)

@app.route("/demo/")
def demo():
	return render_template("demo.html")



if __name__ == "__main__":
	#print pathRouter.fullProcess("Chicago, IL", "Evanston, IL")
	app.run(debug=True)
	#print trip("Chicago, IL", "Champaign, IL")
