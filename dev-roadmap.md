CAMPUS COMPASS - DEVELOPMENT ROADMAP
Phase 1: Project Setup & Environment (Day 1-2)
Focus: Establishing the foundation for both backend and frontend

Initialize Flask project with proper folder structure (blueprints, templates, static, models, routes)

Set up virtual environment and install dependencies (Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, etc.)

Configure SQLite database (development) with plans to migrate to PostgreSQL later if needed

Set up environment variables for security (secret keys, session configs)

Configure Flask app for PWA readiness (proper MIME types for service worker, manifest.json)

Set up Git repository for version control

Deploy to a staging environment (Render.com or PythonAnywhere) early for continuous testing





Phase 2: Database Models & Authentication System (Day 3-5)
Focus: User management and role-based access control

Design and create User model with fields: id, email, password (hashed), full_name, user_type (student/admin), matric_number (if student), created_at, last_login

Design and create SavedLocations model (for future favorites feature) - user_id, place_name, lat, lng, notes

Set up Flask-Login for session management

Implement registration logic (email + password, no verification yet)

Implement login/logout logic with proper session handling

Create role-based decorators (@login_required, @student_required, @admin_required)

Seed database with one default admin user (for initial testing)





Phase 3: Base Templates & UI Framework (Day 6-9)
Focus: Responsive mobile-first templates with navbar/sidebar system

Public Base Template (public_base.html):

Top navigation bar with logo (Campus Compass), nav links (Home, Login, Register)

Hamburger menu icon for mobile (collapsible drawer)

X close icon to close the mobile menu

Desktop view: horizontal nav bar with visible links

Responsive breakpoints: mobile (<600px), tablet (600-1024px), desktop (>1024px)

User Base Template (user_base.html):

Sidebar navigation (collapsible on mobile, persistent on desktop)

Toggle button (hamburger) to show/hide sidebar on mobile

X close icon inside sidebar for mobile close

Sidebar contains: User avatar/name, user type badge, nav items (Dashboard, Map, Favorites, Profile, Logout)

Admin-specific sidebar items (Admin Dashboard, Manage Users, Campus Data Editor) - visible only to admin role

Flash Message System (on both bases):

Position: fixed top-center, elevated above content (z-index high)

Styled with Neo Compass colors (dark glassmorphism + neon cyan accent)

Auto-disappear after 7 seconds (JavaScript setTimeout)

Manual dismissal via X close icon

Multiple message types: success, error, warning, info (each with distinct neon accent variations)

Responsive polish:

Standard max-width for content containers (1200px on desktop, full width on mobile with side padding)

Touch-friendly buttons (min 48px height/width)

Thumb-zone optimization (primary actions in bottom-right area)







Phase 4: Core Pages - Public Section (Day 10-12)
Focus: Landing page, registration, and login flows

Home Page:

Hero section with Campus Compass branding (Neo Compass aesthetic)

Brief explanation of features (GPS navigation, campus map, directions)

Prominent CTA buttons (Login, Register)

Preview/screenshot mockup of the map interface

Footer with basic info (project credits, LASU)

Registration Page:

Form fields: full name, email, password, confirm password, user_type (dropdown: Student/Admin)

Student-only field: matric number

Client-side validation (email format, password strength, matching passwords)

AJAX submission (no page reload) with loading state

Redirect to dashboard on success

Login Page:

Form fields: email, password

"Remember Me" checkbox (optional)

AJAX submission with loading spinner

Redirect to dashboard on success

Link to registration page for new users

Logout Logic: Destroys session and redirects to home page







Phase 5: Core Pages - User Dashboard (Day 13-15)
Focus: Personalized landing after login

Dashboard Page (Student view):

Welcome message with user's name

Quick actions: "Start Navigation", "My Favorites", "Recent Places"

Mini map preview (static or interactive small map)

Campus stats (e.g., "25+ buildings mapped", "500+ students using")

Recent activity (if backend tracks it)

Dashboard Page (Admin view - additional sections):

Overview metrics (total users, total saved locations, most searched buildings)

Quick links to admin functions (Manage Users, Edit Campus Map)

System status (last data update, pending changes)

Favorites Page (for both roles):

List of user's saved campus locations

Each item has: place name, quick "Navigate" button, remove favorite button

Empty state with illustration and call-to-action to explore map

Profile Page:

View and edit profile information (full name, email, password change)

Student-specific: matric number display (non-editable)

Account deletion option (soft delete or confirm prompt)





Phase 6: Campus Map & Navigation Engine (Day 16-20)
Focus: The core functionality - map, GPS, search, directions

Map Page Setup:

Full-screen map container with Leaflet.js

OpenStreetMap tiles (free, no credit card)

GPS geolocation to center on user's position

Custom Neo Compass map markers (neon cyan glow effect)

LASU Campus Data:

Create campus_data.json with all buildings (name, lat, lng, description, building_type)

