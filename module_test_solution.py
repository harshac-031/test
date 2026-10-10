import streamlit as st
import folium
from streamlit_folium import st_folium
from sklearn.cluster import KMeans
import geonamescache

st.title("Animal Rescue Dispatcher")
gc = geonamescache.GeonamesCache()
countries = gc.get_countries()
cities = [city for city in gc.get_cities().values() if city["population"] >= 1_000_000]
country_names = sorted(each["name"] for each in countries.values())
colours = ["red", "blue", "green", "orange", "violet", "gray"]

# LEVEL 1: find the closest city
animal = st.selectbox("Which animal needs help?", ["dog", "cat", "bird", "turtle", "rabbit"])    # Step 1
lat = st.slider("Latitude (North / South)", -90.0, 90.0, 0.0)                                    # Step 2
lon = st.slider("Longitude (East / West)", -180.0, 180.0, 0.0)
def gap(city):                                           # Step 3: smaller gap = closer to the pin
    return (city["latitude"] - lat) ** 2 + (city["longitude"] - lon) ** 2
near = min(cities, key=gap)                              # Step 4: the city with the smallest gap
st.success(f"The closest big city is {near['name']}. Its rescue team will help the {animal}!")

# LEVEL 2: guess the country, then see the answer
country = countries[near["countrycode"]]                 # Step 5
guess = st.selectbox("Guess: which country is that city in?", country_names, index=None)
if guess:
    st.write(f"{near['name']} is in {country['name']}. {near['population']:,} people live there.")
    if guess == country["name"]:
        st.success("Right!")
    else:
        st.error("Not quite!")

# LEVEL 3: rescue regions
number_of_regions = st.slider("How many rescue regions?", 2, 6, 3)                               # Step 6
places = [[city["latitude"], city["longitude"]] for city in cities]                              # Step 7
regions = KMeans(n_clusters=number_of_regions, n_init=10, random_state=0).fit_predict(places)    # Step 8: a region number for each city
my_region = regions[cities.index(near)]                                                          # Step 9
st.warning(f"{near['name']} is in the {colours[my_region]} region. Its rescue centre will help the {animal}!")

# FINISH: the map (one world only). Each city is a dot in its region's colour.
world_map = folium.Map(location=[20, 0], zoom_start=2, min_zoom=1, max_bounds=True, tiles=None)
folium.TileLayer("Esri.WorldImagery", no_wrap=True, bounds=[[-90, -180], [90, 180]]).add_to(world_map)
for city, region in zip(cities, regions):
    folium.CircleMarker([city["latitude"], city["longitude"]], radius=5, color=colours[region], fill=True, tooltip=city["name"]).add_to(world_map)
folium.Marker([lat, lon], tooltip="Animal found here").add_to(world_map)
st_folium(world_map, height=450, returned_objects=[])
