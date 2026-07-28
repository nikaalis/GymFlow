# GymFlow

## Overview

GymFlow is a smart gym equipment reservation system built for a university recreation center. It gives members a clear way to reserve equipment, workout rooms, courts, and group areas while a central Coordinator service prevents double-bookings, enforces reset periods, manages priority waitlists, and tracks attendance.

The project follows a domain-based Django structure inspired by the architecture and documentation conventions of Pynance. GymFlow does not reuse any finance logic.

## Core Functionality

- Reserve equipment, rooms, courts, and group exercise areas.
- Prevent overlapping reservations and enforce three- or five-minute reset periods.
- Queue requests by accessibility, team, class, and individual priority.
- Use FIFO ordering when requests have equal priority.
- Promote the next eligible member after cancellations or missed check-ins.
- Track check-ins, cancellations, no-shows, and temporary booking restrictions.
- Block resources during maintenance and when an area reaches capacity.

## Features

### Member features

- Registration, login, logout, and session authentication
- Searchable resource browsing and area/type filters
- Reservation confirmation or automatic waitlist entry
- Queue-position display
- Mobile-friendly check-in
- Cancellation and reservation history

### Staff features

- Protected staff dashboard
- Resource and area-capacity management
- Maintenance scheduling
- Current and upcoming reservation monitoring
- Cancellation and no-show history

## System Architecture

### Backend

The backend uses four Django apps: `accounts`, `resources`, `reservations`, and `dashboard`. Business rules are separated from views in the reservations service layer. `Coordinator` is the main entry point for reservation, queue, check-in, cancellation, promotion, completion, and no-show workflows.

### Frontend

The interface uses Django templates, custom CSS, and lightweight JavaScript. It includes a dark responsive sidebar, teal visual system, resource cards, status badges, KPI cards, tables, filters, staff controls, and mobile navigation.

### Database

SQLite is used for local development. Django migrations define the custom user, gym areas, resources, maintenance windows, reservations, and priority queue entries.

### Data Processing

Availability checks consider resource status, area capacity, maintenance overlap, confirmed sessions, and the resource reset duration. Queue processing sorts by descending priority and then creation time. Same-priority requests therefore remain FIFO.

## Technology Stack

- Python 3
- Django 5.1.6
- Django templates
- Custom CSS
- JavaScript
- SQLite
- Django sessions
- Django test framework
- Git and GitHub

## Installation and Setup

Clone the repository and enter the project directory:

```bash
git clone https://github.com/YOUR_USERNAME/GymFlow.git
cd GymFlow
```

## Environment Setup

Create and activate a virtual environment.

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS or Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

For a non-development environment, copy `.env.example` to `.env`, set a unique `DJANGO_SECRET_KEY`, and load it into your shell or deployment environment.

## Installing Dependencies

```bash
pip install -r requirements.txt
```

## Database Setup

```bash
python manage.py migrate
python manage.py seed_gymflow
python manage.py createsuperuser
```

The seed command is optional. It adds sample gym areas and resources for local testing.

## Running the Application

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in a browser.

## Running Tests

Run the entire suite:

```bash
python manage.py test
```

Run each app separately:

```bash
python manage.py test apps.accounts
python manage.py test apps.reservations
python manage.py test apps.resources
python manage.py test apps.dashboard
```

## Challenges

The main challenge was keeping booking decisions consistent across direct reservations, waitlists, cancellations, check-ins, maintenance, and reset periods. Moving these decisions into the Coordinator and small service modules avoids duplicating important rules inside views.

Another challenge was maintaining fair queue behavior. GymFlow combines explicit priority levels with FIFO timestamps and only allows a higher-priority request to displace the newest request at the lowest current priority when a queue is full.

## Key Outcomes

- A complete Django project organized by feature domain
- Centralized, testable reservation logic
- Priority and FIFO waitlist behavior
- Protected member and staff workflows
- Responsive frontend without a third-party UI framework
- Eighteen automated tests for the project’s highest-risk rules
- PlantUML source and exported SVG diagrams

## Future Enhancements

- Email, SMS, and push notifications
- QR-code check-in kiosks
- PostgreSQL production configuration
- Live occupancy sensors
- Recurring team and class reservations
- Calendar synchronization
- Analytics charts and downloadable reports
- REST API and native mobile application

## Copyright

Copyright © 2026 GymFlow. This project is provided for educational use.
