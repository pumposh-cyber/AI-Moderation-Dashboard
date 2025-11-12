# Architecture Tradeoff Analysis

## Tech Stack

- **Backend**: FastAPI (Python 3.8+)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Tailwind CSS (via CDN)
- **Testing**: pytest

## Architecture Decisions & Tradeoffs

### 1. FastAPI vs Flask

**Decision**: FastAPI

**Rationale**:
- Built-in async support for better performance
- Automatic API documentation (Swagger/OpenAPI)
- Type hints and Pydantic integration for better developer experience
- Modern Python features and better performance
- Easy to add real-time features later if needed

**Tradeoff**: Slightly steeper learning curve than Flask, but benefits outweigh for API-first application

### 2. SQLite vs PostgreSQL

**Decision**: SQLite

**Rationale**:
- Zero configuration - no separate database server needed
- Perfect for MVP and single-user scenarios
- File-based storage simplifies deployment
- Easy to migrate to PostgreSQL later if needed
- Sufficient for MVP scale (thousands of records)

**Tradeoff**: Limited concurrent writes, but acceptable for MVP. Migration path is straightforward.

### 3. Vanilla JavaScript vs React/Vue

**Decision**: Vanilla JavaScript

**Rationale**:
- No build step required - faster development
- Smaller bundle size
- Simpler deployment (just serve HTML/CSS/JS)
- Sufficient for MVP complexity
- Can migrate to framework later if needed

**Tradeoff**: More manual DOM manipulation, but MVP UI is simple enough that this is manageable.

### 4. Tailwind CDN vs Build Process

**Decision**: Tailwind CSS via CDN

**Rationale**:
- Fastest setup - no build configuration
- Quick prototyping
- Sufficient for MVP styling needs
- Can migrate to build process later for production optimization

**Tradeoff**: Larger initial load, but acceptable for internal tool MVP.

### 5. Mock AI vs Real AI Integration

**Decision**: Mock AI with interface-based design

**Rationale**:
- **MVP**: Mock implementation for rapid development
- **Architecture**: Protocol/ABC pattern allows swapping implementations
- **Future**: Real AI integration (OpenAI API) can be added without changing callers
- Reduces external dependencies during development
- Allows testing without API costs

**Tradeoff**: Mock summaries less realistic, but interface design ensures easy migration.

## AI Service Architecture

### Interface Pattern

```python
# Protocol-based interface (Python 3.8+)
from typing import Protocol

class AIService(Protocol):
    def generate_summary(self, content: str, content_type: str) -> str: ...
    def calculate_priority(self, content: str) -> str: ...
```

### Implementation Strategy

1. **MockAIService** (MVP)
   - Keyword-based priority calculation
   - Template-based summary generation
   - No external API calls

2. **RealAIService** (Future)
   - Same interface as MockAIService
   - Calls OpenAI API for summarization
   - Uses AI model for priority scoring
   - Drop-in replacement

### Benefits

- Zero code changes needed when switching implementations
- Easy testing with mock service
- Can A/B test mock vs real
- Cost control during development

## System Architecture

```
┌─────────────┐
│   Browser   │
│  (Frontend) │
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────┐
│   FastAPI   │
│   Backend   │
└──────┬──────┘
       │
       ├──► SQLite DB
       │    (flagged_items)
       │
       └──► AI Service
            ├── MockAIService (MVP)
            └── RealAIService (Future)
```

## Data Flow

1. **Create Flagged Item**:
   - Frontend → POST /api/flags
   - Backend → AI Service (generate summary, calculate priority)
   - Backend → SQLite (insert record)
   - Backend → Frontend (return created item)

2. **View Flagged Items**:
   - Frontend → GET /api/flags
   - Backend → SQLite (query records)
   - Backend → Frontend (return JSON array)

3. **Update Status**:
   - Frontend → PATCH /api/flags/{id}
   - Backend → SQLite (update record)
   - Backend → Frontend (return updated item)

## Database Schema

```sql
CREATE TABLE flagged_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL CHECK(content_type IN ('message', 'image', 'report')),
    content TEXT NOT NULL,
    priority TEXT NOT NULL CHECK(priority IN ('high', 'medium', 'low')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected', 'escalated')),
    ai_summary TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Design

- RESTful endpoints under `/api/` prefix
- JSON request/response format
- Standard HTTP status codes
- Pydantic models for validation

## Security Considerations (Future)

- Authentication/authorization (not in MVP)
- Input validation (handled by Pydantic)
- SQL injection prevention (SQLite parameterized queries)
- CORS configuration (if needed for separate frontend)

## Scalability Considerations

- SQLite can handle thousands of records efficiently
- FastAPI async support ready for higher concurrency
- Easy migration path to PostgreSQL
- Frontend can be migrated to React/Vue if complexity grows

## Cross-References

- **Requirements**: See [PRD.md](PRD.md) for feature requirements and problem statement
- **Implementation**: See [PLAN.md](PLAN.md) for execution timeline and development steps

