import streamlit as st
import folium
from streamlit_folium import st_folium
from sklearn.cluster import KMeans
import geonamescache

st.title("Animal Rescue Dispatcher")
gc = geonamescache.GeonamesCache()
countries = gc.get_countries()
cities = [city for city in gc.get_cities().values() if city["population"] >= 1_000_000]
colours = ["red", "blue", "green", "orange", "violet", "gray"]

# LEVEL 1: find the closest city
# Step 1: pick an animal
animal = st.selectbox("Which animal needs help?", ["dog", "cat", "bird", "turtle", "rabbit"])

# Step 2: move the pin
lat = st.slider("Latitude (North / South)", -90.0, 90.0, 0.0)
lon = st.slider("Longitude (East / West)", -180.0, 180.0, 0.0)

# Step 3: how far is a city from the pin?
def gap(city):
    return (city["latitude"] - lat) ** 2 + (city["longitude"] - lon) ** 2

# Step 4: the closest city
near = min(cities, key=gap)
st.success(f"The closest big city is {near['name']}. Its rescue team will help the {animal}!")

# LEVEL 2: country and people
# Step 5: which country is it, and how many people live there?
country = countries[near["countrycode"]]
st.write(f"{near['name']} is in {country['name']}. {near['population']:,} people live there.")

# LEVEL 3: rescue regions
# Step 6: how many regions?
number_of_regions = st.slider("How many rescue regions?", 2, 6, 3)

# Step 7: the places of all the cities
places = [[city["latitude"], city["longitude"]] for city in cities]

# Step 8: the computer sorts the cities into regions
regions = KMeans(n_clusters=number_of_regions, n_init=10, random_state=0).fit_predict(places)

# Step 9: which region is the closest city in?
my_region = regions[cities.index(near)]
st.warning(f"{near['name']} is in the {colours[my_region]} region. This region has {list(regions).count(my_region)} big cities that share one rescue centre.")

# FINISH
# Step 10: the map
world_map = folium.Map(location=[20, 0], zoom_start=2, tiles="Esri.WorldImagery")
for number in range(len(places)):
    folium.CircleMarker(places[number], radius=5, color=colours[regions[number]], fill=True, tooltip=cities[number]["name"]).add_to(world_map)
folium.Marker([lat, lon], tooltip="Animal found here").add_to(world_map)
st_folium(world_map, height=450, returned_objects=[])
