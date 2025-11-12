# Railway Clerk Setup Checklist

## ✅ Step 1: CLERK_SECRET_KEY (Done!)
You've already added this. Great!

## ⚠️ Step 2: Add Remaining Environment Variables

You need to add these two more environment variables in Railway:

### 1. CLERK_PUBLISHABLE_KEY
- **Where to find**: Clerk Dashboard → API Keys → Publishable Key
- **Format**: Starts with `pk_test_` (development) or `pk_live_` (production)
- **Value**: Copy the full key from Clerk dashboard

### 2. CLERK_ENABLED
- **Value**: `true`
- **Purpose**: Enables Clerk authentication

## Quick Steps in Railway:

1. Go to your Railway project dashboard
2. Click on your **backend service**
3. Go to **Variables** tab
4. Click **+ New Variable**
5. Add these variables:

```
CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxx
CLERK_ENABLED=true
```

## Step 3: Get Your Clerk Keys

If you haven't already:

1. Go to https://clerk.com/dashboard
2. Select your application
3. Go to **API Keys** section
4. Copy:
   - **Publishable Key** (starts with `pk_`)
   - **Secret Key** (you already have this - starts with `sk_`)

## Step 4: Update CORS Origins

In Railway, also update `CORS_ORIGINS` to include your Railway domain:

```
CORS_ORIGINS=https://your-app.railway.app
```

Or if you want to allow multiple origins:
```
CORS_ORIGINS=https://your-app.railway.app,http://localhost:8000
```

## Step 5: Configure Clerk Dashboard

1. Go to Clerk Dashboard → Settings → Paths
2. Add your Railway domain to **Allowed Origins**:
   - `https://your-app.railway.app`
   - `http://localhost:8000` (for local development)

## Step 6: Redeploy

After adding the environment variables:
- Railway will automatically redeploy
- Or manually trigger: Service → Deployments → Redeploy

## Verification

After deployment, test:

1. Visit your Railway app URL
2. You should see Clerk sign-in UI
3. Sign in with your Clerk account
4. Dashboard should appear after authentication

## Troubleshooting

### "CLERK_PUBLISHABLE_KEY not set"
- Make sure you added `CLERK_PUBLISHABLE_KEY` in Railway
- Check the value is correct (starts with `pk_`)

### "Token verification failed"
- Verify `CLERK_SECRET_KEY` matches your Clerk dashboard
- Check that keys are from the same Clerk application
- Ensure `CLERK_ENABLED=true`

### Sign-in UI not showing
- Check browser console for errors
- Verify Clerk SDK is loading
- Check CSP headers allow Clerk domains

## Current Status

✅ CLERK_SECRET_KEY - Added  
⏳ CLERK_PUBLISHABLE_KEY - **Need to add**  
⏳ CLERK_ENABLED - **Need to add**  
⏳ CORS_ORIGINS - **Should update**

## Quick Copy-Paste for Railway

Add these variables in Railway:

```
CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
CLERK_ENABLED=true
CORS_ORIGINS=https://your-app.railway.app
```

Replace `YOUR_KEY_HERE` with your actual Clerk publishable key and `your-app.railway.app` with your Railway domain.

