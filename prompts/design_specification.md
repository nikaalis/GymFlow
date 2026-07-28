# GymFlow Design Specification

## Product Goal

Build a Django reservation system for a university recreation center. The central service, the Coordinator, assigns reservations, prevents unsafe overlaps, operates priority waitlists, and records member attendance.

## Users

- Members browse resources, request time slots, join waitlists, cancel, check in, and review history.
- Staff manage resources, maintenance windows, area capacity, upcoming reservations, and attendance history.

## Resource Rules

- A single piece of equipment may have one member reservation at a time.
- A room, court, or group area may have one group reservation at a time.
- Equipment requires at least three minutes between reservations.
- Rooms, courts, and group areas require at least five minutes between reservations.
- Inactive resources, maintenance windows, and full areas block confirmation.

## Queue Rules

Priority is ordered from lowest to highest as individual, class, team, and accessibility. Requests at the same priority follow FIFO ordering. Each resource queue holds five requests. A new request may evict the newest request from the current lowest priority only when the new request has a higher priority.

## Attendance Rules

Members may check in from 15 minutes before the start time through 10 minutes after it. Missing the window changes the reservation to no-show and promotes the next eligible queued member. Three no-shows trigger a seven-day booking restriction.

## Interface Direction

Use a dark fixed sidebar, teal accents, responsive cards, searchable resource filters, clear status pills, mobile-friendly forms, KPI cards, capacity indicators, and accessible semantic HTML.

## Architecture

Keep Django models and views within domain apps. Put availability, queue, reservation orchestration, and notification seams in the reservations service layer. Use SQLite for development, Django sessions for authentication, templates for server rendering, and plain CSS and JavaScript for the interface.
