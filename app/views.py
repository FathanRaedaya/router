
''' * Routes:
 *
 * / : Main page. Requires user login (except for admins, redirected to /admin). Displays users, payment options, followers, following lists.
 * 
 * /map : Map display. Requires subscription. Loads GPX files from the current user and shared routes from friends. 
 *
 * /cancel : Cancels the user's active subscription.
 *
 * /update_plan/<int:plan_id> : Updates the user's subscription plan.
 *
 * /follow/<int:friend_id> : Handles the action of following another user.
 *
 * /unfollow/<int:friend_id> : Handles unfollowing a user. 
 *
 * /reject/<int:friend_id> : Allows the user to reject a pending follow request.
 *
 * /login : Processes user login requests.
 *
 * /register : Handles new user registration.
 *
 * /logout : Logs the current user out.
 *
 * /plans : Displays available subscription plans.
 *
 * /payment/<int:plan> : Handles payment processing for the selected plan, storing Fernet encrypted payment info. 
 *
 * /users : Displays a list of users. Allows following/unfollowing (excluding admin).
 *
 * /user/<int:user_id> : Displays a specific user's profile.
 *
 * /upload : Route to handle GPX file uploads. Requires a subscription.
 *
 * /download/<int:file_id> : Allows downloading a specific, previously uploaded GPX file. Requires subscription.
 *
 * /admin : Admin panel (requires admin role). Displays users, subscription activity, etc. 
 *  
 * /profile : Profile management. Allows changing username/password, deleting uploaded routes. 
 *
 * /change_username : Processes username change requests.
 *
 * /change_password : Processes password change requests.
 *
 * /delete_account : Handles user account deletion. 
 *
 * /delete_route/<int:route_id> : Deletes a specific uploaded GPX route.
 *
 * /delete_all_routes : Deletes all uploaded GPX routes for the current user. 
 */
'''

from app import app, models, db
from app.models import User, friendship, PaymentMethod, MapData
from flask import render_template, request, redirect, url_for, \
    jsonify, flash, send_from_directory
from flask_login import \
    LoginManager, login_required, logout_user, current_user, login_user

from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os
from .forms import LoginForm, RegisterForm, PaymentForm, UploadForm,\
    ChangeUsernameForm, ChangePasswordForm
from .auth import admin_not_allowed, admin_required, subscription_required
from werkzeug.exceptions import NotFound
from cryptography.fernet import Fernet

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Load user
@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))


key = "SGFzc2FuSXNBR2VuaXVzTW9oYWJJc0R1bWJTZWNyZXQ="

# Create a Fernet instance
encryptor = Fernet(key)


@app.route('/')
@admin_not_allowed  # This flag is used to limit admin access (only use /admin)
def index():
    users = models.User.query.all()
    form = PaymentForm()

    # Checks if the user is logged in, if so they're redirected to main page
    if not current_user.is_authenticated:
        return render_template('main.html', users=users, form=form)

    following = current_user.friends.all()
    followers = models.User.query.filter(models.User.friends.any
                                         (id=current_user.id)).all()

    is_subscribed = PaymentMethod.query.filter_by(user_id=current_user.id).\
        first()

    # If user is subscribed we send the plan to the template
    if is_subscribed:
        plan = is_subscribed.subscription
        return render_template('main.html', users=users, following=following,
                               followers=followers, form=form,
                               is_subscribed=is_subscribed, plan=plan)

    return render_template('main.html', users=users, following=following,
                           followers=followers, form=form)


