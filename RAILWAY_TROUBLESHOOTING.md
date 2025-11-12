# Railway Deployment Troubleshooting Guide

## Common Issues and Solutions

### Health Check Failures

**Issue**: Health checks failing with "service unavailable"

**Solutions Applied**:
1. ✅ Made `/health` endpoint lightweight (no database check)
2. ✅ Made database initialization non-blocking
3. ✅ Added Railway health check configuration
4. ✅ Removed `set -e` from entrypoint script

**If still failing**:
- Check Railway logs: Go to your service → Logs tab
- Verify PORT environment variable is set (Railway sets this automatically)
- Check if application is starting: Look for "Starting application on port" in logs

### Database Connection Issues

**Issue**: Database connection errors

**Solution**: Make sure you've added a PostgreSQL service in Railway:
1. Go to your Railway project
2. Click "+ New" → "Database" → "Add PostgreSQL"
3. Railway will automatically create `DATABASE_URL` environment variable
4. Your app service will automatically have access to it

**Verify DATABASE_URL format**:
```
postgresql://postgres:PASSWORD@HOST:PORT/railway
```

### PORT Environment Variable

**Issue**: `$PORT` is not a valid port number

**Solution**: ✅ Fixed - Entrypoint script now properly handles PORT variable

The entrypoint script reads `PORT` from environment and defaults to 8000 if not set.

### Application Not Starting

**Check logs for**:
1. Import errors
2. Missing dependencies
3. Database connection issues (shouldn't block startup now)
4. Port binding errors

**Common fixes**:
- Verify all dependencies in `requirements.txt`
- Check that `DATABASE_URL` is set (if using PostgreSQL)
- Ensure Railway has set `PORT` environment variable

### Build Failures

**Issue**: Docker build fails

**Check**:
1. Dockerfile syntax
2. All files are in repository (check `.gitignore`)
3. Requirements.txt is valid
4. Entrypoint script has execute permissions (handled in Dockerfile)

## Railway-Specific Configuration

### Environment Variables

Make sure these are set in Railway:

**Required**:
- `PORT` - Automatically set by Railway (don't set manually)
- `DATABASE_URL` - Automatically set if you add PostgreSQL service

**Recommended**:
- `ENVIRONMENT=production`
- `LOG_LEVEL=INFO`
- `CORS_ORIGINS=https://your-app.railway.app`
- `RATE_LIMIT_ENABLED=true`
- `RATE_LIMIT_PER_MINUTE=60`

### Health Check Configuration

Railway health check is configured in `railway.json`:
- Path: `/health`
- Timeout: 100 seconds
- Interval: 10 seconds

The `/health` endpoint is lightweight and doesn't require database connectivity.

### Database Setup

1. Add PostgreSQL service in Railway
2. Railway automatically creates `DATABASE_URL`
3. Your app will connect automatically
4. Database tables are created on first API call

## Verification Steps

After deployment:

1. **Check service status**: Should show "Active"
2. **Check logs**: Should see "Starting application on port XXXX"
3. **Test health endpoint**: `curl https://your-app.railway.app/health`
4. **Test API**: `curl https://your-app.railway.app/api/stats`

## Getting Help

If issues persist:

1. Check Railway logs (most important!)
2. Verify environment variables are set
3. Check that PostgreSQL service is running
4. Verify health endpoint responds: `curl https://your-app.railway.app/health`

## Quick Fixes

### Restart Service
Railway dashboard → Your service → Settings → Restart

### View Logs
Railway dashboard → Your service → Logs tab

### Check Environment Variables
Railway dashboard → Your service → Variables tab

### Rebuild
Railway dashboard → Your service → Deployments → Redeploy

