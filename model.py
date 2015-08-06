"""Models and database functions for PropShop project."""

from flask_sqlalchemy import SQLAlchemy


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



import urllib2
import xml.etree.ElementTree as ET

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
    totalrooms = db.Column(db.Integer)
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


    @classmethod
    def parse_xlm(cls, url_path):
        #url_path = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm?zws-id=X1-ZWz1a5p2n39v63_anh8k&address=4113+Park+Blvd&citystatezip=Palo+Alto%2C+CA%22'
        raw_xml = urllib2.urlopen(url_path).read().strip()
        root = ET.fromstring(raw_xml)

        #parse xml elements
        zpid = root.find('zpid').text
        homedetails = root.find('zpid').text
        street = root.find('street').text
        zipcode = root.find('zipcode').text
        city = root.find('city').text
        state = root.find('state').text



    
 


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
    zpid = db.Column(db.Integer, db.ForeignKey('movies.movie_id'))
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
# Helper functions

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