import streamlit as st
import folium
from streamlit_folium import st_folium
from sklearn.cluster import KMeans
import geonamescache

st.title("Dream Trip: Plan Your Visit")
st.write("Pick a city you dream of visiting. We will find where it is on Earth, and a second stop in ANOTHER country!")
gc = geonamescache.GeonamesCache()
countries = gc.get_countries()
cities = [city for city in gc.get_cities().values() if city["population"] >= 1_000_000]
city_names = {f"{city['name']}, {countries[city['countrycode']]['name']}": city for city in cities}
colours = ["red", "blue", "green"]

# LEVEL 1: your dream city
dream_name = st.selectbox("Which city do you dream of visiting?", sorted(city_names), index=None, placeholder="Choose a city")   # Step 1
if dream_name is None:
    st.stop()
dream = city_names[dream_name]                           # Step 2
lat, lon = dream["latitude"], dream["longitude"]
st.write(f"{dream_name} is at latitude {lat:.2f} and longitude {lon:.2f}. {dream['population']:,} people live there.")

# LEVEL 2: your second stop (the closest big city in ANOTHER country)
def gap(city):                                           # Step 3: smaller gap = closer
    return (city["latitude"] - lat) ** 2 + (city["longitude"] - lon) ** 2
others = [city for city in cities if city["countrycode"] != dream["countrycode"]]     # Step 4: cities in other countries
second = min(others, key=gap)                            # Step 5: the closest one
country = countries[second["countrycode"]]               # Step 6
st.success(f"Add a second stop: {second['name']}, {country['name']}!")

# LEVEL 3: 3 colour groups (cities that are close together get the same colour)
places = [[city["latitude"], city["longitude"]] for city in cities]               # Step 7
groups = KMeans(n_clusters=3, n_init=10, random_state=0).fit_predict(places)      # Step 8
my_group = groups[cities.index(dream)]                                            # Step 9
st.warning(f"{dream['name']} is in the {colours[my_group]} group. Cities in the same group are close together.")

# FINISH: the map (given)
trip_map = folium.Map(location=[20, 0], zoom_start=2, min_zoom=1, max_bounds=True, tiles=None)
folium.TileLayer("Esri.WorldImagery", no_wrap=True, bounds=[[-90, -180], [90, 180]]).add_to(trip_map)
for city, group in zip(cities, groups):
    folium.CircleMarker([city["latitude"], city["longitude"]], radius=5, color=colours[group], fill=True, fill_opacity=0.8, tooltip=city["name"]).add_to(trip_map)
folium.PolyLine([[lat, lon], [second["latitude"], second["longitude"]]], color="yellow").add_to(trip_map)
folium.Marker([lat, lon], icon=folium.Icon(color="black", icon="star"), tooltip=dream_name).add_to(trip_map)
st_folium(trip_map, height=450, returned_objects=[], use_container_width=True)
st.caption("The black star is your dream city. The yellow line goes to your second stop. Dots with the same colour are in the same group.")
