# Blood on the Clocktower Digital Storyteller

A comprehensive digital storyteller application for Blood on the Clocktower, featuring automated gameplay, real-time multiplayer support, and complete game state management.

## 🎭 Features

### Core Gameplay
- **Automated Storyteller**: Handles night phase automation, day phase timers, and game flow
- **Role Assignment**: Random or manual role distribution with official script support
- **Voting System**: Public/private voting with nomination and execution mechanics
- **Player Management**: Death confirmation, ghost votes, and player status tracking

### Real-time Multiplayer
- **WebSocket Integration**: Live game updates and real-time communication
- **Lobby System**: Host-controlled game setup with join codes
- **Chat System**: In-game messaging with timestamps and connection status
- **Live Updates**: Real-time player status, voting, and game state changes

### Game State Management
- **Save/Load System**: Named save points with automatic and manual saves
- **Action History**: Complete tracking of all game actions with timestamps
- **Undo/Redo**: Host can undo actions with reasons (limited to prevent abuse)
- **Game History**: Full replay data and statistics for completed games

### Official Compatibility
- **Official Scripts**: Trouble Brewing and other official scripts supported
- **Role Database**: Complete role information following official schema
- **Custom Scripts**: Create and share custom role combinations
- **Jinx Support**: Automatic handling of role interactions and restrictions

### Technical Features
- **Containerized Deployment**: Docker and Docker Compose support
- **Production Ready**: PostgreSQL, Redis, and monitoring integration
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Security**: Authentication, session management, and anti-cheating measures

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd blood-on-the-clocktower
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start development environment**
   ```bash
   ./deploy.sh development
   ```

4. **Access the application**
   - Frontend: http://localhost:80
   - Backend API: http://localhost:5000
   - API Documentation: http://localhost:5000/api/docs

### Production Deployment

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Set secure passwords and production settings
   ```

2. **Deploy to production**
   ```bash
   ./deploy.sh production
   ```

3. **Set up SSL (recommended)**
   ```bash
   # Place your SSL certificates
   cp your-cert.pem ssl/cert.pem
   cp your-key.pem ssl/key.pem
   ```

## 📁 Project Structure

```
blood-on-the-clocktower/
├── backend/                 # Flask API server
│   ├── src/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   └── main.py         # Application entry point
│   ├── Dockerfile          # Backend container
│   └── requirements.txt    # Python dependencies
├── frontend/               # React application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   └── App.jsx         # Main application
│   ├── Dockerfile          # Frontend container
│   └── nginx.conf          # Nginx configuration
├── docker-compose.yml      # Development environment
├── docker-compose.prod.yml # Production environment
├── deploy.sh              # Deployment script
└── README.md              # This file
```

## 🎮 How to Play

### For Hosts

1. **Create a Game**
   - Register/login to the application
   - Click "Create Game" and configure settings
   - Select a script (Trouble Brewing recommended for beginners)
   - Set player count and game options

2. **Manage Players**
   - Share the join code with players
   - Wait for players to join and mark ready
   - Assign roles (random or manual)
   - Start the game when ready

3. **Run the Game**
   - Follow automated night phase prompts
   - Manage day phase discussions and voting
   - Use save/load features for complex situations
   - Undo actions if needed with reasons

### For Players

1. **Join a Game**
   - Register/login to the application
   - Enter the join code provided by host
   - Mark yourself as ready when prepared

2. **During the Game**
   - Check your role information privately
   - Participate in day phase discussions via chat
   - Vote on nominations when prompted
   - Follow night phase instructions if applicable

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Security
SECRET_KEY=your-super-secret-key
FLASK_ENV=production

# Database (Production)
POSTGRES_DB=botc
POSTGRES_USER=botc_user
POSTGRES_PASSWORD=secure_password

# Game Settings
MAX_GAMES_PER_USER=5
MAX_PLAYERS_PER_GAME=15
GAME_TIMEOUT_HOURS=24

# Features
RATE_LIMIT_PER_MINUTE=60
BACKUP_ENABLED=true
```

