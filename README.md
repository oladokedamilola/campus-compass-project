Here's the updated README file for your Campus Compass project with links to screenshots:

```markdown
# Campus Compass

A Progressive Web App (PWA) for campus navigation at Lagos State University (LASU), Ojo Campus.

<div align="center">
  <img src="Campus compass screenshots/home.png" alt="Campus Compass Home Page" width="200">
  <img src="Campus compass screenshots/map-page.png" alt="Campus Map Page" width="200">
  <img src="Campus compass screenshots/dashboard.png" alt="Student Dashboard" width="200">
  <img src="Campus compass screenshots/locations.png" alt="All Locations" width="200">
</div>

---

## Project Overview

Campus Compass is a mobile-first web application designed to help students, faculty, and visitors navigate the LASU Ojo campus efficiently. The app uses GPS technology and interactive mapping to provide turn-by-turn directions to buildings, lecture halls, administrative offices, and other points of interest across the campus.

This project addresses the challenges of wayfinding on a large university campus where new students and visitors frequently struggle to locate specific buildings and facilities.

---

## Screenshots

### Public Pages

| Page | Screenshot |
|------|------------|
| Home Page | ![Home Page](Campus%20compass%20screenshots/home.png) |
| Login Page | ![Login Page](Campus%20compass%20screenshots/login.png) |
| Matric Verification | ![Matric Verification](Campus%20compass%20screenshots/verify-matric.png) |
| Registration Page | ![Registration Page](Campus%20compass%20screenshots/register.png) |

### Student Pages

| Page | Screenshot |
|------|------------|
| Student Dashboard | ![Dashboard](Campus%20compass%20screenshots/dashboard.png) |
| Map Navigation | ![Map Page](Campus%20compass%20screenshots/map-page.png) |
| All Locations | ![Locations Grid](Campus%20compass%20screenshots/locations.png) |
| Favorites | ![Favorites](Campus%20compass%20screenshots/favourites.png) |
| Profile | ![Profile](Campus%20compass%20screenshots/profile.png) |

### Admin Pages

| Page | Screenshot |
|------|------------|
| Admin Dashboard | ![Admin Dashboard](Campus%20compass%20screenshots/admin%20dashboard.png) |
| Manage Users | ![Manage Users](Campus%20compass%20screenshots/users.png) |
| Campus Data Editor | ![Campus Editor](Campus%20compass%20screenshots/campus%20editor.png) |
| Reset Requests | ![Reset Requests](Campus%20compass%20screenshots/reset%20requests.png) |

---

## The Problem

Large university campuses like LASU Ojo present significant navigation challenges:

- New students (freshers) spend weeks learning campus layouts, often arriving late to lectures
- Existing map applications like Google Maps lack campus-specific details such as lecture theatre numbers, departmental offices, and walking shortcuts
- Physical signboards are often outdated, vandalized, or obscured
- Visitors and parents have no reliable guidance system

---

## The Solution

Campus Compass provides a dedicated, campus-specific navigation system that:

- Displays an interactive map of LASU Ojo campus with all major buildings and pathways
- Shows the user's real-time location using GPS
- Allows search for specific buildings, lecture halls, and facilities
- Provides turn-by-turn walking directions with landmark-based instructions
- Works offline after initial load (cached map tiles and campus data)
- Is installable as a standalone app on mobile devices (PWA)

---

## Target Users

| User Type | Description |
|-----------|-------------|
| Students | Need to find lecture halls, laboratories, libraries, and eateries |
| Freshers | Require orientation and navigation support during their first weeks |
| Visitors | Parents and guests needing to locate administrative offices |
| Faculty & Staff | May use the app to guide visitors or find less familiar buildings |
| Administrators | Can manage campus data and user accounts (admin role) |

---

## User Roles

### Student
- View interactive campus map
- Search for buildings and points of interest
- Get turn-by-turn directions
- Save favorite locations
- Update profile information (including profile picture)

### Admin
- All student capabilities
- Manage user accounts (activate/deactivate, edit, delete)
- Add, edit, or remove campus locations
- Update building information and coordinates using map picker
- Process password reset requests

---

## Features

### Core Navigation
- Interactive map with OpenStreetMap tiles (Dark/Light/Satellite views)
- GPS geolocation tracking with campus boundary detection
- Search with real-time autocomplete
- Turn-by-turn walking directions with OSRM routing
- Landmark-based guidance

### User Experience
- Mobile-first responsive design
- Collapsible navbar (public pages)
- Collapsible sidebar (authenticated pages)
- Flash messages (auto-dismiss after 7 seconds)
- AJAX notifications for in-app feedback

### PWA Capabilities
- Installable on Android and iOS devices
- Offline access to cached map data
- Service worker for background caching
- Home screen icon and splash screen

### Admin Panel
- User management (view, search, filter, edit, delete)
- Campus data editor with interactive map picker
- Password reset request management (approve/reject)
- Account activation/deactivation

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask (Python) |
| Database | SQLite (development) |
| Authentication | Flask-Login |
| Frontend | HTML5, CSS3, JavaScript |
| CSS Framework | Bootstrap 5 + Custom CSS |
| Maps | Leaflet.js with OpenStreetMap tiles |
| Routing | OSRM / Leaflet Routing Machine |
| PWA | Service Worker + Web App Manifest |
| Deployment | PythonAnywhere |
| Version Control | Git |

---

## Brand Design Concept: Neo Compass

The application follows the **Neo Compass** design concept featuring:

| Element | Specification |
|---------|---------------|
| Primary Color | `#0D0D0D` (Almost Black) |
| Secondary Color | `#FFFFFF` (White) |
| Accent Color | `#00F0FF` (Neon Cyan) |
| Typography (Headings) | Clash Display |
| Typography (Body) | Satoshi |
| UI Style | Glassmorphism + Neubrutalism |
| Theme | Dark mode by default |

