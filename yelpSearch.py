# read API keys
# Use this at the beginning of each program that needs
# to access Yelp's data
# In order for this to work, you need to install yelp-python
# by using the command "sudo pip install yelp" if you're using linux

from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

auth = Oauth1Authenticator(
	consumer_key = "HskFxqEANFZQb6gNpLLTlA",
	consumer_secret = "fQOhbdwOoyLdryogrMzj3isRxxg",
	token = "KpVrnYMEdNnI9jvHD9cK00Tpt0uLBiPX",
	token_secret = "aAZhnQo_a-EowzF8UTFPokTQ5TM"
)

client = Client(auth)


# Searches for food in a 5km radius around the coordinates supplied by the app
# and sorts the results by highest rating. Takes in a coordinate as a 2-tuple.

# Can possibly implement a system where the app user selects the types of food they are
# interested in and bring that in as a list of strings to help with searching.
# Preferences can be fast food, Italian, Mexican etc.

# Creates a dictionary of search parameters
def getSearchParams(term, radius, limit, sort): #list of food preferences and other parameters
	params = {}
	params["term"] = term 				# search term
	params["radius filter"] = radius	# radius of search
	params["limit"] = limit				# limit of search results
	params["sort"] = sort				# sort type: 0 - Best Matched, 1 - Distance, 2 - Highest Rated

	return params

# x and y are coords of center of search radius
def getResults(lat, lng, params):
	return client.search_by_coordinates(lat, lng, **params)



# General Yelp Search API Docs:
# https://www.yelp.com/developers/documentation/v2/search_api

# Yelp API Category Lists:
# https://www.yelp.com/developers/documentation/v2/all_category_list

# Gets list of restaurants using Yelp API
def getRestaurants(lat, lng, radius, limit, sort):
	# List of restaurants
	restList = getResults(lat, lng, getSearchParams("restaurants", radius, limit, sort)).businesses
	#for x in restList:
	#	print x.name
	return restList

# Gets list of gas stations using Yelp API
def getGas(lat, lng, radius, limit, sort):
	knownStations = {"7-11", "Mobil", "Speedway", "Shell", "BP"}
	# Will return gas and service shops (not common gas stations)
	stationList = getResults(lat, lng, getSearchParams("gas", radius, limit, sort)).businesses
	# for x in knownStations:
	# 	stationList += getResults(lat, lng, getSearchParams("gas", radius, limit, sort)).businesses
	#for x in stationList:
	#	print x.name
	return stationList

# Gets list of custom search results using Yelp API
def getOther(lat, lng, term, radius, limit, sort):
	resultList = getResults(lat, lng, getSearchParams(term, radius, limit, sort)).businesses
	return resultList

# Gets list of addresses from a search
def getAddresses(lat, lng, radius, limit, sort):
	addressList = getResults(lat, lng, \
		getSearchParams("restaurants", radius, limit, sort).location.display_address)
	return addressList

# Gets list of coordinates from a search
def getCoordinates(lat, lng, radius, limit, sort):
	coordsList = getResults(lat, lng, \
		getSearchParams("restaurants", radius, limit, sort).location.coordinate)
	return coordsList



if __name__ == "__main__":
	# Using coordinates of Chicago
	coords = (41.8781, -87.6298)
	print "Testing getRestaurants:"
	for x in getRestaurants(coords[0], coords[1] ,5000,10,2):
		print "Name: " + x.name + ", rating: " + str(x.rating)
	print "Testing getGas:"
	for x in getGas(coords[0], coords[1] ,5000,10,2):
		print "Name: " + x.name + ", rating: " + str(x.rating)
		
