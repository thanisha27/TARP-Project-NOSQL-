from flask import Flask, request, jsonify, redirect, render_template, url_for
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import datetime


app = Flask(__name__)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client.calmconnectt  # Connect to 'calmconnectt' database
userdetails = db.userdetails  # 'userdetails' collection for storing user data
quizdetails = db.quizdetails  # 'quizdetails' collection for storing quiz data
dailymood_tracker = db.dailymood_data  # 'mood_tracker' collection for storing mood data
user_feedback = db.user_feedback  # 'user_feedback' collection for storing feedback
questionss= db.questionss
personaldetails= db.personaldetails
# Collections for anxiety levels and reflections
anxiety_collection = db['anxiety_levels']
reflection_collection = db['reflections']

# Collection for therapist quiz
quiz_responses_collection = db['therapist_quiz']  # Replace with your collection name

# Collection for booking details
booking_details_collection = db.bookingdetails
# Route to render the sign-up/login page
@app.route('/')
def signup_page():
    return render_template('signup.html')

# Route for registration (POST)
@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # Check if user already exists
    if userdetails.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Insert user details into MongoDB
    user_data = {
        "name": name,
        "email": email,
        "password": hashed_password
    }

    userdetails.insert_one(user_data)
    return jsonify({"success": "User registered successfully"}), 200

# Route for login (POST)
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    # Find the user by email
    user = userdetails.find_one({"email": email})

    if user and check_password_hash(user['password'], password):
        # Redirect to home page after successful login
        return redirect(url_for('index_page'))
    else:
        return jsonify({"error": "Invalid email or password"}), 401

# Route to serve index.html after successful login
@app.route('/index')
def index_page():
    return render_template('index.html')

# Route to serve about.html
@app.route('/about')
def about_page():
    return render_template('about.html')

# Route to serve blog.html
@app.route('/blog')
def blog_page():
    return render_template('blog.html')

# Route to serve resources.html
@app.route('/resources')
def resources_page():
    return render_template('resources.html')

# Sub-routes for individual resource pages
@app.route('/self-help-resources')
def self_help_resources():
    return render_template('self_help_resources.html')

# Route to render the anxiety resources page
@app.route('/anxiety_resources')
def anxiety_resources():
    return render_template('anxiety_resources.html')

 # Route to save anxiety level
