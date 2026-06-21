# 🚨 Lifeline AI - Crisis Management Platform

> **Powered 100% by Fetch.ai's ASI:One API** - Intelligent emergency response with semantic clustering, geocoding, and AI-powered recommendations.

![Version](https://img.shields.io/badge/version-2.0-blue)
![ASI:One](https://img.shields.io/badge/AI-ASI%3AOne-green)
![Status](https://img.shields.io/badge/status-production--ready-success)

---

## 🎯 What is Lifeline AI?

A **multi-agent emergency intelligence platform** that transforms crisis reports into actionable insights:

- 📊 **Semantic Clustering** - Groups related incidents using AI embeddings
- 🗺️ **Map Visualization** - Interactive geographic view of all incidents
- 🎨 **Color-Coded Categories** - 6 distinct event types for quick identification
- 🤖 **AI Recommendations** - Context-aware emergency response plans
- 📍 **Geocoding** - Automatic location coordinate resolution
- ⚡ **Real-time Updates** - Auto-refresh every 10 seconds

---

## 🌟 Key Features

### 1. Intelligent Clustering
- Uses **ASI:One embeddings** for semantic similarity (not just keyword matching)
- Combines text similarity (70% threshold) + geographic proximity (5km radius)
- Automatically groups related incidents across different locations

### 2. Visual Dashboard
- **Priority Queue**: Ranked by urgency and impact
- **Map View**: Interactive Leaflet map with color-coded markers
- **Clusters Tab**: Category-based organization (Medical, Rescue, Environmental, etc.)

### 3. AI-Powered Insights
- **ASI:One Chat API** generates intelligent recommendations
- Context-aware action plans for emergency responders
- Fallback to rule-based logic if API unavailable

### 4. Color-Coded Categories
- 🔴 **Medical Emergency** - Oxygen, insulin, critical care
- 🟠 **Rescue Request** - Trapped, stuck, immediate help needed
- 🔵 **Flooding** - Water rising, flood warnings
- 🟡 **Power Outage** - Electrical infrastructure issues
- 🟢 **Shelter Update** - Housing, evacuation centers
- 🟣 **General Alert** - Other crisis situations

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Redis server
- ASI:One API key (already configured!)

### Installation

**1. Clone and setup backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Start Redis:**
```bash
redis-server
```

**3. Run backend:**
```bash
uvicorn main:app --reload --port 8000
```

**4. Setup frontend:**
```bash
cd frontend
npm install
npm run dev
```

**5. Open browser:**
```
http://localhost:5173
```

---

## 📖 Usage

### Submit a Crisis Report
1. Enter emergency description (e.g., "Grandmother needs oxygen, water rising")
2. Add location (e.g., "Berkeley, CA")
3. Click "Process Event"

### View Results
- **Priority Queue**: See ranked incidents by urgency
- **Map View**: Visualize incidents geographically
- **Clusters**: Browse by category (Medical, Rescue, etc.)

### Example Reports
```
Text: "My grandmother is trapped and needs oxygen urgently"
Location: "Oakland, CA"
→ Creates Medical Emergency cluster (Red)

Text: "Flooding on Main Street, multiple people stuck"
Location: "Berkeley, CA"
→ Creates Flooding cluster (Blue)

Text: "Power outage affecting hospital backup systems"
Location: "San Francisco, CA"
→ Creates Power Outage cluster (Yellow)
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (React + Leaflet)      │
│  - Priority Queue  - Map View  - Clusters│
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend                 │
│  - Event Processing  - Clustering       │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
┌───────────────┐    ┌────────────────┐
│  ASI:One API  │    │  Redis Cache   │
│  - Embeddings │    │  - Clusters    │
│  - Chat/Recs  │    │  - Incidents   │
└───────────────┘    └────────────────┘
```

---

## 🔑 ASI:One Integration

### Single API Powers Everything!

**Embeddings** (`asi1-embedding`):
- Converts incident text to vector embeddings
- Enables semantic similarity comparison
- Powers intelligent clustering

**Chat Completions** (`asi1-mini`):
- Generates context-aware recommendations
- Analyzes cluster severity and urgency
- Provides actionable response plans

**No OpenAI Required!** 🎉

See [ASI_ONE_INTEGRATION.md](./ASI_ONE_INTEGRATION.md) for detailed API usage.

---

## 📁 Project Structure

```
lifeline-ai/
├── backend/
│   ├── main.py                      # FastAPI app
│   ├── schemas.py                   # Data models
│   ├── asi_client.py                # ASI:One chat API
│   ├── agents/
│   │   ├── asi_coordinator.py       # Event processing
│   │   └── resource_agent.py        # Resource finding
│   ├── processing/
│   │   ├── incident_extractor.py    # Text analysis + geocoding
│   │   ├── incident_fusion.py       # Semantic clustering
│   │   ├── semantic_clustering.py   # ASI:One embeddings
│   │   ├── geocoding.py             # Location → lat/lng
│   │   ├── priority_scorer.py       # Urgency calculation
│   │   └── recommendation_engine.py # AI recommendations
│   ├── memory/
│   │   ├── incident_memory.py       # Redis operations
│   │   └── redis_client.py          # Redis connection
│   └── browser/
│       └── browserbase_search.py    # Resource search
├── frontend/
│   ├── src/
│   │   ├── App.tsx                  # Main app + tabs
│   │   ├── components/
│   │   │   ├── EventInput.tsx       # Report submission
│   │   │   ├── PriorityQueue.tsx    # Ranked list
│   │   │   ├── ClusterMap.tsx       # Interactive map
│   │   │   └── ClustersView.tsx     # Category view
│   │   └── App.css                  # Styling
│   └── package.json
└── docs/
    ├── SETUP.md                     # Installation guide
    ├── IMPROVEMENTS_SUMMARY.md      # What's new
    └── ASI_ONE_INTEGRATION.md       # API details
```

---

## 🎨 Screenshots

### Priority Queue
Color-coded clusters ranked by urgency with AI recommendations

### Map View
Interactive Leaflet map showing all incidents geographically

### Clusters Tab
Organized by category: Medical, Rescue, Environmental, Infrastructure, Shelter, General

---

## 📊 Performance

- **Clustering**: ~1-2s per incident (ASI:One API)
- **Geocoding**: ~0.5-1s per location (Nominatim)
- **Map Rendering**: Optimized for 100+ incidents
- **Auto-refresh**: Every 10 seconds
- **Fallback**: Instant keyword-based clustering if API unavailable

---

## 🛠️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/events/process` | Submit new crisis report |
| `GET` | `/priority-queue` | Get sorted clusters by priority |
| `GET` | `/clusters` | Get all clusters (unsorted) |
| `DELETE` | `/memory` | Clear all clusters from Redis |

---

## 🧪 Testing

### Test Semantic Clustering
```bash
# Submit similar incidents
curl -X POST http://localhost:8000/events/process \
  -H "Content-Type: application/json" \
  -d '{"source":"test","text":"Grandmother needs oxygen","location":"Berkeley, CA"}'

curl -X POST http://localhost:8000/events/process \
  -H "Content-Type: application/json" \
  -d '{"source":"test","text":"Elderly person requires medical oxygen","location":"Berkeley, CA"}'

# Check clustering
curl http://localhost:8000/clusters
```

**Expected**: Both incidents in same cluster (semantic similarity detected)

---

## 🌍 Environment Variables

```bash
# Required
ASI_ONE_API_KEY=sk_...    # Fetch.ai ASI:One API key
REDIS_HOST=localhost
REDIS_PORT=6379

# Optional
BROWSERBASE_API_KEY=...   # For resource search
DEEPGRAM_API_KEY=...      # For future audio processing
```

---

## 🚀 Deployment

### Production Checklist
- [ ] Verify ASI:One API key
- [ ] Configure production Redis
- [ ] Set CORS for production domain
- [ ] Build frontend: `npm run build`
- [ ] Use gunicorn: `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker`
- [ ] Set up monitoring/logging
- [ ] Configure SSL/HTTPS

---

## 🤝 Contributing

This project demonstrates Fetch.ai's ASI:One API capabilities for crisis management. Contributions welcome!

### Enhancement Ideas
- Real Browserbase web scraping for resources
- Historical analytics and trend detection
- Multi-language support
- Voice input via Deepgram
- Mobile app (React Native)
- Notification system for responders

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Fetch.ai** for ASI:One API
- **OpenStreetMap** for map tiles
- **Nominatim** for geocoding
- **Leaflet** for map visualization

---

## 📞 Support

For issues or questions:
1. Check [SETUP.md](./SETUP.md) for installation help
2. Review [ASI_ONE_INTEGRATION.md](./ASI_ONE_INTEGRATION.md) for API details
3. Verify Redis is running: `redis-cli ping`
4. Check console logs for errors

---

## ✨ What Makes This Special?

### 🎯 100% ASI:One Powered
- No OpenAI, Claude, or other AI services needed
- Single API key for all AI features
- Unified billing and quota management

### 🧠 Intelligent Clustering
- Semantic similarity (not just keywords)
- Geographic proximity awareness
- Automatic category assignment

### 🎨 Beautiful UX
- Color-coded visual system
- Interactive map with popups
- Category-based organization
- Real-time updates

### 🛡️ Production-Ready
- Graceful fallbacks
- Error handling
- Redis caching
- Scalable architecture

---

**Built with ❤️ for emergency response teams worldwide**

*Powered by Fetch.ai's ASI:One API - The future of decentralized AI* 🚀
