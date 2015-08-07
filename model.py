"""Models and database functions for PropShop project."""

import sys
import os
from flask_sqlalchemy import SQLAlchemy
#from pyzillow import pyzillow
import xmltodict
import json
import requests
from urllib2 import Request, urlopen, URLError
from xml.dom import minidom


# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of the PropShop website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    fname = db.Column(db.String(20), nullable=True)
    lname = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)




class Property(db.Model):
    """Property on PropShop website."""

    __tablename__ = "properties"

    #Main property information
    zpid = db.Column(db.Integer, primary_key=True)
    homedetails = db.Column(db.String(200)) #URL to Zillow listing 
    market_status = db.Column(db.Boolean) #Scarped or user inputed data read from the listing URL
    listprice = db.Column(db.Integer) #Scarped or user inputed read from the listing URL
    street = db.Column(db.String(100))
    zipcode = db.Column(db.String(5))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))

    #Additional property details
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    FIPScounty = db.Column(db.String(5))
    useCode = db.Column(db.String(10))
    taxAssessmentYear = db.Column(db.Integer)
    taxAssessment = db.Column(db.Float)
    yearBuilt = db.Column(db.Integer)
    lotSizeSqFt = db.Column(db.Integer)
    finishedSqFt = db.Column(db.Integer)
    bathrooms = db.Column(db.Float)
    bedrooms = db.Column(db.Integer)
    totalRooms = db.Column(db.Integer)
    lastSoldDate = db.Column(db.DateTime)
    lastSoldPrice = db.Column(db.Integer)
    z_amount = db.Column(db.Integer)
    z_last_updated = db.Column(db.DateTime)
    z_oneWeekChange_deprecated = db.Column(db.Boolean)
    z_valueChange = db.Column(db.Integer)
    z_valuationRange_low = db.Column(db.Integer)
    z_valuationRante_high = db.Column(db.Integer)
    z_percentile = db.Column(db.Integer)
    region_name  = db.Column(db.String(59))
    region_id = db.Column(db.String(5)) 
    region_type = db.Column(db.String(10))
    zindexValue = db.Column(db.Integer) # not sure what this is but we'll leave it in for now
    neighborhood_url = db.Column(db.String(100)) 


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<ZPID = %s: Address=%s \n %s, %s %s>" % (self.zpid, self.street, self.city, self.state, self.zipcode)

# Need create a similar class for neighborhoods
#class Neighborhood(db.Model):
    


class UserProperty(db.Model):
    """User's saved properties."""

    __tablename__ = "usersproperties"

    user_property_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    zpid = db.Column(db.Integer, db.ForeignKey('property.zpid'))
    time_saved = db.Column(db.DateTime)


    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("usersproperties", order_by=user_property_id))

    # Define relationship to property
    prop = db.relationship("Property",
                            backref=db.backref("usersproperties", order_by=user_property_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User's Property user_property_id=%s user_id=%s zpid=%s>" % (
            self.user_property_id, self.user_id, self.zpid)




##############################################################################
# Helper functions for parsing (from Denise's SunBear Github)

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


def handleTok(tokenlist):
    texts = ""
    for token in tokenlist:
        texts += " "+ getText(token.childNodes)
    return texts

###############################################################
###############################################################

###############################################################

# ZILLOW

### DETAILS PER HOUSE ###
# http://www.zillow.com/howto/api/GetDeepSearchResults.htm
# input:  address and zip
# output: lattitude and longitude (could then be inputed into PV WATTS)
#           valutation range (high and low)
#           home value index -- avg home value in neighborhood?
#           ZPID = a zillow id (per house). used for the other zillow APIs.
#           Tax assessment,Yearbuilt,lotSizeSqFt,finishedSqFt,Bedrooms
#  *** FIPScounty *** = matches county codes in maps, census data, etc



def data_per_house():
    #Zillow_key = os.environ["ZILLOW_ZWSID"]


    # get Deep Search Results data and parse
    url_zillow_house = "http://www.zillow.com/webservice/GetDeepSearchResults.htm?<KEY>&address=<ADDRESS>"
    response = urlopen(url_zillow_house)
    dom_zillow_house = minidom.parse(response)


    # retrieve example data by tag
    for node in dom_zillow_house.getElementsByTagName("result"):

        zpid = (handleTok(node.getElementsByTagName('zpid'))).encode("utf8").strip()
        homedetails = (handleTok(node.getElementsByTagName('homedetails'))).encode("utf8").strip()
        street = (handleTok(node.getElementsByTagName('street'))).encode("utf8").strip()
        zipcode = (handleTok(node.getElementsByTagName('zipcode'))).encode("utf8").strip()
        city = (handleTok(node.getElementsByTagName('city'))).encode("utf8").strip()
        state = (handleTok(node.getElementsByTagName('state'))).encode("utf8").strip()
        
        latitude = (handleTok(node.getElementsByTagName('latitude'))).encode("utf8").strip()
        longitude = (handleTok(node.getElementsByTagName('longitude'))).encode("utf8").strip()
        FIPScounty = (handleTok(node.getElementsByTagName('FIPScounty'))).encode("utf8").strip()
        useCode = (handleTok(node.getElementsByTagName('useCode'))).encode("utf8").strip()
        
        taxAssessmentYear = (handleTok(node.getElementsByTagName('taxAssessmentYear'))).encode("utf8").strip()
        taxAssessment = (handleTok(node.getElementsByTagName('taxAssessment'))).encode("utf8").strip()
        yearBuilt = (handleTok(node.getElementsByTagName('yearBuilt'))).encode("utf8").strip()
        lotSizeSqFt = (handleTok(node.getElementsByTagName('lotSizeSqFt'))).encode("utf8").strip()
        finishedSqFt = (handleTok(node.getElementsByTagName('finishedSqFt'))).encode("utf8").strip()
        bedrooms = (handleTok(node.getElementsByTagName('bedrooms'))).encode("utf8").strip()
        bathrooms = (handleTok(node.getElementsByTagName('bathrooms'))).encode("utf8").strip()
        totalRooms = (handleTok(node.getElementsByTagName('totalRooms'))).encode("utf8").strip()
        
        lastSoldDate = (handleTok(node.getElementsByTagName('lastSoldDate'))).encode("utf8").strip()
        lastSoldPrice = (handleTok(node.getElementsByTagName('lastSoldPrice'))).encode("utf8").strip()
        z_amount = (handleTok(node.getElementsByTagName('amount'))).encode("utf8").strip()



    print "zpid:", zpid
    print "homedetails:", homedetails
    print "street:", street
    print "city:", city
    print "state:", state
    print "zipcode:", zipcode

    print "latitude:", latitude
    print "longitude:", longitude
    print "FIPScounty:", FIPScounty
    print "useCode:", useCode
    
    print "taxAssessmentYear:", taxAssessmentYear
    print "taxAssessment:", taxAssessment
    print "year built:", yearBuilt
    print "lotSizeSqFt:", lotSizeSqFt
    print "Square feet:", finishedSqFt
    print "number of bedrooms:", bedrooms
    print "number of bathrooms:", bathrooms
    print "number of total rooms:", totalRooms

    print "Last Sold Date:", lastSoldDate
    print "lastSoldPrice:", lastSoldPrice
    print "zestimate amount:", z_amount

    #MAYBE TO DO: Get the Additional Updated Property Details


#data_per_house()









def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ratings.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
    # result = request_and_convert_property("test")
    # print ''
    # print ''
    # print "I got %s results for this" % len(result['results'])
    # print json.dumps(result, indent=4)
    # for result in result['results']['result']:
    #     print result