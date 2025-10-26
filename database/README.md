# EduCraft Database Setup

## Supabase PostgreSQL Database

This directory contains the database schema for the EduCraft application.

### Files

- `supabase_schema.sql` - Complete database schema with tables, indexes, and analytics views

### Setup Instructions

#### Option 1: Supabase Dashboard (Recommended)

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor
3. Copy the contents of `supabase_schema.sql`
4. Paste and run in the SQL Editor
5. Verify tables created in Table Editor

#### Option 2: Supabase CLI

```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link to your project
supabase link --project-ref your-project-ref

# Run migration
supabase db push
```

### Schema Overview

**Tables:**
- `users` - Expert validators (email-based identification)
- `generated_syllabi` - All generated course syllabi with metadata

**Views:**
- `user_activity_summary` - User generation statistics
- `domain_level_distribution` - Syllabus distribution by domain/level
- `generation_performance_metrics` - Daily performance stats

### Environment Variables

After creating your Supabase project, add these to your `.env` file:

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key
```

Get these values from:
- Project Settings → API → Project URL
- Project Settings → API → Project API keys → `anon` `public`

### Testing the Connection

```python
from src.utils.supabase_client import get_supabase_manager

# Test connection
db = get_supabase_manager()
users = db.get_all_users()
print(f"Connected! Found {len(users)} users")
```

### Useful Queries

```sql
-- Total syllabi generated
SELECT COUNT(*) FROM generated_syllabi;

-- Unique experts
SELECT COUNT(DISTINCT user_id) FROM generated_syllabi;

-- Domain distribution
SELECT domain, COUNT(*) FROM generated_syllabi GROUP BY domain;

-- Average generation time
SELECT AVG(generation_time_seconds) FROM generated_syllabi;
```

### Data Management

**Backup:**
```bash
# Backup database
supabase db dump --schema public > backup.sql
```

**Reset (careful!):**
```sql
TRUNCATE TABLE generated_syllabi;
TRUNCATE TABLE users CASCADE;
```

### Security Notes

- The `anon` key is safe to use in client-side code
- Row Level Security (RLS) is disabled for MVP simplicity
- Consider enabling RLS for production deployment
- Email addresses are stored in plain text (consider encryption for production)
