import math
import pathRouter
import yelpSearch

MIN_WIDTH = .05
MIN_HEIGHT = .05


# Two sets of Coords ---> Distance between
# Required Params: lat, lng of coords1 \ lat, lng of coords2
# CURRENTLY IN: MILES
def coordsDistance(coords1, coords2):
    #Earth's Radius, 3959 for miles, 6371000 for meters
    r = 3959
    
    #Convert from degrees to radians
    lat1 = math.radians(coords1[0])
    lng1 = math.radians(coords1[1])
    lat2 = math.radians(coords2[0])
    lng2 = math.radians(coords2[1])

    dlng = lng2 - lng1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    
    c = 2 * math.asin(math.sqrt(a))
    return c * r



# Prunes the list for points that are too close together
# TODO: Optimize ading in terminal point (currently just loops until len()-1
# 		and adds at end; may cause terminal point to be close to the last point)
def prunePathPoints(pathPoints):
	goodPoint = 0
	prunedPath = [pathPoints[0]]
	for i in xrange(0, len(pathPoints)-1):
		# Checks if points are too close
		if (coordsDistance(prunedPath[goodPoint], pathPoints[i]) < 150):
			continue
		# Checks if points are within 150 and 250 miles (good)
		elif (coordsDistance(prunedPath[goodPoint], pathPoints[i]) < 250):
			prunedPath.append(pathPoints[i])
			goodPoint+=1
		# If points are over 250 miles apart, creates a midpoint in between
		else:
			# Checks if distance from last point and its midpoint is greater than 250 as well
			# TODO: Replace with loop (what is midpoint is >750 miles away from point?)
			if (coordsDistance(prunedPath[goodPoint], \
					getMidpoint(prunedPath[goodPoint], pathPoints[i])) > 250):
				
				# Adds point between last point and midpoint
				# first one
				prunedPath.append(getMidpoint(prunedPath[goodPoint], \
					getMidpoint(prunedPath[goodPoint], pathPoints[i])))

				# Adds midpoint
				prunedPath.append(getMidpoint(prunedPath[goodPoint], pathPoints[i]))
				
				# Adds point between midpoint and next point
				# COOPER: Should this be i+1? It does the same thing as the first one?
				prunedPath.append(getMidpoint(getMidpoint(prunedPath[goodPoint], \
					pathPoints[i]), pathPoints[i]))

				goodPoint+=3
			else:
				prunedPath.append(getMidpoint(prunedPath[goodPoint], pathPoints[i]))
				prunedPath.append(pathPoints[i])
				goodPoint+=2
	# Adds terminal point
	prunedPath.append(pathPoints[-1])
	return prunedPath



# Makes a list of all regions along the path
def pathRegions(pathPoints):
	REGION_NUM = 1
	regionsList = []
	for i in xrange(0, len(pathPoints)-1):
		regionsList.append(makeRegion(pathPoints[i], pathPoints[i+1], REGION_NUM))
		REGION_NUM += 1
	return regionsList



# Makes a rectangular region between two points that has a minimum width and height
def makeRegion(point1, point2, REGION_NUM):
	latDif = abs((point1[0] - point2[0]))
	lngDif = abs((point1[1] - point2[1]))
	lowLat = min(point1[0], point2[0])
	lowLng = min(point1[1], point2[1])
	hiLat = max(point1[0], point2[0])
	hiLng = max(point1[1], point2[1])
	if (latDif < MIN_HEIGHT):
		lowLat -= MIN_HEIGHT
		hiLat += MIN_HEIGHT
	if (lngDif < MIN_WIDTH):
		lowLng -= MIN_WIDTH
		hiLat += MIN_WIDTH
	region = {"num": REGION_NUM, "origin": point1, "terminal": point2, "low":(lowLat, lowLng), "high":(hiLat, hiLng), "waypoints":[]}
	region = getRegionWaypoints(region)
	return region



# Gets waypoints within a region
# TODO: Check mp --> left of mp --> right of mp --> lefter of mp --> righter of mp...
def getRegionWaypoints(region):
	wpList = []
	midpointSearch(region["origin"],region["terminal"], 5000, wpList)
	for wp in wpList:
		gasList = yelpSearch.getGas(wp[0], wp[1], 5000, 1, 0)
		if len(gasList) > 0:
			break

	for wp in wpList:
		restaurantList = yelpSearch.getRestaurants(wp[0], wp[1], 5000, 1, 0)
		if len(restaurantList) > 0:
			break
	
	if len(gasList)==0:
		wpList = []
		midpointSearch(region["origin"],region["terminal"], 20000, wpList)
		for wp in wpList:
			gasList = yelpSearch.getGas(wp[0], wp[1], 20000, 1, 0)
			if len(gasList) > 0:
				break

	if len(restaurantList)==0:
		wpList = []
		midpointSearch(region["origin"],region["terminal"], 20000, wpList)
		for wp in wpList:
			restaurantList = yelpSearch.getRestaurants(wp[0], wp[1], 20000, 1, 0)
			if len(restaurantList) > 0:
				break

	region["waypoints"] = gasList + restaurantList
	return region
	



# Takes in a a list of names, coordinates and addresses. Returns a dictionary where
# the key is the coordinates, the first entry for each key is the name and the
# second entry is the address.
def makeCompleteList(nameList, coordsList, addressList):
	infoList = []
	for i in xrange(0, len(coordsList)):
		infoList.append([coordsList[i],nameList[i],addressList[i]])
	return infoList



# Sorts the waypoints of a region by which one is closest to the origin point of the region
def sortRegionWaypoints(region):
	waypointList = region['waypoints']
	temp1 = 0
	temp2 = 0
	region["waypoints"][0] = pathRouter.addressToCoords(region["waypoints"][0].location.address[0])
	region["waypoints"][1] = pathRouter.addressToCoords(region["waypoints"][1].location.address[0])
	if (coordsDistance(region['origin'], region['waypoints'][0]) > \
		coordsDistance(region['origin'], region['waypoints'][1])):
		temp1 = region['waypoints'][1]
		temp2 = region['waypoints'][0]
	else:
		temp1 = region['waypoints'][0]
		temp2 = region['waypoints'][1]
	waypointList[0] = temp1
	waypointList[1] = temp2
	region['waypoints'] = waypointList
	return region



# Concatonates all waypoints from the regions to make final waypoint list
def completeWaypointList(regionList):
	finalWaypointList = []
	for i in xrange(0, len(regionList)):
		try:
			finalWaypointList.append(regionList[i]['waypoints'][0])
			finalWaypointList.append(regionList[i]['waypoints'][1])
		except: pass
	return finalWaypointList



# Finds the midpoint between two points
def getMidpoint(pointA, pointB):
	loLat = min(pointA[0], pointB[0])
	hiLat = max(pointA[0], pointB[0])
	loLng = min(pointA[1], pointB[1])
	hiLng = max(pointA[1], pointB[1])
	dy = (hiLng - loLng)*.5
	dx = (hiLat - loLat)*.5
	return (loLat + dx, loLng + dy)



# Adds all midpoints to wpList until distance between is less than r
def midpointSearch(a, b, r, wpList):
	mp = getMidpoint(a, b)
	wpList.append(mp)
	if coordsDistance(a, mp) < r:
		return
	else:
		midpointSearch(a, mp, r, wpList)
		midpointSearch(mp, b, r, wpList)





if __name__ == "__main__":
	pass
