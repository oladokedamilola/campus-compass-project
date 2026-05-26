# Campus Compass

A Progressive Web App (PWA) for campus navigation at Lagos State University (LASU), Ojo Campus.

---

## Project Overview

Campus Compass is a mobile-first web application designed to help students, faculty, and visitors navigate the LASU Ojo campus efficiently. The app uses GPS technology and interactive mapping to provide turn-by-turn directions to buildings, lecture halls, administrative offices, and other points of interest across the campus.

This project addresses the challenges of wayfinding on a large university campus where new students and visitors frequently struggle to locate specific buildings and facilities.

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
- Update profile information

### Admin
- All student capabilities
- Manage user accounts
- Add, edit, or remove campus locations
- Update building information and coordinates
- View system analytics

---

## Planned Features

### Phase 1: Foundation
- User authentication (email + password)
- Role-based access control (Student / Admin)
- Session management

### Phase 2: Core Navigation
- Interactive map with OpenStreetMap tiles
- GPS geolocation tracking
- Searchable database of campus buildings
- Custom markers with building information

### Phase 3: Directions
- Point-to-point route calculation
- Turn-by-turn text instructions
- Landmark-based guidance (e.g., "Turn left at the Library")
- Distance and estimated walking time

### Phase 4: User Experience
- Mobile-first responsive design
- Collapsible navbar (public pages)
- Collapsible sidebar (authenticated pages)
- Flash messages (auto-dismiss after 7 seconds)
- AJAX notifications for in-app feedback

### Phase 5: PWA Capabilities
- Installable on Android and iOS devices
- Offline access to cached map data
- Service worker for background caching
- Home screen icon and splash screen

### Phase 6: Admin Panel
- User management (view, edit, delete)
- Campus data editor (add/remove buildings)
- Real-time updates to map data

### Phase 7: Additional Features
- Saved favorites per user
- Recently visited locations
- Share location feature
- Campus event notifications (future)

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask (Python) |
| Database | SQLite (development) / PostgreSQL (production) |
| Authentication | Flask-Login |
| Frontend | HTML5, CSS3, JavaScript |
| CSS Framework | Bootstrap 5 + Custom CSS |
| Maps | Leaflet.js with OpenStreetMap tiles |
| Routing | OSRM / Leaflet Routing Machine |
| PWA | Service Worker + Web App Manifest |
| Deployment | Render.com / PythonAnywhere |
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
2. Clicks Register / Login
3. Provides email, full name, password (students also provide matric number)
4. Account is created session starts
5. User is redirected to dashboard

### Navigation
1. User opens Map page
2. Map centers on current GPS location
3. User searches for destination (e.g., "Senate Building")
4. Map flies to location and shows marker
5. User clicks "Navigate" for turn-by-turn directions
6. Route is displayed on map with step-by-step instructions

### Saving Favorites
1. User clicks on any building marker
2. Popup displays building information
3. User clicks heart/bookmark icon
4. Location is saved to user's favorites
5. Confirmation notification appears

### Admin Editing Campus Data
1. Admin logs in
2. Navigates to Admin Panel
3. Views list of all campus locations
4. Adds new building with name and coordinates
5. Changes reflect immediately on map

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
│   │   └── admin.py         # Admin panel
│   ├── templates/           # HTML templates
│   ├── static/              # CSS, JS, images
│   └── utils/               # Helper functions
├── instance/                # Database file
├── sw.js                    # Service worker
├── manifest.json            # PWA manifest
└── requirements.txt         # Dependencies
```

---

## Database Schema

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| email | String(120) | Unique, indexed |
| password_hash | String(256) | Hashed password |
| full_name | String(100) | User's full name |
| user_type | String(20) | 'student' or 'admin' |
| matric_number | String(20) | Student only |
| is_active | Boolean | Account status |
| created_at | DateTime | Registration timestamp |
| last_login | DateTime | Last login timestamp |

### Saved Locations Table (Future)
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

## Contact

For questions or feedback regarding this project, please refer to the Department of Computer Science, Faculty of Computing Science, Lagos State University (LASU).

---

**Version:** 1.0  
**Status:** Development Phase
```

---