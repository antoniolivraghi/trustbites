# TrustBites - Restaurant Recommendation App

## Overview

TrustBites is a Streamlit-based web application for sharing trusted restaurant recommendations between friends. The app features interactive maps, user authentication, and a clean UI for managing restaurant lists.

**Current Status**: Fully configured and running in Replit environment

## Project Structure

```
trustbites/
├── trustbites.py           # Main Streamlit application
├── trustbites_logo.png     # App logo
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml        # Streamlit configuration (port 5000, host settings)
├── .gitignore             # Git ignore rules
└── README.md              # Project documentation
```

## Tech Stack

- **Framework**: Streamlit 1.40.0
- **Language**: Python 3.11
- **Maps**: Folium + OpenStreetMap
- **Geocoding**: Nominatim API (OpenStreetMap)
- **Image Processing**: Pillow
- **HTTP Requests**: requests library

## Features

- Local sign up/sign in (session-based)
- Add, edit, and delete restaurant places
- Rate restaurants on food, service, location, and price
- Add tags and personal notes
- Upload photos for each place
- Interactive map with pins for saved places
- Add new places by clicking directly on the map
- Activity feed tracking join/add/edit/pin events
- Profile page with editable information and avatar

## Configuration

### Streamlit Config (.streamlit/config.toml)

The app is configured to run on port 5000 with host 0.0.0.0 to work properly with Replit's iframe proxy:

- Port: 5000
- Address: 0.0.0.0
- CORS and XSRF disabled for Replit compatibility
- Custom theme with light colors

### Workflow

- Name: "TrustBites App"
- Command: `streamlit run trustbites.py`
- Port: 5000
- Output: webview

### Deployment

Configured for autoscale deployment (stateless web app) with Streamlit running on port 5000.

## Data Storage

Currently uses Streamlit session state for data storage (in-memory, session-based). Data is not persisted between sessions.

Potential future enhancements:
- Integrate database (Supabase, Firebase, or PostgreSQL)
- Persistent user accounts
- Integration with external APIs (Google Places, Yelp)

## Recent Changes

- 2024-11-26: Initial Replit setup
  - Installed Python 3.11 and all dependencies
  - Fixed README merge conflict
  - Configured Streamlit for port 5000 with proper host settings
  - Set up workflow for webview
  - Configured deployment settings
  - Added .gitignore for Python projects
