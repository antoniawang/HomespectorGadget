# Homespector Gadget

Homespector Gadget is a full stack web application that allows users to visualize the specs of and map the neighborhood for multiple properties in a clear and concise manner. The same details (e.g. number of bedrooms, lot size) about different properties are displayed side-by-side in a comparison table, similar to the feature found on many retail websites. Users can compare up to four different properties at a time and save properties to a favorites list. 
A map view automatically maps all the properties stored in the user's session. Users can zoom in on a detailed map view around an individual property's neighborhood and do a text search for their preferred points of interest.

### Version
1.0

### Technologies Used

* Python/Flask
* SQLAlchemy
* jQuery/AJAX
* Zillow API
* Leaflet/Mapbox API
* Foursquare API
* Walk Score API
* HTML/CSS
* Bootstrap

### Structure
* server.py - implements the backend Python server using the Flask frameworks.
* model.py - implements an interface from Python to SQL using SQLAlchemy.
* static/property.js - handles the jQuery and AJAX calls to manipulate front end elements.


