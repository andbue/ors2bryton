# ors2bryton
Convert routes from openrouteservice for bryton devices

Since I don't understand the steps bryton wants me to take to put navigation instructions on my Rider 330 GPS cyclocomputer, I wrote some lines of python to convert routes created with [openrouteservice](https://maps.openrouteservice.org) to their binary file format. The GPX file has to be exported in the Ors API GPX format, instructions included. Then simply run `python ors2bryton.py gpxfile.gpx`.

Thanks to https://github.com/erosinnocenti/openbryton for documenting the bryton file format!
