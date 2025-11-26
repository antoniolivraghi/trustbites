import base64
from datetime import datetime
from uuid import uuid4
from io import BytesIO

import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image
import requests


# ------------- PAGE CONFIG -------------
st.set_page_config(page_title="TrustBites", page_icon="🍴", layout="wide")


# ------------- THEME / CSS -------------
def _load_logo_b64():
    try:
        with open("trustbites_logo.png", "rb") as f:  # logo file in same folder
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None


LOGO_B64 = _load_logo_b64()


def inject_styles():
    st.markdown(
        """
    <style>
      :root{
        --brand: #2563EB;
        --brand-strong: #F97316;
        --text: #0F172A;
        --muted: #64748B;
        --panel: #FFFFFF;
        --bg: #F9FAFF;
        --ring: rgba(37,99,235,.18);
      }

      .stApp{
        background:
          radial-gradient(900px 400px at 85% -20%, rgba(37,99,235,.1), transparent),
          radial-gradient(800px 300px at -10% 10%, rgba(249,115,22,.08), transparent),
          var(--bg);
        color: var(--text);
        font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      }

      .main .block-container { max-width: 1120px; padding-top: 1.2rem; }

      .tb-hero{
        background: linear-gradient(90deg, #FFEDD5, #DBEAFE);
        border-radius: 18px;
        padding: 18px 22px;
        border: 1px solid rgba(15,23,42,.06);
        box-shadow: 0 10px 30px rgba(15,23,42,.05);
      }

      .tb-card{
        background: var(--panel);
        border-radius: 14px;
        padding: 16px 18px;
        border: 1px solid rgba(15,23,42,.06);
        box-shadow: 0 8px 24px rgba(15,23,42,.05);
      }

      .tb-card-quick{
        background: #EEF2FF;
        border-radius: 18px;
        padding: 18px 20px;
        border: 1px solid rgba(15,23,42,.06);
        display: flex;
        gap: 16px;
        align-items: center;
      }

      .tb-icon-pill{
        width: 56px;
        height: 56px;
        border-radius: 20px;
        background: linear-gradient(135deg,#2563EB,#F97316);
        display:flex;
        align-items:center;
        justify-content:center;
        color:#FFF;
        font-size:26px;
      }

      div.stButton > button{
        background: var(--brand) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 999px !important;
        padding: .55rem 1.1rem !important;
        font-weight: 700 !important;
        box-shadow: 0 6px 18px var(--ring);
      }
      div.stButton > button:hover{
        filter: brightness(1.04);
      }

      section[data-testid="stSidebar"]{
        background: #FFFFFF;
        border-right: 1px solid rgba(15,23,42,.06);
      }

      .stTextInput>div>div>input,
      .stSelectbox>div>div,
      .stTextArea textarea{
        border-radius: 10px !important;
      }

      .tb-chip{
        display:inline-block;
        padding:.25rem .6rem;
        border-radius:999px;
        font-size:.78rem;
        color:#1F2937;
        background:#E0F2FE;
        margin:0 .35rem .35rem 0;
      }

      .tb-img-ph{
        width:220px; height:150px; border-radius:12px;
        background: linear-gradient(135deg, #EAF7FF, #FFF7ED);
        display:flex; align-items:center; justify-content:center;
        color:#9CA3AF; font-weight:700; border:1px dashed #C7D2FE;
      }

      .tb-feed-icon{
        width:36px; height:36px; border-radius:999px;
        background:#E0F2FE;
        display:flex; align-items:center; justify-content:center;
        font-size:20px;
      }

      /* Hide stray empty text input bars */
      div[data-testid="stTextInput"] > label:empty + div input {
        display: none !important;
      }
      div[data-testid="stTextInput"] > label:empty {
        display: none !important;
      }

    </style>
    """,
        unsafe_allow_html=True,
    )

inject_styles()


