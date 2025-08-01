from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.game import Game
from src.models.player import Player
from src.models.role import Role
from src.models.script import Script
from src.models.vote import Vote, PlayerAction, GameLog
from src.routes.auth import require_auth
import random

game_bp = Blueprint('game', __name__)

@game_bp.route('', methods=['POST'])
@require_auth
def create_game():
    """Create a new game"""
    try:
        data = request.get_json() or {}
        
        script_id = data.get('script_id')
        if script_id:
            script = Script.query.get(script_id)
            if not script:
                return jsonify({'error': 'Script not found'}), 404
        
        # Create game
        game = Game(
            host_id=request.current_user.id,
            script_id=script_id
        )
        
        # Set custom settings if provided
        if 'settings' in data:
            current_settings = game.get_settings()
            current_settings.update(data['settings'])
            game.set_settings(current_settings)
        
        db.session.add(game)
        db.session.commit()
        
        # Add host as first player
        player = Player(
            user_id=request.current_user.id,
            game_id=game.id,
            position=0,
            is_ready=True  # Host is automatically ready
        )
        db.session.add(player)
        db.session.commit()
        
        # Log game creation
        GameLog.log_event(
            game.id,
            'game_created',
            {
                'host_id': request.current_user.id,
                'host_username': request.current_user.username,
                'script_id': script_id,
                'script_name': script.name if script else None
            }
        )
        db.session.commit()
        
        return jsonify({
            'message': 'Game created successfully',
            'game': game.to_dict(include_sensitive=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create game: {str(e)}'}), 500

@game_bp.route('/<int:game_id>', methods=['GET'])
@require_auth
def get_game(game_id):
    """Get game details"""
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # Check if user is in the game
    player = Player.query.filter_by(game_id=game_id, user_id=request.current_user.id).first()
    if not player:
        return jsonify({'error': 'You are not in this game'}), 403
    
    # Include sensitive information if user is host
    include_sensitive = (game.host_id == request.current_user.id)
    
    return jsonify({
        'game': game.to_dict(include_sensitive=include_sensitive)
    }), 200

@game_bp.route('/join', methods=['POST'])
@require_auth
def join_game():
    """Join a game using join code"""
    try:
        data = request.get_json()
        if not data or 'join_code' not in data:
            return jsonify({'error': 'Join code is required'}), 400
        
        join_code = data['join_code'].upper().strip()
        
        game = Game.query.filter_by(join_code=join_code).first()
        if not game:
            return jsonify({'error': 'Invalid join code'}), 404
        
        if game.status != 'lobby':
            return jsonify({'error': 'Game has already started'}), 400
        
        # Check if user is already in the game
        existing_player = Player.query.filter_by(game_id=game.id, user_id=request.current_user.id).first()
        if existing_player:
            return jsonify({'error': 'You are already in this game'}), 400
        
        # Check if game is full
        max_players = game.get_settings().get('max_players', 15)
        if game.get_player_count() >= max_players:
            return jsonify({'error': 'Game is full'}), 400
        
        # Add player to game
        player = Player(
            user_id=request.current_user.id,
            game_id=game.id
        )
        db.session.add(player)
        db.session.commit()
        
        # Log player join
        GameLog.log_event(
            game.id,
            'player_joined',
            {
                'player_id': player.id,
                'user_id': request.current_user.id,
                'username': request.current_user.username,
                'position': player.position
            }
        )
        db.session.commit()
        
        return jsonify({
            'message': 'Joined game successfully',
            'game': game.to_dict(),
            'player': player.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to join game: {str(e)}'}), 500

@game_bp.route('/<int:game_id>/leave', methods=['POST'])
@require_auth
def leave_game(game_id):
    """Leave a game"""
    try:
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        player = Player.query.filter_by(game_id=game_id, user_id=request.current_user.id).first()
        if not player:
            return jsonify({'error': 'You are not in this game'}), 404
        
        # Can't leave if game has started (unless host)
        if game.status != 'lobby' and game.host_id != request.current_user.id:
            return jsonify({'error': 'Cannot leave game after it has started'}), 400
        
        # If host is leaving, either transfer host or end game
        if game.host_id == request.current_user.id:
            other_players = [p for p in game.players if p.user_id != request.current_user.id]
            
            if other_players and game.status == 'lobby':
                # Transfer host to another player
                new_host = other_players[0]
                game.host_id = new_host.user_id
                
                GameLog.log_event(
                    game.id,
                    'host_transferred',
                    {
                        'old_host_id': request.current_user.id,
                        'old_host_username': request.current_user.username,
                        'new_host_id': new_host.user_id,
                        'new_host_username': new_host.user.username
                    }
                )
            else:
                # End the game if no other players or game has started
                game.status = 'ended'
                game.winner = None
                
                GameLog.log_event(
                    game.id,
                    'game_ended',
                    {
                        'reason': 'host_left',
                        'host_id': request.current_user.id,
                        'host_username': request.current_user.username
                    }
                )
        
        # Remove player
        db.session.delete(player)
        
        # Log player leave
        GameLog.log_event(
            game.id,
            'player_left',
            {
                'player_id': player.id,
                'user_id': request.current_user.id,
                'username': request.current_user.username
            }
        )
        
        db.session.commit()
        
        return jsonify({'message': 'Left game successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to leave game: {str(e)}'}), 500

@game_bp.route('/<int:game_id>/ready', methods=['POST'])
@require_auth
def toggle_ready(game_id):
    """Toggle player ready status"""
    try:
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        if game.status != 'lobby':
            return jsonify({'error': 'Game has already started'}), 400
        
        player = Player.query.filter_by(game_id=game_id, user_id=request.current_user.id).first()
        if not player:
            return jsonify({'error': 'You are not in this game'}), 404
        
        player.is_ready = not player.is_ready
        db.session.commit()
        
        # Log ready status change
        GameLog.log_event(
            game.id,
            'player_ready_changed',
            {
                'player_id': player.id,
                'user_id': request.current_user.id,
                'username': request.current_user.username,
                'is_ready': player.is_ready
            }
        )
        db.session.commit()
        
        return jsonify({
            'message': f'Ready status set to {player.is_ready}',
            'is_ready': player.is_ready
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update ready status: {str(e)}'}), 500

@game_bp.route('/<int:game_id>/start', methods=['POST'])
@require_auth
def start_game(game_id):
    """Start the game (host only)"""
    try:
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        if game.host_id != request.current_user.id:
            return jsonify({'error': 'Only the host can start the game'}), 403
        
        if not game.can_start():
            return jsonify({'error': 'Game cannot be started. Check player count and ready status.'}), 400
        
        # Assign roles
        if not assign_roles(game):
            return jsonify({'error': 'Failed to assign roles'}), 500
        
        # Start the game
        game.start_game()
        
        # Log game start
        GameLog.log_event(
            game.id,
            'game_started',
            {
                'host_id': request.current_user.id,
                'host_username': request.current_user.username,
                'player_count': game.get_player_count(),
                'script_id': game.script_id,
                'script_name': game.script.name if game.script else None
            }
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Game started successfully',
            'game': game.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to start game: {str(e)}'}), 500

def assign_roles(game):
    """Assign roles to players"""
    try:
        if not game.script:
            return False
        
        player_count = game.get_player_count()
        distribution = game.script.calculate_distribution(player_count)
        
        if not distribution:
            return False
        
        # Get available roles by type
        available_roles = {
            'townsfolk': game.script.get_townsfolk(),
            'outsider': game.script.get_outsiders(),
            'minion': game.script.get_minions(),
            'demon': game.script.get_demons()
        }
        
        # Select random roles for each type
        selected_roles = []
        for role_type, count in distribution.items():
            roles = available_roles[role_type]
            if len(roles) < count:
                return False
            selected_roles.extend(random.sample(roles, count))
        
        # Shuffle roles and assign to players
        random.shuffle(selected_roles)
        players = list(game.players)
        random.shuffle(players)
        
        for i, player in enumerate(players):
            if i < len(selected_roles):
                player.role_id = selected_roles[i].id
        
        return True
        
    except Exception as e:
        print(f"Error assigning roles: {e}")
        return False

@game_bp.route('/<int:game_id>/vote', methods=['POST'])
@require_auth
def submit_vote(game_id):
    """Submit a vote"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        if game.status != 'day':
            return jsonify({'error': 'Voting is only allowed during day phase'}), 400
        
        player = Player.query.filter_by(game_id=game_id, user_id=request.current_user.id).first()
        if not player:
            return jsonify({'error': 'You are not in this game'}), 404
        
        if not player.can_vote():
            return jsonify({'error': 'You have no votes remaining'}), 400
        
        target_id = data.get('target_id')  # None for abstain
        vote_type = data.get('vote_type', 'execution')
        
        # Validate target if provided
        if target_id:
            target = Player.query.filter_by(game_id=game_id, id=target_id).first()
            if not target:
                return jsonify({'error': 'Invalid target player'}), 400
        
        # Create vote
        vote = Vote(
            game_id=game_id,
            voter_id=player.id,
            target_id=target_id,
            vote_type=vote_type,
            day_number=game.day_number
        )
        
        # Deduct vote from player
        player.cast_vote(target_id)
        
        db.session.add(vote)
        
        # Log vote
        GameLog.log_event(
            game.id,
            'vote_cast',
            {
                'voter_id': player.id,
                'voter_username': player.user.username,
                'target_id': target_id,
                'target_username': target.user.username if target_id else None,
                'vote_type': vote_type,
                'day_number': game.day_number
            },
            day_number=game.day_number
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Vote submitted successfully',
            'vote': vote.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to submit vote: {str(e)}'}), 500

@game_bp.route('/<int:game_id>/nominate', methods=['POST'])
@require_auth
def nominate_player(game_id):
    """Nominate a player for execution"""
    try:
        data = request.get_json()
        if not data or 'target_id' not in data:
            return jsonify({'error': 'Target player ID is required'}), 400
        
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        if game.status != 'day':
            return jsonify({'error': 'Nominations are only allowed during day phase'}), 400
        
        player = Player.query.filter_by(game_id=game_id, user_id=request.current_user.id).first()
        if not player:
            return jsonify({'error': 'You are not in this game'}), 404
        
        if not player.is_alive:
            return jsonify({'error': 'Dead players cannot nominate'}), 400
        
        target_id = data['target_id']
        target = Player.query.filter_by(game_id=game_id, id=target_id).first()
        if not target:
            return jsonify({'error': 'Invalid target player'}), 404
        
        if not target.is_alive:
            return jsonify({'error': 'Cannot nominate dead players'}), 400
        
        if target.id == player.id:
            return jsonify({'error': 'Cannot nominate yourself'}), 400
        
        # Check if player already nominated today
        existing_nominations = game.get_nominations()
        if any(nom['nominator_id'] == player.id for nom in existing_nominations):
            return jsonify({'error': 'You have already nominated someone today'}), 400
        
        # Add nomination
        game.add_nomination(player.id, target.id)
        
        # Log nomination
        GameLog.log_event(
            game.id,
            'player_nominated',
            {
                'nominator_id': player.id,
                'nominator_username': player.user.username,
                'nominee_id': target.id,
                'nominee_username': target.user.username,
                'day_number': game.day_number
            },
            day_number=game.day_number
        )
        
        db.session.commit()
        
        return jsonify({
            'message': f'{target.user.username} has been nominated for execution',
            'nominations': game.get_nominations()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to nominate player: {str(e)}'}), 500

@game_bp.route('/<int:game_id>/history', methods=['GET'])
@require_auth
def get_game_history(game_id):
    """Get game history/logs"""
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    # Check if user is in the game
    player = Player.query.filter_by(game_id=game_id, user_id=request.current_user.id).first()
    if not player:
        return jsonify({'error': 'You are not in this game'}), 403
    
    # Get game logs
    logs = GameLog.query.filter_by(game_id=game_id).order_by(GameLog.timestamp).all()
    
    return jsonify({
        'history': [log.to_dict() for log in logs]
    }), 200

