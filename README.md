# CESO Photobooth

Professional Offline Web-Based Photobooth System

## Overview

A complete, production-quality offline web-based photobooth application that runs entirely on a Windows PC. Uses the computer's webcam to capture three photos, combines them into a customizable photobooth strip, generates a QR code for downloading, and allows guests to download their photo through their mobile devices on the same local network.

**No subscriptions. No cloud services. No internet dependency.**

## Features

- Live camera preview with modern UI
- 3-photo capture with animated countdown
- Photo review with retake option
- Customizable PNG template system
- QR code generation for mobile download
- Mobile-friendly download page
- SQLite session storage
- Admin configuration system
- STI College-inspired professional design

## Project Structure

```
photobooth/
├── backend/
│   ├── main.py              # FastAPI application entry
│   ├── database.py          # SQLite database operations
│   ├── models.py            # Pydantic data models
│   ├── requirements.txt     # Python dependencies
│   ├── routers/
│   │   └── api.py           # REST API endpoints
│   └── services/
│       ├── image_processor.py  # Image processing engine
│       ├── qr_generator.py    # QR code generation
│       └── session_manager.py  # Session management
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── public/
│   │   └── download.html    # Mobile download page
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── components/
│       │   ├── WelcomeScreen.jsx
│       │   ├── CaptureScreen.jsx
│       │   ├── ReviewScreen.jsx
│       │   ├── LoadingScreen.jsx
│       │   ├── ResultScreen.jsx
│       │   └── Footer.jsx
│       ├── hooks/
│       │   └── useCamera.js
│       ├── services/
│       │   └── api.js
│       └── utils/
│           └── helpers.js
├── config/
│   ├── settings.json        # Application settings
│   └── template.json        # Template photo placement config
├── photos/
│   ├── originals/
│   └── strips/
├── templates/               # PNG template files
├── qrcodes/
├── database/
└── sessions/
```

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Webcam connected to the PC

## Installation

### Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
# source venv/bin/activate

pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Start Backend Server

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Configuration

### Application Settings (`config/settings.json`)

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "camera": {
    "width": 1280,
    "height": 720
  },
  "capture": {
    "photo_count": 3,
    "countdown_duration": 3,
    "delay_between_photos": 2
  }
}
```

### Template Configuration (`config/template.json`)

```json
{
  "template_name": "default",
  "template_file": "templates/default.png",
  "output_width": 600,
  "output_height": 1800,
  "photo_slots": [
    {
      "slot_index": 1,
      "x": 30,
      "y": 100,
      "width": 540,
      "height": 400,
      "border_radius": 12
    }
  ]
}
```

## Changing Templates

1. Place your PNG template in the `templates/` directory
2. The template should have transparent areas where photos will appear
3. Update `config/template.json` with:
   - `template_file`: path to your PNG file
   - `photo_slots`: coordinates and sizes for each photo
4. Restart the backend server

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/settings` | Get app settings |
| POST | `/api/session/create` | Create new session |
| POST | `/api/session/{id}/save-photo` | Save captured photo |
| POST | `/api/session/{id}/generate-strip` | Generate strip + QR |
| GET | `/api/preview/{id}` | Preview strip image |
| GET | `/api/download/{id}` | Download strip |
| GET | `/api/qr/{id}` | Get QR code |
| GET | `/api/session/{id}/info` | Get session info |

## Deployment on Windows

1. Install Python 3.8+ and Node.js 16+
2. Follow installation steps above
3. For production, build the frontend:
   ```bash
   cd frontend
   npm run build
   ```
4. Serve the `dist/` folder with the backend or a static server
5. Ensure firewall allows port 8000 for QR downloads on local network

## Troubleshooting

**Camera not working:**
- Ensure webcam is connected and not used by another app
- Grant camera permissions in browser
- Check browser console for errors

**QR code not scanning:**
- Ensure mobile device is on the same Wi-Fi network
- Check that port 8000 is not blocked by firewall
- Verify the server IP address in the QR code

**Server won't start:**
- Ensure all dependencies are installed
- Check if port 8000 is already in use
- Verify Python version is 3.8+

## Dependencies

### Backend
- FastAPI - Web framework
- Pillow - Image processing
- qrcode - QR code generation
- Uvicorn - ASGI server
- aiosqlite - Async SQLite

### Frontend
- React - UI library
- Vite - Build tool
- Tailwind CSS - Styling
- Framer Motion - Animations
- Axios - HTTP client
- react-webcam - Camera component

## Future Scalability

The architecture supports adding:
- Multiple strip templates
- Landscape layouts
- GIF/Boomerang mode
- Video recording
- Printer integration
- Email sharing
- Gallery mode
- AI enhancements
- Cloud storage
- Event branding
- Analytics dashboard
