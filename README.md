# TrustBites 🍴

TrustBites is a prototype web app for **sharing trusted restaurant recommendations between friends**.  
It is built with **Streamlit** and uses **OpenStreetMap (Nominatim) + Folium** for interactive maps and geolocation.

---

## 🚀 Features

- 🔐 Local sign up / sign in (session-based, no external backend)
- ➕ Add / ✏️ edit / ❌ delete restaurant places
- ⭐ Rate food, service, location, and price
- 🏷️ Add tags and personal notes
- 🖼️ Upload a photo for each place
- 🗺️ Interactive map with pins for saved places
- 📍 Add new places by clicking directly on the map
- 📰 Activity feed (join / add / edit / pin events)
- 👤 Profile page with editable name, email, bio, and avatar

---

## 🧱 Tech Stack

- **Frontend/App:** Streamlit  
- **Maps:** Folium + OpenStreetMap tiles  
- **Geocoding:** Nominatim (OpenStreetMap API)  
- **Language:** Python 3.10+

### Potential Extensions (Future Work)

- Integration with Google Places / Yelp / Foursquare APIs  
- Supabase or Firebase for authentication and persistent storage  
- Full production stack with FastAPI + React / Next.js  

---

## 📦 Installation

From the project directory, install all dependencies:
```bash
pip install -r requirements.txt
```

If your system uses Python 3 explicitly (macOS/Linux):
```bash
python3 -m pip install -r requirements.txt
```

After installing the dependencies, run:
```bash
streamlit run app.py
```

If streamlit is not on your PATH:
```bash
python3 -m streamlit run app.py
```

The application will automatically open in your browser at:
http://localhost:8501

📁 Project Structure
trustbites/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation

## 🌍 APIs & Data Sources
	•	Geocoding: Nominatim API (OpenStreetMap)
	•	Map tiles: OpenStreetMap
	•	Icons & UI: Custom CSS within Streamlit component

## 🙏 Acknowledgements
	•	Streamlit community for the web application framework
	•	OpenStreetMap & Nominatim for free geospatial services
	•	Folium contributors for the mapping library

## 📄 License
This project is for educational purposes.