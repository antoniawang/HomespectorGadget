"""Homespector Gadget"""

from collections import OrderedDict
from datetime import datetime
import os
# import string

from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
import usaddress

from model import connect_to_db, db, User, Property, UserProperty
from utils import RGB_TUPLES, HEX_COLOR_STRINGS, make_marker_text, get_zoom_level

######################################################################################
app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

mapbox_api_key = os.environ["MAPBOX_KEY"]
foursq_clientid = os.environ["FOURSQ_CLIENTID"]
foursq_clientsecret = os.environ["FOURSQ_CLIENTSECRET"]


###################################
# General registration and login #
###################################

@app.route('/', methods=['GET','POST'])
def index():
    """Base.html"""

    return render_template("base.html")

@app.route('/homepage')
def homepage():
    """Homepage"""
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

        return render_template("registration-confirm.html", error_message = "New user %s added." % email)

    else:
        return render_template("error-dialog.html", error_message = "This email is already Registered.\n Please login or register with a different email.")


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

    # if user.password != password:
    if not user.check_password(password):
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id

    liked = UserProperty.query.filter_by(user_id=user.user_id).all()
    liked = [x.zpid for x in liked]

    session['properties'] = liked
    session['comp_table'] = []
    session['used_color_map']={}

    for zpid in liked:
        if str(zpid) not in session['used_color_map']:
            rgb_tuple = RGB_TUPLES.pop()
            print "Prepopulating color map with", rgb_tuple
            r,g,b = rgb_tuple
            hex_color_string = HEX_COLOR_STRINGS.pop()
            color_map = {'r': r, 'g': g, 'b': b, 'hex': hex_color_string}
            session['used_color_map'][str(zpid)] = color_map


    flash("Hello, %s!" % user.fname)

    print session["user_id"], "********************************"

    return render_template("session-login.html", session=session)


@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]

    if session['properties']:
        del session['properties']

    if session['comp_table']:
        del session['comp_table']

    flash("Logged Out.")
    return redirect("/")

##########################################################
# Searching, populating session, side column and table #
##########################################################

@app.route('/search', methods=['GET'])
def parse_address_search():
    """Parses the address for API call"""
    if request.args:
        raw_address_text = request.args.get("address-search")
        print "raw_address_text", raw_address_text, "$$$$$$$$$$$$$$$"
    raw_address_parsed = usaddress.tag(raw_address_text)
    print "raw_address_parsed", raw_address_parsed, "$$$$$$$$$$$$$$$"
    address_ordered_dict = raw_address_parsed[0]
    print "address_ordered_dict", address_ordered_dict, "$$$$$$$$$$$$$$$"
    
    address_keys = ['AddressNumber','StreetName','StreetNamePostType','OccupancyType','OccupancyIdentifier']
    address_string_list=[]
    for key in address_keys:
        if address_ordered_dict.get(key) is not None:
            address_string_list.append(address_ordered_dict[key])
    address_string = ' '.join(address_string_list)
    print "address_string", address_string, "$$$$$$$$$$$$$$$"
    address_url_encode = address_string.replace(' ','+').strip()
    print "address url encode is", address_url_encode, "$$$$$$$$$$$$$$$"
    
    citystatezip_string = address_ordered_dict.get('PlaceName','')
    citystatezip_string += '%2C ' + address_ordered_dict.get('StateName','')
    citystatezip_string += ' ' + address_ordered_dict.get('ZipCode','')
    citystatezip_url_encode = citystatezip_string.strip().replace(' ','+')

    address_for_walkscore = address_url_encode + "," + citystatezip_url_encode
    print address_for_walkscore


    property_from_url, error_code = Property.generate_from_address(address=address_url_encode,
                        citystatezip=citystatezip_url_encode) 

    #instantiate a session
    if 'properties' not in session.keys():
        session['properties'] = []

    if error_code == Property.ERROR_OK:    
        if property_from_url.zpid not in session['properties']:
            session['properties'].append(property_from_url.zpid)
        
        this_property = Property.query.filter(Property.zpid == property_from_url.zpid).first()

        if this_property is None:
            db.session.add(property_from_url)
            db.session.commit()
    
        this_property = property_from_url 

        return render_template("address-confirmation.html", house=this_property)

    elif error_code == Property.ERROR_MANY:
        return render_template("error-dialog.html", error_message = "Ambiguous Result. Please check your address and specify a unique property.")

    else:
        return render_template("error-dialog.html", error_message = "No property found. Please search again.")