---

## Mobile-First Design

Campus Compass is built with a mobile-first approach, ensuring optimal usability on smartphones while remaining fully responsive on tablets and desktop screens.

| Screen Size | Layout Behavior |
|-------------|-----------------|
| Mobile (< 600px) | Bottom navigation bar, full-screen map, modal bottom sheets |
| Tablet (600px - 1024px) | Collapsible sidebar, map takes 70% of width |
| Desktop (> 1024px) | Persistent sidebar, map takes 80% of width |

---

## Key User Flows

### Registration & Login
1. User visits landing page
2. Enters matric number for verification
3. System validates against LASU student database
4. User creates password
5. Account created and user logged in

### Navigation
1. User opens Map page
2. Map centers on current GPS location (if within LASU campus)
3. User searches for destination
4. Map flies to location and shows marker with details
5. User clicks "Navigate" for turn-by-turn directions
6. Route is displayed on map with step-by-step instructions

### Saving Favorites
1. User clicks on any building marker
2. Popup displays building information
3. User clicks heart icon
4. Location is saved to user's favorites
5. Confirmation notification appears

### Admin Editing Campus Data
1. Admin logs in
2. Navigates to Campus Data Editor
3. Views list of all campus buildings
4. Adds new building with name, type, description, and coordinates (click on map)
5. Changes reflect immediately on the map

---

## Design Principles

### Mobile-First
- Touch targets minimum 48px
- Thumb-zone optimized (primary actions in bottom-right area)
- Readable font sizes (minimum 16px for body text)

### Offline First
- Core assets cached on first visit
- Map tiles cached for offline use
- Campus data stored locally

### Accessibility
- WCAG 2.1 AA compliant color contrast
- Semantic HTML structure
- Keyboard navigable

### Performance
- Lazy loading of map components
- Minimized initial load time
- Efficient caching strategy

---

## Project Structure

```
campus-compass/
├── app/
│   ├── __init__.py          # App factory
│   ├── models.py            # Database models
│   ├── routes/              # Blueprint routes
│   │   ├── auth.py          # Authentication
│   │   ├── main.py          # Public pages
│   │   ├── dashboard.py     # User dashboard
│   │   ├── map.py           # Map navigation
│   │   ├── admin.py         # Admin panel
│   │   └── upload.py        # Image upload
│   ├── templates/           # HTML templates
│   ├── static/              # CSS, JS, images
│   └── utils/               # Helper functions
├── instance/                # Database file
├── sw.js                    # Service worker
├── manifest.json            # PWA manifest
├── seed_admin.py            # Admin seeder script
├── seed_student_database.py # Student database seeder
└── requirements.txt         # Dependencies
```

---

## Database Schema

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| matric_number | String(20) | Unique login identifier |
| password_hash | String(256) | Hashed password |
| full_name | String(100) | User's full name |
| user_type | String(20) | 'student' or 'admin' |
| faculty | String(100) | Student's faculty |
| department | String(100) | Student's department |
| phone | String(15) | Contact number |
| profile_image | String(255) | Profile picture filename |
| is_active | Boolean | Account status |
| created_at | DateTime | Registration timestamp |
| last_login | DateTime | Last login timestamp |

