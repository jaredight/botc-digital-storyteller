from src.models.user import db
import json

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.String(50), unique=True, nullable=False)  # Official character ID like "widow"
    name = db.Column(db.String(100), nullable=False)
    edition = db.Column(db.String(50), default='trouble-brewing')  # trouble-brewing, sects-and-violets, bad-moon-rising, experimental
    team = db.Column(db.String(20), nullable=False)  # townsfolk, outsider, minion, demon, traveller, fabled
    ability = db.Column(db.Text, nullable=False)  # Character ability description
    first_night = db.Column(db.Integer, nullable=True)  # Wake order on first night (0 if doesn't wake)
    first_night_reminder = db.Column(db.Text, default='')  # Reminder text for first night
    other_night = db.Column(db.Integer, nullable=True)  # Wake order on other nights (0 if doesn't wake)
    other_night_reminder = db.Column(db.Text, default='')  # Reminder text for other nights
    reminders = db.Column(db.Text, default='[]')  # JSON array of reminder tokens
    reminders_global = db.Column(db.Text, default='[]')  # JSON array of global reminder tokens
    setup = db.Column(db.Boolean, default=False)  # True if role affects game setup
    image = db.Column(db.Text, default='[]')  # JSON array of image URLs
    special = db.Column(db.Text, default='[]')  # JSON array of special abilities
    jinxes = db.Column(db.Text, default='[]')  # JSON array of jinx interactions
    is_official = db.Column(db.Boolean, default=True)  # True for official roles
    
    # Relationships
    players = db.relationship('Player', backref='role', lazy=True)
    script_roles = db.relationship('ScriptRole', backref='role', lazy=True)

    def get_reminders(self):
        """Get reminder tokens as list"""
        try:
            return json.loads(self.reminders)
        except:
            return []

    def set_reminders(self, reminders_list):
        """Set reminder tokens from list"""
        self.reminders = json.dumps(reminders_list)

    def get_reminders_global(self):
        """Get global reminder tokens as list"""
        try:
            return json.loads(self.reminders_global)
        except:
            return []

    def set_reminders_global(self, reminders_list):
        """Set global reminder tokens from list"""
        self.reminders_global = json.dumps(reminders_list)

    def get_image(self):
        """Get image URLs as list"""
        try:
            return json.loads(self.image)
        except:
            return []

    def set_image(self, image_list):
        """Set image URLs from list"""
        self.image = json.dumps(image_list)

    def get_special(self):
        """Get special abilities as list"""
        try:
            return json.loads(self.special)
        except:
            return []

    def set_special(self, special_list):
        """Set special abilities from list"""
        self.special = json.dumps(special_list)

    def get_jinxes(self):
        """Get jinx interactions as list"""
        try:
            return json.loads(self.jinxes)
        except:
            return []

    def set_jinxes(self, jinxes_list):
        """Set jinx interactions from list"""
        self.jinxes = json.dumps(jinxes_list)

    def is_good(self):
        """Check if role is on the good team"""
        return self.team in ['townsfolk', 'outsider']

    def is_evil(self):
        """Check if role is on the evil team"""
        return self.team in ['minion', 'demon']

    def wakes_first_night(self):
        """Check if role wakes on first night"""
        return self.first_night is not None and self.first_night > 0

    def wakes_other_nights(self):
        """Check if role wakes on other nights"""
        return self.other_night is not None and self.other_night > 0

    def affects_setup(self):
        """Check if role affects game setup"""
        return self.setup

    # Legacy property for backward compatibility
    @property
    def type(self):
        """Legacy property mapping team to type"""
        return self.team

    def __repr__(self):
        return f'<Role {self.name} ({self.team})>'

    def to_dict(self):
        """Convert role to dictionary"""
        return {
            'id': self.id,
            'character_id': self.character_id,
            'name': self.name,
            'edition': self.edition,
            'team': self.team,
            'ability': self.ability,
            'first_night': self.first_night,
            'first_night_reminder': self.first_night_reminder,
            'other_night': self.other_night,
            'other_night_reminder': self.other_night_reminder,
            'reminders': self.get_reminders(),
            'reminders_global': self.get_reminders_global(),
            'setup': self.setup,
            'image': self.get_image(),
            'special': self.get_special(),
            'jinxes': self.get_jinxes(),
            'is_official': self.is_official,
            # Legacy fields for backward compatibility
            'type': self.team,
            'first_night_order': self.first_night,
            'other_nights': self.other_night
        }

