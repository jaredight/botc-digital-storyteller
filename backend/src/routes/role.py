from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.role import Role
from src.models.script import Script, ScriptRole
from src.routes.auth import require_auth

role_bp = Blueprint('role', __name__)

@role_bp.route('/roles', methods=['GET'])
def get_roles():
    """Get all available roles"""
    try:
        # Get query parameters
        team = request.args.get('team')
        is_official = request.args.get('official')
        
        # Build query
        query = Role.query
        
        if team:
            query = query.filter(Role.team == team)
        
        if is_official is not None:
            is_official_bool = is_official.lower() in ['true', '1', 'yes']
            query = query.filter(Role.is_official == is_official_bool)
        
        roles = query.order_by(Role.team, Role.name).all()
        
        # Group roles by team
        roles_by_team = {
            'townsfolk': [],
            'outsider': [],
            'minion': [],
            'demon': []
        }
        
        for role in roles:
            if role.team in roles_by_team:
                roles_by_team[role.team].append(role.to_dict())
        
        return jsonify({
            'roles': [role.to_dict() for role in roles],
            'roles_by_team': roles_by_team,
            'total_count': len(roles)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get roles: {str(e)}'}), 500

@role_bp.route('/roles/<int:role_id>', methods=['GET'])
def get_role(role_id):
    """Get specific role details"""
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Role not found'}), 404
    
    return jsonify({'role': role.to_dict()}), 200

@role_bp.route('/scripts', methods=['GET'])
def get_scripts():
    """Get all available scripts"""
    try:
        # Get query parameters
        is_official = request.args.get('official')
        include_roles = request.args.get('include_roles', 'false').lower() in ['true', '1', 'yes']
        
        # Build query
        query = Script.query
        
        if is_official is not None:
            is_official_bool = is_official.lower() in ['true', '1', 'yes']
            query = query.filter(Script.is_official == is_official_bool)
        
        scripts = query.order_by(Script.is_official.desc(), Script.name).all()
        
        return jsonify({
            'scripts': [script.to_dict(include_roles=include_roles) for script in scripts],
            'total_count': len(scripts)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get scripts: {str(e)}'}), 500

@role_bp.route('/scripts/<int:script_id>', methods=['GET'])
def get_script(script_id):
    """Get specific script details"""
    script = Script.query.get(script_id)
    if not script:
        return jsonify({'error': 'Script not found'}), 404
    
    include_roles = request.args.get('include_roles', 'true').lower() in ['true', '1', 'yes']
    
    return jsonify({'script': script.to_dict(include_roles=include_roles)}), 200

@role_bp.route('/scripts', methods=['POST'])
@require_auth
def create_script():
    """Create a custom script"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        role_ids = data.get('role_ids', [])
        
        if not name:
            return jsonify({'error': 'Script name is required'}), 400
        
        if not description:
            return jsonify({'error': 'Script description is required'}), 400
        
        if not role_ids or len(role_ids) < 5:
            return jsonify({'error': 'Script must have at least 5 roles'}), 400
        
        # Check if script name already exists
        existing_script = Script.query.filter_by(name=name).first()
        if existing_script:
            return jsonify({'error': 'Script name already exists'}), 409
        
        # Validate all role IDs exist
        roles = Role.query.filter(Role.id.in_(role_ids)).all()
        if len(roles) != len(role_ids):
            return jsonify({'error': 'One or more invalid role IDs'}), 400
        
        # Validate role distribution
        role_counts = {'townsfolk': 0, 'outsider': 0, 'minion': 0, 'demon': 0}
        for role in roles:
            if role.team in role_counts:
                role_counts[role.team] += 1
        
        # Must have at least one demon and some good roles
        if role_counts['demon'] == 0:
            return jsonify({'error': 'Script must have at least one Demon'}), 400
        
        if role_counts['townsfolk'] + role_counts['outsider'] < 3:
            return jsonify({'error': 'Script must have at least 3 good roles'}), 400
        
        # Create script
        script = Script(
            name=name,
            description=description,
            author=request.current_user.username,
            is_official=False,
            player_count_min=data.get('player_count_min', 5),
            player_count_max=data.get('player_count_max', 15),
            version=data.get('version', '1.0')
        )
        
        db.session.add(script)
        db.session.flush()  # Get script ID
        
        # Add roles to script
        for role_id in role_ids:
            script_role = ScriptRole(script_id=script.id, role_id=role_id)
            db.session.add(script_role)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Script created successfully',
            'script': script.to_dict(include_roles=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create script: {str(e)}'}), 500

@role_bp.route('/scripts/<int:script_id>', methods=['PUT'])
@require_auth
def update_script(script_id):
    """Update a custom script (author only)"""
    try:
        script = Script.query.get(script_id)
        if not script:
            return jsonify({'error': 'Script not found'}), 404
        
        if script.is_official:
            return jsonify({'error': 'Cannot modify official scripts'}), 403
        
        if script.author != request.current_user.username:
            return jsonify({'error': 'Only the script author can modify it'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update basic fields
        if 'name' in data:
            new_name = data['name'].strip()
            if new_name != script.name:
                existing_script = Script.query.filter_by(name=new_name).first()
                if existing_script:
                    return jsonify({'error': 'Script name already exists'}), 409
                script.name = new_name
        
        if 'description' in data:
            script.description = data['description'].strip()
        
        if 'player_count_min' in data:
            script.player_count_min = data['player_count_min']
        
        if 'player_count_max' in data:
            script.player_count_max = data['player_count_max']
        
        if 'version' in data:
            script.version = data['version']
        
        # Update roles if provided
        if 'role_ids' in data:
            role_ids = data['role_ids']
            
            if len(role_ids) < 5:
                return jsonify({'error': 'Script must have at least 5 roles'}), 400
            
            # Validate all role IDs exist
            roles = Role.query.filter(Role.id.in_(role_ids)).all()
            if len(roles) != len(role_ids):
                return jsonify({'error': 'One or more invalid role IDs'}), 400
            
            # Remove existing script roles
            ScriptRole.query.filter_by(script_id=script.id).delete()
            
            # Add new script roles
            for role_id in role_ids:
                script_role = ScriptRole(script_id=script.id, role_id=role_id)
                db.session.add(script_role)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Script updated successfully',
            'script': script.to_dict(include_roles=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update script: {str(e)}'}), 500

@role_bp.route('/scripts/<int:script_id>', methods=['DELETE'])
@require_auth
def delete_script(script_id):
    """Delete a custom script (author only)"""
    try:
        script = Script.query.get(script_id)
        if not script:
            return jsonify({'error': 'Script not found'}), 404
        
        if script.is_official:
            return jsonify({'error': 'Cannot delete official scripts'}), 403
        
        if script.author != request.current_user.username:
            return jsonify({'error': 'Only the script author can delete it'}), 403
        
        # Check if script is being used in any active games
        from src.models.game import Game
        active_games = Game.query.filter_by(script_id=script.id).filter(Game.status.in_(['lobby', 'night', 'day'])).count()
        
        if active_games > 0:
            return jsonify({'error': 'Cannot delete script while it is being used in active games'}), 400
        
        db.session.delete(script)
        db.session.commit()
        
        return jsonify({'message': 'Script deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete script: {str(e)}'}), 500

@role_bp.route('/scripts/<int:script_id>/distribution/<int:player_count>', methods=['GET'])
def get_role_distribution(script_id, player_count):
    """Get role distribution for a script and player count"""
    script = Script.query.get(script_id)
    if not script:
        return jsonify({'error': 'Script not found'}), 404
    
    if player_count < 5 or player_count > 15:
        return jsonify({'error': 'Player count must be between 5 and 15'}), 400
    
    distribution = script.calculate_distribution(player_count)
    if not distribution:
        return jsonify({'error': 'Invalid player count for this script'}), 400
    
    can_support = script.can_support_player_count(player_count)
    
    return jsonify({
        'player_count': player_count,
        'distribution': distribution,
        'can_support': can_support,
        'available_roles': {
            'townsfolk': len(script.get_townsfolk()),
            'outsider': len(script.get_outsiders()),
            'minion': len(script.get_minions()),
            'demon': len(script.get_demons())
        }
    }), 200

