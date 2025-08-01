# Blood on the Clocktower API Documentation

This document provides comprehensive documentation for the Blood on the Clocktower Digital Storyteller API.

## Base URL

- **Development**: `http://localhost:5000/api`
- **Production**: `https://yourdomain.com/api`

## Authentication

The API uses session-based authentication. Include credentials in requests:

```javascript
fetch('/api/endpoint', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
})
```

## Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "timestamp": "2025-01-01T00:00:00Z"
}
```

Error responses:
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Authentication Endpoints

### Register User
**POST** `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "username": "string (3-50 chars, alphanumeric + underscore)",
  "email": "string (valid email)",
  "password": "string (min 8 chars)"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "player1",
    "email": "player1@example.com",
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

**Error Codes:**
- `USERNAME_TAKEN` - Username already exists
- `EMAIL_TAKEN` - Email already registered
- `INVALID_INPUT` - Validation failed

### Login User
**POST** `/auth/login`

Authenticate user and create session.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "player1",
    "email": "player1@example.com"
  }
}
```

### Logout User
**POST** `/auth/logout`

End user session.

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### Get Current User
**GET** `/auth/me`

Get current authenticated user information.

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "player1",
    "email": "player1@example.com",
    "games_played": 15,
    "games_won": 8
  }
}
```

## Game Management Endpoints

### List Games
**GET** `/games`

Get list of games with optional filtering.

**Query Parameters:**
- `status` - Filter by game status (`lobby`, `active`, `completed`)
- `host_id` - Filter by host user ID
- `limit` - Number of results (default: 20, max: 100)
- `offset` - Pagination offset

**Response:**
```json
{
  "success": true,
  "games": [
    {
      "id": 1,
      "name": "Epic Game",
      "status": "lobby",
      "host": {
        "id": 1,
        "username": "storyteller1"
      },
      "player_count": 8,
      "max_players": 12,
      "script": {
        "id": 1,
        "name": "Trouble Brewing"
      },
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total_count": 1,
  "has_more": false
}
```

### Create Game
**POST** `/games`

Create a new game (requires authentication).

**Request Body:**
```json
{
  "name": "string (required, 3-100 chars)",
  "script_id": "integer (required)",
  "max_players": "integer (5-15, default: 10)",
  "is_private": "boolean (default: false)",
  "settings": {
    "allow_spectators": "boolean (default: true)",
    "chat_enabled": "boolean (default: true)",
    "voting_timeout": "integer (seconds, default: 300)"
  }
}
```

