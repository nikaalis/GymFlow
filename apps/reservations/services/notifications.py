def reservation_notice(reservation, event):
    """Notification seam for future email, SMS, or push integrations."""
    return {
        "user_id": reservation.user_id,
        "reservation_id": reservation.pk,
        "event": event,
    }
