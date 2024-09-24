from flask import Flask, render_template, request
import pandas as pd
import requests
import logging
import time
import concurrent.futures
from ski_resort_scraper.geolocation import GeoLocator

app = Flask(__name__)


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
    url = f"http://router.project-osrm.org/route/v1/driving/{longitude1},{latitude1};{longitude2},{latitude2}"

    data = get_page(url)
    # Extract distance (in meters) and duration (in seconds)
    if data:
        distance = data['routes'][0]['distance'] / 1000  # in kilometers
        duration = data['routes'][0]['duration'] / 3600  # in hours
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
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        # Map the calculation function to each row in the dataframe
        results = list(executor.map(calculate_for_row, [row for idx, row in df.iterrows()]))

    # Unpack the results into distances and durations
    distances, durations = zip(*results)

    # Add results to the dataframe
    df['distance [km]'] = distances
    df['travel time [h]'] = durations

    return df


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        city = request.form.get('city')
        origin_country = request.form.get('origin_country')
        filter_countries = request.form.getlist('filter_countries')
        total_slopes_min = float(request.form.get('total_slopes_min', 0))
        total_slopes_max = float(request.form.get('total_slopes_max', 500))
        total_lifts_min = int(request.form.get('total_lifts_min', 0))
        total_lifts_max = int(request.form.get('total_lifts_max', 100))
        max_travel_time = float(request.form.get('max_travel_time', 24))

        g = GeoLocator()
        lat, long = g.get_coordinates(city, origin_country)

        if long is None or lat is None:
            return render_template('index.html', error="Could not find coordinates for the given city and country.")

        try:
            df = pd.read_csv('ski_resorts.csv')
        except FileNotFoundError:
            return render_template('index.html', error="Ski resort data not available.")

        # Filter by selected countries
        if filter_countries:
            df = df[df['country'].isin(filter_countries)]

        # Filter by total slopes and lifts
        df = df[(df['total_slopes'] >= total_slopes_min) & (df['total_slopes'] <= total_slopes_max)]
        df = df[(df['total_lifts'] >= total_lifts_min) & (df['total_lifts'] <= total_lifts_max)]

        if df.empty:
            return render_template('index.html', error="No ski resorts found matching your criteria.")

        df.dropna(inplace=True)
        # Start the timer
        start_time = time.time()
        df = add_travel_times(df, long, lat)
        # End the timer and calculate the total time taken
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Time taken: {execution_time:.2f} seconds")
        df = df.sort_values('travel time [h]')
        # Filter by maximum travel time
        df = df[df['travel time [h]'] <= max_travel_time]

        return render_template('results.html', df=df)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