### Docker Services

#### Development
- **backend**: Flask API server (port 5000)
- **frontend**: React development server (port 80)

#### Production
- **backend**: Flask API with PostgreSQL
- **frontend**: Nginx-served React build
- **postgres**: PostgreSQL database
- **redis**: Session storage and caching
- **nginx**: Load balancer and SSL termination
- **prometheus**: Monitoring (optional)
- **grafana**: Dashboards (optional)

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### Game Management
- `GET /api/games` - List games
- `POST /api/games` - Create game
- `GET /api/games/{id}` - Get game details
- `POST /api/games/{id}/join` - Join game
- `POST /api/games/{id}/start` - Start game
- `POST /api/games/{id}/finish` - Finish game

### Role and Script Management
- `GET /api/roles` - List all roles
- `GET /api/roles/{id}` - Get role details
- `GET /api/scripts` - List scripts
- `POST /api/scripts` - Create custom script
- `GET /api/scripts/{id}/distribution/{count}` - Get role distribution

### Game State Management
- `POST /api/games/{id}/save` - Save game state
- `GET /api/games/{id}/states` - List saved states
- `POST /api/games/{id}/load/{state_id}` - Load game state
- `GET /api/games/{id}/actions` - Get action history
- `POST /api/games/{id}/actions/{action_id}/undo` - Undo action

### WebSocket Events
- `join_game` - Join game room
- `leave_game` - Leave game room
- `player_ready` - Mark player ready
- `chat_message` - Send chat message
- `game_update` - Receive game state updates

## 🛠️ Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

### Frontend Development

```bash
cd frontend
pnpm install
pnpm run dev
```

### Database Management

```bash
# Reset database (development)
rm backend/src/database/app.db
python backend/src/main.py

# Backup database (production)
./backup.sh
```

### Testing

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
pnpm test

# Integration tests
docker-compose -f docker-compose.yml up --build
curl http://localhost:5000/api/roles
```

## 🔒 Security Features

- **Authentication**: Session-based user authentication
- **Authorization**: Role-based access control for hosts/players
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: API rate limiting to prevent abuse
- **CORS Protection**: Configured cross-origin request handling
- **SQL Injection Prevention**: Parameterized queries with SQLAlchemy
- **XSS Protection**: Content Security Policy headers
- **Session Security**: Secure cookie configuration

## 📊 Monitoring and Logging

### Production Monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Health Checks**: Automated service health monitoring
- **Log Aggregation**: Centralized logging with rotation

### Key Metrics
- Active games and players
- API response times
- Database performance
- WebSocket connections
- Error rates and types

## 🚨 Troubleshooting

### Common Issues

**Backend not starting**
```bash
# Check logs
docker-compose logs backend

# Reset database
rm backend/src/database/app.db
docker-compose restart backend
```

**Frontend not loading**
```bash
# Check nginx logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
```

**WebSocket connection issues**
```bash
# Check CORS configuration
# Verify backend WebSocket support
# Check firewall settings
```

**Database connection errors**
```bash
# Check PostgreSQL status
docker-compose logs postgres

# Verify environment variables
cat .env | grep POSTGRES
```

### Performance Optimization

**Database**
- Index frequently queried columns
- Use connection pooling
- Regular database maintenance

**Frontend**
- Enable gzip compression
- Optimize bundle size
- Use CDN for static assets

**Backend**
- Implement caching with Redis
- Use async operations where possible
- Monitor memory usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript
- Write tests for new features
- Update documentation for API changes
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **The Pandemonium Institute** for creating Blood on the Clocktower
- **Official BotC Community** for game rules and role information
- **Contributors** who helped build and improve this application

## 📞 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check the wiki for detailed guides
- **Community**: Join the Discord server for discussions
- **Email**: Contact support@yourdomain.com for urgent issues

---

**Note**: This is an unofficial digital implementation. Blood on the Clocktower is a trademark of The Pandemonium Institute. Please support the official game by purchasing it from the official website.