# ------------- STATE HELPERS -------------
def _ensure_state():
    st.session_state.setdefault(
        "auth",
        {"signed_in": False, "email": "", "first_name": "", "last_name": ""},
    )
    st.session_state.setdefault(
        "profile",
        {"name": "", "bio": "", "photo_b64": None},
    )
    st.session_state.setdefault("users", {})
    st.session_state.setdefault("places", [])
    st.session_state.setdefault("feed", [])
    st.session_state.setdefault("edit_item", None)
    st.session_state.setdefault("page", "Home")   # current page we route on
    st.session_state.setdefault("map_center", None)
    st.session_state.setdefault("map_last_click", None)
    st.session_state.setdefault("last_map_click", None)


def hero(title: str, subtitle: str):
    logo_html = ""
    if LOGO_B64:
        logo_html = f'<img src="data:image/png;base64,{LOGO_B64}" style="height:34px;margin-right:10px;border-radius:8px;" />'
    st.markdown(
        f"""
        <div class="tb-hero">
          <div style="display:flex;align-items:center;gap:.9rem">
            <div>{logo_html}</div>
            <div>
              <h1 style="margin:0;color:#0F172A">{title}</h1>
              <div style="color:#64748B;margin-top:4px">{subtitle}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)


def _avatar():
    p = st.session_state["profile"]
    if p.get("photo_b64"):
        return f"data:image/jpeg;base64,{p['photo_b64']}"
    a = st.session_state["auth"]
    initials = "".join(
        [x[:1] for x in [a.get("first_name", ""), a.get("last_name", "")] if x]
    ).upper() or "?"
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64">
      <circle cx="32" cy="32" r="32" fill="#1F2937"/>
      <text x="50%" y="52%" dominant-baseline="middle" text-anchor="middle"
            fill="#E5E7EB" font-family="system-ui" font-size="28">{initials}</text>
    </svg>""".strip()
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def _feed_push(kind: str, text: str):
    st.session_state["feed"].append(
        {
            "id": str(uuid4()),
            "ts": datetime.now().isoformat(timespec="seconds"),
            "kind": kind,
            "text": text,
        }
    )


def _ensure_places_schema():
    for p in st.session_state["places"]:
        p.setdefault("tags", [])
        p.setdefault("photo_b64", None)
        p.setdefault("city", "")
        p.setdefault("food", 0)
        p.setdefault("service", 0)
        p.setdefault("location", 0)
        p.setdefault("price", 0)
        p.setdefault("notes", "")
        p.setdefault("lat", None)   
        p.setdefault("lon", None)


def image_file_to_b64(file, max_size=1024):
    if not file:
        return None
    try:
        img = Image.open(file).convert("RGB")
        img.thumbnail((max_size, max_size))
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        return None


# ---------- GEO HELPERS ----------
def geocode_place(query: str):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "TrustBitesStudentProject/0.1"}
        params = {"q": query, "format": "json", "limit": 1}
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        data = resp.json()
        if not data:
            return None
        return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        return None


def reverse_geocode_city(lat: float, lon: float) -> str:
    """
    Given coordinates, try to guess the city using OpenStreetMap Nominatim.
    Returns a short city/town/village string or 'Unknown city'.
    """
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        headers = {"User-Agent": "TrustBites/0.1 (student project)"}
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 10,
        }
        resp = requests.get(url, headers=headers, params=params, timeout=5)
        data = resp.json()
        addr = data.get("address", {})
        for key in ["city", "town", "village", "municipality"]:
            if addr.get(key):
                return addr[key]
    except Exception:
        pass
    return "Unknown city"


CITY_CENTERS = {
    "Lisbon": (38.7223, -9.1393),
    "Milan": (45.4642, 9.19),
}


