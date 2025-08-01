from src.models.user import db
from datetime import datetime
import json

class GameState(db.Model):
    """Model for saving and loading game states"""
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    state_name = db.Column(db.String(100), nullable=False)
    state_data = db.Column(db.Text, nullable=False)  # JSON serialized game state
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_auto_save = db.Column(db.Boolean, default=False)  # Auto-saves vs manual saves
    phase = db.Column(db.String(20), nullable=False)  # day/night
    day_number = db.Column(db.Integer, default=1)
    
    def __init__(self, **kwargs):
        super(GameState, self).__init__(**kwargs)
    
    def set_state_data(self, data):
        """Set state data from dictionary"""
        self.state_data = json.dumps(data, default=str)
    
    def get_state_data(self):
        """Get state data as dictionary"""
        try:
            return json.loads(self.state_data)
        except:
            return {}
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'game_id': self.game_id,
            'state_name': self.state_name,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'is_auto_save': self.is_auto_save,
            'phase': self.phase,
            'day_number': self.day_number,
            'state_preview': self.get_state_preview()
        }
    
    def get_state_preview(self):
        """Get a preview of the game state for display"""
        data = self.get_state_data()
        return {
            'player_count': len(data.get('players', [])),
            'alive_count': len([p for p in data.get('players', []) if p.get('is_alive', True)]),
            'phase': self.phase,
            'day': self.day_number
        }

class GameAction(db.Model):
    """Model for tracking individual game actions for undo/redo"""
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # vote, nominate, kill, etc.
    action_data = db.Column(db.Text, nullable=False)  # JSON serialized action data
    performed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    performed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_undone = db.Column(db.Boolean, default=False)
    undo_reason = db.Column(db.String(200), nullable=True)
    phase = db.Column(db.String(20), nullable=False)
    day_number = db.Column(db.Integer, default=1)
    
    def set_action_data(self, data):
        """Set action data from dictionary"""
        self.action_data = json.dumps(data, default=str)
    
    def get_action_data(self):
        """Get action data as dictionary"""
        try:
            return json.loads(self.action_data)
        except:
            return {}
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'game_id': self.game_id,
            'action_type': self.action_type,
            'action_data': self.get_action_data(),
            'performed_by': self.performed_by,
            'performed_at': self.performed_at.isoformat(),
            'is_undone': self.is_undone,
            'undo_reason': self.undo_reason,
            'phase': self.phase,
            'day_number': self.day_number
        }

class GameHistory(db.Model):
    """Model for storing complete game history and replay data"""
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    history_data = db.Column(db.Text, nullable=False)  # Complete game history
    final_state = db.Column(db.Text, nullable=False)  # Final game state
    winner_team = db.Column(db.String(20), nullable=True)  # good/evil
    game_duration = db.Column(db.Integer, nullable=True)  # Duration in seconds
    total_days = db.Column(db.Integer, default=1)
    total_executions = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_history_data(self, data):
        """Set history data from dictionary"""
        self.history_data = json.dumps(data, default=str)
    
    def get_history_data(self):
        """Get history data as dictionary"""
        try:
            return json.loads(self.history_data)
        except:
            return {}
    
    def set_final_state(self, data):
        """Set final state data from dictionary"""
        self.final_state = json.dumps(data, default=str)
    
    def get_final_state(self):
        """Get final state data as dictionary"""
        try:
            return json.loads(self.final_state)
        except:
            return {}
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'game_id': self.game_id,
            'winner_team': self.winner_team,
            'game_duration': self.game_duration,
            'total_days': self.total_days,
            'total_executions': self.total_executions,
            'created_at': self.created_at.isoformat(),
            'history_preview': self.get_history_preview()
        }
    
    def get_history_preview(self):
        """Get a preview of the game history"""
        history = self.get_history_data()
        final_state = self.get_final_state()
        
        return {
            'total_actions': len(history.get('actions', [])),
            'final_player_count': len(final_state.get('players', [])),
            'winner_team': self.winner_team,
            'duration_minutes': self.game_duration // 60 if self.game_duration else 0
        }

# Game state management utility functions
class GameStateManager:
    """Utility class for managing game state operations"""
    
    @staticmethod
    def save_game_state(game, state_name, created_by_id, is_auto_save=False):
        """Save current game state"""
        from src.models.game import Game
        from src.models.player import Player
        
        # Collect current game state
        players_data = []
        for player in game.players:
            player_data = player.to_dict(include_sensitive=True)
            players_data.append(player_data)
        
        state_data = {
            'game_info': {
                'id': game.id,
                'phase': game.phase,
                'day_number': game.day_number,
                'status': game.status,
                'settings': game.get_settings()
            },
            'players': players_data,
            'script': game.script.to_dict() if game.script else None,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Create game state record
        game_state = GameState(
            game_id=game.id,
            state_name=state_name,
            created_by=created_by_id,
            is_auto_save=is_auto_save,
            phase=game.phase,
            day_number=game.day_number
        )
        game_state.set_state_data(state_data)
        
        db.session.add(game_state)
        db.session.commit()
        
        return game_state
    
    @staticmethod
    def load_game_state(game_state_id):
        """Load a saved game state"""
        game_state = GameState.query.get(game_state_id)
        if not game_state:
            return None
        
        return game_state.get_state_data()
    
    @staticmethod
    def auto_save_game(game):
        """Create an automatic save point"""
        state_name = f"Auto-save {game.phase} Day {game.day_number}"
        return GameStateManager.save_game_state(
            game, 
            state_name, 
            game.host_id, 
            is_auto_save=True
        )
    
    @staticmethod
    def record_action(game, action_type, action_data, performed_by_id):
        """Record a game action for undo/redo functionality"""
        action = GameAction(
            game_id=game.id,
            action_type=action_type,
            performed_by=performed_by_id,
            phase=game.phase,
            day_number=game.day_number
        )
        action.set_action_data(action_data)
        
        db.session.add(action)
        db.session.commit()
        
        return action
    
    @staticmethod
    def undo_action(action_id, undo_reason=""):
        """Mark an action as undone"""
        action = GameAction.query.get(action_id)
        if action and not action.is_undone:
            action.is_undone = True
            action.undo_reason = undo_reason
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_game_actions(game_id, limit=50):
        """Get recent game actions"""
        return GameAction.query.filter_by(
            game_id=game_id,
            is_undone=False
        ).order_by(GameAction.performed_at.desc()).limit(limit).all()
    
    @staticmethod
    def create_game_history(game):
        """Create a complete game history record when game ends"""
        from src.models.game import Game
        
        # Collect all actions
        actions = GameAction.query.filter_by(game_id=game.id).order_by(GameAction.performed_at).all()
        actions_data = [action.to_dict() for action in actions]
        
        # Collect final state
        final_state = GameStateManager.save_game_state(
            game, 
            "Final State", 
            game.host_id
        ).get_state_data()
        
        # Calculate game statistics
        game_duration = None
        if game.started_at and game.ended_at:
            game_duration = int((game.ended_at - game.started_at).total_seconds())
        
        total_executions = len([a for a in actions if a.action_type == 'execute'])
        
        # Create history record
        history = GameHistory(
            game_id=game.id,
            winner_team=game.winner_team,
            game_duration=game_duration,
            total_days=game.day_number,
            total_executions=total_executions
        )
        
        history_data = {
            'actions': actions_data,
            'game_info': final_state['game_info'],
            'script': final_state['script']
        }
        
        history.set_history_data(history_data)
        history.set_final_state(final_state)
        
        db.session.add(history)
        db.session.commit()
        
        return history

