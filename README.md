# AI-native Campaign Orchestrator

A proof-of-concept platform for orchestrating and managing multi-channel marketing campaigns through an AI-focused interface. This system enables campaign managers to plan, configure, execute, and analyze campaigns across various channels from a unified interface using text prompts.

## Features

- **AI-native Interface**: Create campaigns through natural language prompts
- **Agent Orchestration**: Intelligent routing to specialized agents for campaign generation and analysis
- **Multi-channel Support**: Email, SMS, and Push notification channels
- **Dialog-based Interaction**: Conversational interface with reasoning steps
- **Search Functionality**: Unified search across campaigns, segments, and compendium
- **Mock Data**: Complete POC with mock data for demonstration

## Architecture

### Backend (FastAPI + Python)
- FastAPI REST API
- Agent orchestration engine
- Dialog session management
- JSON-based data storage (for POC)

### Frontend (Svelte 5 + TypeScript)
- Action Bar with User Input and Dialog History
- Agent Canvas with Dialog Panel and Experience Panel
- Responsive UI with dark mode support
- Real-time updates

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the backend server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### Creating a Campaign

1. Enter a campaign description in the User Input field (e.g., "Create a summer sale campaign for high-value customers using email and SMS")
2. The AI agent will analyze your request and generate a campaign configuration
3. Review the generated configuration in the Experience Panel
4. Edit any fields as needed
5. Click "Save Campaign" to create the campaign

### Searching

- Enter a short query (< 50 characters) to search for existing campaigns, segments, or compendium articles
- Select a result from the dropdown to view details in the Experience Panel

### Dialog History

- Click "Dialog History" to view and restore previous conversation sessions
- Select "New Request" to start a fresh session

### Empty State

When no dialog is active, you can:
- View Campaigns: Browse all existing campaigns
- View Segments: Browse audience segments
- View Compendium: Browse knowledge base articles

## API Endpoints

### Agent Orchestration
- `POST /api/v1/agent/orchestrate` - Process user prompt and route to agent

### Dialog Sessions
- `GET /api/v1/dialog/sessions` - List all sessions
- `POST /api/v1/dialog/sessions` - Create new session
- `GET /api/v1/dialog/sessions/:id` - Get session details
- `POST /api/v1/dialog/sessions/:id/messages` - Add message to session

### Campaigns
- `GET /api/v1/campaigns` - List campaigns
- `POST /api/v1/campaigns` - Create campaign
- `GET /api/v1/campaigns/:id` - Get campaign details
- `GET /api/v1/campaigns/:id/metrics` - Get campaign metrics (mock)

### Search
- `GET /api/v1/search?q=query&type=all` - Unified search

### Segments
- `GET /api/v1/segments` - List segments
- `POST /api/v1/segments` - Create segment

### Compendium
- `GET /api/v1/compendium` - List articles
- `POST /api/v1/compendium` - Create article

## Project Structure

```
CampaignOrchestratorDemo/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── data/                # JSON data files
│       ├── campaigns.json
│       ├── segments.json
│       ├── compendium.json
│       └── dialog_sessions.json
├── frontend/
│   ├── src/
│   │   ├── components/      # Svelte components
│   │   ├── App.svelte
│   │   ├── main.ts
│   │   └── stores.ts        # State management
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Technology Stack

### Backend
- FastAPI 0.104.1
- Python 3.8+
- Uvicorn

### Frontend
- Svelte 5
- TypeScript
- Vite
- Tailwind CSS (via CDN)

## Mock Data

The POC uses mock data stored in JSON files:
- Campaigns with sample configurations
- Audience segments with demographics and behaviors
- Compendium articles with best practices
- Mock metrics for completed campaigns

## Development Notes

- This is a proof-of-concept demonstration
- Data is stored in JSON files (not production-ready)
- No authentication required for POC
- Mock data is used for all integrations
- Agent orchestration uses rule-based routing (can be enhanced with LLM)

## Future Enhancements

- Integration with actual LLM for agent intelligence
- Database migration from JSON to PostgreSQL
- Real channel integrations (SendGrid, Twilio, etc.)
- Advanced user flow visualization
- A/B testing analytics dashboard
- WebSocket support for real-time updates

## License

This is a proof-of-concept project for demonstration purposes.
