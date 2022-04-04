from flask import Blueprint, render_template, request
import folium
import pgeocode
from flask_sqlalchemy import SQLAlchemy
from database import users, add_user

map_app = Blueprint("map_app", __name__, static_folder="static", template_folder="templates")
# map_app.config["SQLALCHEMY_DATABASE_URL"] = "sqlite://users.sqlite3"
# map_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
nomi = pgeocode.Nominatim('ca')



@map_app.route("/", methods=["GET", "POST"])
def base_map():
  
  world_map = folium.Map(
    location=[58.785504, -97.251307],
     zoom_start=3
    )
  
  if request.method == "POST":
    
    postal_code = request.form["pc"]
    if len(request.form) > 1:
      level = request.form["rl"]

    coords = nomi.query_postal_code(postal_code)

    if len(request.form) > 1:
      found_user = users.query.filter_by(postal=postal_code).first()
      if found_user:
        found_user.delete()
      
      usr = users(postal_code, level)
      add_user(usr)
      

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


@map_app.route('/dmap')
def dmap():
  return render_template('data_map.html')
