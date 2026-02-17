#app/processing.py
from .models import Event
from django.utils import timezone
from django.db import transaction



def process_event(event: Event):
    if event.status != Event.Status.VERIFIED:
        return
    
    event.status = Event.Status.PROCESSING
    event.processing_started_at = timezone.now()
    event.save(update_fields=["status", "processing_started_at"])


    try:
        normalized_payload = None

        if event.source == "stripe":
            normalized_payload = normalize_event(event.raw_payload)

        if normalized_payload is None:
            event.status = Event.Status.UNSUPPORTED
            event.save(update_fields=["status"])
            return

        event.normalized_payload = normalized_payload
        event.status = Event.Status.PROCESSED
        event.processed_at = timezone.now()
        event.save(update_fields=["normalized_payload", "status", "processed_at"])

    except Exception as e:
        event.status = Event.Status.FAILED
        event.processing_error = str(e)
        event.save(update_fields=["status", "processing_error"])


        

def normalize_event(stripe_event, db_event):
    if stripe_event.get("type") != "payment_intent.succeeded":
        return None


    obj = stripe_event.get("data", {}).get("object")
    if obj is None:
        raise ValueError("Stripe event data object is null")
        
    required_fields = ["id", "amount", "currency", "status"]
    for field in required_fields:
        if field not in obj:
            raise ValueError(f"Missing required field: {field}")


    return {
        "payment_intent_id": obj["id"],
        "amount": obj["amount"],
        "currency": obj["currency"],
        "customer_id": obj.get("customer"),
        "stripe_status": obj["status"],
    }
