from src.models.user import db
from datetime import datetime

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    voter_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)  # None for abstain
    vote_type = db.Column(db.String(20), default='execution')  # execution, nomination, etc.
    day_number = db.Column(db.Integer, nullable=False)
    is_valid = db.Column(db.Boolean, default=True)  # Can be invalidated by host
    cast_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        target_name = self.target.user.username if self.target else 'abstain'
        return f'<Vote {self.voter.user.username} -> {target_name}>'

    def to_dict(self):
        """Convert vote to dictionary"""
        return {
            'id': self.id,
            'game_id': self.game_id,
            'voter_id': self.voter_id,
            'voter_username': self.voter.user.username,
            'target_id': self.target_id,
            'target_username': self.target.user.username if self.target else None,
            'vote_type': self.vote_type,
            'day_number': self.day_number,
            'is_valid': self.is_valid,
            'cast_at': self.cast_at.isoformat() if self.cast_at else None
        }


class PlayerAction(db.Model):
    """Track player actions during night phases"""
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # ability name or action type
    target_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)  # Target player if any
    night_number = db.Column(db.Integer, nullable=False)
    phase = db.Column(db.Integer, nullable=False)  # Phase within the night
    action_data = db.Column(db.Text, default='{}')  # JSON data for complex actions
    performed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_valid = db.Column(db.Boolean, default=True)
    
    def get_action_data(self):
        """Get action data as dict"""
        try:
            import json
            return json.loads(self.action_data)
        except:
            return {}

    def set_action_data(self, data_dict):
        """Set action data from dict"""
        import json
        self.action_data = json.dumps(data_dict)

    def __repr__(self):
        target_name = self.target.user.username if self.target else 'no target'
        return f'<PlayerAction {self.player.user.username} {self.action_type} -> {target_name}>'

    def to_dict(self):
        """Convert action to dictionary"""
        return {
            'id': self.id,
            'player_id': self.player_id,
            'player_username': self.player.user.username,
            'game_id': self.game_id,
            'action_type': self.action_type,
            'target_id': self.target_id,
            'target_username': self.target.user.username if self.target else None,
            'night_number': self.night_number,
            'phase': self.phase,
            'action_data': self.get_action_data(),
            'performed_at': self.performed_at.isoformat() if self.performed_at else None,
            'is_valid': self.is_valid
        }


class GameLog(db.Model):
    """Track all game events for history and replay"""
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # phase_change, death, vote, etc.
    event_data = db.Column(db.Text, nullable=False)  # JSON data describing the event
    day_number = db.Column(db.Integer, nullable=True)
    phase = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_event_data(self):
        """Get event data as dict"""
        try:
            import json
            return json.loads(self.event_data)
        except:
            return {}

    def set_event_data(self, data_dict):
        """Set event data from dict"""
        import json
        self.event_data = json.dumps(data_dict)

    def __repr__(self):
        return f'<GameLog {self.game_id} {self.event_type}>'

    def to_dict(self):
        """Convert log entry to dictionary"""
        return {
            'id': self.id,
            'game_id': self.game_id,
            'event_type': self.event_type,
            'event_data': self.get_event_data(),
            'day_number': self.day_number,
            'phase': self.phase,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

    @staticmethod
    def log_event(game_id, event_type, event_data, day_number=None, phase=None):
        """Helper method to log game events"""
        log_entry = GameLog(
            game_id=game_id,
            event_type=event_type,
            day_number=day_number,
            phase=phase
        )
        log_entry.set_event_data(event_data)
        db.session.add(log_entry)
        return log_entry

