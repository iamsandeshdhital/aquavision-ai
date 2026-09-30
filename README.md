# AquaVision AI

**Real-Time Water Quality Monitoring Using Computer Vision**

Detects water pollution, algae blooms, oil spills, and chemical contamination in real-time from camera feeds — before contaminated water reaches communities.

---

## The Problem

Water contamination currently takes **days** to detect via lab tests. By the time results come back, entire communities may have been exposed. AquaVision AI detects pollution **in real-time** from camera feeds.

## Features

| Feature | Description |
|---------|-------------|
| **Real-time Detection** | Detects algae blooms, oil spills, chemical contamination, sediment |
| **Water Quality Analysis** | Estimates turbidity (NTU), dissolved oxygen (mg/L), pH |
| **Multi-Camera Support** | Monitor multiple water sources simultaneously |
| **Smart Alerts** | Email/SMS notifications with severity-based escalation |
| **REST API** | External system integration |
| **Database** | SQLite persistence with historical analysis |
| **Docker** | One-command deployment |
| **CI/CD** | Automated testing with GitHub Actions |

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run in Demo Mode
```bash
python aquavision.py --demo
```

### 3. Run Tests
```bash
python -m pytest tests/ -v --cov=core
```

### 4. Docker Deployment
```bash
docker-compose up -d
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | System health check |
| `/api/readings` | GET | Recent water quality readings |
| `/api/alerts` | GET | Active alerts |
| `/api/statistics` | GET | Analysis statistics |
| `/api/cameras` | GET | Camera list |

## Project Structure

```
aquavision-ai/
├── aquavision.py          # Main application
├── config.yaml            # Configuration
├── requirements.txt       # Dependencies
├── Dockerfile             # Container definition
├── docker-compose.yml     # Multi-service deployment
├── Makefile               # Build automation
├── README.md              # This file
├── core/
│   ├── __init__.py
│   ├── water_analyzer.py  # Computer vision analysis
│   ├── simulator.py       # Camera feed simulation
│   ├── alert_system.py    # Alert management
│   ├── dashboard.py       # Real-time dashboard
│   ├── database.py        # Data persistence
│   └── api.py             # REST API
├── tests/
│   ├── test_water_analyzer.py
│   ├── test_simulator.py
│   ├── test_alert_system.py
│   ├── test_dashboard.py
│   ├── test_database.py
│   └── test_api.py
├── data/                  # Database files
└── .github/
    └── workflows/
        └── ci.yml         # CI/CD pipeline
```

## Configuration

Edit `config.yaml` to customize:
- Camera sources (RTSP, HTTP, USB)
- Detection thresholds
- Alert recipients
- Dashboard refresh rate

## Testing

```bash
# Run all tests
make test

# Run with coverage
python -m pytest tests/ -v --cov=core --cov-report=html

# Run specific test
python -m pytest tests/test_water_analyzer.py -v
```

## Docker Deployment

```bash
# Build image
docker build -t aquavision-ai:latest .

# Run container
docker run -p 8050:8050 -v $(pwd)/data:/app/data aquavision-ai:latest

# Or use docker-compose
docker-compose up -d
```

## CI/CD

The project includes GitHub Actions workflows for:
- Automated testing on Python 3.9, 3.10, 3.11
- Code coverage reporting
- Docker image building

## License

MIT License

## Disclaimer

This system is designed to **assist** water quality professionals, not replace them. Always confirm AI detections with laboratory testing before taking action.
