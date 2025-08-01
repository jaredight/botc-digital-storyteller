#!/bin/bash

# Blood on the Clocktower Deployment Script
# Usage: ./deploy.sh [development|production]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default environment
ENVIRONMENT=${1:-development}

echo -e "${BLUE}🎭 Blood on the Clocktower Deployment Script${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo ""

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p backups
mkdir -p ssl

# Set up environment file
if [ ! -f .env ]; then
    print_warning "No .env file found. Creating from .env.example..."
    cp .env.example .env
    print_warning "Please edit .env file with your configuration before running again."
    exit 1
fi

# Load environment variables
source .env

# Validate required environment variables
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-super-secret-key-change-this-in-production" ]; then
    print_error "Please set a secure SECRET_KEY in your .env file"
    exit 1
fi

# Choose docker-compose file based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    print_status "Using production configuration"
    
    # Additional production checks
    if [ -z "$POSTGRES_PASSWORD" ] || [ "$POSTGRES_PASSWORD" = "change_this_secure_password" ]; then
        print_error "Please set a secure POSTGRES_PASSWORD in your .env file for production"
        exit 1
    fi
    
    # Check for SSL certificates in production
    if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        print_warning "SSL certificates not found. HTTPS will not be available."
        print_warning "Place your SSL certificate as ssl/cert.pem and private key as ssl/key.pem"
    fi
else
    COMPOSE_FILE="docker-compose.yml"
    print_status "Using development configuration"
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f $COMPOSE_FILE down

# Pull latest images
print_status "Pulling latest base images..."
docker-compose -f $COMPOSE_FILE pull

# Build and start services
print_status "Building and starting services..."
docker-compose -f $COMPOSE_FILE up --build -d

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
sleep 10

# Check service health
print_status "Checking service health..."

# Check backend health
if curl -f http://localhost:5000/api/roles > /dev/null 2>&1; then
    print_status "Backend service is healthy"
else
    print_error "Backend service is not responding"
    docker-compose -f $COMPOSE_FILE logs backend
    exit 1
fi

# Check frontend health (only in development, production uses nginx)
if [ "$ENVIRONMENT" = "development" ]; then
    if curl -f http://localhost:80 > /dev/null 2>&1; then
        print_status "Frontend service is healthy"
    else
        print_error "Frontend service is not responding"
        docker-compose -f $COMPOSE_FILE logs frontend
        exit 1
    fi
fi

# Show running containers
print_status "Deployment completed successfully!"
echo ""
echo -e "${BLUE}Running containers:${NC}"
docker-compose -f $COMPOSE_FILE ps

echo ""
echo -e "${GREEN}🎉 Blood on the Clocktower is now running!${NC}"

if [ "$ENVIRONMENT" = "development" ]; then
    echo -e "${BLUE}Frontend:${NC} http://localhost:80"
    echo -e "${BLUE}Backend API:${NC} http://localhost:5000"
else
    echo -e "${BLUE}Application:${NC} http://localhost (or your domain)"
    echo -e "${BLUE}Monitoring:${NC} http://localhost:3000 (Grafana)"
fi

echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  View logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "  Stop services: docker-compose -f $COMPOSE_FILE down"
echo "  Restart services: docker-compose -f $COMPOSE_FILE restart"
echo "  Update services: ./deploy.sh $ENVIRONMENT"

# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
# Backup script for Blood on the Clocktower

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "Creating backup: $DATE"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
if [ "$ENVIRONMENT" = "production" ]; then
    docker-compose exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > $BACKUP_DIR/database_$DATE.sql
else
    docker cp botc-backend:/app/src/database/app.db $BACKUP_DIR/database_$DATE.db
fi

# Backup configuration
cp .env $BACKUP_DIR/env_$DATE.backup

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x backup.sh
print_status "Backup script created: ./backup.sh"