**Response:**
```json
{
  "success": true,
  "game": {
    "id": 1,
    "name": "Epic Game",
    "join_code": "ABC123",
    "status": "lobby",
    "host_id": 1,
    "script_id": 1,
    "max_players": 10,
    "settings": {},
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

### Get Game Details
**GET** `/games/{game_id}`

Get detailed information about a specific game.

**Response:**
```json
{
  "success": true,
  "game": {
    "id": 1,
    "name": "Epic Game",
    "status": "active",
    "phase": "day",
    "day_number": 2,
    "host": {
      "id": 1,
      "username": "storyteller1"
    },
    "script": {
      "id": 1,
      "name": "Trouble Brewing",
      "roles": []
    },
    "players": [
      {
        "id": 1,
        "user": {
          "id": 2,
          "username": "player1"
        },
        "position": 1,
        "is_alive": true,
        "votes_remaining": 1,
        "role": {
          "id": 5,
          "name": "Butler",
          "team": "townsfolk"
        }
      }
    ],
    "settings": {},
    "created_at": "2025-01-01T00:00:00Z",
    "started_at": "2025-01-01T01:00:00Z"
  }
}
```

### Join Game
**POST** `/games/{game_id}/join`

Join a game using join code or direct invitation.

**Request Body:**
```json
{
  "join_code": "string (optional if game_id provided)"
}
```

**Response:**
```json
{
  "success": true,
  "player": {
    "id": 1,
    "game_id": 1,
    "user_id": 2,
    "position": 1,
    "is_ready": false,
    "joined_at": "2025-01-01T00:00:00Z"
  }
}
```

### Leave Game
**POST** `/games/{game_id}/leave`

Leave a game (if not started or as spectator).

**Response:**
```json
{
  "success": true,
  "message": "Left game successfully"
}
```

### Start Game
**POST** `/games/{game_id}/start`

Start a game (host only, requires all players ready).

**Request Body:**
```json
{
  "assign_roles": "string (random|manual, default: random)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Game started successfully",
  "game": {
    "id": 1,
    "status": "night",
    "phase": "night",
    "day_number": 1,
    "started_at": "2025-01-01T01:00:00Z"
  }
}
```

### Update Player Ready Status
**POST** `/games/{game_id}/ready`

Mark player as ready or not ready.

**Request Body:**
```json
{
  "is_ready": "boolean"
}
```

**Response:**
```json
{
  "success": true,
  "player": {
    "id": 1,
    "is_ready": true
  }
}
```

## Role and Script Endpoints

### List Roles
**GET** `/roles`

Get all available roles with optional filtering.

**Query Parameters:**
- `team` - Filter by team (`townsfolk`, `outsider`, `minion`, `demon`)
- `official` - Filter by official status (`true`, `false`)

**Response:**
```json
{
  "success": true,
  "roles": [
    {
      "id": 1,
      "character_id": "butler",
      "name": "Butler",
      "team": "townsfolk",
      "ability": "Each night, choose a player (not yourself): tomorrow, you may only vote if they are voting too.",
      "first_night": 0,
      "other_night": 1,
      "reminders": ["Master"],
      "setup": false,
      "is_official": true
    }
  ],
  "roles_by_team": {
    "townsfolk": [],
    "outsider": [],
    "minion": [],
    "demon": []
  },
  "total_count": 22
}
```

### Get Role Details
**GET** `/roles/{role_id}`

Get detailed information about a specific role.

**Response:**
```json
{
  "success": true,
  "role": {
    "id": 1,
    "character_id": "butler",
    "name": "Butler",
    "team": "townsfolk",
    "ability": "Each night, choose a player (not yourself): tomorrow, you may only vote if they are voting too.",
    "first_night": 0,
    "first_night_reminder": "",
    "other_night": 1,
    "other_night_reminder": "The Butler chooses a player (not themselves): mark that player with the Butler's \"Master\" reminder. The Butler may only vote if their Master is voting too.",
    "reminders": ["Master"],
    "setup": false,
    "jinxes": [],
    "is_official": true
  }
}
```

### List Scripts
**GET** `/scripts`

Get all available scripts.

**Query Parameters:**
- `official` - Filter by official status (`true`, `false`)
- `include_roles` - Include role details (`true`, `false`, default: `false`)

**Response:**
```json
{
  "success": true,
  "scripts": [
    {
      "id": 1,
      "name": "Trouble Brewing",
      "description": "The original Blood on the Clocktower script",
      "author": "The Pandemonium Institute",
      "is_official": true,
      "player_count_min": 5,
      "player_count_max": 15,
      "version": "1.0",
      "roles": []
    }
  ],
  "total_count": 1
}
```

### Get Script Details
**GET** `/scripts/{script_id}`

Get detailed information about a specific script.

**Query Parameters:**
- `include_roles` - Include role details (`true`, `false`, default: `true`)

**Response:**
```json
{
  "success": true,
  "script": {
    "id": 1,
    "name": "Trouble Brewing",
    "description": "The original Blood on the Clocktower script",
    "author": "The Pandemonium Institute",
    "is_official": true,
    "player_count_min": 5,
    "player_count_max": 15,
    "version": "1.0",
    "roles": [
      {
        "id": 1,
        "name": "Butler",
        "team": "townsfolk"
      }
    ],
    "role_distribution": {
      "townsfolk": 13,
      "outsider": 4,
      "minion": 4,
      "demon": 1
    }
  }
}
```

### Create Custom Script
**POST** `/scripts`

Create a custom script (requires authentication).

**Request Body:**
```json
{
  "name": "string (required, 3-100 chars)",
  "description": "string (required, 10-500 chars)",
  "role_ids": "array of integers (required, min 5 roles)",
  "player_count_min": "integer (5-15, default: 5)",
  "player_count_max": "integer (5-15, default: 15)",
  "version": "string (default: '1.0')"
}
```

**Response:**
```json
{
  "success": true,
  "script": {
    "id": 2,
    "name": "Custom Script",
    "description": "My custom script",
    "author": "player1",
    "is_official": false,
    "roles": []
  }
}
```

### Get Role Distribution
**GET** `/scripts/{script_id}/distribution/{player_count}`

Get role distribution for a script at specific player count.

**Response:**
```json
{
  "success": true,
  "player_count": 10,
  "distribution": {
    "townsfolk": 5,
    "outsider": 2,
    "minion": 2,
    "demon": 1
  },
  "can_support": true,
  "available_roles": {
    "townsfolk": 13,
    "outsider": 4,
    "minion": 4,
    "demon": 1
  }
}
```

## Game State Management Endpoints

### Save Game State
**POST** `/games/{game_id}/save`

Save current game state (host only).

**Request Body:**
```json
{
  "state_name": "string (required, 1-100 chars)"
}
```

**Response:**
```json
{
  "success": true,
  "game_state": {
    "id": 1,
    "game_id": 1,
    "state_name": "Before Final Vote",
    "created_by": 1,
    "created_at": "2025-01-01T02:00:00Z",
    "is_auto_save": false,
    "phase": "day",
    "day_number": 3,
    "state_preview": {
      "player_count": 8,
      "alive_count": 4,
      "phase": "day",
      "day": 3
    }
  }
}
```

### List Game States
**GET** `/games/{game_id}/states`

Get all saved states for a game.

**Response:**
```json
{
  "success": true,
  "states": [
    {
      "id": 1,
      "state_name": "Before Final Vote",
      "created_at": "2025-01-01T02:00:00Z",
      "is_auto_save": false,
      "state_preview": {
        "player_count": 8,
        "alive_count": 4
      }
    }
  ]
}
```

### Load Game State
**POST** `/games/{game_id}/load/{state_id}`

Load a saved game state (host only).

**Response:**
```json
{
  "success": true,
  "message": "Game state 'Before Final Vote' loaded successfully"
}
```

### Create Auto-Save
**POST** `/games/{game_id}/auto-save`

Create an automatic save point (host only).

**Response:**
```json
{
  "success": true,
  "game_state": {
    "id": 2,
    "state_name": "Auto-save day Day 2",
    "is_auto_save": true
  }
}
```

### Get Game Actions
**GET** `/games/{game_id}/actions`

Get recent game actions.

**Query Parameters:**
- `limit` - Number of actions (default: 50, max: 200)

**Response:**
```json
{
  "success": true,
  "actions": [
    {
      "id": 1,
      "action_type": "vote",
      "action_data": {
        "voter_id": 2,
        "nominee_id": 3,
        "vote": "yes"
      },
      "performed_by": 2,
      "performed_at": "2025-01-01T02:00:00Z",
      "is_undone": false,
      "phase": "day",
      "day_number": 2
    }
  ]
}
```

### Undo Action
**POST** `/games/{game_id}/actions/{action_id}/undo`

Undo a game action (host only).

**Request Body:**
```json
{
  "reason": "string (optional, max 200 chars)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Action 'vote' undone successfully"
}
```

### Finish Game
**POST** `/games/{game_id}/finish`

Finish a game and create history record (host only).

**Request Body:**
```json
{
  "winner_team": "string (good|evil, optional)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Game completed successfully",
  "history": {
    "id": 1,
    "winner_team": "good",
    "game_duration": 3600,
    "total_days": 3,
    "total_executions": 2
  }
}
```

### Get Game History
**GET** `/games/{game_id}/history`

Get game history for completed games.

**Query Parameters:**
- `full` - Include full history data (`true`, `false`, default: `false`)

**Response:**
```json
{
  "success": true,
  "history": {
    "id": 1,
    "winner_team": "good",
    "game_duration": 3600,
    "total_days": 3,
    "total_executions": 2,
    "created_at": "2025-01-01T03:00:00Z",
    "history_preview": {
      "total_actions": 45,
      "final_player_count": 8,
      "duration_minutes": 60
    }
  }
}
```

## WebSocket Events

The application uses Socket.IO for real-time communication.

### Client Events (Emit)

#### Join Game Room
```javascript
socket.emit('join_game', {
  game_id: 1,
  user_id: 2
})
```

#### Leave Game Room
```javascript
socket.emit('leave_game', {
  game_id: 1,
  user_id: 2
})
```

#### Send Chat Message
```javascript
socket.emit('chat_message', {
  game_id: 1,
  message: 'Hello everyone!',
  type: 'public' // or 'private', 'system'
})
```

#### Update Player Status
```javascript
socket.emit('player_ready', {
  game_id: 1,
  is_ready: true
})
```

### Server Events (Listen)

#### Game State Update
```javascript
socket.on('game_update', (data) => {
  // data contains updated game state
  console.log('Game updated:', data.game)
})
```

#### Player Joined/Left
```javascript
socket.on('player_joined', (data) => {
  console.log('Player joined:', data.player)
})

