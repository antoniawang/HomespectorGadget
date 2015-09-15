# Homespector Gadget

Homespector Gadget is a full stack web application that allows users to visualize the specs of and map the neighborhood for multiple properties in a clear and concise manner. The same details (e.g. number of bedrooms, lot size) about different properties are displayed side-by-side in a comparison table, similar to the feature found on many retail websites. Users can compare up to four different properties at a time and save properties to a favorites list. 
A map view automatically maps all the properties stored in the user's session. Users can zoom in on a detailed map view around an individual property's neighborhood and do a text search for their preferred points of interest.

###Features
####Current
* Find a specific property and retrieve the specs by searching its addresss (Zillow API)
* The Walk Score is also retrieved from the search (Walk Score API)
* Default map view places all the properties in the session and calculates the center and optimal zoom levels (Leaflet/Mapbox API)
* Detailed map view zooms in on selected property and locates nearby points-of-interest that users searched (Leaflet/Mapbox API, Foursquare API)
* Users can register, login and save properties to a favorites list
* User's saved properties are automatically loaded into the session upon login.

####Future
* Twilio integration allows users to text a property's address and receive a link to the proeprty's Zillow listing page

### Version
1.0

### Technologies Used

* Python/Flask
* SQLAlchemy
* SQLite3
* jQuery/AJAX
* Zillow API
* Leaflet/Mapbox API
* Foursquare API
* Walk Score API
* HTML5/CSS
* Bootstrap
* Jinja2

### Structure
* server.py - implements the backend Python server using the Flask frameworks
* model.py - implements an interface from Python to SQL using SQLAlchemy
* utils.py - contains the helper functions
* static/property.js - handles the jQuery and AJAX calls to manipulate front end elements


