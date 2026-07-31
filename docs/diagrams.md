# GymFlow System Diagrams

These diagrams describe the implemented Django website. GitHub and IDE Markdown
previewers with Mermaid support render them directly. The original PlantUML
source and exported class/use-case SVG files remain available in the repository.

## 1. System Architecture

```mermaid
flowchart TB
    browser["Member or staff browser"]

    subgraph django["GymFlow Django website"]
        urls["URL routing"]
        views["Domain views and forms"]
        templates["Django templates"]
        static["CSS and JavaScript"]
        auth["Django session authentication"]
        coordinator["Reservation Coordinator"]
        availability["Availability service"]
        queue["Priority queue service"]
        notifications["Notification seam"]
        orm["Django ORM and domain models"]
    end

    database[("SQLite database")]

    browser --> urls
    urls --> views
    views --> auth
    views --> coordinator
    views --> templates
    templates --> browser
    static --> browser
    coordinator --> availability
    coordinator --> queue
    coordinator --> notifications
    availability --> orm
    queue --> orm
    coordinator --> orm
    orm --> database
```

## 2. Use Cases

```mermaid
flowchart LR
    member(["Member"])
    staff(["Staff"])

    subgraph gymflow["GymFlow website"]
        register["Register and sign in"]
        browse["Browse and filter resources"]
        reserve["Request a reservation"]
        waitlist["Join the priority waitlist"]
        checkin["Check in"]
        cancel["Cancel a reservation"]
        history["Review reservation history"]
        dashboard["View staff dashboard"]
        manage["Manage resources and capacity"]
        maintenance["Schedule maintenance"]
        attendance["Process completions and no-shows"]
    end

    member --> register
    member --> browse
    member --> reserve
    member --> waitlist
    member --> checkin
    member --> cancel
    member --> history

    staff --> dashboard
    staff --> manage
    staff --> maintenance
    staff --> attendance

    reserve -. "when unavailable" .-> waitlist
```

## 3. Domain Class Diagram

```mermaid
classDiagram
    class User {
        +username
        +role
        +no_show_count
        +cancellation_count
        +restricted_until
        +is_booking_restricted
        +is_gym_staff
    }

    class Area {
        +name
        +max_capacity
        +current_occupancy
        +is_at_capacity
    }

    class Resource {
        +name
        +resource_type
        +capacity
        +reset_minutes
        +is_active
        +is_under_maintenance
    }

    class MaintenanceWindow {
        +start_time
        +end_time
        +reason
        +overlaps()
    }

    class Reservation {
        +start_time
        +end_time
        +status
        +priority
        +check_in_at
        +created_at
    }

    class PriorityQueueEntry {
        +priority
        +created_at
    }

    class Coordinator {
        +request_reservation()
        +cancel()
        +promote_next()
        +check_in()
        +mark_no_show()
        +complete()
    }

    Area "1" --> "*" Resource
    Resource "1" --> "*" MaintenanceWindow
    User "1" --> "*" Reservation
    Resource "1" --> "*" Reservation
    Reservation "1" --> "0..1" PriorityQueueEntry
    Coordinator ..> Reservation
    Coordinator ..> PriorityQueueEntry
    Coordinator ..> Resource
```

## 4. Reservation State Diagram

```mermaid
stateDiagram-v2
    [*] --> Requested

    Requested --> Pending: resource available
    Requested --> Queued: unavailable or conflicting
    Queued --> Pending: promoted from waitlist
    Queued --> Cancelled: member cancels or queue rejects request

    Pending --> Active: valid check-in
    Pending --> Cancelled: member cancels
    Pending --> NoShow: check-in window missed

    Active --> Completed: staff completes session
    Active --> Cancelled: reservation cancelled

    Completed --> [*]
    Cancelled --> [*]
    NoShow --> [*]
```

## Existing Exported UML

- [Class diagram SVG](../UMLdiagrams/gymflow_uml/class_diagram.svg)
- [Use-case diagram SVG](../UMLdiagrams/gymflow_uml/use_case_diagram.svg)
- [PlantUML source](../gymflow_uml.puml)
