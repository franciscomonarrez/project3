from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

migrate = Migrate(app, db)

user_club_association = db.Table('user_club_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True)
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    dob = db.Column(db.Date())
    bio = db.Column(db.Text)
    interests = db.Column(db.Text)
    clubs = db.relationship('Club', secondary=user_club_association, backref=db.backref('members', lazy='dynamic'))

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        dob = request.form.get("dob")
        dob=datetime.datetime.strptime(dob, '%Y-%m-%d').date()
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"), method='sha256')

        new_user = User(name=name, dob=dob, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("Please check your login details and try again.", "login")
            return redirect(url_for("login"))

        login_user(user)

        return redirect(url_for("home"))  

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/home")
@login_required
def home():
    return render_template("home.html", user=current_user) 

@app.route("/calendar")
@login_required
def calendar():
    return render_template("calendar.html")

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.name = request.form.get("name")
        current_user.dob = datetime.datetime.strptime(request.form.get("dob"), '%Y-%m-%d').date()
        current_user.email = request.form.get("email")
        current_user.bio = request.form.get("bio")
        current_user.interests = request.form.get("interests")

        db.session.commit()

        flash("Profile updated successfully.", "profile")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=current_user)

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        current_user.username = request.form.get("username")
        current_user.name = request.form.get("name")
        current_user.dob = datetime.datetime.strptime(request.form.get("dob"), '%Y-%m-%d').date()

        db.session.commit()

        flash("Settings updated successfully.", "settings")
        return redirect(url_for("settings"))

    return render_template("settings.html", user=current_user)

@app.route('/delete_account')
@login_required
def delete_account():
    user = User.query.filter_by(email=current_user.email).first()
    db.session.delete(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))

@app.route('/golf_club')
def golf_club():
    return render_template('clubs/golf_club.html')

@app.route('/about')
def about():
    return render_template('about.html')  # Replace with your about page template name

@app.route('/surf_club')
def surf_club():
    return render_template('clubs/surf_club.html')

@app.route('/latinx_club')
def latinx_club():
    return render_template('clubs/latinx_club.html')

@app.route('/african_american_club')
def african_american_club():
    return render_template('clubs/african_american_club.html')

@app.route('/chess_club')
def chess_club():
    return render_template('clubs/chess_club.html')

@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    if request.method == 'POST':
        # handle the POST request here. This is where you would typically
        # validate the email and send a password reset link.
        email = request.form.get('email')
        # code to send password reset email goes here...
        return "Link Sent"

    # render the forgot password page
    return render_template('forgotpassword.html')


@app.route('/photography_club')
def photography_club():
    return render_template('clubs/photography_club.html')

@app.route('/drama_club')
def drama_club():
    return render_template('clubs/drama_club.html')

@app.route('/music_club')
def music_club():
    return render_template('clubs/music_club.html')

@app.route('/robotics_club')
def robotics_club():
    return render_template('clubs/robotics_club.html')

@app.route('/user_agreement')
def user_agreement():
    return render_template('user_agreement.html')  

@app.route('/debate_club')
def debate_club():
    return render_template('clubs/debate_club.html')

@app.route('/volunteering_club')
def volunteering_club():
    return render_template('clubs/volunteering_club.html')

@app.route('/copyright_policy')
def copyright_policy():
    return render_template('copyright_policy.html')

@app.route('/profile', methods=['POST'])
def update_profile():
    # get the uploaded file
    file = request.files['profile_pic']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # update user's profile picture in database here
        # redirect to the profile page or somewhere else on successful update
        return redirect(url_for('profile'))
    else:
        # handle invalid file here
        return "Invalid file"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/community_guidelines')
def community_guidelines():
    return render_template('community_guidelines.html')


@app.route('/programming_club')
def programming_club():
    return render_template('clubs/programming_club.html')

@app.route('/notInterested', methods=['POST'])
def not_interested():
    club_id = request.form['clubId']
    club = Club.query.filter_by(name=club_id).first()
    if not club:
        return jsonify({'error': 'Club not found'}), 400
    if club in current_user.clubs:
        current_user.clubs.remove(club)
    db.session.commit()
    clubs_list = [club.name for club in current_user.clubs]
    return jsonify({'joined_clubs': clubs_list})

def format_club_name(club_name):
    # Replace underscores with spaces and capitalize each word
    return ' '.join(word.capitalize() for word in club_name.split('_'))

