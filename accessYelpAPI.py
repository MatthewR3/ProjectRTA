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
