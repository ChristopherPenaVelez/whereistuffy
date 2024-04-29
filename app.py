from flask import Flask, render_template, redirect, url_for, request, jsonify, session
import random
import math
import os
from math import radians, cos, sin, asin, sqrt

app = Flask(__name__)
app.secret_key = "super secret key"
app.static_folder = 'static'  # Default static folder

photos = {
    "001": {"filename": "temp1.jpg", "location": "Library"},
    "002": {"filename": "temp2.jpg", "location": "Main Gate"},
    "003": {"filename": "temp3.jpg", "location": "Cafeteria"},
    "004": {"filename": "temp4.jpg", "location": "TSU"},
    "005": {"filename": "temp5.jpg", "location": "GYM"},
}

locations = {
    "Library": {"lat": 33.8751, "lng": -117.8867},
    "Main Gate": {"lat": 33.8765, "lng": -117.8850}
}
33.88126429705333, -117.88526229759773



photo_locations = {
    "temp1.jpg": {"lat": 33.8809, "lng": -117.8854},
    "temp2.jpg": {"lat": 33.8815, "lng": -117.8863},
    "temp3.jpg": {"lat": 33.8815, "lng": -117.8858},
    "temp4.jpg": {"lat": 33.8800, "lng": -117.8855},
    "temp5.jpg": {"lat": 33.8813, "lng": -117.8853},
}


def calculate_score_and_distance(user_guess, correct_coords):
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    lat1, lon1 = map(radians, [user_guess['lat'], user_guess['lng']])
    lat2, lon2 = map(radians, [correct_coords['lat'], correct_coords['lng']])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    distance_km = c * r

    # Assuming a simple scoring rule where 0 distance = perfect score of 100
    # and score goes down the further away the guess is.
    # The scale factor determines how quickly the score drops off - can be adjusted.
    max_distance_km = 1
    score = max(0, (1 - (distance_km / max_distance_km)) * 100)
    score = round(score)
    
    return score, distance_km

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/play', methods=['GET', 'POST'])
def play():
    if 'round' not in session:
        session['round'] = 1  # Starting round
        session['total_score'] = 0  # Starting total score

    if session['round'] > 5:
        total_score = session['total_score']
        session.pop('round')  # Remove 'round' from session
        session.pop('total_score')  # Remove 'total_score' from session
        return render_template('game_over.html', total_score=total_score)

    photo_filenames = list(photo_locations.keys())
    random_photo = random.choice(photo_filenames)
    photo_data = photo_locations[random_photo]

    return render_template('index.html', photo_filename=random_photo, photo_data=photo_data)


@app.route('/guess', methods=['POST'])
def guess():
    # Processing of guess to be implemented.
    return jsonify({"result": "Processing of guess not yet implemented."})


@app.route('/check_guess', methods=['POST'])
def check_guess():
    data = request.get_json()
    user_guess = data['guess']
    correct_coords = data['correct']
    score, distance_km = calculate_score_and_distance(user_guess, correct_coords)
    session['total_score'] += score
    if 'round' in session:
        session['round'] += 1
    else:
        session['round'] = 1
    print(session['round'])

    # Instead of returning JSON, render a template with score and distance

    if session['round'] > 5:
        return jsonify(game_over=True, total_score=session['total_score'])
    else:
        return jsonify(round=session['round'], score=score, distance_km=distance_km)
    

@app.route('/next_round', methods=['GET'])
def next_round():
    # This route prepares the next round
    if 'round' in session and session['round'] <= 5:
        return redirect(url_for('play'))
    else:
        # If the game is over, redirect to a game over page or reset the game
        reset_game()
        return render_template('game_over.html', total_score=session['total_score'])
    

@app.route('/reset_game', methods=['POST'])
def reset_game():
    # Reset the game state in the session
    session['round'] = 1
    session['total_score'] = 0
    return jsonify(status='ok')

if __name__ == '__main__':
    app.run(debug=True)