@app.route('/map', methods=['GET', 'POST'])
@subscription_required  # This is used for routes that require subscription
@admin_not_allowed
def map():
    upload = UploadForm()
    choices = [(friend.id, friend.username) for friend in
               current_user.friends.all() if current_user in
               friend.friends.filter(friendship.c.friend_id ==
                                     current_user.id)]
    choices.insert(0, ("-1", "All"))
    choices.insert(0, ("-2", "Only Me"))
    upload.share.choices = choices
    # Loop through all gpx files for current user to give as options
    gpx_files = [file for file in models.MapData.query.filter_by(
        user_id=current_user.id)]
    gpx_files_p = [(file.file_path, file.date, current_user.username, file.description) for file in gpx_files]
    following = current_user.friends.all()
    friends = []
    # Loop through friends to add to friends list
    for friend in following:
        if current_user in friend.friends.filter(
                friendship.c.friend_id == current_user.id):
            friends.append(friend)
    rank = PaymentMethod.query.filter_by(user_id=current_user.id).first().\
        subscription
    user = current_user

    if request.method == 'POST':
        selected_friends = request.json.get('friends', [])
        files_for_friend = []
        for friend in selected_friends:
            for file in models.MapData.query.filter_by(user_id=friend):
                # If file is shared with all friends
                if file.share == ["-1"]:
                    files_for_friend.append((file.file_path, file.date,\
                        models.User.query.filter_by(id=friend).first().username, file.description))
                # If file is shared with nobody
                elif file.share == ["-2"]:
                    continue
                # if specific friends selected and current user in list
                elif str(current_user.id) in file.share:
                    files_for_friend.append((file.file_path, file.date,\
                        models.User.query.filter_by(id=friend).first().username, file.description))
            gpx_files_p.extend(files_for_friend)
        response_data = {
            'success': True,
            'gpx_files': list(gpx_files_p)
        }
        return jsonify(response_data)

    # Depending on the users rank, we limit the amount of gpx files
    if rank == 1:
        gpx_files = gpx_files[:5]
    elif rank == 2:
        gpx_files = gpx_files[:25]

    return render_template('map.html', gpx_files=gpx_files_p, form=upload,
                           friends=friends, files=gpx_files, user=user)


@app.route('/cancel', methods=["GET", "POST"])
@subscription_required
@admin_not_allowed
def cancel():
    user = current_user
    payment = PaymentMethod.query.filter_by(user_id=user.id).first()
    db.session.delete(payment)  # Remove payment method from db to cancel
    db.session.commit()

    return redirect(url_for("index"))


@app.route('/update_plan/<int:plan_id>')
@subscription_required
@admin_not_allowed
def update_plan(plan_id):
    user = current_user
    payment = PaymentMethod.query.filter_by(user_id=user.id).first()
    payment.subscription = plan_id
    db.session.commit()
    return redirect(url_for("index"))


# Route which allows users to follow others
@app.route('/follow/<int:friend_id>')
@admin_not_allowed
def follow(friend_id):
    friend = models.User.query.filter_by(id=friend_id).first()
    if friend in current_user.friends.all():
        print("Already following")
        return redirect(url_for('users'))
    if friend == current_user:
        print("Can't follow yourself")
        return redirect(url_for('users'))
    if friend.admin:
        print("Can't follow admin")
        return redirect(url_for('users'))

    current_user.friends.append(friend)
    db.session.commit()
    return redirect(url_for('users'))


# Route which allows users to unfollow others
@app.route('/unfollow/<int:friend_id>')
@admin_not_allowed
def unfollow(friend_id):
    friend = models.User.query.filter_by(id=friend_id).first()
    if friend not in current_user.friends.all():
        print("Not following")
        return redirect(url_for('users'))
    if friend == current_user:
        print("Can't unfollow yourself")
        return redirect(url_for('users'))
    if friend.admin:
        print("Can't unfollow admin")
        return redirect(url_for('users'))
    if friend in current_user.friends.all():
        if current_user not in friend.friends.all():
            current_user.friends.remove(friend)
            db.session.commit()
            return redirect(url_for('users'))
    current_user.friends.remove(friend)
    friend.friends.remove(current_user)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/reject/<int:friend_id>')
@admin_not_allowed
def reject(friend_id):
    friend = models.User.query.filter_by(id=friend_id).first()
    friend.friends.remove(current_user)
    db.session.commit()
    return redirect(url_for('index'))


