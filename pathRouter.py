# This file serves to be the main module for defining the path for a user to take
 
import httplib2, socket, ssl
import json, unicodedata
import math
import yelpSearch
import regions
 
GOOGLE_KEY = "AIzaSyDrG7t4ut71GwOCSYXUJryP5HOPWZJWAMs"
YELP_KEY = "HskFxqEANFZQb6gNpLLTlA"
 
 
 
# Google Goeocoding API Docs:
#https://developers.google.com/maps/documentation/geocoding/intro#geocoding
 
# Address --> Coords using Google Geocoding API
# Required Params: address, key
# Example Request:
# https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,
# +Mountain+View,+CA&key=AIzaSyDrG7t4ut71GwOCSYXUJryP5HOPWZJWAMs
def addressToCoords(address):
	requestURL = "https://maps.googleapis.com/maps/api/geocode/json?address=" + \
 				address.replace(" ", "") + "&key=" + GOOGLE_KEY
	con = httplib2.Http()
	# Warning, don't try to print full content or contentDict; it can be very 
	# large and may crash the script
	response, content = con.request(requestURL)
	if response.status == 200:
		contentDict = json.loads(content)
		return 	(contentDict["results"][0]["geometry"]["location"]["lat"], \
				contentDict["results"][0]["geometry"]["location"]["lng"])
	return None


# Coords --> Address using Google Geocoding API
# Required Params: latlng, key
# Example Request:
# https://maps.googleapis.com/maps/api/geocode/json \
# ?latlng=40.714224,-73.961452&key=AIzaSyDrG7t4ut71GwOCSYXUJryP5HOPWZJWAMs
def coordsToAddress(coords):
	requestURL = "https://maps.googleapis.com/maps/api/geocode/json?latlng=" + \
				str(coords[0]) + "," + str(coords[1]) + "&key=" + GOOGLE_KEY
	con = httplib2.Http()
	response, content = con.request(requestURL)
	# Warning, don't try to print full content or contentDict; it can be very large 
	# and may crash the script
	if response.status == 200:
		contentDict = json.loads(content)
		if contentDict["results"] == []:
			return None
		addressComp = contentDict["results"][0]["address_components"]
		return 	addressComp[0]["long_name"] + " " + addressComp[1]["long_name"] + " " +\
				addressComp[2]["long_name"] + ", " + addressComp[3]["long_name"]
	return None



# PlaceID --> Address using Google Geocoding API
# Required Params: placeID, key
# Example Request:
# https://maps.googleapis.com/maps/api/geocode/json?
# place_id=ChIJd8BlQ2BZwokRAFUEcm_qrcA&key=AIzaSyDrG7t4ut71GwOCSYXUJryP5HOPWZJWAMs
def placeIDToAddress(placeID):
	requestURL = "https://maps.googleapis.com/maps/api/geocode/json?place_id=" + \
				placeID + "&key=" + GOOGLE_KEY
	con = httplib2.Http()
	response, content = con.request(requestURL)
	# Warning, don't try to print full content; it can be very large and may crash 
	# the script
	if response.status == 200:
		contentDict = json.loads(content)
		addressComp = contentDict["results"][0]["address_components"]
		return 	addressComp[0]["long_name"] + " " + addressComp[1]["long_name"] + " " +\
				addressComp[2]["long_name"] + ", " + addressComp[3]["long_name"]
	return None



# Google Directions API Docs:
#https://developers.google.com/maps/documentation/directions/intro#RequestParameters

# Directions Path using Google Directions API
# Example of Toronto --> Montreal B request URL
# https://maps.googleapis.com/maps/api/directions/json
# ?origin=Toronto&destination=Montreal&key=AIzaSyDrG7t4ut71GwOCSYXUJryP5HOPWZJWAMs
def getBasicPath(pointA, pointB):
	requestURL = "https://maps.googleapis.com/maps/api/directions/json?origin=" +\
				str(pointA).replace(" ", "") + "&destination=" + \
				str(pointB).replace(" ", "") + "&key=" + GOOGLE_KEY
	con = httplib2.Http()
	response, content = con.request(requestURL)
	# Warning, don't try to print full content or contentDict; it can be very large 
	# and may crash the script
	if response.status == 200:
		contentDict = json.loads(content)
		#contentDict["results"][0]["address_components"][0]["long_name"]
		return contentDict
	return None

	# Returns a JSON object of format:
	# https://developers.google.com/maps/documentation/directions/intro#sample-response



