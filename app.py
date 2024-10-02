from flask import Flask, jsonify, request
import pandas as pd
import requests
import logging
import concurrent.futures
from ski_resort_scraper.geolocation import GeoLocator
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


def get_page(page_url: str):
    """
    Function to get a page from link
    :param page_url:
    :return:
    """
    try:
        response = requests.get(page_url, params={'overview': 'false'})
        response.raise_for_status()
        logging.info("Successful request for %s", page_url)
        return response.json()
    except requests.RequestException as e:
        logging.exception("Connection error: %s - URL: %s", e, page_url)
        return None


def calculate_path(latitude1: float, longitude1: float, latitude2: float, longitude2: float):
    """
    Function to calculate the path between two cities
    :param latitude1:
    :param longitude1:
    :param latitude2:
    :param longitude2:
    """
    url = (f"http://34.88.129.39:8080/ors/v2/directions/driving-car?&start={longitude1},{latitude1}&end={longitude2},"
           f"{latitude2}")

    data = get_page(url)
    # Extract distance (in meters) and duration (in seconds)
    if data:
        first_feature = data['features'][0]
        first_segment = first_feature['properties']['segments'][0]

        distance = first_segment['distance'] / 1000
        duration = first_segment['duration'] / 3600
    else:
        distance = None
        duration = None

    return distance, duration


def add_travel_times(df, input_long, input_lat):
    """
    Function to calculate the travel times between two cities using multithreading
    :param df: DataFrame with 'latitude' and 'longitude' columns
    :param input_long: Longitude of the starting location
    :param input_lat: Latitude of the starting location
    :return df: Updated dataframe with travel times
    """

    def calculate_for_row(row):
        # Unpack the row's latitude and longitude
        latitude, longitude = row['latitude'], row['longitude']
        # Calculate the distance and duration for this row
        return calculate_path(input_lat, input_long, latitude, longitude)

    # Using ThreadPoolExecutor for multithreading
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        # Map the calculation function to each row in the dataframe
        results = list(executor.map(calculate_for_row, [row for idx, row in df.iterrows()]))

    # Unpack the results into distances and durations
    distances, durations = zip(*results)

    # Add results to the dataframe
    df['distance'] = distances
    df['travel_time'] = durations

    return df


@app.route('/', methods=['POST'])
def get_ski_resorts():
    data = request.get_json()

    city = data.get('city')
    origin_country = data.get('origin_country')
    total_slopes_min = float(data.get('total_slopes_min', 0))
    total_slopes_max = float(data.get('total_slopes_max', 500))
    total_lifts_min = int(data.get('total_lifts_min', 0))
    total_lifts_max = int(data.get('total_lifts_max', 100))
    max_travel_time = float(data.get('max_travel_time', 24))
    filter_countries = data.get('filter_countries')
    if filter_countries:
        filter_countries = json.loads(filter_countries)
    # Get coordinates of the origin city
    g = GeoLocator()
    lat, long = g.get_coordinates(city, origin_country)

    if long is None or lat is None:
        return jsonify({"error": "Could not find coordinates for the given city and country."}), 400

    try:
        df = pd.read_csv('./data/ski_resorts.csv')
    except FileNotFoundError:
        return jsonify({"error": "Ski resort data not available."}), 500

    # Filter by selected countries
    if filter_countries:
        df = df[df['country'].isin(filter_countries)]

    # Filter by total slopes and lifts
    df = df[(df['total_slopes'] >= total_slopes_min) & (df['total_slopes'] <= total_slopes_max)]
    df = df[(df['total_lifts'] >= total_lifts_min) & (df['total_lifts'] <= total_lifts_max)]

    if df.empty:
        return jsonify({"error": "No ski resorts found matching your criteria."}), 404

    df.dropna(inplace=True)
    df = add_travel_times(df, long, lat)
    df = df[df['travel_time'] <= max_travel_time]
    # Convert the DataFrame to a list of dictionaries
    # Returning 21 best ski resorts according to rating
    df = df.head(21)
    result = df.to_dict(orient='records')

    return jsonify(result), 200


if __name__ == '__main__':
    app.run(port=8080)
