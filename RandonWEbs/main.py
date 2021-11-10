from flask import Flask, render_template, request, redirect, session
import folium
# from map_app import map_app
import json
from flask_sqlalchemy import SQLAlchemy
import pgeocode

app = Flask(__name__)
# app.register_blueprint(map_app, url_prefix="/datamap")
nomi = pgeocode.Nominatim('ca')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usersresults.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database class
class users(db.Model):
  _id = db.Column("id", db.Integer, primary_key=True)
  postal = db.Column(db.String(100))
  lat = db.Column(db.String(100))
  log = db.Column(db.String(100))
  level = db.Column(db.Integer)

  def __init__(self, postal, lat, log, level):
    self.postal = postal
    self.lat = lat
    self.log = log
    self.level = level



@app.route("/home", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():
  start_coords = (58.785504, -97.251307)

  folium_map = folium.Map(location=start_coords, zoom_start=5)
  

  with open("geo.json") as canadaOutline:
    Canada = json.load(canadaOutline)
  
  canadaData = {
    'Alberta': 30000,
    'British Columbia': 30000,
    'Manitoba': 36000,
    'New Brunswick': 36000,
    'Newfoundland': 15000,
    'Northwest Territories': 1700,
    'Nova Scotia': 18000,
    'Nunavut': 7200,
    'Ontario': 30000,
    'Prince Edward Island': 1728,
    'Quebec': 31000,
    'Saskachewan': 36000,
    'Yukon': 30000
  }
  folium_map.choropleth(
    geo_data=Canada,
    data=canadaData,
    columns=['Province', 'Profit'],
    key_on='feature.properties.name',
    fill_color='YlOrRd', 
    fill_opacity=0.7, 
    line_opacity=0.2,
    legend_name='Canada data'
  ) 
  folium_map.save('templates/map.html')
  
  return render_template('index.html')

@app.route('/map')
def map():
  return render_template('map.html')

@app.route('/testinformation')
def testInfo():
  return render_template('testing_info.html')

@app.route('/why-you-should-use-us')
def importance():
  return render_template('importance.html')

# map_app

@app.route('/datamap', methods=["GET", "POST"])
def base_map():
  
  world_map = folium.Map(
    location=[58.785504, -97.251307],
     zoom_start=3
    )
  
  for user in users.query.all():
      folium.Marker(
          location=[user.lat, user.log],
          popup=f"<b>{user.postal} {user.level}</b>",
          tooltip=f"{user.level}"
      ).add_to(world_map)

  if request.method == "POST":
    
    postal_code = request.form["pc"]
    if len(request.form) > 1:
      level = request.form["rl"]


    coords = nomi.query_postal_code(postal_code)

    if len(request.form) > 1:
      
      usr = users(str(postal_code), str(coords.latitude), str(coords.longitude), int(level))

      db.session.add(usr)
      db.session.commit()
      
      print(users.query.all())
      folium.Marker(
          location=[coords.latitude, coords.longitude],
          popup=f"<b>{postal_code} {level}</b>",
          tooltip=f"{level}"
      ).add_to(world_map)

    else:
      folium.Marker(
          location=[coords.latitude, coords.longitude],
          popup=f"<b>{postal_code}</b>",
      ).add_to(world_map)

  world_map.save('templates/data_map.html')
  return render_template("data_map_page.html")


@app.route('/datamap/dmap')
def dmap():
  return render_template('data_map.html')

if __name__ == "__main__":  # Makes sure this is the main process
  app.run(debug=True, host='0.0.0.0', port=8080)