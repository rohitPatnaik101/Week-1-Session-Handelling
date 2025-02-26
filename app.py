from flask import Flask, session, request, render_template, redirect, url_for, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = '7484b74173018a19cc60f4e7783fcbcb'

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

db = SQLAlchemy(app)

# Define the User db model 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    login_time = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

@app.route('/')
def home():
    """API Home Route"""
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Route (Render HTML Form and Store User)"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not username or not email or not phone:
            return render_template('login.html', error="All fields are required.")

        # Store user info in session
        session['username'] = username
        session['email'] = email
        session['phone'] = phone
        session['login_time'] = login_time

        # Insert user info into the database
        new_user = User(username=username, email=email, phone=phone, login_time=login_time)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/showme', methods=['GET'])
def showme():
    """Retrieve session details (Logged-in user info) using jsonify"""
    if 'username' in session:
        return jsonify({
            "message": "User is logged in",
            "username": session.get('username'),
            "email": session.get('email'),
            "phone": session.get('phone'),
            "login_time": session.get('login_time')
        })
    return jsonify({"message": "No active session"}), 401


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Dashboard Route (Show logged-in user details)"""
    if 'username' in session:
        login_time = datetime.strptime(session.get('login_time'), '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        logged_in_duration = str(current_time - login_time)

        return render_template('dashboard.html', username=session['username'], email=session['email'], 
                               logged_in_duration=logged_in_duration)
    
    return redirect(url_for('login'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Logout Route - Clears session"""
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