List to cover: Faculties (Science, Engineering, Arts, etc.), Admin buildings (Senate), Lecture halls (3-in-1 Hall), Library, Eateries, Hostels (if applicable), Sport complex

Load markers dynamically from JSON onto map

Search Feature:

Search bar at top (floating, glassmorphic)

Autocomplete/dropdown as user types (filtering building names)

On selection: fly map to location, open popup with building details

"Navigate" button in popup to trigger directions

Turn-by-Turn Directions:

Integration with OSRM (Open Source Routing Machine) or Leaflet Routing Machine

Current location → selected destination

Display route line on map (neon cyan stroke)

Step-by-step list of instructions (collapsible on mobile)

Landmark-based instructions (prioritize "turn left at the Library" over "walk 50 meters")

"Center on My Location" Button:

Floating Action Button (FAB) - bottom right

Re-centers map to user's GPS position

Glow effect on active use

Save to Favorites:

AJAX call to save current building/marker to user's favorites

Heart/bookmark icon on popup

Toast notification on success





Phase 7: AJAX Notifications & Real-time Feedback (Day 21-22)
Focus: In-app notifications without page reloads

Notification System Design:

Global AJAX notification handler

Types: success (green), error (red), warning (yellow), info (neon cyan)

Position: top-right or top-center (consistent with flash messages)

Auto-dismiss after 4-6 seconds (shorter than flash messages)

Integration Points:

After saving/removing a favorite

After updating profile

After successful map direction calculation

On failed GPS acquisition

On form submission errors

Notification UI:

Toast-style popups

Slide-in animation

Progress bar showing time until dismissal

Manual X close







Phase 8: Admin Panel & Campus Data Management (Day 23-25)
Focus: Giving admin ability to manage users and campus data

Admin Dashboard:

Total users count (students vs admins)

Recently registered users

Quick edit buttons

Manage Users (Admin only):

List all registered users with search/filter

Edit user details (name, email, user_type)

Reset user password (admin-initiated)

Delete user accounts

Campus Data Editor (Admin only):

List all Points of Interest (POIs) on campus

Add new building: name, coordinates (lat/lng picker on map), description, building type

Edit existing building details

Delete obsolete locations

Changes saved to campus_data.json (or database) and instantly reflected on map

Audit Log (Optional): Track who changed what and when





Phase 9: PWA Implementation (Day 26-28)
Focus: Making the app installable and offline-capable

Manifest.json:

App name: "Campus Compass"

Short name: "CampusComp"

Start URL: /dashboard (for authenticated users, fallback to home)

Icons: multiple sizes (72x72, 96x96, 128x128, 144x144, 152x152, 192x192, 384x384, 512x512)

Theme color: #0D0D0D (primary dark)

Background color: #0D0D0D

Display: "standalone" (opens like a native app)

Orientation: "portrait-primary" (for mobile)

Service Worker:

Cache core assets (HTML, CSS, JS, manifest, icons)

Cache map tiles for offline use (critical for campus dead zones)

Cache LASU campus data JSON

Implement fetch event with cache-first strategy

Background sync for saved favorites (when offline → online)

Install Prompt:

Detect when app is installable (beforeinstallprompt event)

Show custom "Install App" banner/snackbar

Buttons: Install Now, Not Now

Offline Fallback Page:

Custom offline page when no network + uncached resource

Informs user that map may be limited but saved places work







Phase 10: Testing, Optimization & Documentation (Day 29-31)
Focus: Polishing before final submission

Cross-Browser Testing:

Chrome (primary target for Android/PWA)

Firefox

Safari (iOS compatibility - PWA works differently, ensure basic functionality)

Device Testing:

Mobile (iPhone SE, Pixel, Samsung Galaxy - or emulators)

Tablet (iPad, Android tablet)

Desktop (laptop/desktop screens)

Performance Optimization:

Minimize initial load time (code splitting if needed)

Compress images and icons

Lazy load map components

Reduce main thread work during scrolling

GPS Testing:

Test on actual campus (or simulate using browser devtools)

Test in "dead zone" scenarios (offline mode)

Handle GPS permission denial gracefully

User Acceptance Testing:

Have 2-3 fellow students test the app

Collect feedback on confusing parts

Fix critical bugs

Documentation:

Write user manual (for students and admins)






Phase 11: Deployment & Final Submission (Day 32)
Focus: Getting the app live and submitting the project

Production Deployment:

Deploy to Render.com or PythonAnywhere (HTTPS required for PWA)

Configure environment variables for production

Set up database (migrate from SQLite to PostgreSQL if needed)

PWA Validation:

Run Lighthouse audit (aim for 90+ in PWA category)

Verify installability on real Android device

Test offline functionality after installation

Final Checks:

All links working

All forms submitting via AJAX (no page reloads except intentional navigations)

Flash messages and notifications working

Admin panel accessible only to admin users