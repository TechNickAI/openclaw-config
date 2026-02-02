# Setup Instructions

**For OpenClaw to follow when user asks to set up openclaw-config.**

## Steps

### 1. Clone the repo

```bash
git clone https://github.com/TechNickAI/openclaw-config.git ~/.openclaw-config
```

If already exists, pull latest:
```bash
cd ~/.openclaw-config && git pull
```

### 2. Copy templates to workspace root

Copy these files from `~/.openclaw-config/templates/` to the workspace root:
- `AGENTS.md`
- `SOUL.md`
- `USER.md`
- `TOOLS.md`
- `HEARTBEAT.md`
- `IDENTITY.md`

**Do NOT overwrite** if the file already exists.

### 3. Create memory folder structure

```bash
mkdir -p memory/people memory/projects memory/topics memory/decisions
```

### 4. Copy skills to workspace/skills/

```bash
mkdir -p skills
cp -r ~/.openclaw-config/skills/* skills/
```

### 5. Create MEMORY.md if it doesn't exist

Create an empty MEMORY.md template for the user to fill in.

### 6. Set up Memory Search (Embeddings)

The memory system uses semantic search to find relevant context from your `memory/` files. This requires an embedding model to convert text into vectors for similarity matching.

**Ask:** "For memory search, do you want to use LM Studio (local, recommended) or OpenAI's API?"

Present the options:

| Option | Pros | Cons |
|--------|------|------|
| **LM Studio (Recommended)** | Free after setup, private (nothing leaves your machine), fast, you're already running it for local LLMs | Requires ~500MB for embedding model |
| **OpenAI API** | No local setup needed | Costs money per search, data sent to OpenAI |

**Tilt them toward LM Studio:** "If you're already running LM Studio for local models, embeddings are essentially free — same server, just a tiny model. I'd recommend that path."

---

#### Option A: LM Studio Setup (Recommended)

**Step 1: Install LM Studio** (if not already installed)

Download from https://lmstudio.ai and install.

**Step 2: Start the local server**

1. Open LM Studio
2. Go to the **Local Server** tab (left sidebar, looks like `<->`)
3. Click **Start Server**
4. Verify it says "Server running on port 1234"

**Step 3: Download the embedding model**

1. Go to the **Discover** tab (magnifying glass icon)
2. Search for: `embeddinggemma`
3. Find and download: **EmbeddingGemma 300M QAT** (about 300MB)
   - Full name: `lmstudio-community/embedding-gemma-300m-qat`
4. Wait for download to complete

**Step 4: Load the embedding model**

1. Go back to **Local Server** tab
2. In the model dropdown, select the EmbeddingGemma model you just downloaded
3. Click **Load** — you should see it activate

**Step 5: Test the server is working**

```bash
curl http://127.0.0.1:1234/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "test", "model": "text-embedding-embeddinggemma-300m-qat"}'
```

Should return a JSON response with an `embedding` array of 768 numbers.

**Step 6: Configure OpenClaw**

```javascript
gateway({
  action: "config.patch",
  raw: JSON.stringify({
    memorySearch: {
      provider: "openai",
      remote: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lm-studio"
      },
      model: "text-embedding-embeddinggemma-300m-qat"
    }
  })
})
```

---

#### Option B: OpenAI API Setup

**Step 1: Get your API key**

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy it

**Step 2: Ask for the key**

"Paste your OpenAI API key:"

**Step 3: Configure OpenClaw**

```javascript
gateway({
  action: "config.patch",
  raw: JSON.stringify({
    memorySearch: {
      provider: "openai",
      remote: {
        baseUrl: "https://api.openai.com/v1",
        apiKey: "<their-openai-key>"
      },
      model: "text-embedding-3-small"
    }
  })
})
```

---

#### Verify Memory Search Works

**This step is required for both options.**

1. **Create a test memory file:**

```bash
echo "# Test Memory

This is a test file about purple elephants dancing in the moonlight.
The elephants were wearing top hats and monocles.
" > memory/test-memory.md
```