@app.route('/join', methods=['POST'])
@login_required
def join_club():
    club_id = request.form.get('club_id')
    club = Club.query.get(club_id)

    if club and club not in current_user.clubs:
        current_user.clubs.append(club)
        print("Club added to user's clubs:", current_user.clubs)  # Debug message
        db.session.add(current_user)
        db.session.commit()

    return redirect(url_for('community'))

@app.route('/community')
def community():
    clubs = [
        # Add the names of clubs and organizations here
        {'name': 'chess_club'},
        {'name': 'photography_club'},
        # Add more clubs here
    ]
    return render_template('my_community.html', clubs=clubs)

# Sample data for conversations
conversations = {
    "john_doe": [
        {"sender": "John Doe", "message": "Hello there! How are you doing?", "date": "July 24, 2023"},
        {"sender": "You", "message": "Hi John Doe, I'm doing great. Thanks for asking!", "date": "July 25, 2023"},
        {"sender": "John Doe", "message": "That's wonderful to hear! How can I assist you today?", "date": "July 26, 2023"},
    ],
    "golf_club": [
        {"sender": "Golf Club", "message": "Hey there, we have a golf tournament coming up next week. Are you joining?", "date": "July 24, 2023"},
        {"sender": "You", "message": "Hi Golf Club, I would love to join the tournament! Can you share more details?", "date": "July 25, 2023"},
        {"sender": "Golf Club", "message": "Sure! The tournament will be held on August 1st at Green Valley Golf Course. Shotgun start at 8:00 AM. Don't forget to bring your clubs!", "date": "July 26, 2023"},
    ],
    "alice": [
        {"sender": "Alice", "message": "Hi there! How have you been?", "date": "July 27, 2023"},
        {"sender": "You", "message": "Hello Alice! I've been doing well. How about you?", "date": "July 28, 2023"},
        {"sender": "Alice", "message": "I'm good too, thanks! By the way, do you want to join us for a movie night this Friday?", "date": "July 29, 2023"},
        {"sender": "You", "message": "That sounds fun! Count me in!", "date": "July 30, 2023"},
    ],
    "soccer_club": [
        {"sender": "Soccer Club", "message": "Hey, we have a soccer match this weekend. Are you playing?", "date": "July 31, 2023"},
        {"sender": "You", "message": "Hi Soccer Club, I'll be there for the match! What time should I arrive?", "date": "August 1, 2023"},
        {"sender": "Soccer Club", "message": "Great! The match starts at 3:00 PM. See you on the field!", "date": "August 2, 2023"},
    ],
}

@app.route('/messages')
def messages():
    return render_template('messages.html', conversations=conversations)

@app.route('/view_conversation/<sender>', methods=['GET', 'POST'])
def view_conversation(sender):
    if request.method == 'POST':
        message_content = request.form['message_content'].strip()
        if message_content:
            date = "July 30, 2023"  # You can modify this to get the current date dynamically
            new_message = {"sender": "You", "message": message_content, "date": date}
            conversations[sender].append(new_message)

    conversation = conversations.get(sender, [])
    return render_template('view_conversation.html', sender=sender, conversation=conversation)

# Sample data for clubs
clubs = [
    {"name": "chess_club"},
    {"name": "photography_club"},
    {"name": "music_society"},
]

# View function for the mycommunity page
@app.route('/my_community')
def my_community():
    return render_template('my_community.html', clubs=clubs)

# View function for dropping out of a club
@app.route('/drop_out', methods=['POST'])
def drop_out():
    data = request.get_json()
    club_name = data.get('clubName')
    if club_name:
        for club in clubs:
            if club['name'] == club_name:
                clubs.remove(club)
                return jsonify({"message": f"You have been dropped out of {club_name.replace('_', ' ').title()}."})
    return jsonify({"message": "Club not found."})

# Sample data for notifications
notifications = [
    {"id": 1, "title": "Club Meeting", "message": "The Chess Club is having a meeting on July 30th."},
    {"id": 2, "title": "Photography Exhibition", "message": "The Photography Club is organizing an exhibition on August 5th."},
    {"id": 3, "title": "Music Concert", "message": "Don't miss the Music Society's concert on August 10th."},
]


# Route for the notifications page
@app.route('/notifications')
def view_notifications():
    return render_template('notifications.html', notifications=notifications)

if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