### StudentUniversity Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| matric_number | String(20) | LASU matric number |
| full_name | String(100) | Student's full name |
| email | String(120) | University email |
| faculty | String(100) | Student's faculty |
| department | String(100) | Student's department |
| year_of_admission | Integer | Admission year |
| is_active | Boolean | Enrollment status |
| has_registered | Boolean | Platform registration status |

### SavedLocation Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to users |
| place_name | String(150) | Building name |
| latitude | Float | GPS coordinate |
| longitude | Float | GPS coordinate |
| description | String(300) | Optional notes |

---

## API Integrations

| Service | Purpose |
|---------|---------|
| Leaflet.js | Interactive map rendering |
| OpenStreetMap | Free map tiles |
| Browser Geolocation | GPS position tracking |
| OSRM | Route calculation and directions |

---

## Academic Context

This project is built upon established wayfinding theories, particularly Kevin Lynch's *The Image of the City* (1964), which identifies five elements of urban navigation: paths, edges, districts, nodes, and landmarks. The application applies these principles to the LASU campus environment.

The literature review also draws from research on:

- Location-Based Services (LBS) in education
- GPS accuracy and limitations in campus settings
- Pedestrian navigation vs. vehicular navigation
- Smart campus initiatives in Nigerian universities
- PWA adoption and offline-first strategies

---

## Challenges Encountered

### CSRF Token Issues with AJAX Requests
Ensuring that AJAX requests included necessary CSRF tokens was a challenge. The solution involved creating a function to retrieve the CSRF token from a hidden input and including it in request headers for all AJAX operations.

### Profile Image Upload
Image upload required proper CSRF token handling and file validation. The solution implemented a dedicated upload blueprint with proper CSRF token inclusion in FormData.

### GPS Location Detection and Accuracy
GPS accuracy varied especially inside buildings. The solution implemented campus boundary detection that checks whether user location falls within LASU Ojo campus area and provides appropriate messaging.

### Map Tile Loading and Styling (Including Google Maps API Challenge)
The initial implementation using Google Maps API required a credit card for billing. The solution switched to Leaflet.js with CartoDB tile layers, which provides clear labeling, multiple style options, and requires no API key or billing information.

### Real-Time Search Performance
Filtering buildings on every keystroke caused lag. The solution implemented debounced input handling that waits for the user to pause typing before performing the search.

### Deployment on PythonAnywhere
Static file configuration and WSGI setup required careful attention. The solution involved creating a proper wsgi.py file and configuring static file mappings in the PythonAnywhere web interface.

---

## Limitations (Current Scope)

| Limitation | Explanation |
|------------|-------------|
| Outdoor only | Indoor navigation requires different technology (GPS signals do not penetrate buildings reliably) |
| Internet required for first load | Initial map tile download needs connectivity; subsequent use works offline |
| GPS accuracy | 5-10 meter accuracy typical; may be affected by tall buildings or weather |
| Battery usage | Continuous GPS tracking consumes battery |
| Android PWA priority | While iOS supports PWAs, Android provides the optimal experience |

---

## Future Enhancements

- Indoor navigation for major buildings (using Bluetooth beacons or Wi-Fi positioning)
- Real-time crowd-sourced updates (road closures, construction)
- Integration with academic calendar (show lecture locations based on schedule)
- Push notifications for campus announcements
- Multiple campus support (if expanded beyond LASU Ojo)

---

## Installation

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/campus-compass.git
cd campus-compass
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///campus.db
```

5. Initialize database:
```bash
python -c "from app import create_app, db; app = create_app(); with app.app_context(): db.create_all()"
```

6. Seed the database:
```bash
python seed_admin.py
python seed_student_database.py
```

7. Run the application:
```bash
python run.py
```

8. Visit `http://localhost:5000`

---

## Deployment

The application is deployed on PythonAnywhere at: [https://campuscompass.pythonanywhere.com/](https://campuscompass.pythonanywhere.com/)

---

## License

This project is for academic purposes as part of a Bachelor's degree in Computer Science.

---

## Acknowledgments

- Kevin Lynch - Wayfinding theory foundation
- OpenStreetMap contributors - Free map data
- Leaflet.js team - Interactive mapping library
- Academic supervisor for guidance and feedback
- All students who participated in testing

---

## Author

**Awoniyi Azeez Adeola**
- Matric Number: 220591095
- Department: Computer Science
- Faculty: Computing Science
- Lagos State University (LASU)

---

## Contact

For questions or feedback regarding this project, please refer to the Department of Computer Science, Faculty of Computing Science, Lagos State University (LASU).

---

**Live Demo:** [https://campuscompass.pythonanywhere.com/](https://campuscompass.pythonanywhere.com/)

**Version:** 1.0  
**Status:** Production
```