# Updated default roles for Trouble Brewing script using official format
DEFAULT_ROLES = [
    # Townsfolk
    {
        'character_id': 'washerwoman',
        'name': 'Washerwoman',
        'edition': 'trouble-brewing',
        'team': 'townsfolk',
        'ability': 'You start knowing that 1 of 2 players is a particular Townsfolk.',
        'first_night': 1,
        'first_night_reminder': 'Show the character token of a Townsfolk in play. Point to two players, one of which is that character.',
        'other_night': 0,
        'other_night_reminder': '',
        'reminders': ['Townsfolk', 'Wrong'],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'librarian',
        'name': 'Librarian',
        'edition': 'trouble-brewing',
        'team': 'townsfolk',
        'ability': 'You start knowing that 1 of 2 players is a particular Outsider. (Or that zero are in play.)',
        'first_night': 2,
        'first_night_reminder': 'Show the character token of an Outsider in play. Point to two players, one of which is that character. Or, if no Outsider is in play, show the "No Outsider" token and shake your head.',
        'other_night': 0,
        'other_night_reminder': '',
        'reminders': ['Outsider', 'Wrong'],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'investigator',
        'name': 'Investigator',
        'edition': 'trouble-brewing',
        'team': 'townsfolk',
        'ability': 'You start knowing that 1 of 2 players is a particular Minion.',
        'first_night': 3,
        'first_night_reminder': 'Show the character token of a Minion in play. Point to two players, one of which is that character.',
        'other_night': 0,
        'other_night_reminder': '',
        'reminders': ['Minion', 'Wrong'],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'chef',
        'name': 'Chef',
        'edition': 'trouble-brewing',
        'team': 'townsfolk',
        'ability': 'You start knowing how many pairs of evil players there are.',
        'first_night': 4,
        'first_night_reminder': 'Show the finger signal (0, 1, 2, etc.) for the number of pairs of evil players.',
        'other_night': 0,
        'other_night_reminder': '',
        'reminders': [],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'empath',
        'name': 'Empath',
        'edition': 'trouble-brewing',
        'team': 'townsfolk',
        'ability': 'Each night, you learn how many of your 2 alive neighbours are evil.',
        'first_night': 5,
        'first_night_reminder': 'Show the finger signal (0, 1, 2) for the number of evil alive neighbours of the Empath.',
        'other_night': 1,
        'other_night_reminder': 'Show the finger signal (0, 1, 2) for the number of evil alive neighbours of the Empath.',
        'reminders': [],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'fortune_teller',
        'name': 'Fortune Teller',
        'edition': 'trouble-brewing',
        'team': 'townsfolk',
        'ability': 'Each night, choose 2 players: you learn if either is a Demon. There is a good player that registers as a Demon to you.',
        'first_night': 6,
        'first_night_reminder': 'The Fortune Teller points to two players. Give a thumbs up if either is a Demon. Give a thumbs down if neither is a Demon.',
        'other_night': 2,
        'other_night_reminder': 'The Fortune Teller points to two players. Give a thumbs up if either is a Demon. Give a thumbs down if neither is a Demon.',
        'reminders': ['Red herring'],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'undertaker',
        'name': 'Undertaker',
        'edition': 'trouble-brewing',
        'team': 'townsfolk',
        'ability': 'Each night*, you learn which character died by execution today.',
        'first_night': 0,
        'first_night_reminder': '',
        'other_night': 3,
        'other_night_reminder': 'If a player was executed today: Show that player\'s character token.',
        'reminders': ['Died today'],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'monk',
        'name': 'Monk',
        'edition': 'trouble-brewing',
        'team': 'townsfolk',
        'ability': 'Each night*, choose a player (not yourself): they are safe from the Demon tonight.',
        'first_night': 0,
        'first_night_reminder': '',
        'other_night': 4,
        'other_night_reminder': 'The Monk points to a player (not themselves). That player is safe from the Demon tonight.',
        'reminders': ['Safe'],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'ravenkeeper',
        'name': 'Ravenkeeper',
        'edition': 'trouble-brewing',
        'team': 'townsfolk',
        'ability': 'If you die at night, you are woken to choose a player: you learn their character.',
        'first_night': 0,
        'first_night_reminder': '',
        'other_night': 0,
        'other_night_reminder': 'If the Ravenkeeper died tonight: The Ravenkeeper points to a player. Show that player\'s character token.',
        'reminders': [],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'virgin',
        'name': 'Virgin',
        'edition': 'trouble-brewing',
        'team': 'townsfolk',
        'ability': 'The 1st time you are nominated, if the nominator is a Townsfolk, they are executed immediately.',
        'first_night': 0,
        'first_night_reminder': '',
        'other_night': 0,
        'other_night_reminder': '',
        'reminders': ['No ability'],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'slayer',
        'name': 'Slayer',
        'edition': 'trouble-brewing',
        'team': 'townsfolk',
        'ability': 'Once per game, during the day, publicly choose a player: if they are the Demon, they die.',
        'first_night': 0,
        'first_night_reminder': '',
        'other_night': 0,
        'other_night_reminder': '',
        'reminders': ['No ability'],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'soldier',
        'name': 'Soldier',
        'edition': 'trouble-brewing',
        'team': 'townsfolk',
        'ability': 'You are safe from the Demon.',
        'first_night': 0,
        'first_night_reminder': '',
        'other_night': 0,
        'other_night_reminder': '',
        'reminders': [],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'mayor',
        'name': 'Mayor',
        'edition': 'trouble-brewing',
        'team': 'townsfolk',
        'ability': 'If only 3 players live & no execution occurs, your team wins. If you die at night, another player might die instead.',
        'first_night': 0,
        'first_night_reminder': '',
        'other_night': 0,
        'other_night_reminder': '',
        'reminders': [],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    
    # Outsiders
    {
        'character_id': 'drunk',
        'name': 'Drunk',
        'edition': 'trouble-brewing',
        'team': 'outsider',
        'ability': 'You do not know you are the Drunk. You think you are a Townsfolk character, but you are not.',
        'first_night': 0,
        'first_night_reminder': '',
        'other_night': 0,
        'other_night_reminder': '',
        'reminders': [],
        'reminders_global': [],
        'setup': True,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'recluse',
        'name': 'Recluse',
        'edition': 'trouble-brewing',
        'team': 'outsider',
        'ability': 'You might register as evil & as a Minion or Demon, even if dead.',
        'first_night': 0,
        'first_night_reminder': '',
        'other_night': 0,
        'other_night_reminder': '',
        'reminders': [],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'saint',
        'name': 'Saint',
        'edition': 'trouble-brewing',
        'team': 'outsider',
        'ability': 'If you die by execution, your team loses.',
        'first_night': 0,
        'first_night_reminder': '',
        'other_night': 0,
        'other_night_reminder': '',
        'reminders': [],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'butler',
        'name': 'Butler',
        'edition': 'trouble-brewing',
        'team': 'outsider',
        'ability': 'Each night, choose a player (not yourself): tomorrow, you may only vote if they are voting too.',
        'first_night': 9,
        'first_night_reminder': 'The Butler points to a player. That player is their master.',
        'other_night': 8,
        'other_night_reminder': 'The Butler points to a player. That player is their master.',
        'reminders': ['Master'],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    
    # Minions
    {
        'character_id': 'poisoner',
        'name': 'Poisoner',
        'edition': 'trouble-brewing',
        'team': 'minion',
        'ability': 'Each night, choose a player: they are poisoned tonight and tomorrow day.',
        'first_night': 7,
        'first_night_reminder': 'The Poisoner points to a player. That player is poisoned.',
        'other_night': 5,
        'other_night_reminder': 'The Poisoner points to a player. That player is poisoned.',
        'reminders': ['Poisoned'],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'spy',
        'name': 'Spy',
        'edition': 'trouble-brewing',
        'team': 'minion',
        'ability': 'Each night, you see the Grimoire. You might register as good & as a Townsfolk or Outsider, even if dead.',
        'first_night': 8,
        'first_night_reminder': 'Show the Grimoire to the Spy for as long as they need.',
        'other_night': 6,
        'other_night_reminder': 'Show the Grimoire to the Spy for as long as they need.',
        'reminders': [],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [{'name': 'grimoire', 'type': 'signal', 'time': 'night'}],
        'jinxes': []
    },
    {
        'character_id': 'scarlet_woman',
        'name': 'Scarlet Woman',
        'edition': 'trouble-brewing',
        'team': 'minion',
        'ability': 'If there are 5 or more players alive & the Demon dies, you become the Demon.',
        'first_night': 0,
        'first_night_reminder': '',
        'other_night': 0,
        'other_night_reminder': '',
        'reminders': [],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    },
    {
        'character_id': 'baron',
        'name': 'Baron',
        'edition': 'trouble-brewing',
        'team': 'minion',
        'ability': 'There are extra Outsiders in play. [+2 Outsiders]',
        'first_night': 0,
        'first_night_reminder': '',
        'other_night': 0,
        'other_night_reminder': '',
        'reminders': [],
        'reminders_global': [],
        'setup': True,
        'image': [],
        'special': [],
        'jinxes': []
    },
    
    # Demons
    {
        'character_id': 'imp',
        'name': 'Imp',
        'edition': 'trouble-brewing',
        'team': 'demon',
        'ability': 'Each night*, choose a player: they die. If you kill yourself this way, a Minion becomes the Imp.',
        'first_night': 0,
        'first_night_reminder': '',
        'other_night': 7,
        'other_night_reminder': 'The Imp points to a player. That player dies.',
        'reminders': ['Dead'],
        'reminders_global': [],
        'setup': False,
        'image': [],
        'special': [],
        'jinxes': []
    }
]