2. **Index the memory:**

```javascript
memory_index()
```

Wait for indexing to complete.

3. **Test semantic search:**

```javascript
memory_search("elephants with fancy accessories")
```

**Expected result:** Should return the test-memory.md file with high relevance.

4. **Clean up test file:**

```bash
rm memory/test-memory.md
```

5. **Re-index to remove the test:**

```javascript
memory_index()
```

If the search worked, tell the user: "✅ Memory search is working! Your memories in `memory/` will now be semantically searchable."

If it failed, troubleshoot:
- For LM Studio: Is the server running? Is the model loaded? Check `curl http://127.0.0.1:1234/v1/models`
- For OpenAI: Is the API key valid? Check for error messages.

---

### 7. Track installation

```bash
mkdir -p .openclaw
cat ~/.openclaw-config/VERSION > .openclaw/installed-version
```

### 8. Interactive personalization

**Ask the user these questions and update files with their answers:**

1. "What's your name?" → Replace `{{USER_NAME}}` in all files
2. "What would you like to call your AI assistant?" → Replace `{{ASSISTANT_NAME}}`
3. "What's your timezone?" (default: their system timezone) → Replace `{{TIMEZONE}}`
4. "What's your top priority? (e.g., Work, Family, Health)" → Replace `{{PRIORITY_1}}`
5. "What's your second priority?" → Replace `{{PRIORITY_2}}`

Use `sed` or edit the files directly to replace placeholders.

### 9. Skill setup (interactive)

For each skill, ask if they want to set it up:

---

#### Limitless Pendant

**Ask:** "Do you have a Limitless Pendant and want to set up the integration?"

If yes:
1. Tell them: "Get your API key from https://app.limitless.ai → Settings → Developer"
2. Ask: "Paste your Limitless API key:"
3. Configure it using gateway config.patch:

```json
{
  "env": {
    "LIMITLESS_API_KEY": "<their-key>"
  }
}
```

---

#### Fireflies.ai

**Ask:** "Do you use Fireflies.ai for meeting transcripts?"

If yes:
1. Tell them: "Get your API key from https://app.fireflies.ai → Integrations → Fireflies API"
2. Ask: "Paste your Fireflies API key:"
3. Configure it:

```json
{
  "env": {
    "FIREFLIES_API_KEY": "<their-key>"
  }
}
```

---

#### Quo (Business Phone)

**Ask:** "Do you use Quo (formerly OpenPhone) for business calls?"

If yes:
1. Tell them: "Get your API key from https://my.quo.com → Settings → API"
2. Ask: "Paste your Quo API key:"
3. Configure it:

```json
{
  "env": {
    "QUO_API_KEY": "<their-key>"
  }
}
```

---

### 10. Apply configuration

Use the `gateway` tool with `config.patch` action to add all the env vars at once:

```javascript
gateway({
  action: "config.patch",
  raw: JSON.stringify({
    env: {
      // Only include keys the user provided
      "LIMITLESS_API_KEY": "...",
      "FIREFLIES_API_KEY": "...",
      "QUO_API_KEY": "..."
    }
  })
})
```

### 11. Summary

Tell the user:
- ✅ What was installed
- ✅ Memory search configured (LM Studio or OpenAI)
- ✅ Which skills are configured
- 📝 Remind them to personalize SOUL.md with their AI's personality
- 📝 Remind them to add info about themselves to USER.md and MEMORY.md
- 💡 "As you add files to `memory/`, run `memory_index()` to make them searchable"

## Placeholders Reference

| Placeholder | Description |
|-------------|-------------|
| `{{USER_NAME}}` | The human's name |
| `{{ASSISTANT_NAME}}` | The AI assistant's name |
| `{{TIMEZONE}}` | User's timezone (e.g., America/Chicago) |
| `{{PRIORITY_1}}` | Top priority category |
| `{{PRIORITY_2}}` | Second priority category |