socket.on('player_left', (data) => {
  console.log('Player left:', data.player)
})
```

#### Chat Message Received
```javascript
socket.on('chat_message', (data) => {
  console.log('New message:', data.message)
})
```

#### Connection Status
```javascript
socket.on('connect', () => {
  console.log('Connected to server')
})

socket.on('disconnect', () => {
  console.log('Disconnected from server')
})
```

## Error Handling

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (not logged in)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (duplicate resource)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

### Common Error Codes

- `INVALID_INPUT` - Request validation failed
- `NOT_AUTHENTICATED` - User not logged in
- `ACCESS_DENIED` - Insufficient permissions
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `GAME_FULL` - Cannot join, game at capacity
- `GAME_STARTED` - Cannot perform action, game already started
- `INVALID_GAME_STATE` - Action not valid in current game state
- `RATE_LIMITED` - Too many requests

### Error Response Example

```json
{
  "success": false,
  "error": "Game is full and cannot accept more players",
  "code": "GAME_FULL",
  "details": {
    "current_players": 10,
    "max_players": 10
  }
}
```

## Rate Limiting

API endpoints are rate limited to prevent abuse:

- **Authentication**: 5 requests per minute
- **Game Creation**: 3 requests per minute
- **General API**: 60 requests per minute
- **WebSocket**: 100 events per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `limit` - Number of items (default: 20, max: 100)
- `offset` - Number of items to skip

**Response:**
```json
{
  "success": true,
  "data": [],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total_count": 150,
    "has_more": true
  }
}
```

## API Versioning

The API uses URL versioning:
- Current version: `/api/v1/`
- Future versions: `/api/v2/`, etc.

Version headers are included in responses:
```
API-Version: 1.0
```

## Testing

### Example API Test

```javascript
// Test user registration
const response = await fetch('/api/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  credentials: 'include',
  body: JSON.stringify({
    username: 'testuser',
    email: 'test@example.com',
    password: 'securepassword123'
  })
})

const data = await response.json()
console.log('Registration result:', data)
```

### Postman Collection

A Postman collection is available for testing all API endpoints. Import the collection file `botc-api.postman_collection.json` into Postman.

## SDK and Libraries

### JavaScript/TypeScript SDK

```javascript
import { BotcApiClient } from 'botc-api-client'

const client = new BotcApiClient({
  baseUrl: 'http://localhost:5000/api',
  credentials: 'include'
})

// Login
await client.auth.login('username', 'password')

// Create game
const game = await client.games.create({
  name: 'My Game',
  script_id: 1,
  max_players: 10
})

// Join game
await client.games.join(game.id)
```

### Python SDK

```python
from botc_api import BotcClient

client = BotcClient(base_url='http://localhost:5000/api')

# Login
client.auth.login('username', 'password')

# Create game
game = client.games.create(
    name='My Game',
    script_id=1,
    max_players=10
)

# Join game
client.games.join(game['id'])
```

