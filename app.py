
from model import get_db_connection
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
#import cv2
import mysql.connector
from datetime import datetime
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import python_weather
import asyncio


app = Flask(__name__)
app.secret_key = 'wverihdfuvuwi2482'


app.config['PROFILE_UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'profiles')
os.makedirs(app.config['PROFILE_UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename, filetype):
    if filetype == 'image':
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    return False




@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        number = request.form['number']
        password = request.form['password']
        profile_image = request.files['profile_image']

        if profile_image and allowed_file(profile_image.filename, 'image'):
            filename = secure_filename(profile_image.filename)
            image_path = os.path.join(app.config['PROFILE_UPLOAD_FOLDER'], filename)
            profile_image.save(image_path)
        else:
            flash('Invalid image file.', 'danger')
            return redirect(request.url)

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (name, email, number, password, image_path) VALUES (%s, %s, %s, %s, %s)',
                (name, email, number, hashed_password, filename)
            )
            conn.commit()
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Email already exists.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html', title="Register")




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) 
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()
    
        if user and check_password_hash(user['password'], password):
            print("Stored hash:", user['password'])
            print("Entered password:", password)

            session['email'] = user['email']
            session['name'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html', title="Login")




@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if 'email' not in session:
        flash('Please login to view This Page.', 'warning')
        return redirect(url_for('login'))
   
    
    return render_template('task.html' )



@app.route('/contact' , methods=['GET', 'POST'])
def contact():
    if 'email' not in session:
        flash('Please login to view This Page.', 'warning')
        return redirect(url_for('login'))
    return render_template('contact.html')


@app.route('/profile')
def profile():
    if 'email' not in session:
        flash('Please login to view your profile.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    cursor.execute("SELECT * FROM users WHERE email = %s", (session['email'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('login'))

    return render_template('profile.html', user=user)



@app.route('/controls', methods=['GET', 'POST'])
def controls():
    if 'email' not in session:
        flash('Please login to view This Page.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        action = request.form.get('value', '0')  

        action_map = {
            '0': 'Stop',
            '1': 'Front',
            '2': 'Back',
            '3': 'Left',
            '4': 'Right'
        }
        action_text = action_map.get(action, 'Unknown')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE control_data SET action = %s WHERE id = 1",
            (action,)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash(f'Control : {action_text}', 'success')
        return redirect(url_for('controls'))

    return render_template('controls.html', title="Controls")



@app.route('/control_data', methods=['GET', 'POST'])
def control_data():
    if request.method == 'GET':
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  
        cursor.execute('SELECT * FROM control_data WHERE id = 1')
        control = cursor.fetchone()
        cursor.close()
        conn.close()

        if control:
            return str(control['action']), 200
        else:
            return "No control data found", 404


@app.route('/api/control_data', methods=['GET'])
def get_control_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM control_data WHERE id = 1')
        control = cursor.fetchone()

        cursor.close()
        conn.close()

        if control:
           
            return str(control['action']), 200
        else:
            return "No control data found", 404

    except Exception as e:
        return str(e), 500




@app.route('/update_sensor_data', methods=['GET'])
def update_sensor_data():
    try:
      
        temperature = request.args.get("temperature", "0")
        humidity = request.args.get("humidity", "0")
        soil_moisture = request.args.get("soil_moisture", "0")

       
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sensor_data (temperature, humidity, soil_moisture) VALUES (%s, %s, %s)",
            (str(temperature), str(humidity), str(soil_moisture))
        )
        conn.commit()
        cursor.close()
        conn.close()

       
        return jsonify({
          
            "message": "Sensor data stored successfully",
            "data": {
                "temperature": temperature,
                "humidity": humidity,
                "soil_moisture": soil_moisture
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to store sensor data",
            "error": str(e)
        }), 500




@app.route('/sensordata')
def sensordata():
    if 'email' not in session:
        flash('Please login to view This Page.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    cursor.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC')
    sensor_data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('sensordata.html', title="Sensor Data", sensor_data=sensor_data)



@app.route('/', methods=['GET', 'POST'])
def dashboard():
    if 'email' not in session:
        flash('Please login to view This Page.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', title="Dashboard")

@app.route('/farming', methods=['GET', 'POST'])
def farming():
    if 'email' not in session:
        flash('Please login to view this page.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        action = request.form.get('action')
        cursor.execute("SELECT * FROM dashboard_data WHERE id = 1")
        row = cursor.fetchone()
        valid_actions = ['seeding', 'ploughing', 'diggingUpDown', 'diggingHole']
        if action in valid_actions:
            new_value = 0 if str(row[action]) == '1' else 1
            cursor.execute(f"UPDATE dashboard_data SET {action} = %s WHERE id = 1", (new_value,))
            conn.commit()
            print(f"{action} toggled to {new_value}")
            return jsonify({"action": action, "value": new_value})

    cursor.execute("SELECT * FROM dashboard_data WHERE id = 1")
    task_values = cursor.fetchone()

    
    for key in ['seeding', 'ploughing', 'diggingUpDown', 'diggingHole']:
        task_values[key] = int(task_values[key])

    cursor.close()
    conn.close()
    return render_template('farming.html', title="Farming", task=task_values)


@app.route('/api/dashboard_data', methods=['GET'])
def get_dashboard_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM dashboard_data WHERE id = 1')
        dashboard = cursor.fetchone()
        cursor.close()
        conn.close()

        if dashboard:
           
            values = [
                int(dashboard.get('seeding', 0)),
                int(dashboard.get('ploughing', 0)),
                int(dashboard.get('diggingUpDown', 0)),
                int(dashboard.get('diggingHole', 0))
            ]

          
            return jsonify(values), 200

        else:
            return jsonify({"error": "No dashboard data found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500





@app.route('/camera')
def camera_feed():
    if 'email' not in session:
        flash('Please login to view This Page.', 'warning')
        return redirect(url_for('login'))
    return render_template('camera.html', title="Camera Feed")




@app.route('/team')
def team():
    if 'email' not in session:
        flash('Please login to view This Page.', 'warning')
        return redirect(url_for('login'))
    return render_template('team.html', title="Team HUB")




@app.route('/weather')
def weather():
    if 'email' not in session:
        flash('Please login to view this page.', 'warning')
        return redirect(url_for('login'))

    async def get_weather():
        client = python_weather.Client() 
        weather = await client.get("Bangalore")  
        await client.close()
        return weather

    weather_data = asyncio.run(get_weather())

    
    current_temp = weather_data.temperature
    sky = weather_data.description or "Unavailable"
    humidity = getattr(weather_data, "humidity", "N/A")
    wind = getattr(weather_data, "wind_speed", "N/A")

    today = datetime.now().strftime("%A, %d %B %Y")

    print(f"\n Weather in Bangalore on {today}: {current_temp}°C, {sky}, Humidity: {humidity}, Wind: {wind}\n")

    
    hourly_forecasts = []


    if hasattr(weather_data, "next_days") and weather_data.next_days:
       for forecast in weather_data.next_days[:6]:
          hourly_forecasts.append({
            "date": forecast.date.strftime('%A'),
            "temp": forecast.temperature,
            "sky": forecast.description or "Clear"
        })
    else:

      from datetime import timedelta
      for i in range(6):
        future_date = datetime.now() + timedelta(days=i)
        hourly_forecasts.append({
            "date": future_date.strftime('%A'),
            "temp": weather_data.temperature + (i % 3 - 1),  
            "sky": weather_data.description or "Clear"
        })


    return render_template(
        'weather.html',
        title="Weather",
        current_temp=current_temp,
        sky=sky,
        humidity=humidity,
        wind=wind,
        hourly_forecasts=hourly_forecasts,
        today=today
    )

@app.route('/ai', methods=['GET'])
def ai():
    if 'email' not in session:
        flash('Please login to view this page.', 'warning')
        return redirect(url_for('login'))


    query = request.args.get('q', '').strip().lower()

   
    if not query:
      
        return render_template('ai.html', title="AI Farming Assistant")

    try:
       
        df = pd.read_csv('clean_crops.csv')

       
        df['combined'] = (
            df['crop_name'].astype(str) + ' ' +
            df['season'].astype(str) + ' ' +
            df['soil_type'].astype(str) + ' ' +
            df['description'].astype(str)
        ).str.lower()

       
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(df['combined'])
        query_vec = vectorizer.transform([query])
        similarity_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

       
        best_index = similarity_scores.argmax()
        best_score = similarity_scores[best_index]

        if best_score < 0.1:
            return jsonify({"message": "Ai Not understand."})

        result = df.iloc[best_index].to_dict()

        response = {
            "crop_name": result["crop_name"],
            "season": result["season"],
            "soil_type": result["soil_type"],
            "watering_frequency": result["watering_frequency"],
            "fertilizer": result["fertilizer"],
            "harvest_time": result["harvest_time"],
            "description": result["description"],
            "similarity_score": round(float(best_score), 3)
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/analytics')
def analytics():
    if 'email' not in session:
        flash('Please login to view this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('analytics.html', title="Analytics")




@app.route('/inventory')
def inventory():
    if 'email' not in session:
        flash('please login to view this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('inventory.html', title="Inventory")

@app.route('/maintenance')
def maintenance():
    if 'email' not in session:
        flash('please login to view this page.', 'warning')
        return redirect(url_for('login'))
    return render_template ('maintenance.html', title= "Maintenance" )



@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
