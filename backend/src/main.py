import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
from src.models.user import db
from src.models.game import Game
from src.models.player import Player
from src.models.role import Role
from src.models.script import Script, ScriptRole
from src.models.vote import Vote, PlayerAction, GameLog
from src.models.game_state import GameState, GameAction, GameHistory
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.game import game_bp
from src.routes.role import role_bp
from src.routes.game_state import game_state_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app, origins=['*'])

# Initialize SocketIO with CORS support
socketio = SocketIO(app, cors_allowed_origins=['http://localhost:5173', 'http://localhost:3000', '*'])

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(game_bp, url_prefix='/api/games')
app.register_blueprint(role_bp, url_prefix='/api')
app.register_blueprint(game_state_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to Blood on the Clocktower server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

@socketio.on('join_game')
def handle_join_game(data):
    game_id = data.get('game_id')
    if game_id:
        join_room(f'game_{game_id}')
        emit('joined_game', {'game_id': game_id}, room=f'game_{game_id}')
        print(f'Client {request.sid} joined game {game_id}')

@socketio.on('leave_game')
def handle_leave_game(data):
    game_id = data.get('game_id')
    if game_id:
        leave_room(f'game_{game_id}')
        emit('left_game', {'game_id': game_id}, room=f'game_{game_id}')
        print(f'Client {request.sid} left game {game_id}')

@socketio.on('game_update')
def handle_game_update(data):
    game_id = data.get('game_id')
    update_type = data.get('type')
    update_data = data.get('data', {})
    
    if game_id:
        emit('game_updated', {
            'type': update_type,
            'data': update_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f'game_{game_id}')

@socketio.on('chat_message')
def handle_chat_message(data):
    game_id = data.get('game_id')
    message = data.get('message')
    username = data.get('username')
    
    if game_id and message and username:
        emit('chat_message', {
            'username': username,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f'game_{game_id}')

@socketio.on('player_action')
def handle_player_action(data):
    game_id = data.get('game_id')
    action_type = data.get('action_type')
    action_data = data.get('action_data', {})
    
    if game_id and action_type:
        emit('player_action', {
            'action_type': action_type,
            'action_data': action_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f'game_{game_id}')

@socketio.on('night_action')
def handle_night_action(data):
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    action_type = data.get('action_type')
    target_id = data.get('target_id')
    
    if game_id and player_id and action_type:
        # Broadcast night action to storyteller/host only
        emit('night_action_received', {
            'player_id': player_id,
            'action_type': action_type,
            'target_id': target_id,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f'game_{game_id}_host')

@socketio.on('storyteller_update')
def handle_storyteller_update(data):
    game_id = data.get('game_id')
    update_type = data.get('type')
    update_data = data.get('data', {})
    
    if game_id:
        # Broadcast storyteller updates to all players
        emit('storyteller_update', {
            'type': update_type,
            'data': update_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f'game_{game_id}')

# Store socketio instance for use in other modules
app.socketio = socketio

def init_database():
    """Initialize database with default data"""
    with app.app_context():
        db.create_all()
        
        # Check if roles already exist
        if Role.query.count() == 0:
            from src.models.role import DEFAULT_ROLES
            print("Initializing default roles...")
            
            for role_data in DEFAULT_ROLES:
                role = Role(
                    character_id=role_data['character_id'],
                    name=role_data['name'],
                    edition=role_data['edition'],
                    team=role_data['team'],
                    ability=role_data['ability'],
                    first_night=role_data['first_night'],
                    first_night_reminder=role_data['first_night_reminder'],
                    other_night=role_data['other_night'],
                    other_night_reminder=role_data['other_night_reminder'],
                    setup=role_data['setup']
                )
                role.set_reminders(role_data.get('reminders', []))
                role.set_reminders_global(role_data.get('reminders_global', []))
                role.set_image(role_data.get('image', []))
                role.set_special(role_data.get('special', []))
                role.set_jinxes(role_data.get('jinxes', []))
                db.session.add(role)
            
            db.session.commit()
            print(f"Added {len(DEFAULT_ROLES)} default roles")
        
        # Check if Trouble Brewing script exists
        if Script.query.filter_by(name='Trouble Brewing').first() is None:
            from src.models.script import TROUBLE_BREWING_SCRIPT
            print("Initializing Trouble Brewing script...")
            
            script = Script(
                name=TROUBLE_BREWING_SCRIPT['name'],
                author=TROUBLE_BREWING_SCRIPT['author'],
                description=TROUBLE_BREWING_SCRIPT['description'],
                is_official=TROUBLE_BREWING_SCRIPT['is_official'],
                player_count_min=TROUBLE_BREWING_SCRIPT['player_count_min'],
                player_count_max=TROUBLE_BREWING_SCRIPT['player_count_max'],
                version=TROUBLE_BREWING_SCRIPT['version']
            )
            db.session.add(script)
            db.session.commit()
            
            # Add roles to script
            for role_name in TROUBLE_BREWING_SCRIPT['roles']:
                role = Role.query.filter_by(name=role_name).first()
                if role:
                    script_role = ScriptRole(script_id=script.id, role_id=role.id)
                    db.session.add(script_role)
            
            db.session.commit()
            print("Added Trouble Brewing script with roles")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    init_database()
    print("Starting Blood on the Clocktower server with WebSocket support...")
    print("Frontend should connect to: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
