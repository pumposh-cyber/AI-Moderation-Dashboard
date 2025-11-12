# Clerk Authentication Setup Guide

This guide explains how to set up Clerk authentication for the AI Moderation Dashboard.

## Quick Start

### 1. Create Clerk Account

1. Go to https://clerk.com
2. Sign up for a free account
3. Create a new application

### 2. Get Your Clerk Keys

1. In Clerk Dashboard, go to **API Keys**
2. Copy:
   - **Publishable Key** (starts with `pk_`)
   - **Secret Key** (starts with `sk_`)

### 3. Configure Environment Variables

Add these to your `.env` file or Railway/Render environment:

```bash
# Clerk Authentication
CLERK_ENABLED=true
CLERK_SECRET_KEY=sk_test_...
CLERK_PUBLISHABLE_KEY=pk_test_...
```

### 4. Update Frontend Configuration

The frontend automatically reads `CLERK_PUBLISHABLE_KEY` from the backend and injects it into the HTML.

## How It Works

### Backend

- **Authentication Middleware**: All `/api/*` endpoints require authentication
- **User Isolation**: Each user only sees their own flagged items
- **Token Verification**: Clerk JWT tokens are verified on every request
- **Development Mode**: If `CLERK_ENABLED=false`, uses mock user for development

### Frontend

- **Clerk SDK**: Loads Clerk JavaScript SDK
- **Sign In UI**: Shows Clerk sign-in component when not authenticated
- **Protected Routes**: Dashboard only visible when signed in
- **Auto Token**: Automatically adds `Authorization: Bearer <token>` header to all API requests

## Features

✅ **User Authentication** - Sign in/sign out with Clerk  
✅ **User Isolation** - Each user sees only their data  
✅ **Protected API** - All endpoints require authentication  
✅ **Token Management** - Automatic token refresh  
✅ **Development Mode** - Works without Clerk for local dev  

## API Endpoints

All API endpoints now require authentication:

- `GET /api/flags` - Get user's flagged items
- `GET /api/flags/{id}` - Get user's specific flagged item
- `POST /api/flags` - Create flagged item (associated with user)
- `PATCH /api/flags/{id}` - Update user's flagged item
- `DELETE /api/flags/{id}` - Delete user's flagged item
- `GET /api/stats` - Get user's statistics

**Public endpoints** (no auth required):
- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /metrics` - Prometheus metrics
- `GET /` - Frontend (handles auth in browser)

## Database Changes

The database schema now includes `user_id`:

```sql
CREATE TABLE flagged_items (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,  -- Added
    content_type VARCHAR(20) NOT NULL,
    ...
);
```

All queries are filtered by `user_id` to ensure data isolation.

## Development Mode

To disable Clerk for local development:

```bash
CLERK_ENABLED=false
```

This will:
- Use a mock user (`dev_user_123`)
- Allow API access without tokens
- Skip token verification

## Production Deployment

### Railway

1. Add environment variables in Railway dashboard:
   ```
   CLERK_ENABLED=true
   CLERK_SECRET_KEY=sk_live_...
   CLERK_PUBLISHABLE_KEY=pk_live_...
   ```

2. Update CORS origins to include your Railway domain:
   ```
   CORS_ORIGINS=https://your-app.railway.app
   ```

### Render

Same as Railway - add environment variables in Render dashboard.

## Clerk Dashboard Configuration

### Allowed Origins

In Clerk Dashboard → Settings → Paths:
- Add your frontend URL: `https://your-app.railway.app`
- Add localhost for development: `http://localhost:8000`

### Sign-In Methods

Configure in Clerk Dashboard → User & Authentication:
- Email/Password
- Social providers (Google, GitHub, etc.)

## Troubleshooting

### "Authorization header missing"

- Check that Clerk SDK is loaded in browser
- Verify `CLERK_PUBLISHABLE_KEY` is set
- Check browser console for Clerk errors

### "Token verification failed"

- Verify `CLERK_SECRET_KEY` is correct
- Check that token hasn't expired
- Ensure Clerk keys match (test vs live)

### Users can see other users' data

- Verify database queries include `user_id` filter
- Check that `get_current_user` dependency is used
- Review database migration was applied

## Security Notes

- ✅ All API endpoints protected
- ✅ User data isolated by `user_id`
- ✅ JWT tokens verified on every request
- ✅ Tokens automatically refreshed by Clerk SDK
- ✅ CORS configured for your domain

## Next Steps

1. Set up Clerk account
2. Add environment variables
3. Deploy to Railway/Render
4. Test sign-in flow
5. Verify user data isolation

For more information, see [Clerk Documentation](https://clerk.com/docs).

