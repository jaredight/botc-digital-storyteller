from flask import Blueprint, request, jsonify, session
from src.models.user import db
from src.models.game import Game
from src.models.player import Player
from src.models.game_state import GameState, GameAction, GameHistory, GameStateManager
from datetime import datetime

game_state_bp = Blueprint('game_state', __name__)

@game_state_bp.route('/games/<int:game_id>/save', methods=['POST'])
def save_game_state(game_id):
    """Save current game state"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    data = request.get_json()
    
    if not data or 'state_name' not in data:
        return jsonify({'error': 'State name is required'}), 400
    
    # Get game and verify user is host
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    if game.host_id != user_id:
        return jsonify({'error': 'Only the host can save game states'}), 403
    
    try:
        state_name = data['state_name']
        game_state = GameStateManager.save_game_state(game, state_name, user_id)
        
        return jsonify({
            'success': True,
            'game_state': game_state.to_dict()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@game_state_bp.route('/games/<int:game_id>/states', methods=['GET'])
def get_game_states(game_id):
    """Get all saved states for a game"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    # Get game and verify user is participant
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    player = Player.query.filter_by(game_id=game_id, user_id=user_id).first()
    if not player and game.host_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get saved states
    states = GameState.query.filter_by(game_id=game_id).order_by(GameState.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'states': [state.to_dict() for state in states]
    })

@game_state_bp.route('/games/<int:game_id>/load/<int:state_id>', methods=['POST'])
def load_game_state(game_id, state_id):
    """Load a saved game state"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    # Get game and verify user is host
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    if game.host_id != user_id:
        return jsonify({'error': 'Only the host can load game states'}), 403
    
    # Get game state
    game_state = GameState.query.filter_by(id=state_id, game_id=game_id).first()
    if not game_state:
        return jsonify({'error': 'Game state not found'}), 404
    
    try:
        state_data = game_state.get_state_data()
        
        # Create auto-save before loading
        GameStateManager.auto_save_game(game)
        
        # Update game with loaded state
        game_info = state_data.get('game_info', {})
        game.phase = game_info.get('phase', 'day')
        game.day_number = game_info.get('day_number', 1)
        game.status = game_info.get('status', 'active')
        
        if 'settings' in game_info:
            game.set_settings(game_info['settings'])
        
        # Update players with loaded state
        players_data = state_data.get('players', [])
        for player_data in players_data:
            player = Player.query.filter_by(
                game_id=game_id, 
                user_id=player_data.get('user_id')
            ).first()
            
            if player:
                player.role_id = player_data.get('role_id')
                player.is_alive = player_data.get('is_alive', True)
                player.votes_remaining = player_data.get('votes_remaining', 1)
                player.position = player_data.get('position', 0)
                
                if 'abilities_used' in player_data:
                    player.set_abilities_used(player_data['abilities_used'])
                if 'status_effects' in player_data:
                    player.set_status_effects(player_data['status_effects'])
        
        db.session.commit()
        
        # Record the load action
        GameStateManager.record_action(
            game, 
            'load_state', 
            {'state_id': state_id, 'state_name': game_state.state_name},
            user_id
        )
        
        return jsonify({
            'success': True,
            'message': f'Game state "{game_state.state_name}" loaded successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_state_bp.route('/games/<int:game_id>/actions', methods=['GET'])
def get_game_actions(game_id):
    """Get recent game actions"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    # Get game and verify user is participant
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    player = Player.query.filter_by(game_id=game_id, user_id=user_id).first()
    if not player and game.host_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    limit = request.args.get('limit', 50, type=int)
    actions = GameStateManager.get_game_actions(game_id, limit)
    
    return jsonify({
        'success': True,
        'actions': [action.to_dict() for action in actions]
    })