@app.route('/save_anxiety', methods=['POST'])
def save_anxiety():
    try:
        level = request.json.get('level')
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Insert anxiety level into MongoDB
        anxiety_data = {
            "date": date,
            "level": level
        }
        anxiety_collection.insert_one(anxiety_data)
        return jsonify({"message": "Anxiety level saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to save journal reflection
@app.route('/save_reflection', methods=['POST'])
def save_reflection():
    try:
        reflection = request.json.get('reflection')
        # date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Insert reflection into MongoDB
        reflection_data = {
            # "date": date,
            "reflection": reflection
        }
        reflection_collection.insert_one(reflection_data)
        print("nakku",reflection_data)
        return jsonify({"message": "Reflection saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  

@app.route('/get_anxiety_data', methods=['GET'])
def get_anxiety_data():
    # Fetch the latest 7 entries from the collection, sorted by date
    entries = anxiety_collection.find().sort("date", -1).limit(7)
    
    # Convert entries to a list of dictionaries
    anxiety_data = []
    for entry in entries:
        anxiety_data.append({
            "date": entry["date"],
            "level": int(entry["level"])
        })

    # Sort the data by date to display in chronological order
    anxiety_data = sorted(anxiety_data, key=lambda x: x['date'])
    return jsonify(anxiety_data)

# Route for Therapist Matching Quiz
@app.route('/therapist_matching_quiz', methods=['GET', 'POST'])
def therapist_matching_quiz():
    if request.method == 'POST':
        # Collect data from the quiz form
        quiz_data = {
            'gender': request.form.get('gender'),
            'experience_level': request.form.get('experience-level'),
            'language': request.form.get('language'),
            'other_language': request.form.get('other-language'),
            'approaches': request.form.getlist('approaches'),
            'session_format': request.form.get('session-format'),
            'frequency': request.form.get('frequency'),
            'issues': request.form.getlist('issues'),
            'contact_method': request.form.get('contact-method'),
            'specific_requests': request.form.get('specific-requests')
        }

        # Insert data into therapist_quiz collection
        quiz_responses_collection.insert_one(quiz_data)
        return redirect(url_for('therapist_matching_quiz'))  # Redirect to the same page or a results page

    return render_template('therapist_matching_quiz.html')


# Route to render the book consultation page
@app.route('/book_consultation', methods=['GET', 'POST'])
def book_consultation_page():
    if request.method == 'POST':
        # Collect data from the booking form
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            date = request.form.get('date')
            time = request.form.get('time')

            # Print form data for debugging
            print(f"Booking Data: Name={name}, Email={email}, Phone={phone}, Date={date}, Time={time}")

            # Insert data into MongoDB
            booking_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'date': date,
                'time': time
            }

            booking_details_collection.insert_one(booking_data)
            print("Booking data inserted successfully.")

            return jsonify({"success": "Your booking has been confirmed. We will contact you shortly!"}), 200

        except Exception as e:
            print(f"Error occurred during booking: {e}")
            return jsonify({"error": str(e)}), 500

    # Render the book consultation HTML template if GET request
    return render_template('book_consultation.html')

@app.route('/therapist-resources')
def therapist_resources():
    return render_template('therapist_resources.html')

@app.route('/video-resources')
def video_resources():
    return render_template('video_resources.html')

# Route for the 7-Day Self-Care Challenge
@app.route('/challenge')
def challenge_page():
    return render_template('challenge.html')

# Route for Day 6 Exercises
@app.route('/day6-exercises')
def day6_exercises_page():
    return render_template('day6-exercises.html')

# Route for Progress Tracker
@app.route('/progress-tracker')
def progress_tracker_page():
    return render_template('progress-tracker.html')

# Route for the Mood Tracker form
@app.route('/mood-tracker', methods=['POST'])
def mood_tracker():
    mood = request.form.get('mood')
    return jsonify({"success": "Mood logged successfully!"}), 200

# Route for the Feedback form
@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    name = request.form.get('name')
    email = request.form.get('email')
    topic = request.form.get('topic')
    feedback = request.form.get('feedback')

    feedback_data = {
        "name": name,
        "email": email,
        "topic": topic,
        "feedback": feedback
    }
    user_feedback.insert_one(feedback_data)
    return jsonify({"success": "Feedback submitted successfully!"}), 200

# Route for the Quiz page
@app.route('/quiz')
def quiz_page():
    return render_template('quiz.html')

# Route to handle quiz form submission and save data to MongoDB
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    name = request.form.get('name')
    email = request.form.get('email')
    q1 = request.form.get('q1')
    q2 = request.form.get('q2')
    q3 = request.form.get('q3')
    q4 = request.form.get('q4')
    q5 = request.form.get('q5')
    q6 = request.form.get('q6')
    q7 = request.form.get('q7')
    q8 = request.form.get('q8')
    q9 = request.form.get('q9')
    mood = request.form.get('mood')

    quiz_data = {
        'name': name,
        'email': email,
        'q1': q1,
        'q2': q2,
        'q3': q3,
        'q4': q4,
        'q5': q5,
        'q6': q6,
        'q7': q7,
        'q8': q8,
        'q9': q9,
        'mood': mood
    }

    quizdetails.insert_one(quiz_data)
    return redirect(url_for('index_page'))

# Route to handle mood data submission
@app.route('/submit_mood_data', methods=['POST'])
def log_data():
    name = request.form['name']
    email = request.form['email']
    mood = request.form['mood']

    mood_data = {
        'name': name,
        'email': email,
        'mood': mood
    }

    dailymood_tracker.insert_one(mood_data)
    return redirect(url_for('resources_page'))

# Route for the User Feedback form submission
@app.route('/submit_feedbacks', methods=['POST'])
def submit_feedbacks():
    name = request.form.get('name')
    email = request.form.get('email')
    topic = request.form.get('topic')
    feedback = request.form.get('feedback')

    feedback_data = {
        "name": name,
        "email": email,
        "topic": topic,
        "feedback": feedback
    }

    user_feedback.insert_one(feedback_data)
    return redirect(url_for('resources_page'))

# Route to handle personal story submissions
@app.route('/submit_story', methods=['POST'])
def submit_story():
    story = request.form.get('story')  # Get the story content from the form

    # Insert the story into 'personaldetails' collection in MongoDB
    personaldetails.insert_one({'story': story})

    # Return success message as JSON response
    return jsonify({"success": "Your personal story has been submitted successfully!"}), 200

# Route to handle expert question submissions
@app.route('/submit_question', methods=['POST'])
def submit_question():
    question = request.form.get('question')  # Get the question content from the form

    # Insert the question into 'questionss' collection in MongoDB
    questionss.insert_one({'question': question})

    # Return success message as JSON response
    return jsonify({"success": "Your question has been submitted successfully!"}), 200


@app.route('/nearest_facilities')
def nearest_facilities():
    # Code to handle facility search
    return render_template("nearest_facilities.html")

@app.route('/book_consultation', methods=['GET', 'POST'])
def book_consultation():
    if request.method == 'POST':
        # Logic for booking consultation (if needed)
        return redirect(url_for('nearest_facilities'))
    return render_template("book_consultation.html")


if __name__ == '__main__':
    app.run(debug=True)