# Takes contentDict from getBasicPath() and returns list of coordinate tuples of 
# points along the basic path
# TODO: Check that points don't have overlapping search radii (probably use 
# (distance < (radius / 2) as cutoff)
def getPathPoints(path):
	pathPoints = []
	for x in range(len(path["routes"][0]["legs"][0]["steps"])):
		lat = path["routes"][0]["legs"][0]["steps"][x]["start_location"]["lat"]
		lng = path["routes"][0]["legs"][0]["steps"][x]["start_location"]["lng"]
		pathPoints += (lat, lng),
	prunedPathPoints = regions.prunePathPoints(pathPoints)
	return prunedPathPoints


# Point A --> Point B with waypoints using Google Directions API
# NOTE: Use list of addresses for waypoints
# Example of Boston --> Concord with waypoints Charlestown and Lexington request URL
# https://maps.googleapis.com/maps/api/directions/json
# ?origin=Boston,MA&destination=Concord,MA&waypoints=Charlestown,MA
# |Lexington,MA&key=AIzaSyDrG7t4ut71GwOCSYXUJryP5HOPWZJWAMs
def getFullPath(pointA, pointB, waypoints):
	# OLD REQUEST URL: Keep just in case
	# Google Maps uses a new URL with "embed" in the path; use that one 
	# (example given in demo.html)
	# requestURL = "https://maps.googleapis.com/maps/api/directions/json?origin=" \
	# + pointA.replace(" ", "") + "&destination=" + pointB.replace(" ", "") + \
	# "&waypoints="
	requestURL = "https://www.google.com/maps/embed/v1/directions?key=" + GOOGLE_KEY \
				+ "&origin=" + pointA.replace(" ", ",") + "&destination=" \
				+ pointB.replace(" ", ",").replace(",,", ",") + "&waypoints="
	for waypoint in waypoints:
		requestURL += waypoint.replace(" ", ",") + "|"
	# Removes trailing pipe
	requestURL = requestURL[:-1]
	requestURL += "&key=" + GOOGLE_KEY
	return requestURL



def fullProcess(pointA, pointB, debug):
	if debug:
		return debugFullProcess(pointA, pointB)
	else:
		basicPath = getBasicPath(pointA, pointB)
		pathPoints = getPathPoints(basicPath)
		regionsList = regions.pathRegions(pathPoints)
		completeWaypointList = regions.completeWaypointList(regionsList)
		finalAddressList = []
		# Converts addresses to coords
		for i in xrange(0,len(completeWaypointList)):
			finalAddressList.append(coordsToAddress(( \
					completeWaypointList[i].location.coordinate.latitude, \
					completeWaypointList[i].location.coordinate.longitude)))
		fullPathURL = getFullPath(pointA, pointB, finalAddressList)
		return fullPathURL



# Same as full process, but with print statements for each step
def debugFullProcess(pointA, pointB):

	# FULL PROCESS

	a1 = pointA
	a2 = pointB
	p1 = addressToCoords(a1)
	p2 = addressToCoords(a2)
	print "POINT 1:"
	print p1
	print "POINT 2:"
	print p2

	# Gets basic path
	basicPath = getBasicPath(a1, a2)
	print "BASIC PATH LENGTH:"
	print len(basicPath["routes"][0]["legs"][0]["steps"])

	# Gets path points and prunes
	pathPoints = getPathPoints(basicPath)
	print "PATH POINTS LENGTH:"
	print len(pathPoints)

	# Gets list of regions along path
	regionsList = regions.pathRegions(pathPoints)
	print "REGIONS LIST LENGTH:"
	print len(regionsList)
	print "REGIONS LIST:"
	print regionsList

	# Gets all waypoints along route
	completeWaypointList = regions.completeWaypointList(regionsList)
	print "COMPLETE WAYPOINTS LIST LENGTH:"
	print len(completeWaypointList)
	print "COMPLETE WAYPOINTS LIST:"
	print completeWaypointList
	finalAddressList = []
	# Converts coords to addresses
	for i in xrange(0,len(completeWaypointList)):
		print completeWaypointList[i]
		finalAddressList.append(coordsToAddress(( \
					completeWaypointList[i].location.coordinate.latitude, \
					completeWaypointList[i].location.coordinate.longitude)))
	print "FINAL ADDRESS LIST:"
	print finalAddressList

	fullPathURL = getFullPath(a1, a2, finalAddressList)
	print "FULL PATH URL:"
	print fullPathURL
	print "\n\n\n"

	# Gets region boundary points in order to show markers on debug map
	regionCoords = []
	for region in regionsList:
		regionCoords += [region["low"], region["high"]]

	return fullPathURL, regionCoords










# Testing functions
if __name__ == "__main__":

	a1 = "Chicago, IL"
	a2 = "Champaign, IL"



	# print "Testing Full Process:"
	# fullPathURL = fullProcess(pointA, pointB, False)
	# print fullPathURL

	print "Testing Debug Full Process:"
	debugFullProcess(a1, a2)