@game_state_bp.route('/games/<int:game_id>/actions/<int:action_id>/undo', methods=['POST'])
def undo_action(game_id, action_id):
    """Undo a game action"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    data = request.get_json() or {}
    
    # Get game and verify user is host
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    if game.host_id != user_id:
        return jsonify({'error': 'Only the host can undo actions'}), 403
    
    # Get action
    action = GameAction.query.filter_by(id=action_id, game_id=game_id).first()
    if not action:
        return jsonify({'error': 'Action not found'}), 404
    
    if action.is_undone:
        return jsonify({'error': 'Action already undone'}), 400
    
    try:
        undo_reason = data.get('reason', 'Undone by host')
        success = GameStateManager.undo_action(action_id, undo_reason)
        
        if success:
            # Record the undo action
            GameStateManager.record_action(
                game,
                'undo_action',
                {
                    'undone_action_id': action_id,
                    'undone_action_type': action.action_type,
                    'reason': undo_reason
                },
                user_id
            )
            
            return jsonify({
                'success': True,
                'message': f'Action "{action.action_type}" undone successfully'
            })
        else:
            return jsonify({'error': 'Failed to undo action'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@game_state_bp.route('/games/<int:game_id>/auto-save', methods=['POST'])
def create_auto_save(game_id):
    """Create an automatic save point"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    # Get game and verify user is host
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    if game.host_id != user_id:
        return jsonify({'error': 'Only the host can create saves'}), 403
    
    try:
        game_state = GameStateManager.auto_save_game(game)
        
        return jsonify({
            'success': True,
            'game_state': game_state.to_dict()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@game_state_bp.route('/games/<int:game_id>/history', methods=['GET'])
def get_game_history(game_id):
    """Get game history (for completed games)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    # Get game and verify user is participant
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    player = Player.query.filter_by(game_id=game_id, user_id=user_id).first()
    if not player and game.host_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get game history
    history = GameHistory.query.filter_by(game_id=game_id).first()
    
    if not history:
        return jsonify({'error': 'Game history not found'}), 404
    
    include_full_data = request.args.get('full', 'false').lower() == 'true'
    
    result = history.to_dict()
    
    if include_full_data:
        result['history_data'] = history.get_history_data()
        result['final_state'] = history.get_final_state()
    
    return jsonify({
        'success': True,
        'history': result
    })

@game_state_bp.route('/games/<int:game_id>/finish', methods=['POST'])
def finish_game(game_id):
    """Finish a game and create history record"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    data = request.get_json() or {}
    
    # Get game and verify user is host
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    if game.host_id != user_id:
        return jsonify({'error': 'Only the host can finish the game'}), 403
    
    if game.status == 'completed':
        return jsonify({'error': 'Game already completed'}), 400
    
    try:
        # Update game status
        game.status = 'completed'
        game.ended_at = datetime.utcnow()
        game.winner_team = data.get('winner_team')  # 'good' or 'evil'
        
        db.session.commit()
        
        # Create game history
        history = GameStateManager.create_game_history(game)
        
        # Record the finish action
        GameStateManager.record_action(
            game,
            'finish_game',
            {
                'winner_team': game.winner_team,
                'final_day': game.day_number
            },
            user_id
        )
        
        return jsonify({
            'success': True,
            'message': 'Game completed successfully',
            'history': history.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_state_bp.route('/users/<int:user_id>/game-history', methods=['GET'])
def get_user_game_history(user_id):
    """Get game history for a user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    session_user_id = session['user_id']
    
    # Users can only view their own history unless they're viewing public data
    if session_user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get games where user was a participant
    player_games = db.session.query(Game.id).join(Player).filter(
        Player.user_id == user_id,
        Game.status == 'completed'
    ).subquery()
    
    # Get games where user was host
    host_games = db.session.query(Game.id).filter(
        Game.host_id == user_id,
        Game.status == 'completed'
    ).subquery()
    
    # Get all game histories for these games
    histories = GameHistory.query.filter(
        db.or_(
            GameHistory.game_id.in_(player_games),
            GameHistory.game_id.in_(host_games)
        )
    ).order_by(GameHistory.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'histories': [history.to_dict() for history in histories]
    })

