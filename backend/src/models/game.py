from src.models.user import db
from datetime import datetime
import json
import secrets
import string

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    join_code = db.Column(db.String(8), unique=True, nullable=False)
    script_id = db.Column(db.Integer, db.ForeignKey('script.id'), nullable=True)
    status = db.Column(db.String(20), default='lobby')  # lobby, night, day, ended
    phase = db.Column(db.Integer, default=0)  # Current phase number
    day_number = db.Column(db.Integer, default=0)  # Current day number
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    winner = db.Column(db.String(20), nullable=True)  # good, evil, or null
    settings = db.Column(db.Text, default='{}')  # JSON string for game settings
    current_nominations = db.Column(db.Text, default='[]')  # JSON array of current nominations
    
    # Relationships
    players = db.relationship('Player', backref='game', lazy=True, cascade='all, delete-orphan')
    game_logs = db.relationship('GameLog', backref='game', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='game', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        if not self.join_code:
            self.join_code = self.generate_join_code()
        if not self.settings:
            self.settings = json.dumps(self.get_default_settings())

    @staticmethod
    def generate_join_code():
        """Generate a unique 6-character join code"""
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            if not Game.query.filter_by(join_code=code).first():
                return code

    def get_default_settings(self):
        """Get default game settings"""
        return {
            'max_players': 15,
            'discussion_time': 600,  # 10 minutes in seconds
            'voting_time': 120,      # 2 minutes in seconds
            'nomination_time': 60,   # 1 minute in seconds
            'house_rules': {
                'allow_dead_vote': True,
                'show_vote_counts': False,
                'allow_whispers': True,
                'auto_advance_phases': True
            }
        }

    def get_settings(self):
        """Get game settings as dict"""
        try:
            return json.loads(self.settings)
        except:
            return self.get_default_settings()

    def set_settings(self, settings_dict):
        """Set game settings from dict"""
        self.settings = json.dumps(settings_dict)

    def get_nominations(self):
        """Get current nominations as list"""
        try:
            return json.loads(self.current_nominations)
        except:
            return []

    def set_nominations(self, nominations_list):
        """Set current nominations from list"""
        self.current_nominations = json.dumps(nominations_list)

    def add_nomination(self, nominator_id, nominee_id):
        """Add a nomination"""
        nominations = self.get_nominations()
        nomination = {
            'nominator_id': nominator_id,
            'nominee_id': nominee_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        nominations.append(nomination)
        self.set_nominations(nominations)

    def clear_nominations(self):
        """Clear all current nominations"""
        self.set_nominations([])

    def get_alive_players(self):
        """Get list of alive players"""
        return [p for p in self.players if p.is_alive]

    def get_dead_players(self):
        """Get list of dead players"""
        return [p for p in self.players if not p.is_alive]

    def get_player_count(self):
        """Get total number of players"""
        return len(self.players)

    def get_alive_count(self):
        """Get number of alive players"""
        return len(self.get_alive_players())

    def can_start(self):
        """Check if game can be started"""
        player_count = self.get_player_count()
        return (self.status == 'lobby' and 
                player_count >= 5 and 
                player_count <= self.get_settings().get('max_players', 15) and
                all(p.is_ready for p in self.players))

    def start_game(self):
        """Start the game"""
        if self.can_start():
            self.status = 'night'
            self.phase = 1
            self.day_number = 0
            self.started_at = datetime.utcnow()
            return True
        return False

    def advance_phase(self):
        """Advance to next phase"""
        if self.status == 'night':
            self.status = 'day'
            self.day_number += 1
        elif self.status == 'day':
            self.status = 'night'
            self.phase += 1
        self.clear_nominations()

    def end_game(self, winner):
        """End the game with specified winner"""
        self.status = 'ended'
        self.winner = winner
        self.ended_at = datetime.utcnow()
        
        # Update player statistics
        for player in self.players:
            player.user.games_played += 1

    def check_win_condition(self):
        """Check if any win condition is met"""
        alive_players = self.get_alive_players()
        
        # Count alive players by team
        alive_good = sum(1 for p in alive_players if p.role and p.role.type in ['townsfolk', 'outsider'])
        alive_evil = sum(1 for p in alive_players if p.role and p.role.type in ['minion', 'demon'])
        
        # Evil wins if good players <= evil players
        if alive_good <= alive_evil:
            return 'evil'
        
        # Good wins if no demons are alive
        alive_demons = sum(1 for p in alive_players if p.role and p.role.type == 'demon')
        if alive_demons == 0:
            return 'good'
        
        return None

    def __repr__(self):
        return f'<Game {self.id} - {self.join_code}>'

    def to_dict(self, include_sensitive=False):
        """Convert game to dictionary"""
        data = {
            'id': self.id,
            'host_id': self.host_id,
            'join_code': self.join_code,
            'script_id': self.script_id,
            'status': self.status,
            'phase': self.phase,
            'day_number': self.day_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'winner': self.winner,
            'settings': self.get_settings(),
            'player_count': self.get_player_count(),
            'alive_count': self.get_alive_count()
        }
        
        if include_sensitive:
            data['nominations'] = self.get_nominations()
            data['players'] = [p.to_dict(include_sensitive=True) for p in self.players]
        else:
            data['players'] = [p.to_dict(include_sensitive=False) for p in self.players]
        
        return data