# Route which process login requests
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_pw(form.pw.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            # Return error variable to be rendered by template
            return render_template('login.html', form=form, error='Invalid \
                                   username or password')
    return render_template('login.html', form=form)


# Registration page route
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        email = request.form["email"]
        fName = request.form["fName"]
        lName = request.form["lName"]
        username = request.form["username"]
        pw = request.form["pw"]
        pw2 = request.form["pw2"]

        # Multiple serverside validation checks which return error variable
        if len(list(models.User.query.filter_by(username=username))) != 0:
            return render_template("register.html", title="Register",
                                   form=form, error="Username already in use!")

        elif len(list(models.User.query.filter_by(email=email))):
            return render_template("register.html", title="Register",
                                   form=form, error="Email already in use!")

        elif pw != pw2:
            return render_template("register.html", title="Register",
                                   form=form, error="Passwords must match!")

        pw_hash = generate_password_hash(pw)  # Encrypt password before db
        new_user = models.User(
            email=email, fName=fName, lName=lName,
            pw_hash=pw_hash, username=username
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html", title="Register", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/plans', methods=["GET", "POST"])
@admin_not_allowed
def plans():
    return render_template("plans.html", title="Plans")


# Route to process payment detail submission and assigning plan
@app.route('/payment/<int:plan>', methods=["GET", "POST"])
@admin_not_allowed
def payment(plan):
    user = current_user

    if request.method == "POST":
        # Retrieve form data
        fName = request.form["fName"]
        lName = request.form["lName"]
        cardNum = request.form["cardNum"]
        expirationM = request.form["expirationM"]
        expirationY = request.form["expirationY"]
        cvv = request.form["cvv"]
        country = request.form["country"]
        city = request.form["city"]
        stAddr = request.form["stAddr"]
        stAddr2 = request.form["stAddr2"]
        pc = request.form["pc"]

        encrypted_cardNum = encryptor.encrypt(cardNum.encode())
        encrypted_cvv = encryptor.encrypt(cvv.encode())
        encrypted_month = encryptor.encrypt(expirationM.encode())
        encrypted_year = encryptor.encrypt(expirationY.encode())

        payment_method = models.PaymentMethod(
            fName=fName, lName=lName, cardNum=encrypted_cardNum,
            expirationM=encrypted_month, expirationY=encrypted_year,
            cvv=encrypted_cvv, country=country, city=city, stAddr=stAddr,
            stAddr2=stAddr2, pc=pc, subscription=plan, user_id=user.id
        )
        db.session.add(payment_method)
        db.session.commit()

    return redirect(url_for("index"))


# Route that loops through all users and returns them to be rendered
@app.route('/users')
@admin_not_allowed
def users():
    all_users = User.query.filter(User.id != current_user.id).all()
    users_info = []

    is_subscribed = PaymentMethod.query.filter_by(user_id=current_user.id).\
        first()

    for user in all_users:

        if user.admin:
            continue

        is_following = current_user.friends.filter(friendship.c.friend_id ==
                                                   user.id).count() > 0
        followed_by = user.friends.filter(friendship.c.friend_id ==
                                          current_user.id).count() > 0
        users_info.append({
            'user': user,
            'is_following': is_following,
            'followed_by': followed_by
        })

    if is_subscribed:
        return render_template('users.html', users_info=users_info,
                               is_subscribed=is_subscribed)

    return render_template('users.html', users_info=users_info)


@app.route('/user/<int:user_id>')
@admin_not_allowed
def user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return redirect(url_for('index'))
    is_following = current_user.friends.filter(friendship.c.friend_id ==
                                               user.id).count() > 0
    followed_by = user.friends.filter(friendship.c.friend_id ==
                                      current_user.id).count() > 0
    return render_template('user.html', user=user, is_following=is_following,
                           followed_by=followed_by)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] == "gpx"


# Route which allows gpx files to be uploaded by the user
@app.route('/upload', methods=["GET", "POST"])
@subscription_required
@admin_not_allowed
def upload():
    form = UploadForm()
    route = form.route.data
    share = request.form.getlist("share")
    following = current_user.friends.all()
    friends = []
    for friend in following:
        if current_user in friend.friends.filter(friendship.c.friend_id ==
                                                 current_user.id):
            friends.append(friend)
    description = request.form["description"]
    # Filename is done uniquely by utilising datetime
    unique_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    original_filename = secure_filename(route.filename)
    if allowed_file(original_filename):
        filename = unique_filename + "-" + str(current_user.id) + ".gpx"
        file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            app.config['UPLOAD_FOLDER'], filename
        )
        route.save(file_path)
        new_route = models.MapData(
            file_path=app.config['UPLOAD_FOLDER']+"/"+filename,
            description=description,
            share=share, user_id=current_user.id
        )
        db.session.add(new_route)
        db.session.commit()
        return redirect(url_for('map'))
    else:
        flash('Please Upload a GPX File', 'danger')


