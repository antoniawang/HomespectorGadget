import json
import requests



sutter = requests.get("http://www.zillow.com/webservice/GetDeepSearchResults.htm?zws-id=X1-ZWz1a5p2n39v63_anh8k&address=952+Sutter+St&citystatezip=San+Francisco%2C+CA")

print sutter

charleston_meadows = requests.get("http://www.zillow.com/webservice/GetDemographics.htm?zws-id=X1-ZWz1a5p2n39v63_anh8k&state=CA&city=Palo+Alto&neighborhood=Charleston+Meadows")

print charleston_meadows