# ---------- NAV + SIDEBAR ----------
def _navbar():
    auth = st.session_state["auth"]
    with st.sidebar:
        # avatar + email
        st.markdown('<div class="tb-card" style="padding:.9rem">', unsafe_allow_html=True)
        st.image(_avatar(), width=56)
        if auth["signed_in"]:
            st.caption(auth["email"])
        st.markdown('</div>', unsafe_allow_html=True)

        profile_clicked = False

        # Blue Profile button
        if auth["signed_in"]:
            if st.button("Profile", key="profile_btn", use_container_width=True):
                # go to profile page; remember that this click happened
                st.session_state["page"] = "Profile"
                profile_clicked = True

        st.markdown("## TrustBites")

        if auth["signed_in"]:
            nav_options = ["Home", "Add a place", "My list", "Map", "Feed"]

            # what page are we currently on?
            current_page = st.session_state.get("page", "Home")
            # for the radio, if page is not in nav (i.e. Profile), default to Home
            default_for_radio = current_page if current_page in nav_options else "Home"

            page_from_radio = st.radio(
                label="",
                options=nav_options,
                index=nav_options.index(default_for_radio),
                label_visibility="collapsed",
                key="nav_radio",
            )

            # if the user did NOT just click the Profile button,
            # let the radio control navigation
            if not profile_clicked:
                st.session_state["page"] = page_from_radio

            # route based on the central "page" state
            return st.session_state["page"]

        else:
            st.markdown("### Navigate")
            st.write("Home")
            return "Home"
                
# ---------- AUTH / PROFILE ----------
def page_auth_home():
    hero("TrustBites", "Discover trusted restaurant recommendations from your friends.")
    auth = st.session_state["auth"]
    users = st.session_state["users"]

    st.markdown('<div class="tb-card">', unsafe_allow_html=True)
    tab_signup, tab_signin = st.tabs(["✨ Create account", "🔐 Sign in"])

    # SIGN UP
    with tab_signup:
        st.write("Fields with * are required.")
        with st.form("signup"):
            c1, c2 = st.columns(2)
            with c1:
                first = st.text_input("First name *")
                email = st.text_input("Email *")
            with c2:
                last = st.text_input("Last name *")
                pw = st.text_input("Password *", type="password")

            city = st.text_input("City (optional)")
            fav = st.text_input("Favorite food (optional)")
            bio = st.text_area("Bio (optional)", height=80)
            sub = st.form_submit_button("Create my account")

            if sub:
                if not first or not last or not email or not pw:
                    st.error("Please fill in all required fields.")
                elif "@" not in email:
                    st.error("Please enter a valid email address.")
                elif email in users:
                    st.error("An account with this email already exists. Please sign in.")
                else:
                    users[email] = {
                        "password": pw,
                        "first_name": first,
                        "last_name": last,
                        "city": city,
                        "fav": fav,
                        "bio": bio,
                    }
                    st.session_state["users"] = users
                    auth.update(
                        {
                            "signed_in": True,
                            "email": email,
                            "first_name": first,
                            "last_name": last,
                        }
                    )
                    st.session_state["profile"].update(
                        {"name": f"{first} {last}".strip(), "bio": bio}
                    )
                    _feed_push("join", f"{first} {last} joined TrustBites.")
                    st.success("Welcome! Account created.")
                    st.rerun()

    # SIGN IN
    with tab_signin:
        with st.form("signin"):
            email2 = st.text_input("Email")
            pw2 = st.text_input("Password", type="password")
            s = st.form_submit_button("Sign in")

            if s:
                if email2 not in users:
                    st.error("No account found with this email. Please sign up first.")
                elif users[email2]["password"] != pw2:
                    st.error("Incorrect password.")
                else:
                    auth.update(
                        {
                            "signed_in": True,
                            "email": email2,
                            "first_name": users[email2].get("first_name", ""),
                            "last_name": users[email2].get("last_name", ""),
                        }
                    )
                    if not st.session_state["profile"]["name"]:
                        fn = users[email2].get("first_name", "")
                        ln = users[email2].get("last_name", "")
                        st.session_state["profile"]["name"] = f"{fn} {ln}".strip()
                    st.success("Signed in!")
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def page_profile():
    auth = st.session_state["auth"]
    users = st.session_state["users"]
    email = auth["email"]
    user_record = users.get(email, {})

    hero("Profile", "Update your basic profile information.")

    first_default = user_record.get("first_name", auth.get("first_name", ""))
    last_default = user_record.get("last_name", auth.get("last_name", ""))
    bio_default = st.session_state["profile"].get("bio", user_record.get("bio", ""))

    st.markdown('<div class="tb-card">', unsafe_allow_html=True)
    
    up = st.file_uploader("Avatar photo (optional)", type=["png", "jpg", "jpeg"], key="profile_photo_uploader")
    if up is not None:
        new_photo_b64 = image_file_to_b64(up)
        if new_photo_b64:
            st.session_state["profile"]["photo_b64"] = new_photo_b64
            st.success("Photo uploaded! Click 'Save profile' to save all changes.")
    
    current_photo = st.session_state["profile"].get("photo_b64")
    if current_photo:
        st.image(f"data:image/jpeg;base64,{current_photo}", width=100, caption="Current avatar")
    
    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            first = st.text_input("First name", value=first_default)
        with c2:
            last = st.text_input("Last name", value=last_default)

        email_new = st.text_input("Email", value=email)
        bio = st.text_area("Bio", value=bio_default, height=120)

        save = st.form_submit_button("Save profile")

        if save:
            if not first or not last or not email_new:
                st.error("First name, last name and email cannot be empty.")
            elif "@" not in email_new:
                st.error("Please enter a valid email address.")
            elif email_new != email and email_new in users:
                st.error("Another account already uses this email.")
            else:
                record = users.pop(email, user_record)
                record["first_name"] = first
                record["last_name"] = last
                record["bio"] = bio
                users[email_new] = record
                st.session_state["users"] = users

                st.session_state["auth"].update(
                    {"email": email_new, "first_name": first, "last_name": last}
                )
                st.session_state["profile"].update(
                    {"name": f"{first} {last}".strip(), "bio": bio}
                )
                st.success("Profile updated.")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ---------- APP PAGES ----------