# Route which allows users to download their uploaded gpx files
@app.route('/download/<int:file_id>', methods=["GET", "POST"])
@subscription_required
def download(file_id):
    file = MapData.query.filter_by(id=file_id).first()
    if not file:
        return redirect(url_for('map'))

    c = 0

    for i in range(len(file.file_path)):
        if file.file_path[i].isnumeric():
            c = i
            break

    file_name = file.file_path[c:]

    try:
        return send_from_directory(
            app.config['UPLOAD_FOLDER'], file_name, as_attachment=True
        )
    except NotFound:
        # if the file doesnt exist in the directory, handle the error
        flash("File not found.", "error")
        return redirect(url_for('map'))


# Route for admins to access and see all data which is returned
@app.route('/admin')
@admin_required
def admin():
    user_count = models.User.query.count()
    users = models.User.query.all()
    weekly = models.PaymentMethod.query.filter_by(subscription=1)
    monthly = models.PaymentMethod.query.filter_by(subscription=2)
    yearly = models.PaymentMethod.query.filter_by(subscription=3)
    weekly = [str(payment.date) for payment in weekly]
    monthly = [str(payment.date) for payment in monthly]
    yearly = [str(payment.date) for payment in yearly]

    return render_template('admin.html', users=users, user_count=user_count,
                           weekly=weekly, monthly=monthly, yearly=yearly)


# Route which renderes profile management page
@app.route('/profile')
@admin_not_allowed
def profile():
    is_subscribed = PaymentMethod.query.filter_by(user_id=current_user.id).\
        first()
    userForm = ChangeUsernameForm()
    passForm = ChangePasswordForm()
    mapdata = MapData.query.filter_by(user_id=current_user.id).all()

    return render_template('profile.html', is_subscribed=is_subscribed,
                           userForm=userForm, passForm=passForm,
                           mapdata=mapdata)


# Functions below all are used in profile management
@app.route('/change_username', methods=["POST"])
@admin_not_allowed
def change_username():
    form = ChangeUsernameForm()
    if form.validate_on_submit():
        new_username = form.username1.data
        current_user.username = new_username
        db.session.commit()
    else:
        flash("Invalid form data", "error")
        print(form.errors)
    return redirect(url_for('profile'))


@app.route('/change_password', methods=["POST"])
@admin_not_allowed
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        new_password = form.pw.data
        current_user.pw_hash = generate_password_hash(new_password)
        db.session.commit()
    else:
        flash("Invalid form data", "error")
        print(form.errors)
    return redirect(url_for('profile'))


@app.route('/delete_account')
@admin_not_allowed
def delete_account():
    user = current_user
    logout_user()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('login'))


@app.route('/delete_route/<int:route_id>')
@admin_not_allowed
def delete_route(route_id):
    route = MapData.query.filter_by(id=route_id).first()
    os.remove(os.path.join(os.getcwd(), "app", route.file_path))
    db.session.delete(route)
    db.session.commit()
    return redirect(url_for('profile'))


@app.route('/delete_all_routes')
@admin_not_allowed
def delete_all_routes():
    routes = MapData.query.filter_by(user_id=current_user.id).all()
    for route in routes:
        os.remove(os.path.join(os.getcwd(), "app", route.file_path))
        db.session.delete(route)
    db.session.commit()
    return redirect(url_for('profile'))
