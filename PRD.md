# Product Requirements Document (PRD)
## AI-Assisted Moderation Dashboard MVP

### Problem Statement

Trust & Safety teams at Discord need efficient tools to review and moderate flagged content (messages, images, or user reports). The current process is manual and time-consuming, making it difficult to prioritize and process flagged items at scale.

### MVP Features

#### Core Functionality
1. **View Flagged Items**
   - Display flagged items (messages, images, user reports) in a prioritized list
   - Support for multiple content types: `message`, `image`, `report`
   - Sortable and filterable list view

2. **AI-Generated Summaries**
   - Each flagged item receives an AI-generated summary
   - Summaries help moderators quickly understand context
   - *Note: MVP uses mock AI service; real AI integration path is prepared (see [ARCHITECTURE.md](ARCHITECTURE.md))*

3. **Priority Scoring**
   - Automatic priority assignment: `high`, `medium`, `low`
   - Priority based on content analysis
   - Visual indicators for priority levels

4. **CRUD Operations**
   - **Create**: Submit new flagged items with content type and content
   - **Read**: View individual flagged item details
   - **Update**: Change status (Approve/Reject/Escalate)
   - **Delete**: Remove flagged items from the system

5. **Status Management**
   - Status options: `pending`, `approved`, `rejected`, `escalated`
   - Track status changes with timestamps

6. **Stats Dashboard**
   - Total flagged items count
   - Breakdown by priority (high/medium/low)
   - Breakdown by status (pending/approved/rejected/escalated)

7. **Data Persistence**
   - SQLite database for persistent storage
   - All flagged items stored locally
   - Timestamps for creation and updates

### Out of Scope for MVP

- Real-time updates/notifications
- Advanced filtering and search
- Bulk actions (approve/reject multiple items)
- User authentication and authorization
- Real AI integration (interface prepared, but mock implementation for MVP)
- Image upload/preview functionality
- Audit logs and history tracking
- Export functionality
- Multi-user collaboration features

### Success Criteria

- Moderators can create and view flagged items
- AI summaries are generated for all flagged items
- Priority is automatically assigned
- Status can be updated through the UI
- Stats dashboard displays accurate counts
- All data persists across application restarts

### Future Enhancements

- Integration with real AI service (OpenAI API)
- Advanced filtering and search
- Bulk moderation actions
- User authentication
- Real-time updates via WebSockets
- Image preview and analysis
- Export to CSV/JSON

### Cross-References

- **Architecture Decisions**: See [ARCHITECTURE.md](ARCHITECTURE.md) for technical tradeoffs and design decisions
- **Implementation Timeline**: See [PLAN.md](PLAN.md) for 40-minute execution plan

