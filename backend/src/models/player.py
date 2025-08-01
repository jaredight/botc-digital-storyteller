from src.models.user import db
from datetime import datetime
import json

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    position = db.Column(db.Integer, nullable=False)  # Seating position (0-based)
    is_alive = db.Column(db.Boolean, default=True)
    is_ready = db.Column(db.Boolean, default=False)
    votes_remaining = db.Column(db.Integer, default=1)  # Dead players get 1 vote
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    died_at = db.Column(db.DateTime, nullable=True)
    abilities_used = db.Column(db.Text, default='[]')  # JSON array of used abilities
    status_effects = db.Column(db.Text, default='[]')  # JSON array of status effects
    notes = db.Column(db.Text, default='')  # Host notes about this player
    
    # Relationships
    votes_cast = db.relationship('Vote', foreign_keys='Vote.voter_id', backref='voter', lazy=True)
    votes_received = db.relationship('Vote', foreign_keys='Vote.target_id', backref='target', lazy=True)
    actions_performed = db.relationship('PlayerAction', foreign_keys='PlayerAction.player_id', backref='player', lazy=True)

    @property
    def username(self):
        """Get the player's username"""
        from src.models.user import User
        user = User.query.get(self.user_id)
        return user.username if user else 'Unknown'

    @property
    def role_name(self):
        """Get the player's role name"""
        from src.models.role import Role
        role = Role.query.get(self.role_id) if self.role_id else None
        return role.name if role else 'No Role'

    @property
    def team(self):
        """Get the player's team"""
        from src.models.role import Role
        role = Role.query.get(self.role_id) if self.role_id else None
        return role.team if role else 'unknown'

    @property
    def role(self):
        """Get the player's role object"""
        from src.models.role import Role
        return Role.query.get(self.role_id) if self.role_id else None

    def is_good(self):
        """Check if player is on good team"""
        return self.team in ['townsfolk', 'outsider']

    def is_evil(self):
        """Check if player is on evil team"""
        return self.team in ['minion', 'demon']

    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)
        if self.position is None:
            # Auto-assign position based on existing players in game
            existing_positions = [p.position for p in Player.query.filter_by(game_id=self.game_id).all()]
            self.position = 0
            while self.position in existing_positions:
                self.position += 1

    def get_abilities_used(self):
        """Get used abilities as list"""
        try:
            return json.loads(self.abilities_used)
        except:
            return []

    def set_abilities_used(self, abilities_list):
        """Set used abilities from list"""
        self.abilities_used = json.dumps(abilities_list)

    def add_ability_used(self, ability_name, night_number=None):
        """Add an ability to the used list"""
        abilities = self.get_abilities_used()
        ability_record = {
            'ability': ability_name,
            'night': night_number or self.game.phase,
            'timestamp': datetime.utcnow().isoformat()
        }
        abilities.append(ability_record)
        self.set_abilities_used(abilities)

    def get_status_effects(self):
        """Get status effects as list"""
        try:
            return json.loads(self.status_effects)
        except:
            return []

    def set_status_effects(self, effects_list):
        """Set status effects from list"""
        self.status_effects = json.dumps(effects_list)

    def add_status_effect(self, effect_name, duration=None, source=None):
        """Add a status effect"""
        effects = self.get_status_effects()
        effect = {
            'name': effect_name,
            'duration': duration,
            'source': source,
            'applied_at': datetime.utcnow().isoformat()
        }
        effects.append(effect)
        self.set_status_effects(effects)

    def remove_status_effect(self, effect_name):
        """Remove a status effect by name"""
        effects = self.get_status_effects()
        effects = [e for e in effects if e.get('name') != effect_name]
        self.set_status_effects(effects)

    def has_status_effect(self, effect_name):
        """Check if player has a specific status effect"""
        effects = self.get_status_effects()
        return any(e.get('name') == effect_name for e in effects)

    def kill(self, cause='execution'):
        """Kill the player"""
        self.is_alive = False
        self.died_at = datetime.utcnow()
        self.votes_remaining = 1 if self.game.get_settings().get('house_rules', {}).get('allow_dead_vote', True) else 0

    def resurrect(self):
        """Resurrect the player"""
        self.is_alive = True
        self.died_at = None
        self.votes_remaining = 1

    def can_vote(self):
        """Check if player can vote"""
        return self.votes_remaining > 0

    def cast_vote(self, target_player_id=None):
        """Cast a vote (decrements remaining votes)"""
        if self.can_vote():
            self.votes_remaining -= 1
            return True
        return False

    def reset_votes(self):
        """Reset vote count for new day"""
        if self.is_alive:
            self.votes_remaining = 1
        elif self.game.get_settings().get('house_rules', {}).get('allow_dead_vote', True):
            self.votes_remaining = 1
        else:
            self.votes_remaining = 0

    def get_neighbors(self):
        """Get neighboring players in seating order"""
        all_players = sorted(self.game.players, key=lambda p: p.position)
        player_count = len(all_players)
        
        if player_count <= 1:
            return {'left': None, 'right': None}
        
        current_index = next(i for i, p in enumerate(all_players) if p.id == self.id)
        
        left_neighbor = all_players[(current_index - 1) % player_count]
        right_neighbor = all_players[(current_index + 1) % player_count]
        
        return {'left': left_neighbor, 'right': right_neighbor}

    def get_alive_neighbors(self):
        """Get alive neighboring players"""
        neighbors = self.get_neighbors()
        alive_neighbors = {}
        
        # Find closest alive neighbor to the left
        all_players = sorted([p for p in self.game.players if p.is_alive], key=lambda p: p.position)
        if not all_players:
            return {'left': None, 'right': None}
        
        current_index = next((i for i, p in enumerate(all_players) if p.id == self.id), None)
        if current_index is None:
            return {'left': None, 'right': None}
        
        player_count = len(all_players)
        alive_neighbors['left'] = all_players[(current_index - 1) % player_count]
        alive_neighbors['right'] = all_players[(current_index + 1) % player_count]
        
        return alive_neighbors

    def __repr__(self):
        return f'<Player {self.user.username} in Game {self.game_id}>'

    def to_dict(self, include_sensitive=False, for_player_id=None):
        """Convert player to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'game_id': self.game_id,
            'position': self.position,
            'is_alive': self.is_alive,
            'is_ready': self.is_ready,
            'votes_remaining': self.votes_remaining,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'died_at': self.died_at.isoformat() if self.died_at else None
        }
        
        # Include role information based on permissions
        if self.role:
            if include_sensitive or for_player_id == self.id:
                # Full role info for the player themselves or host
                data['role'] = self.role.to_dict()
            else:
                # Limited role info for other players
                data['role'] = {
                    'id': self.role.id,
                    'name': self.role.name if not self.is_alive else None,  # Only show role if dead
                    'team': self.role.team if not self.is_alive else None
                }
        else:
            data['role'] = None
        
        # Include sensitive information only for host or the player themselves
        if include_sensitive or for_player_id == self.id:
            data['abilities_used'] = self.get_abilities_used()
            data['status_effects'] = self.get_status_effects()
            data['notes'] = self.notes
        
        return data

