''' 
* This file defines database models for a web application, likely one that includes user management, route sharing, and payment features. It also sets up the database and includes logic to create a default admin user if one doesn't exist. 
 *
 * Database Models:
 * * User:
 *    - Stores user credentials (username, hashed password, email), profile details (first/last name), and an admin flag.
 *    - Manages friendships/connections between users.
 * * MapData: 
 *    - Stores information about uploaded routes/maps.
 *    - Includes a description, a flag to control sharing, the file path to the route data, upload date, and a link to the owner (User).
 * * PaymentMethod: 
 *    - Stores user's payment information for subscriptions or other transactions.
 *    - Includes cardholder name, card number, expiration, CVV, billing address, subscription type, and a link to the associated user.
 *
 * Database Setup:
 * * Creates all database tables using SQLAlchemy's `db.create_all()` 
 *
 * Admin User Creation:
 * * Checks if an admin user exists. If not, creates a default 'admin' user with basic credentials for initial setup. 
 '''

from app import db
from app import app
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType


friendship = db.Table('friendship',
                      db.Column('user_id', db.Integer,
                                db.ForeignKey('user.id'), primary_key=True),
                      db.Column('friend_id', db.Integer,
                                db.ForeignKey('user.id'),
                                primary_key=True),
                      db.Column('accepted', db.Boolean, default=False)
                      )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    fName = db.Column(db.String(80), nullable=False)
    lName = db.Column(db.String(80), nullable=False)
    pw_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    admin = db.Column(db.Boolean, default=False)
    friends = db.relationship('User', secondary=friendship,
                              primaryjoin=(id == friendship.c.user_id),
                              secondaryjoin=(id == friendship.c.friend_id),
                              backref=db.backref('friendship', lazy='dynamic'),
                              lazy='dynamic')

    @property
    def pw(self):
        raise AttributeError("password is not a readable attribute")

    @pw.setter
    def password(self, pw):
        self.pw_hash = generate_password_hash(pw)

    def verify_pw(self, pw):
        return check_password_hash(self.pw_hash, pw)

    def check_friend(self, user):
        # check if user is following self and if self is following user
        return self.friends.filter(friendship.c.friend_id ==
                                   user.id).count() > 0 and \
            user.friends.filter(friendship.c.friend_id == self.id).count() > 0


class MapData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), default="No Description")
    share = db.Column(MutableList.as_mutable(PickleType), default=[])
    file_path = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fName = db.Column(db.String(80), nullable=False)
    lName = db.Column(db.String(80), nullable=False)
    cardNum = db.Column(db.String(16), nullable=False)
    expirationM = db.Column(db.Integer, nullable=False)
    expirationY = db.Column(db.Integer, nullable=False)
    cvv = db.Column(db.String(3), nullable=False)
    country = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    stAddr = db.Column(db.String(80), nullable=False)
    stAddr2 = db.Column(db.String(80), nullable=True)
    pc = db.Column(db.String(10), nullable=False)
    subscription = db.Column(db.Integer, nullable=False, default=0)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


with app.app_context():
    db.create_all()

    admin_user = User.query.filter_by(admin=True).first()

    if not admin_user:
        admin = User(username='admin',
                     fName='Admin',
                     lName='User',
                     email='admin@example.com',
                     pw_hash=generate_password_hash('adminpassword'),
                     admin=True)
        db.session.add(admin)
        db.session.commit()
