"""Models and database functions for PropShop project."""

from datetime import datetime
import json
import os
import requests
import sqlite3
import sys
import urllib
from urllib2 import Request, urlopen, URLError
from xml.dom import minidom


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from sqlalchemy.ext.declarative import declarative_base as real_declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
import xmltodict

from utils import handleTok 

# Let's make this a class decorator
declarative_base = lambda cls: real_declarative_base(cls=cls)


# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()

def getAttributes(clazz):
    return {name: attr for name, attr in clazz.__dict__.items()
        if not name.startswith("__") 
        and not callable(attr)
        and not type(attr) is staticmethod}

##############################################################################
# Model definitions

class User(db.Model):
    """User of the Homespector Gadget website."""

    def __init__(self, email=None, password=None, fname=None, lname=None, zipcode=None):
        self.email = email
        self.set_password(password)

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    fname = db.Column(db.String(20), nullable=True)
    lname = db.Column(db.String(20), nullable=True)
    zipcode = db.Column(db.String(5), nullable=True)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)


class Property(db.Model):
    """Property on Homespector Gadget website.
    A wrapper object that corresponds to rows in the properties table.
    """

    ERROR_OK = 0
    ERROR_NO_RESULTS = 1
    ERROR_MANY = 2

    def __init__(self,
                 zpid=None,
                 homedetails=None,
                 street=None, city=None, state=None, zipcode=None,
                 bedrooms=None, bathrooms=None, z_amount=None,
                 latitude=None, longitude=None, FIPScounty=None,
                 useCode=None, taxAssessmentYear=None, taxAssessment=None,
                 yearBuilt=None, lotSizeSqFt=None, finishedSqFt=None,
                 totalRooms=None, lastSoldDate=None, lastSoldPrice=None,
                 walkscore=None):
        self.zpid = zpid
        self.homedetails = homedetails
        self.street = street
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms
        self.z_amount = z_amount
        self.latitude = latitude
        self.longitude = longitude
        self.FIPScounty = FIPScounty
        self.useCode = useCode
        self.taxAssessmentYear = taxAssessmentYear
        self.taxAssessment = taxAssessment
        self.yearBuilt = yearBuilt
        self.lotSizeSqFt = lotSizeSqFt
        self.finishedSqFt = finishedSqFt
        self.totalRooms = totalRooms
        self.lastSoldDate = lastSoldDate
        self.lastSoldPrice = lastSoldPrice
        self.walkscore = walkscore
        self.rgb_tuple = None
        self.hex_color_string = None

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
    lastSoldDate = db.Column(db.String(10))
    lastSoldPrice = db.Column(db.Integer)
    z_amount = db.Column(db.Integer)

    #Walk and Transit Scores
    walkscore = db.Column(db.Integer)
    transitscore = db.Column(db.Integer)


    @staticmethod 
    def generate_from_address(address, citystatezip):
        """ create new property object from url """
    
        Zillow_key = os.environ["ZILLOW_ZWSID"]
        ################################################
        #Fix after creating a parsed searched text
        ################################################
        # get Deep Search Results data and parse
        url_zillow_house = "http://www.zillow.com/webservice/GetDeepSearchResults.htm?zws-id=%s&address=%s&citystatezip=%s" % (Zillow_key, address, citystatezip) 
        response = urlopen(url_zillow_house)
        dom_zillow_house = minidom.parse(response)

        # retrieve example data by tag
        results = dom_zillow_house.getElementsByTagName("result")
        print "results are", results, "with length", len(results), "$$$$$$$$$$$$$$$$"

        if len(results) > 1:
            return None, Property.ERROR_MANY

        if len(results) == 0:
            return None, Property.ERROR_NO_RESULTS

        for node in results:

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

        new_property = Property(zpid=zpid,
                        homedetails=homedetails,
                        street=street,
                        city=city,
                        state=state,
                        zipcode=zipcode,
                        latitude=latitude,
                        longitude=longitude,
                        FIPScounty=FIPScounty,
                        useCode=useCode,
                        taxAssessmentYear=taxAssessmentYear,
                        taxAssessment=taxAssessment,
                        yearBuilt=yearBuilt,
                        lotSizeSqFt=lotSizeSqFt,
                        finishedSqFt=finishedSqFt,
                        bedrooms=bedrooms,
                        bathrooms=bathrooms,
                        totalRooms=totalRooms,
                        lastSoldDate=lastSoldDate,
                        lastSoldPrice=lastSoldPrice,
                        z_amount=z_amount
                        )
        new_property.get_walkscore()
        return new_property, Property.ERROR_OK

    
    def get_walkscore(self):
        """gets the WalkScore and Transit Scores from url"""

        self.walkscore = None
        
        Walkscore_key = os.environ["WALKSCORE_KEY"]
        address = urllib.quote(self.street + " " + self.city + " " + self.state + " " + self.zipcode)
        json_walkscore = "http://api.walkscore.com/score?format=json&address=%s&lat=%s&lon=%s&wsapikey=%s" % (address, self.latitude, self.longitude, Walkscore_key)
        print "json_walkscore is", json_walkscore

        response = urlopen(json_walkscore).read()

        results_dict = json.loads(response)

        if results_dict['status'] == 1:
            self.walkscore=results_dict['walkscore']

        return self.walkscore

    # MAY NOT NEED THIS
    @classmethod
    def get_by_id(cls, zpid):
        """Query for a specific property in the database by the primary key"""

        cursor = get_db_cursor()
        QUERY = """
                  SELECT zpid,
                         street,
                         city,
                         state,
                         zipcode,
                         bedrooms,
                         bathrooms,
                         z_amount
                   FROM Properties
                   WHERE zpid = ?;
               """

        cursor.execute(QUERY, (zpid,))

        row = cursor.fetchone()

        if not row:
            return None

        house = Property(*row)

        return house


        #MAYBE TO DO: Get the Additional Updated Property Details

    # def to_dict(self):
    #     return getAttributes(Property)
    
    def serialize(self):
        """Return object data in easily serializeable format"""
        obj_dict = {c: getattr(self, c) for c in inspect(self).attrs.keys()}
        print obj_dict
        return obj_dict

    @staticmethod
    def serialize_list(houses):
        return [house.serialize() for house in houses]

    @property
    def columns(self):
        return [ c.name for c in self.__table__.columns ]

    @property
    def columnitems(self):
        return dict([ (c, getattr(self, c)) for c in self.columns ])

    def __repr__(self):
        """Provide helpful representation when printed."""

        return '{}({})'.format(self.__class__.__name__, self.columnitems)

    def __str__(self):
        """Provide helpful representation when printed."""

        return '{}({})'.format(self.__class__.__name__, self.columnitems)

    def tojson(self):
        return self.columnitems


class UserProperty(db.Model):
    """User's saved properties."""

    __tablename__ = "usersproperties"

    user_property_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    zpid = db.Column(db.Integer, db.ForeignKey('properties.zpid'))
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


###############################################################

def get_db_cursor():
    """Return a database cursor"""
    mypath = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(os.path.join(mypath, "propshop.db"))
    cursor = conn.cursor()
    return cursor

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    dbpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'propshop.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+dbpath
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # bug fix for SQLAlchemy misbehaving on Apache servers
    db.app = app 
    db.init_app(app)
    # ensure that the databases are created for each context
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."


    #my_property = Property().load_from_address(address=, citystatezip=)