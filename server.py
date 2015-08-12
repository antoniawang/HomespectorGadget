"""Prop Shop"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Property, UserProperty

import model

from datetime import datetime

import usaddress

from collections import OrderedDict

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template('registration-form.html')


@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    user_email = request.form['email']
    user = User.query.filter(User.email == user_email).first()
    print user, "**********************************************"

    if user is None:
        # Get form variables
        fname = request.form["fname"]
        lname = request.form["lname"]
        email = request.form["email"]
        password = request.form["password"]
        zipcode = request.form["zipcode"]

        new_user = User(fname=fname, lname=lname, email=email, password=password, zipcode=zipcode)

        db.session.add(new_user)
        db.session.commit()

        flash("User %s added." % email)
        return redirect("/")

    else:
        flash("This email has already been registered.\nPlease use a different email.") 
        return redirect("/register")


@app.route('/login', methods=['GET'])
def login_form():
    """Show login form."""

    return render_template("login-form.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user. Please register an account.")
        return redirect("/register")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("Hello, %s!" % user.fname)
    return redirect("/") #Change redirect path later


@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]

    if session['properties']:
        del session['properties']

    flash("Logged Out.")
    return redirect("/")


######################################################
@app.route('/search', methods=['GET'])
def parse_address_search():
    """Parses the address for API call"""
    if request.args:
        raw_address_text = request.args.get("address_search")
    raw_address_parsed = usaddress.tag(raw_address_text)
    address_ordered_dict = raw_address_parsed[0]
    
    address_keys = ['AddressNumber','StreetName','StreetNamePostType','OccupancyType','OccupancyIdentifier']
    address_string_list=[]
    for key in address_keys:
        if address_ordered_dict.get(key) is not None:
            address_string_list.append(address_ordered_dict[key])
    address_string = ' '.join(address_string_list)
    address_url_encode = address_string.replace(' ','+').strip()

    
    citystatezip_string = address_ordered_dict.get('PlaceName','')
    citystatezip_string += '%2C ' + address_ordered_dict.get('StateName','')
    citystatezip_string += ' ' + address_ordered_dict.get('ZipCode','')
    citystatezip_url_encode = citystatezip_string.strip().replace(' ','+')

    property_from_url = Property.generate_from_address(address=address_url_encode,
                        citystatezip=citystatezip_url_encode)  

    #instantiate a session
    if 'properties' not in session.keys():
        session['properties'] = []

    if property_from_url.zpid not in session['properties']:
        session['properties'].append(property_from_url.zpid)
    
    this_property = Property.query.filter(Property.zpid == property_from_url.zpid).first()

    if this_property is None:
        db.session.add(property_from_url)
        db.session.commit()
    else:
        this_property = property_from_url 
                       
    print session['properties'], "********HITHERE*********************"
    return render_template("address-confirmation.html", this_property=this_property, raw_address_text=str(property_from_url))

# USE THIS TO CREATE THE MY PROFILE PAGE
# @app.route("/users/<int:user_id>")
# def user_detail(user_id):
#     """Show info about user."""

#     user = User.query.get(user_id)
#     return render_template("user.html", user=user)

@app.route("/delete-property", methods=['POST'])
def delete_property():
    """Delete the property from session and SQL
    if wrong address was returned."""

    zpid = request.form['Delete-Property']
    props_in_list = session['properties']
    props_in_list.pop()

    wrong_house = Property.query.filter_by(zpid=zpid).first()
    db.session.delete(wrong_house)

    db.session.commit()

    print props_in_list, "********HELLOWORLD**********"
    flash("Please search again")

    return redirect ("/")



@app.route("/property-table", methods=['GET'])
def get_propeties_list():
    """Have user confirm the search results.
    Upon confirmation, add property to session.
    Show list of properties stored in the session.

    If a user is logged in, let them save a property to favorites."""

    
    #Get the properties stored in session or create an empty session
    #Turn the list of properties into a set to get rid of repeats
    props_in_set = set(session.get('properties',[]))

    # Our output cart will be a dictionary (so we can easily see if we
    # already have the property in there
    properties = []

    # Loop over the ZPIDs in the session cart and add each one to
    # the output cart

    for zpid in props_in_set:
        house_data = Property.query.get(zpid)
        if house_data is not None:
            properties.append(house_data)
        # else:
        #     pass # what can you do if it's not found?

    user_id = session.get('user_id')

    if user_id:
        liked = UserProperty.query.filter_by(user_id=user_id, zpid=zpid).first()
    
    else:
        liked = None

    return render_template("property-table.html", properties=properties, liked=liked)


@app.route("/property-table", methods=['POST']) #TO DO: FIX
def add_to_favorites():
    """Add a property to user's favorites list"""

    # Get form variable
    like = request.form['Like']

    user_id = session.get('user_id')

    if not user_id:
        raise Exception("No user logged in.")

    liked = UserProperty.query.filter_by(user_id=user_id, zpid=zpid).first()

    if liked:
        flash("You already saved this property.")

    else:
        flash("Property added to favorites.")
        db.session.add(like)

    db.session.commit()

    return render_template('property-table.html', properties=properties, liked=liked)




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()