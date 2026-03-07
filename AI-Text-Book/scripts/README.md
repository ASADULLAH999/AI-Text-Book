# Testing Scripts

Quick scripts to launch and test the RAG chatbot system.

## Quick Start

### 1. Start the API Server

```bash
.\scripts\start-api.bat
```

This will:
- Navigate to the `api/` directory
- Check for `.env` file
- Start the FastAPI server on `http://localhost:8000`
- Display API docs URL: `http://localhost:8000/api/v1/docs`

### 2. Start the Frontend

Open a **new terminal** and run:

```bash
.\scripts\start-frontend.bat
```

This will:
- Start the Docusaurus development server
- Open browser at `http://localhost:3000`

### 3. Test the API

Open a **third terminal** and run:

```bash
.\scripts\test-api.bat
```

This will:
- Test the health check endpoint
- Test the chat endpoint with a sample query

## Manual Testing

See the comprehensive testing guide: [`docs/TESTING_GUIDE.md`](../docs/TESTING_GUIDE.md)

## Troubleshooting

**Port Already in Use:**
```bash
# Find process on port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <pid> /F
```

**Environment Variables Missing:**
```bash
# Check if api/.env exists
cd api
type .env

# If missing, create from template
copy .env.template .env
# Then edit .env with your API keys
```

**Frontend Won't Start:**
```bash
# Clear node modules and reinstall
rm -rf node_modules
npm install
npm start
```
