# Photobooth System

A professional offline web-based photobooth application that runs entirely on a Windows PC without requiring any paid services, subscriptions, cloud hosting, or third-party APIs.

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Access

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Mobile Access

1. Find your PC's IP address: `ipconfig`
2. Update `config/settings.json` with your IP in `host_display`
3. Access from mobile: `http://YOUR_IP:5173`

## Project Structure

```
photobooth/
├── frontend/              # React + Vite + Tailwind
│   └── src/
│       ├── components/    # React components
│       ├── App.jsx        # Main app
│       └── api.js         # API client
├── backend/               # FastAPI + Python
│   ├── main.py            # Main server
│   └── services/          # Business logic
├── config/                # Configuration files
├── templates/             # PNG template files
├── sessions/              # Session storage
└── database/              # SQLite database
```

## Configuration

Edit `config/settings.json` to customize settings.
Edit `config/templates.json` to manage templates.

## Changing Templates

1. Place PNG template in `templates/` folder
2. Update `config/templates.json` with coordinates
3. Restart backend server