@app.route("/delete-property", methods=['POST'])
def delete_property():
    """Delete the property from session
    if wrong address was returned."""

    zpid = request.form['Delete-Property']

    props_in_list = session['properties']
    index = props_in_list.index(zpid)
    if index >=0 :
        props_in_list.pop(index)

    return "Deleted"



@app.route("/property-list", methods=['GET'])
def get_propeties_list():
    """Have user confirm the search results.
    Upon confirmation, add property to session.
    Show list of properties stored in the session."""

    
    #Get the properties stored in session or create an empty session
    #Turn the list of properties into a set to get rid of repeats
    props_in_set = set(session.get('properties',[]))

    # Our output cart will be a dictionary (so we can easily see if we
    # already have the property in there
    properties = []
    used_color_map = session.get('used_color_map', {})

    # Loop over the ZPIDs in the session cart and add each one to
    # the output cart

    for zpid in props_in_set:
        house_data = Property.query.get(zpid)
        if house_data is not None:
            properties.append(house_data)
            if str(zpid) not in used_color_map:
                rgb_tuple = RGB_TUPLES.pop()
                print rgb_tuple
                r,g,b = rgb_tuple
                hex_color_string = HEX_COLOR_STRINGS.pop()
                color_map = {'r': r, 'g': g, 'b': b, 'hex': hex_color_string}
                used_color_map[str(zpid)] = color_map


    session['used_color_map'] = used_color_map
    user_id = session.get('user_id')
    liked = None

    if user_id:
        results = db.session.query(UserProperty.zpid).filter_by(user_id=user_id).all()
        liked = [zpid for (zpid, ) in results]

    print session.get('comp_table',[]),"$$$$$$$$$$$$$$$"
    props_in_table = [int(x) for x in session.get('comp_table',[])]

    return render_template("left-column.html", properties=properties, liked=liked, props_in_table=props_in_table, used_color_map=used_color_map)


@app.route("/add-favorites", methods=['POST'])
def add_to_favorites():
    """Add a property to user's favorites list
    Done with Ajax to add an record in the UserProperty table
    linking the user_id to the zpid"""

    user_id = session.get('user_id')

    if user_id:
        zpid = request.form.get('property') 

        liked = UserProperty.query.filter_by(user_id=user_id, zpid=zpid).first()
    else:
        raise Exception("No user logged in.")

    if liked:
        db.session.delete(liked)

    else:
        new_like = UserProperty(user_id=user_id,
                                 zpid=zpid,
                                 time_saved=datetime.utcnow())
        db.session.add(new_like)

    db.session.commit()

    return "Victory"


@app.route("/delete-from-session", methods=['POST'])
def delete_from_session():
    """Delete a property from the session.
    Also deletes a property from comparison table
    when it's deleted from session.
    Done with Ajax to take out the property from the table"""

    global RGB_TUPLES 
    global HEX_COLOR_STRINGS

    #delete from session
    props_in_list = session.get('properties',[])
    used_color_map = session.get('used_color_map',{})

    zpid = request.form.get('property') 
    print "zpid is: ", zpid, "and type: ", type(zpid), "$$$$$$$$$$"

    if zpid in props_in_list:
        zpid_index = props_in_list.index(zpid)
        props_in_list.pop(zpid_index)
        if str(zpid) in used_color_map:
            color_map = used_color_map[str(zpid)]
            rgb_tuple = (color_map['r'], color_map['g'], color_map['b'])
            hex_color_string = color_map['hex']
            RGB_TUPLES.append(rgb_tuple)
            HEX_COLOR_STRINGS.append(hex_color_string)
            del used_color_map[str(zpid)]
            print "deleted from colormap", zpid, used_color_map

    zpids_in_table = session.get('comp_table',[])
    if zpid in zpids_in_table:
        zpid_index2 = zpids_in_table.index(zpid)
        zpids_in_table.pop(zpid_index2) 



    return "Victory"


@app.route("/comparison-table", methods=['GET', 'POST'])
def generate_comparison_table():
    """Populate and change comparison table."""
    zpids_in_table = set(session.get('comp_table',[]))

    props_in_table = []

    for zpid in zpids_in_table:
        house = Property.query.get(zpid)
        props_in_table.append(house)

    return render_template("comparison-table.html", props_in_table=props_in_table)  

