from src.models.user import db
from datetime import datetime
import json

class Script(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_official = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    player_count_min = db.Column(db.Integer, default=5)
    player_count_max = db.Column(db.Integer, default=15)
    version = db.Column(db.String(20), default='1.0')
    
    # Relationships
    script_roles = db.relationship('ScriptRole', backref='script', lazy=True, cascade='all, delete-orphan')
    games = db.relationship('Game', backref='script', lazy=True)

    def get_roles(self):
        """Get all roles in this script"""
        return [sr.role for sr in self.script_roles]

    def get_roles_by_type(self, role_type):
        """Get roles of specific type"""
        return [sr.role for sr in self.script_roles if sr.role.type == role_type]

    def get_townsfolk(self):
        """Get townsfolk roles"""
        return self.get_roles_by_type('townsfolk')

    def get_outsiders(self):
        """Get outsider roles"""
        return self.get_roles_by_type('outsider')

    def get_minions(self):
        """Get minion roles"""
        return self.get_roles_by_type('minion')

    def get_demons(self):
        """Get demon roles"""
        return self.get_roles_by_type('demon')

    def calculate_distribution(self, player_count):
        """Calculate role distribution for given player count"""
        if player_count < 5 or player_count > 15:
            return None
        
        # Standard Blood on the Clocktower distribution
        distributions = {
            5: {'townsfolk': 3, 'outsider': 0, 'minion': 1, 'demon': 1},
            6: {'townsfolk': 3, 'outsider': 1, 'minion': 1, 'demon': 1},
            7: {'townsfolk': 5, 'outsider': 0, 'minion': 1, 'demon': 1},
            8: {'townsfolk': 5, 'outsider': 1, 'minion': 1, 'demon': 1},
            9: {'townsfolk': 5, 'outsider': 2, 'minion': 1, 'demon': 1},
            10: {'townsfolk': 7, 'outsider': 0, 'minion': 2, 'demon': 1},
            11: {'townsfolk': 7, 'outsider': 1, 'minion': 2, 'demon': 1},
            12: {'townsfolk': 7, 'outsider': 2, 'minion': 2, 'demon': 1},
            13: {'townsfolk': 9, 'outsider': 0, 'minion': 3, 'demon': 1},
            14: {'townsfolk': 9, 'outsider': 1, 'minion': 3, 'demon': 1},
            15: {'townsfolk': 9, 'outsider': 2, 'minion': 3, 'demon': 1}
        }
        
        return distributions.get(player_count)

    def can_support_player_count(self, player_count):
        """Check if script can support the given player count"""
        distribution = self.calculate_distribution(player_count)
        if not distribution:
            return False
        
        # Check if we have enough roles of each type
        for role_type, needed in distribution.items():
            available = len(self.get_roles_by_type(role_type))
            if available < needed:
                return False
        
        return True

    def __repr__(self):
        return f'<Script {self.name}>'

    def to_dict(self, include_roles=False):
        """Convert script to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'author': self.author,
            'description': self.description,
            'is_official': self.is_official,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'player_count_min': self.player_count_min,
            'player_count_max': self.player_count_max,
            'version': self.version,
            'role_count': len(self.script_roles)
        }
        
        if include_roles:
            data['roles'] = [sr.role.to_dict() for sr in self.script_roles]
            data['roles_by_type'] = {
                'townsfolk': [r.to_dict() for r in self.get_townsfolk()],
                'outsider': [r.to_dict() for r in self.get_outsiders()],
                'minion': [r.to_dict() for r in self.get_minions()],
                'demon': [r.to_dict() for r in self.get_demons()]
            }
        
        return data


class ScriptRole(db.Model):
    """Many-to-many relationship between Scripts and Roles"""
    id = db.Column(db.Integer, primary_key=True)
    script_id = db.Column(db.Integer, db.ForeignKey('script.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate role assignments
    __table_args__ = (db.UniqueConstraint('script_id', 'role_id', name='unique_script_role'),)

    def __repr__(self):
        return f'<ScriptRole {self.script.name} - {self.role.name}>'

    def to_dict(self):
        """Convert script role to dictionary"""
        return {
            'id': self.id,
            'script_id': self.script_id,
            'role_id': self.role_id,
            'script_name': self.script.name,
            'role_name': self.role.name,
            'added_at': self.added_at.isoformat() if self.added_at else None
        }


# Default Trouble Brewing script
TROUBLE_BREWING_SCRIPT = {
    'name': 'Trouble Brewing',
    'author': 'The Pandemonium Institute',
    'description': 'The original Blood on the Clocktower script. A perfect introduction to the game with straightforward roles and clear interactions.',
    'is_official': True,
    'player_count_min': 5,
    'player_count_max': 15,
    'version': '1.0',
    'roles': [
        # Townsfolk
        'Washerwoman', 'Librarian', 'Investigator', 'Chef', 'Empath',
        'Fortune Teller', 'Undertaker', 'Monk', 'Ravenkeeper', 'Virgin',
        'Slayer', 'Soldier', 'Mayor',
        # Outsiders
        'Drunk', 'Recluse', 'Saint', 'Butler',
        # Minions
        'Poisoner', 'Spy', 'Scarlet Woman', 'Baron',
        # Demons
        'Imp'
    ]
}

