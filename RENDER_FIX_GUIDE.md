# Fixing the Render 500 Error - Database Connection Issue

## Problem Identified ✅
Your Render deployment is failing because it's trying to connect to Supabase using an **IPv6 address**, which is causing connection failures.

**Current DATABASE_URL format (WRONG):**
```
postgresql://postgres:PASSWORD@[2406:da18:243:741e:6c74:2a21:37e7:f48f]:5432/postgres
```

## Solution: Use Supabase Connection Pooler

### Step 1: Get the Correct Connection String from Supabase

1. Go to https://supabase.com/dashboard
2. Select your project: `tdlwoqpsrabmlvjpydqx`
3. Click **Settings** (gear icon) → **Database**
4. Scroll to **Connection String** section
5. Select **"Connection Pooling"** tab (NOT "Direct Connection")
6. Choose **"Transaction"** mode
7. Copy the connection string - it should look like:
   ```
   postgresql://postgres.tdlwoqpsrabmlvjpydqx:[YOUR-PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
   ```

### Step 2: Update Render Environment Variable

1. Go to https://dashboard.render.com
2. Click on your service: **web-aswin-dev**
3. Go to **Environment** tab
4. Find `DATABASE_URL` variable
5. Click **Edit**
6. Replace with the connection pooling string from Step 1
7. Click **Save Changes**

**Important:** Make sure to replace `[YOUR-PASSWORD]` with your actual database password!

### Step 3: Redeploy

Render should automatically redeploy after you save the environment variable. If not:
1. Go to **Manual Deploy** tab
2. Click **Deploy latest commit**

### Step 4: Verify

After deployment (2-3 minutes):
1. Visit: https://web-aswin-dev.onrender.com/health/
2. Check that `"database": "OK"`
3. Visit: https://web-aswin-dev.onrender.com/
4. Your site should now work! 🎉

## Why This Fixes It

- **IPv6 addresses** in connection strings can cause issues with some hosting providers
- **Connection Pooler** uses a hostname instead of an IP address
- **Port 6543** (pooler) is more reliable than direct port 5432
- **Transaction mode** is better for web applications with multiple requests

## Alternative: Use Direct Connection with Hostname

If you prefer direct connection, you can also use:
```
postgresql://postgres:[YOUR-PASSWORD]@db.tdlwoqpsrabmlvjpydqx.supabase.co:5432/postgres
```

This uses the hostname instead of IPv6 address.

## Need Help?

If you still see errors after this:
1. Check Render logs for the exact error message
2. Verify your database password is correct
3. Make sure your Supabase project is active and not paused