@app.route('/clear-comparison-table', methods=['GET', 'POST'])
def clear_comp_table():
    if 'comp_table' in session:
        del session['comp_table']
        return "Cleared, please go back to previous page"
    return "Not cleared, but go back anyway"

@app.route("/update-comparison-table", methods=['GET','POST'])
def update_comp_table():
    """Adds or remove a property in comparison table"""
    zpid = request.form.get('zpid')
    is_in_table = request.form.get('is_in_table')

    zpids_in_table = set(session.get('comp_table',[]))
    result = 1

    if is_in_table == "true":
        if zpid in zpids_in_table:
            zpids_in_table.remove(zpid)
    else:
        if zpid not in zpids_in_table:
            if len(zpids_in_table) < 4:
                zpids_in_table.add(zpid)
                
            else:
                flash("Too many!")
                result = 0
    zpids_in_table = list(zpids_in_table)
    session['comp_table'] = zpids_in_table
    return str(result)

#########
# Maps #
#########

def get_session_lonlats():
    """Helper function that creates a list of lon, lat tuples
    for all the properties in the session."""

    lonlat_list = []

    props_in_list = session.get('properties',[])
    print "session['properties'] is ", props_in_list
    for zpid in props_in_list:
        this_house = Property.query.filter(Property.zpid == int(zpid)).first()
        longitude = this_house.longitude
        latitude = this_house.latitude

        lonlat_list.append((zpid, longitude,latitude))

    return lonlat_list


# DEFAULT MAP
#  generate marker text for an API call of the form:   {name}-{label}+{color}({lon},{lat})
#  example : pin-l-park+482(-73.975,40.767)
#   NAME MUST BE pin-l, pin-m or pin-s
#   Text string for API call in util.py

@app.route("/default-map", methods=['GET'])
def show_default_map():
    """Get the longitude and latitudes from the get_session_lonlats.
    Generate marker text from make_marker_text for each house.
    Show the properties stored in session on a map
    then allow to zoom in on properties to show pindrops
    or heat maps"""

    lonlat_tuples = get_session_lonlats()

    marker_string_list = make_marker_text(lonlat_tuples)

    marker_api_string = ",".join(marker_string_list)

    imgwidth = 1024
    imgheight = 650

    #calculate map centers
    lon_center = sum([float(lon) for zpid, lon, lat in lonlat_tuples])/len(lonlat_tuples)
    lat_center = sum([float(lat) for zpid, lon, lat in lonlat_tuples])/len(lonlat_tuples)

    #calculate bounds with max and mins
    lon_max =  max([float(lon) for zpid, lon, lat in lonlat_tuples])
    lon_min =  min([float(lon) for zpid, lon, lat in lonlat_tuples])
    lat_max =  max([float(lat) for zpid, lon, lat in lonlat_tuples])
    lat_min =  min([float(lat) for zpid, lon, lat in lonlat_tuples])

    zoom_level = get_zoom_level(lat_max, lat_min, lon_max, lon_min, imgheight, imgwidth) if len(lonlat_tuples) > 1 else 21

    lon_lat_zoom = str(lon_center) + ',' + str(lat_center) + ',' + str(zoom_level)

    imgsize = str(imgwidth) + 'x' + str(imgheight)

    # mapbox_api_key = 'pk.eyJ1IjoiYW50b25pYXdhbmciLCJhIjoiNTc1OGJmMDZlNjQ4ZjlhMmRkZTU4ZGMwOTMxZDg2ODAifQ.nVRLoueu9vmdpYYDc_-zgg'

    new_src = 'https://api.mapbox.com/v4/mapbox.streets/' + marker_api_string + '/' + lon_lat_zoom + '/' + imgsize + '.png?access_token=' + mapbox_api_key

    return render_template("map.html", imgwidth=imgwidth, imgheight=imgheight, src=new_src)


@app.route("/detailed-map", methods=['POST'])
def generate_detailed_map():
    print "Detailed map app route is running."
    zpid = request.form.get('property')
    query = request.form.get('query')
    
    map_color_dict = session.get('used_color_map',{})
    color = map_color_dict[zpid]['hex']


    this_property = Property.query.filter(Property.zpid == zpid).first()

    return render_template("detailed-map.html", house=this_property, color=color, query=query, placeholder_text=query if query is not None else "Search for places, e.g. coffee", MapboxKey=mapbox_api_key, FourSqID=foursq_clientid, FourSqSecret=foursq_clientsecret)


################################
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()

else:
    connect_to_db(app)