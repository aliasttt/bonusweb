# Fix: OperationalError - no such column: accounts_profile.interests

## Problem
The database is missing the `interests` column in the `accounts_profile` table. This happens when migrations haven't been applied to the production database.

## Solution

### Step 1: Run the Migration on Scalingo

You need to run the migration on your Scalingo production server. Use one of these methods:

#### Method 1: Using Scalingo CLI (Recommended)

```powershell
# Make sure you're logged in
scalingo login

# Run the migration
scalingo --app mywebsite run python manage.py migrate accounts
```

#### Method 2: Using the Provided Script

Run the PowerShell script that's already in your project:

```powershell
.\run_migration_scalingo.ps1
```

#### Method 3: Using Scalingo Dashboard

1. Go to https://dashboard.scalingo.com
2. Select your app: `mywebsite`
3. Go to **"One-off containers"** or **"Run command"**
4. Enter: `python manage.py migrate accounts`
5. Click **"Run"**

### Step 2: Verify the Migration

After running the migration, verify it was successful:

```powershell
scalingo --app mywebsite run python manage.py showmigrations accounts
```

You should see `[X]` next to `0004_profile_interests`, indicating it's been applied.

### Step 3: Test the Application

After the migration completes, test your application:

1. Try accessing `/partners/dashboard/` again
2. The error should be resolved

## Temporary Workaround

I've updated the middleware (`accounts/middleware.py`) to handle this error gracefully, so your application won't crash. However, **you still need to run the migration** to fully fix the issue.

## Why This Happened

The migration file `accounts/migrations/0004_profile_interests.py` exists in your codebase, but it hasn't been applied to your production database. This typically happens when:

1. Code was deployed but migrations weren't run
2. The migration was created after deployment
3. Migrations were run locally but not on production

## Prevention

To prevent this in the future:

1. **Always run migrations after deployment:**
   ```powershell
   scalingo --app mywebsite run python manage.py migrate
   ```

2. **Check migration status before deployment:**
   ```powershell
   scalingo --app mywebsite run python manage.py showmigrations
   ```

3. **Consider adding migrations to your deployment process** (e.g., in `Procfile` or deployment scripts)

## Related Files

- Migration file: `accounts/migrations/0004_profile_interests.py`
- Model definition: `accounts/models.py` (line 25)
- Middleware: `accounts/middleware.py` (updated to handle errors gracefully)

