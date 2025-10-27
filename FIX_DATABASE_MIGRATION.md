# Fix Database Migration Conflict

## Problem
The `core_student_subgrupos` table was created by the auto-fix script, which conflicts with Django migrations.

## Solution Steps

### Step 1: Connect to Render Database
```bash
render psql dpg-d3q0ocm3jp1c738a137g-a
```

### Step 2: Drop the Conflicting Table
Once connected to the database, run this command:
```sql
DROP TABLE IF EXISTS core_student_subgrupos CASCADE;
```

### Step 3: Exit psql
```
\q
```

### Step 4: Commit and Push the Fixed Code
The auto-fix code has been disabled. Now commit and push:
```bash
git add .
git commit -m "Disable auto-fix scripts to prevent migration conflicts"
git push origin main
```

### Step 5: The deployment on Render will now succeed!

## What Was Fixed

1. **auto_fix_tables.py** - Disabled the function completely
2. **settings.py** - Removed the entire "CORRECCIÓN EXTREMA" block that was creating tables manually

Now Django migrations will handle ALL table creation properly, without conflicts.

## Verification

After deployment, you can verify with:
```bash
python backend_django/manage.py showmigrations
```

All migrations should show `[X]` (applied) instead of `[ ]` (pending).
