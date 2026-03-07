# RAG Chatbot - End-to-End Testing Guide

This guide will walk you through testing the complete RAG chatbot system from backend to frontend.

## Prerequisites

✅ All environment variables configured in `api/.env`:
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `OPENAI_API_KEY`
- `NEON_DATABASE_URL`

✅ Data pipeline completed:
- 588 chunks embedded and uploaded to Qdrant
- Embeddings cache created

## Step 1: Start the Backend API

### Terminal 1 - API Server

```bash
cd api
python src/main.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     RAG Chatbot API starting...
INFO:     Qdrant collection verified
INFO:     Postgres connection established
INFO:     API startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Test API Health

Open a new terminal and run:

```bash
curl http://localhost:8000/api/v1/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "chat-api",
  "timestamp": "2026-02-15T..."
}
```

### Test Chat Endpoint (Non-Streaming)

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is ROS2?",
    "mode": "book_only"
  }'
```

**Expected Response:**
```json
{
  "message": "Based on the textbook content, here's what I found:\n\n[Module 1 ROS2] ...",
  "citations": [
    {
      "id": "cite-1",
      "number": 1,
      "chunk_id": "module_1_ros2_...",
      "text": "...",
      "score": 0.85,
      "source": {
        "chapter": "Module 1 ROS2",
        "section": "The Robotics Revolution",
        "heading": null,
        "page_number": null
      },
      "preview": "..."
    }
  ],
  "refused": false,
  "metadata": {
    "mode": "book_only",
    "retrieved_chunks": 5
  },
  "timestamp": "2026-02-15T..."
}
```

### Test Chat Endpoint (Streaming)

```bash
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain ROS2 nodes",
    "mode": "book_only"
  }'
```

**Expected Response (SSE Stream):**
```
event: start
data: {"status": "processing"}

data: {"type": "message_chunk", "content": "Based ", "index": 0}
data: {"type": "message_chunk", "content": "on ", "index": 1}
...

event: citations
data: {"type": "citations", "citations": [...]}

event: done
data: {"status": "complete"}
```

## Step 2: Start the Frontend

### Terminal 2 - Docusaurus Dev Server

```bash
npm start
```

**Expected Output:**
```
Starting the development server...
Docusaurus website is running at: http://localhost:3000/
```

## Step 3: Test the Complete Chat Interface

### 3.1 Access the Application

1. Open browser: http://localhost:3000
2. Navigate to any documentation page
3. Look for the chat panel in the **bottom-right corner**

### 3.2 Chat Panel UI Tests

**Test 1: Panel Visibility & Collapse**
- ✅ Chat panel should be visible (not collapsed by default)
- ✅ Click collapse button (▼) - panel should minimize
- ✅ Click again (▲) - panel should expand

**Test 2: Mode Selector**
- ✅ Three modes should be available:
  - 📚 Book Only
  - 🎯 Guided
  - 🔍 Exploratory
- ✅ Default mode: Book Only
- ✅ Change mode - dropdown should update

**Test 3: Streaming Toggle**
- ✅ Checkbox: "Stream responses"
- ✅ Default: checked (streaming enabled)
- ✅ Toggle should work

### 3.3 Chat Functionality Tests

**Test 4: Send a Message (Non-Streaming)**
1. Uncheck "Stream responses"
2. Type: "What is ROS2?"
3. Press Enter

**Expected Behavior:**
- ✅ Message appears in chat (user message, right-aligned, blue background)
- ✅ Loading indicator appears (animated dots + "Thinking...")
- ✅ Assistant response appears (left-aligned, gray background)
- ✅ Citations appear below response (numbered badges)
- ✅ Response time: < 3 seconds

**Test 5: Send a Message (Streaming)**
1. Check "Stream responses"
2. Type: "Explain ROS2 nodes"
3. Press Enter

**Expected Behavior:**
- ✅ User message appears immediately
- ✅ Assistant message appears word-by-word (streaming cursor: |)
- ✅ Citations appear after message completes
- ✅ Streaming completes smoothly

**Test 6: Character Limit**
1. Type 450 characters
2. Character counter should show: 50 (yellow warning)
3. Type 50 more characters
4. Character counter should show: 0 (red, at limit)
5. Cannot type more characters

