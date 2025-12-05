# Vercel Deployment Guide

This project is now configured for deployment on Vercel.

## Prerequisites

- Vercel account (free at https://vercel.com)
- GitHub account with this repository
- (Optional) PostgreSQL database for persistent data storage

## Important: Database Configuration

### Option 1: Development (SQLite - Ephemeral)
The app currently uses SQLite by default. **Note:** Vercel's file system is ephemeral, meaning data will be lost on each deployment. This is suitable for development/testing only.

### Option 2: Production (PostgreSQL - Recommended)
For production, you should use PostgreSQL or another persistent database:

1. Set up a PostgreSQL database (e.g., using Supabase, Heroku, or AWS RDS)
2. Add the `DATABASE_URL` environment variable to your Vercel project:
   - Go to Vercel Project Settings → Environment Variables
   - Add: `DATABASE_URL=postgresql://user:password@host:port/dbname`
3. The app will automatically use the PostgreSQL connection if `DATABASE_URL` is set

## Deployment Steps

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Configure for Vercel deployment"
   git push origin main
   ```

2. **Deploy on Vercel:**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Select Python project type
   - No additional configuration needed (vercel.json handles it)
   - Click "Deploy"

3. **Set Environment Variables (if using PostgreSQL):**
   - After deployment, go to Project Settings → Environment Variables
   - Add `DATABASE_URL` if using PostgreSQL
   - Redeploy the project

## Files Modified for Vercel Compatibility

- **vercel.json**: Vercel configuration file that specifies build and routing rules
- **api/index.py**: Entry point for Vercel serverless functions (imports and exposes the FastAPI app)
- **requirements.txt**: Removed `uvicorn` (not needed on Vercel), added `sqlalchemy` and `jinja2`
- **app/main.py**: Removed local uvicorn startup (replaced with Vercel's ASGI handler)

## Structure

```
├── api/
│   └── index.py           # Vercel serverless function entry point
├── app/
│   ├── main.py            # FastAPI application
│   ├── templates/         # HTML templates
│   └── groupme.sqlite     # Database (ephemeral on Vercel)
├── vercel.json            # Vercel configuration
└── requirements.txt       # Python dependencies
```

## Local Development

To run locally for testing:

```bash
pip install -r requirements.txt
python -m uvicorn api.index:app --reload
```

Or using the app directly:

```bash
pip install uvicorn
python -m uvicorn app.main:app --reload
```

## Troubleshooting

- **Module not found errors**: Ensure all imports in `api/index.py` are correct
- **Database errors**: Check that `DATABASE_URL` is properly set for PostgreSQL
- **Static files not loading**: Verify paths in `vercel.json` routes match your file structure
- **502 Bad Gateway**: Check Vercel logs in the dashboard for detailed error messages

## Additional Notes

- The app uses SQLite for simplicity. For production with multiple concurrent users, PostgreSQL is strongly recommended.
- Vercel has a 10-second timeout for serverless functions. Complex operations should be optimized.
- For large file uploads, consider using a CDN or cloud storage service.
