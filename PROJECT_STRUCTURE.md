# Blood on the Clocktower - Project Structure

## Overview
This document outlines the organized file structure for the Blood on the Clocktower Digital Storyteller application.

## Root Directory Structure

```
blood-on-the-clocktower/
├── backend/                    # Flask API server
│   ├── src/
│   │   ├── models/            # Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py        # User model and authentication
│   │   │   ├── game.py        # Game model and logic
│   │   │   ├── player.py      # Player model and game participation
│   │   │   ├── role.py        # Role definitions and abilities
│   │   │   ├── script.py      # Script management and role distribution
│   │   │   ├── vote.py        # Voting system and player actions
│   │   │   └── game_state.py  # Game state management and history
│   │   ├── routes/            # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── user.py        # User management endpoints
│   │   │   ├── game.py        # Game management endpoints
│   │   │   ├── role.py        # Role and script endpoints
│   │   │   └── game_state.py  # Game state management endpoints
│   │   ├── static/            # Static files served by Flask
│   │   │   ├── index.html     # API test interface
│   │   │   └── favicon.ico
│   │   └── main.py            # Application entry point with WebSocket
│   ├── Dockerfile             # Backend container configuration
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React application
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── ui/           # Reusable UI components (shadcn/ui)
│   │   │   ├── GameBoard.jsx  # Main game interface
│   │   │   ├── GameLobby.jsx  # Game lobby and setup
│   │   │   ├── GameChat.jsx   # Real-time chat component
│   │   │   ├── GameStateManager.jsx # Save/load game states
│   │   │   ├── Header.jsx     # Application header
│   │   │   ├── HomePage.jsx   # Main dashboard
│   │   │   └── LoginPage.jsx  # Authentication interface
│   │   ├── hooks/             # Custom React hooks
│   │   │   ├── useAuth.jsx    # Authentication management
│   │   │   ├── useGame.jsx    # Game state and API calls
│   │   │   ├── useGameState.jsx # Game state persistence
│   │   │   ├── useSocket.jsx  # WebSocket communication
│   │   │   └── use-mobile.js  # Mobile detection utility
│   │   ├── lib/               # Utility functions
│   │   │   └── utils.js       # Common utilities
│   │   ├── App.jsx            # Main application component
│   │   ├── App.css            # Global styles and Tailwind config
│   │   ├── main.jsx           # React application entry point
│   │   └── index.css          # Additional styles
│   ├── public/                # Static assets
│   │   └── favicon.ico
│   ├── Dockerfile             # Frontend container configuration
│   ├── nginx.conf             # Nginx configuration for production
│   ├── package.json           # Node.js dependencies and scripts
│   ├── pnpm-lock.yaml         # Package lock file
│   ├── vite.config.js         # Vite build configuration
│   ├── eslint.config.js       # ESLint configuration
│   ├── components.json        # shadcn/ui configuration
│   ├── jsconfig.json          # JavaScript project configuration
│   └── index.html             # HTML template
├── docs/                      # Documentation
│   ├── API_DOCUMENTATION.md   # Complete API reference
│   ├── USER_GUIDE.md          # User manual and gameplay guide
│   ├── DEPLOYMENT_SUMMARY.md  # Deployment and technical overview
│   ├── OVERVIEW.md            # Project overview
│   └── TODO.md                # Project roadmap and tasks
├── docker-compose.yml         # Development environment
├── docker-compose.prod.yml    # Production environment
├── deploy.sh                  # Automated deployment script
├── backup.sh                  # Database backup script
├── .env.example               # Environment configuration template
├── .dockerignore              # Docker build optimization
├── .gitignore                 # Git ignore patterns
├── README.md                  # Project overview and setup
└── PROJECT_STRUCTURE.md       # This file
```

## Directory Purposes

### `/backend/`
Contains the Flask API server with all server-side logic:
- **Models**: Database schema and business logic
- **Routes**: API endpoints and request handling
- **Static**: Files served directly by Flask (API test interface)
- **Configuration**: Docker and Python dependency files

### `/frontend/`
Contains the React application with all client-side code:
- **Components**: Reusable UI components and pages
- **Hooks**: Custom React hooks for state management
- **Lib**: Utility functions and helpers
- **Configuration**: Build tools, linting, and dependency management

### `/docs/`
Project documentation accessible to all stakeholders:
- API documentation for developers
- User guides for players and hosts
- Deployment guides for system administrators
- Project planning and roadmap

### Root Level Files
- **Docker Compose**: Environment orchestration
- **Deployment Scripts**: Automated setup and management
- **Configuration**: Environment templates and build settings
- **Documentation**: Project overview and structure

## Key Benefits of This Organization

1. **Clear Separation**: Frontend and backend code are completely separated
2. **Scalability**: Each service can be developed and deployed independently
3. **Maintainability**: Related files are grouped together logically
4. **Documentation**: All docs are easily accessible at the root level
5. **Deployment**: Docker configurations support both development and production
6. **Development**: Clear structure makes it easy for new developers to understand

## Development Workflow

1. **Backend Development**: Work in `/backend/` directory
2. **Frontend Development**: Work in `/frontend/` directory
3. **Full Stack**: Use Docker Compose for integrated development
4. **Documentation**: Update relevant docs in `/docs/` directory
5. **Deployment**: Use scripts and configurations at root level

This structure follows modern full-stack application best practices and makes the codebase much more maintainable and scalable.