**Test 7: Keyboard Shortcuts**
- ✅ Enter → sends message
- ✅ Shift+Enter → new line in textarea
- ✅ Textarea auto-resizes with content

**Test 8: Error Handling**
1. Stop the API server
2. Send a message

**Expected Behavior:**
- ✅ Error message appears (red banner)
- ✅ Error can be dismissed (× button)
- ✅ Assistant message shows error text

### 3.4 Citation Tests

**Test 9: Citation Display**
For each citation:
- ✅ Numbered badge (1, 2, 3...)
- ✅ Confidence indicator (colored bar)
- ✅ Source text: "Chapter • Section"
- ✅ Heading text (if available)

**Test 10: Citation Hover Preview**
1. Hover over a citation card

**Expected Behavior:**
- ✅ Preview tooltip appears
- ✅ Shows: Chapter, Section, Heading, Page, Relevance %
- ✅ Shows text preview (150 chars)
- ✅ Shows hint: "Click to navigate to source"

**Test 11: Citation Click Navigation (T049)**
1. Click on a citation card

**Expected Behavior:**
- ✅ Page scrolls to source location (if found)
- ✅ Target element highlights (yellow background)
- ✅ Highlight fades after 2 seconds
- ✅ Console logs citation details (fallback)

### 3.5 Refusal Tests

**Test 12: Insufficient Content**
1. Ask: "What is the meaning of life?"

**Expected Behavior:**
- ✅ Refusal message appears
- ✅ Helpful suggestions provided
- ✅ Refusal badge shown

**Test 13: Low Relevance**
1. Ask: "How do I make a sandwich?"

**Expected Behavior:**
- ✅ Either refusal or very low confidence citations
- ✅ System gracefully handles irrelevant queries

### 3.6 Conversation Tests

**Test 14: Multiple Messages**
1. Ask 3-4 questions in sequence

**Expected Behavior:**
- ✅ All messages displayed in chronological order
- ✅ Auto-scroll to latest message
- ✅ Timestamps shown correctly

**Test 15: Clear Conversation**
1. Click trash icon (🗑️)

**Expected Behavior:**
- ✅ All messages cleared
- ✅ Empty state shown: "Ask a question"
- ✅ Chat input still functional

## Step 4: API Documentation

### View Interactive API Docs

Open: http://localhost:8000/api/v1/docs

**Test 16: Swagger UI**
- ✅ All endpoints listed:
  - POST /api/v1/chat
  - POST /api/v1/chat/stream
  - GET /api/v1/health
- ✅ Try out chat endpoint from UI
- ✅ View request/response schemas

## Step 5: Performance & Edge Cases

**Test 17: Long Messages**
- Send 500-character message
- ✅ Should work normally

**Test 18: Special Characters**
- Send: "What's ROS2? How does it work?"
- ✅ Apostrophes, question marks handled correctly

**Test 19: Rapid Fire**
- Send 5 messages quickly
- ✅ All messages processed in order
- ✅ No race conditions or errors

**Test 20: Mode Switching**
1. Send message in Book Only mode
2. Switch to Guided mode
3. Send another message
- ✅ Mode changes reflected in responses

## Troubleshooting

### API Won't Start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <pid> /F
```

### Frontend Build Errors
```bash
# Clear cache and rebuild
npm run clear
npm install
npm start
```

### Citations Not Showing
- Check Qdrant connection
- Verify chunks uploaded: 588 chunks expected
- Check API logs for retrieval errors

### Styling Issues
- Clear browser cache
- Check CSS modules loaded
- Inspect console for errors

## Success Criteria

✅ **Backend:**
- API starts without errors
- Health check returns healthy
- Chat endpoint responds with citations
- Streaming endpoint works

✅ **Frontend:**
- Chat panel visible and interactive
- Messages send and receive correctly
- Citations display with metadata
- Streaming works smoothly
- Error handling works

✅ **Integration:**
- Frontend communicates with backend
- Citations navigate to sources
- All modes functional
- Performance acceptable (< 3s p95)

## Next Steps

After successful testing:
1. ✅ Create unit tests (T050-T052)
2. ✅ Add LLM integration (replace placeholders)
3. ✅ Implement additional modes
4. ✅ Deploy to production

---

**Testing Completed:** ___/20 tests passed

**Notes:**
