##############################################################################
# Helper functions 
##############################################################################
import math
import random
import struct

from flask import session

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


##MAKE LIST OF POSSIBLE MARKER COLORS##
def make_marker_colors():

    rbg_range = range(50, 251, 50)
    marker_rgb_list = [(r, g, b) for r in rbg_range for b in rbg_range for g in rbg_range]

    random.shuffle(marker_rgb_list)

    marker_hex_list = []

    for rgb_tuple in marker_rgb_list:
        hex_color_string = struct.pack('BBB', *rgb_tuple).encode('hex')
        marker_hex_list.append(hex_color_string)

    return marker_rgb_list, marker_hex_list    

RGB_TUPLES, HEX_COLOR_STRINGS = make_marker_colors()


#Make the string for the default map API call
def make_marker_text(lonlat_tuples_list):
    """Parse and join the strings that go in the mapbox api call"""
    used_color_map = session.get('used_color_map', {})
    marker_text_list = []
    # color = '84638F'
    name = 'pin-m'
    
    for index, lonlat_tuple in enumerate(lonlat_tuples_list):
        label = "building"
        zpid, lon, lat = lonlat_tuple
    
        color = used_color_map[str(zpid)]['hex']
        marker_text = name + '-' + label + '+' + color + '(' + str(lon) + ',' + str(lat) + ')'
        marker_text_list.append(marker_text)

    return marker_text_list


#Determine optimal zoom level
def get_zoom_level(lat_max, lat_min, lon_max, lon_min, imgheight, imgwidth):
    """Figure out the optimal zoom level,
    given the NE, SW bounds(max(lat, lon); min(lat, lon)) 
    from the list of lon, lat tuples."""

    world_dim = { 'height': 256, 'width': 256 } #always 256 px
    zoom_max = 21 #max zoom for Mapbox


    def lat_radius(lat):
        sin = math.sin(lat * math.pi / 180);
        rad_x2 = math.log((1 + sin) / (1 - sin)) / 2
        return max(min(rad_x2, math.pi), -math.pi) / 2

    def zoom(map_px, world_px, fraction):
        return math.floor(math.log(map_px / world_px / fraction) / math.log(2))

    # northeast = (lat_max, lon_max)
    # southwest = (lat_min, lon_min)

    lat_fraction = (lat_radius(lat_max) - lat_radius(lat_min)) / math.pi
    
    lon_diff = lon_max - lon_min
    if (lon_diff < 0):
        lon_fraction = (lon_diff + 360) / 360
    else:
        lon_fraction = (lon_diff / 360)

    lat_zoom = zoom(imgheight, world_dim['height'], lat_fraction)
    lon_zoom = zoom(imgwidth, world_dim['width'], lon_fraction)
    
    zoom = min([lat_zoom, lon_zoom, zoom_max])

    return zoom