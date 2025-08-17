from dotenv import load_dotenv
import os

load_dotenv()
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from weather import main as get_weather, get_weather_by_coords, get_coords_metadata
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

@app.route('/weather-by-coords', methods=['POST'])
def weather_by_coords():
    coords = request.get_json()
    lat = coords.get('lat')
    lon = coords.get('lon')

    if lat is None or lon is None:
        return jsonify({'error': 'Missing coordinates'}), 400

    weather_data = get_weather_by_coords(lat, lon)
    session['auto_data'] = weather_data

    meta = get_coords_metadata(lat, lon)
      
    return jsonify({
        'status': 'ok',
        'city': meta['city'],
        'state': meta['state'],
        'country': meta['country']
    })

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    city = state = country = ""
    if request.method == 'POST':
        city = request.form['cityName']
        state = request.form['stateName']
        country = request.form['countryName']
        data = get_weather(city, state, country)
        session.pop('auto_data', None)
    elif 'auto_data' in session:
        data = session['auto_data']
       
    return render_template('index.html', data=data, city=city, state=state, country=country)

if __name__ == '__main__':
    app.run(debug=True)
