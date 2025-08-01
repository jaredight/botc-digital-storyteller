from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    games_played = db.Column(db.Integer, default=0)
    preferences = db.Column(db.Text, default='{}')  # JSON string for user preferences
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    hosted_games = db.relationship('Game', backref='host', lazy=True, foreign_keys='Game.host_id')
    players = db.relationship('Player', backref='user', lazy=True)

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def get_preferences(self):
        """Get user preferences as dict"""
        try:
            return json.loads(self.preferences)
        except:
            return {}

    def set_preferences(self, prefs_dict):
        """Set user preferences from dict"""
        self.preferences = json.dumps(prefs_dict)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'games_played': self.games_played,
            'preferences': self.get_preferences(),
            'is_active': self.is_active
        }
