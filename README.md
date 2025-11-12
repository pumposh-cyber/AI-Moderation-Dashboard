# AI-Assisted Moderation Dashboard MVP

A minimal prototype of an AI-assisted moderation dashboard for Trust & Safety teams to review and moderate flagged content (messages, images, or user reports).

## Features

- **View Flagged Items**: Display flagged items in a prioritized list
- **AI-Generated Summaries**: Automatic summaries for each flagged item (mock AI for MVP)
- **Priority Scoring**: Automatic priority assignment (high/medium/low)
- **CRUD Operations**: Create, read, update, and delete flagged items
- **Status Management**: Track status (pending/approved/rejected/escalated)
- **Stats Dashboard**: View statistics on flagged items

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Tailwind CSS
- **Testing**: pytest
- **Deployment**: Docker, Docker Compose, Nginx
- **Monitoring**: Prometheus, Structured Logging

## Project Structure

```
/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app and endpoints
│   ├── models.py            # Pydantic models
│   ├── database.py          # Database operations (PostgreSQL/SQLite)
│   ├── ai_service.py        # AI service (mock MVP, real-ready interface)
│   ├── config.py            # Configuration management
│   ├── middleware.py        # Security and logging middleware
│   └── monitoring.py        # Health checks and metrics
├── frontend/
│   ├── index.html           # Main dashboard UI
│   └── app.js               # Frontend JavaScript logic
├── nginx/
│   └── nginx.conf           # Nginx reverse proxy configuration
├── tests/
│   └── test_api.py          # Pytest tests
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD pipeline
├── Dockerfile               # Production Docker image
├── docker-compose.yml       # Docker Compose configuration
├── Makefile                 # Common commands
├── requirements.txt
├── PRD.md                   # Product Requirements Document
├── ARCHITECTURE.md          # Architecture and tradeoff analysis
├── PLAN.md                  # Implementation plan
├── DEPLOYMENT.md            # Production deployment guide
├── PRODUCTION_READINESS.md  # Production readiness checklist
└── README.md                # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone or navigate to the project directory:
   ```bash
   cd /path/to/project
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the FastAPI server:
   ```bash
   uvicorn backend.main:app --reload
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

3. The dashboard will be displayed with:
   - Stats cards showing total flags, high priority, and pending items
   - A form to create new flagged items
   - A table listing all flagged items with actions

## Running Tests

Run the test suite:
```bash
pytest tests/
```

Run tests with verbose output:
```bash
pytest tests/ -v
```

Or use Make:
```bash
make test
```

## Production Deployment

This application is production-ready with Docker, PostgreSQL, Nginx, monitoring, and security features.

### Quick Start with Docker

```bash
# Build and start all services
make build
make up

# Check health
make health

# View logs
make logs
```

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment instructions.

Key features:
- ✅ Docker containerization
- ✅ PostgreSQL database with connection pooling
- ✅ Nginx reverse proxy with SSL/TLS support
- ✅ Health checks and monitoring endpoints
- ✅ Structured logging
- ✅ Prometheus metrics
- ✅ Rate limiting and security headers
- ✅ CI/CD pipeline

### Production Readiness

See [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md) for the complete checklist.

## API Endpoints

### Get All Flags
```
GET /api/flags
```
Returns a list of all flagged items.

### Get Flag by ID
```
GET /api/flags/{id}
```
Returns a single flagged item by ID.

### Create Flag
```
POST /api/flags
Content-Type: application/json

{
  "content_type": "message" | "image" | "report",
  "content": "string"
}
```
Creates a new flagged item. Priority and AI summary are automatically generated.

### Update Flag Status
```
PATCH /api/flags/{id}
Content-Type: application/json

{
  "status": "pending" | "approved" | "rejected" | "escalated"
}
```
Updates the status of a flagged item.

### Delete Flag
```
DELETE /api/flags/{id}
```
Deletes a flagged item.

### Get Statistics
```
GET /api/stats
```
Returns dashboard statistics including counts by priority and status.

## API Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database

The application uses SQLite for data persistence. The database file (`moderation.db`) is created automatically on first run in the project root directory.

## AI Service

The MVP uses a mock AI service that:
- Generates summaries based on content type
- Calculates priority based on keyword matching

The architecture is designed to easily swap in a real AI service (e.g., OpenAI API) without changing the rest of the codebase. See `backend/ai_service.py` for the interface pattern.

## Development Notes

- The database is initialized automatically on server start
- All timestamps are handled automatically by SQLite
- The frontend uses vanilla JavaScript - no build step required
- Tailwind CSS is loaded via CDN for quick prototyping

## Documentation

- **[PRD.md](PRD.md)**: Product Requirements Document with feature specifications
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Architecture decisions and tradeoff analysis
- **[PLAN.md](PLAN.md)**: 40-minute implementation plan

## Future Enhancements

- Real AI integration (OpenAI API)
- Advanced filtering and search
- Bulk moderation actions
- User authentication
- Real-time updates via WebSockets
- Image preview and analysis
- Export functionality

## License

This is a prototype/minimal viable product for demonstration purposes.