def page_home():
    hero("TrustBites", "Discover trusted restaurant recommendations from your friends.")
    st.markdown("### Quick actions")

    col_left, col_right = st.columns(2)

    # ---------- LEFT COLUMN ----------
    with col_left:
        # Add a place card
        st.markdown(
            """
            <div class="tb-card" style="display:flex;align-items:center;gap:12px;">
              <div style="
                    width:48px;height:48px;border-radius:16px;
                    background:linear-gradient(135deg,#ffa94d,#ff6b4a);
                    display:flex;align-items:center;justify-content:center;
                    font-size:26px;">
                ➕
              </div>
              <div>
                <div style="font-weight:700;">Add a place</div>
                <div style="font-size:13px;color:#4b5563;">
                  Quickly add a new spot with ratings & tags.
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Add a place", key="home_add"):
            st.session_state["page"] = "Add a place"
            st.rerun()

        st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

        # Map card
        st.markdown(
            """
            <div class="tb-card" style="display:flex;align-items:center;gap:12px;">
              <div style="
                    width:48px;height:48px;border-radius:16px;
                    background:linear-gradient(135deg,#6cbcff,#3867ff);
                    display:flex;align-items:center;justify-content:center;
                    font-size:26px;">
                🗺️
              </div>
              <div>
                <div style="font-weight:700;">Map</div>
                <div style="font-size:13px;color:#4b5563;">
                  Pin places and explore by city on a map.
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Map", key="home_map"):
            st.session_state["page"] = "Map"
            st.rerun()

    # ---------- RIGHT COLUMN ----------
    with col_right:
        # My list card
        st.markdown(
            """
            <div class="tb-card" style="display:flex;align-items:center;gap:12px;">
              <div style="
                    width:48px;height:48px;border-radius:16px;
                    background:linear-gradient(135deg,#7bdcb5,#16a085);
                    display:flex;align-items:center;justify-content:center;
                    font-size:26px;">
                📂
              </div>
              <div>
                <div style="font-weight:700;">My list</div>
                <div style="font-size:13px;color:#4b5563;">
                  Browse, search and edit your saved places.
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to My list", key="home_list"):
            st.session_state["page"] = "My list"
            st.rerun()

        st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

        # Feed card
        st.markdown(
            """
            <div class="tb-card" style="display:flex;align-items:center;gap:12px;">
              <div style="
                    width:48px;height:48px;border-radius:16px;
                    background:linear-gradient(135deg,#ffd86b,#ff9f43);
                    display:flex;align-items:center;justify-content:center;
                    font-size:26px;">
                🧾
              </div>
              <div>
                <div style="font-weight:700;">Feed</div>
                <div style="font-size:13px;color:#4b5563;">
                  See recent activity from your session.
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Feed", key="home_feed"):
            st.session_state["page"] = "Feed"
            st.rerun()

def page_add_place():
    hero("Add a new place", "Add ratings, tags and notes for a restaurant.")

    _ensure_places_schema()
    editing = st.session_state.get("edit_item")

    st.markdown('<div class="tb-card">', unsafe_allow_html=True)

    if editing:
        st.markdown(f"#### Editing *{editing['name']}*")
    else:
        st.markdown("#### New place")

    name = st.text_input("Place name", value=editing["name"] if editing else "")
    city = st.text_input("City", value=editing["city"] if editing else "")

    c1, c2 = st.columns(2)
    with c1:
        food = st.slider("Food", 1, 5, editing["food"] if editing else 3)
        location = st.slider("Location", 1, 5, editing["location"] if editing else 3)
    with c2:
        service = st.slider("Service", 1, 5, editing["service"] if editing else 3)
        price = st.slider("Price", 1, 5, editing["price"] if editing else 3)

    predefined_tags = ["Casual", "Romantic", "Pizza", "Seafood", "Cocktails", "Brunch"]

    if editing:
        # normalize stored tags (e.g. "CASUAL" -> "Casual") and keep only valid ones
        existing_tags = [t.title() for t in editing.get("tags", [])]
        default_tags = [t for t in existing_tags if t in predefined_tags]
    else:
        default_tags = []

    selected_tags = st.multiselect(
        "Tags",
        options=predefined_tags,
        default=default_tags,
    )
    other_tags_raw = st.text_input(
        "Other tags (comma separated, optional)", value=""
    )
    notes = st.text_area("Notes", height=140, value=editing["notes"] if editing else "")

    up = st.file_uploader("Photo (optional)", type=["png", "jpg", "jpeg"])
    photo_b64_preview = image_file_to_b64(up) if up else None

    clicked_save = st.button("Save place", use_container_width=True, key="save_place")

    st.markdown("</div>", unsafe_allow_html=True)

    if not clicked_save:
        return

    if not name or not city:
        st.error("Please provide both a place name and a city.")
        return

    # First letter uppercase, rest lowercase (e.g. "Casual")
    tags_final = [t.strip().title() for t in selected_tags]
    if other_tags_raw:
        extra = [t.strip().title() for t in other_tags_raw.split(",") if t.strip()]
        tags_final.extend(extra)

    if editing:
        # try to (re)geocode if we have a city
        lat, lon = editing.get("lat"), editing.get("lon")
        if city.strip():
            coords = geocode_place(f"{name} {city}")
            if coords:
                lat, lon = coords

        editing.update(
            {
                "name": name.strip(),
                "city": city.strip(),
                "food": int(food),
                "service": int(service),
                "location": int(location),
                "price": int(price),
                "notes": notes.strip(),
                "tags": tags_final,
                "photo_b64": photo_b64_preview or editing.get("photo_b64"),
                # "lat": lat,
                # "lon": lon,
            }
        )

        _feed_push("edit", f"Edited {name} in {city}.")
        st.success("Place updated.")

        # ✅ finish the edit session
        st.session_state["edit_item"] = None

        # ✅ go back to My list after editing
        st.session_state["page"] = "My list"
        st.rerun()
        return
                    
    # --- NEW: try to geocode the place so it appears on the map ---
    lat, lon = None, None
    query = f"{name} {city}".strip()
    if query:
        coords = geocode_place(query)
        if not coords and city.strip():
            # fallback: try just the city
            coords = geocode_place(city.strip())
        if coords:
            lat, lon = coords

    st.session_state["places"].insert(
        0,
        {
            "id": str(uuid4()),
            "name": name.strip(),
            "city": city.strip(),
            "food": int(food),
            "service": int(service),
            "location": int(location),
            "price": int(price),
            "notes": notes.strip(),
            "tags": tags_final,
            "photo_b64": photo_b64_preview,
            "created_at": datetime.utcnow().isoformat(timespec="seconds"),
            "lat": lat,
            "lon": lon,
        },
    )
    _feed_push("add", f"Added {name} in {city}.")
    st.success("Place added.")
    st.session_state["page"] = "My list"   # ⬅️ go straight to My list
    st.rerun()

def render_place_card(p):
    left, mid, right = st.columns([1.15, 3, 1])

    with left:
        if p.get("photo_b64"):
            st.markdown(
                f'<img src="data:image/jpeg;base64,{p["photo_b64"]}" '
                f'style="width:220px;height:150px;object-fit:cover;border-radius:12px;" />',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="tb-img-ph">No photo</div>', unsafe_allow_html=True)

    with mid:
        st.subheader(p["name"])
        st.caption(p["city"] or "—")

        # ratings first
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Food", p["food"])
        with m2:
            st.metric("Service", p["service"])
        with m3:
            st.metric("Location", p["location"])
        with m4:
            st.metric("Price", p["price"])

        # tags just below ratings
        if p.get("tags"):
            chips = "".join(f'<span class="tb-chip">{t}</span>' for t in p["tags"])
            st.markdown(chips, unsafe_allow_html=True)

        if p.get("notes"):
            st.markdown(f"*Notes*: {p['notes']}")
        st.caption(f"Added: {p.get('created_at', '—')}")

    with right:
        if st.button("Edit", key=f"edit_{p['id']}", use_container_width=True):
            st.session_state["edit_item"] = p
            st.session_state["page"] = "Add a place"
            st.rerun()

        if st.button("Delete", key=f"del_{p['id']}", use_container_width=True):
            st.session_state["places"] = [
                x for x in st.session_state["places"] if x["id"] != p["id"]
            ]
            st.success("Place deleted.")
            st.rerun()


def page_list():
    hero("My list", "Discover trusted restaurant recommendations from your friends.")
    _ensure_places_schema()

    if not st.session_state["places"]:
        st.info("No places yet. Add your first one from *Add a place*.")
        return

    c1, c2, c3 = st.columns([2, 2, 1.5])
    with c1:
        q = st.text_input("Search by name/city", placeholder="e.g. trattoria, Lisbon")
    with c2:
        tag_options = sorted(
            {t for p in st.session_state["places"] for t in p.get("tags", [])}
        )
        tag_filter = st.multiselect("Filter by tags", options=tag_options)
    with c3:
        sort_by = st.selectbox(
            "Sort by", ["Newest", "Name", "Food", "Service", "Location", "Price"]
        )

    def sort_key(p):
        mapping = {
            "Name": p["name"].lower(),
            "Food": p["food"],
            "Service": p["service"],
            "Location": p["location"],
            "Price": p["price"],
            "Newest": p.get("created_at", ""),
        }
        return mapping[sort_by]

    items = st.session_state["places"]

    if q:
        ql = q.lower().strip()
        items = [
            p
            for p in items
            if ql in p["name"].lower() or ql in p["city"].lower()
        ]
    if tag_filter:
        items = [
            p
            for p in items
            if set(tag_filter).issubset(set(p.get("tags", [])))
        ]

    items = sorted(items, key=sort_key, reverse=True)

    for p in items:
        st.markdown('<div class="tb-card">', unsafe_allow_html=True)
        render_place_card(p)
        st.markdown("</div>", unsafe_allow_html=True)


def page_map():
    hero("Map", "Pin places and explore restaurants on a map.")
    st.title("Map")

    _ensure_places_schema()

    # --- choose center: last clicked point or default Lisbon ---
    default_center = (38.7223, -9.1393)
    last_click = st.session_state.get("last_map_click")
    if last_click:
        center = (last_click["lat"], last_click["lng"])
    else:
        center = default_center

    # --- build folium map with existing pins ---
    fmap = folium.Map(location=center, zoom_start=13, tiles="OpenStreetMap")

    # existing saved places (red pins)
    for p in st.session_state["places"]:
        if p.get("lat") is not None and p.get("lon") is not None:
            folium.Marker(
                [p["lat"], p["lon"]],
                popup=f"{p['name']} – {p.get('city','')}",
                icon=folium.Icon(color="red", icon="cutlery", prefix="fa"),
            ).add_to(fmap)

    # temporary pin at last selected point (blue)
    if last_click:
        folium.Marker(
            [last_click["lat"], last_click["lng"]],
            popup="Selected point",
            icon=folium.Icon(color="blue", icon="map-marker", prefix="fa"),
        ).add_to(fmap)

    # show the map and capture clicks
    map_state = st_folium(fmap, width=980, height=560, key="trustbites_map")

    # if user clicked, remember that location for the NEXT rerun
    if map_state and map_state.get("last_clicked"):
        st.session_state["last_map_click"] = map_state["last_clicked"]
        last_click = st.session_state["last_map_click"]

    # --- form to add a place from selected point ---
    if last_click:
        st.success(f"Selected: {last_click['lat']:.5f}, {last_click['lng']:.5f}")

        pname = st.text_input("Place name *", key="map_pname")
        city = st.text_input("City", key="map_city")

        colf, cols, coll, colp = st.columns(4)
        food = colf.slider("Food", 1, 5, 3, key="mf")
        serv = cols.slider("Service", 1, 5, 3, key="ms")
        loc_ = coll.slider("Location", 1, 5, 3, key="ml")
        price = colp.slider("Price", 1, 5, 3, key="mp")

        notes = st.text_area("Notes", height=80, key="map_notes")
        tags = st.multiselect(
            "Tags",
            ["Casual", "Romantic", "Pizza", "Seafood", "Cocktails", "Brunch"],
            key="map_tags",
        )

        submitted = st.button("Add this place", key="map_add_btn")

        if submitted:
            if not pname.strip():
                st.error("Place name is required.")
            else:
                st.session_state["places"].append(
                    {
                        "id": str(uuid4()),
                        "name": pname.strip(),
                        "city": city.strip(),
                        "food": int(food),
                        "service": int(serv),
                        "location": int(loc_),
                        "price": int(price),
                        "notes": notes.strip(),
                        "tags": [t.strip().title() for t in tags],
                        "photo_b64": None,
                        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
                        "lat": last_click["lat"],
                        "lon": last_click["lng"],
                    }
                )

                # Determine city for the feed: use input if present, otherwise reverse-geocode
                city_text = city.strip()
                if not city_text:
                    city_text = reverse_geocode_city(last_click["lat"], last_click["lng"])

                _feed_push("pin", f"pinned {pname.strip()} in {city_text}.")

                st.session_state["last_map_click"] = None
                st.success("Place added to your list.")
                st.rerun()

def page_feed():
    hero("Feed", "See recent activity from your session.")
    feed = list(reversed(st.session_state["feed"]))

    if not feed:
        st.info("No activity yet.")
        return

    icon_for_kind = {"join": "👤", "add": "➕", "edit": "✏️", "pin": "📍"}

    for ev in feed:
        icon = icon_for_kind.get(ev["kind"], "🧾")
        st.markdown(
            f"""
        <div class="tb-card">
          <div style="display:flex;gap:12px;align-items:center;">
            <div class="tb-feed-icon">{icon}</div>
            <div>
              <div style="font-weight:600;">{ev['text']}</div>
              <div style="opacity:.7;font-size:13px;">{ev['ts']}</div>
            </div>
          </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


# ------------- MAIN ROUTING -------------
_ensure_state()

auth = st.session_state["auth"]

# Sign out button ONLY when signed in
_ensure_state()

auth = st.session_state["auth"]

# Sign out button ONLY when signed in
if auth["signed_in"]:
    if st.button("Sign out", key="signout_top"):
        st.session_state["auth"] = {
            "signed_in": False,
            "email": "",
            "first_name": "",
            "last_name": "",
        }
        st.session_state["profile"] = {"name": "", "bio": "", "photo_b64": None}
        st.rerun()

current = _navbar()   # this also keeps st.session_state["page"] in sync

if st.session_state.get("force_page") is not None:
    current = st.session_state["force_page"]
    st.session_state["force_page"] = None   

if not auth["signed_in"]:
    page_auth_home()
else:
    if current == "Home":
        page_home()
    elif current == "Add a place":
        page_add_place()
    elif current == "My list":
        page_list()
    elif current == "Map":
        page_map()
    elif current == "Feed":
        page_feed()
    elif current == "Profile":
        page_profile()