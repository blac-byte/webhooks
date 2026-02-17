import stripe
import json
from .models import Event

from django.views import View
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt

endpoint_secret='whsec_c421b9ac971a479fe95e39ccb0952a3c01ce355962eb7e8f547563c00c94040e'

@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    def post(self, request):
        payload = request.body
        sig_header = request.headers.get("Stripe-Signature")

        stripe_event, error = stripe_event_constructor(payload, sig_header)
        if error:
            return error

        try:
            db_event = Event.objects.create(
                source = "stripe",
                external_event_id = stripe_event["id"],
                raw_payload = stripe_event,
                status = Event.Status.VERIFIED,
                )

        except IntegrityError:
            return HttpResponse(status=200)
        
        return HttpResponse(status=200)
    

    def get(self, request):
        return HttpResponse(status=405)



def stripe_event_constructor(payload, sig_header):
    try:
        stripe_event = stripe.Webhook.construct_event(
        payload = payload, 
        sig_header = sig_header,
        secret = endpoint_secret
        )
    except stripe.error.SignatureVerificationError:
        return None, HttpResponse(status = 400)
    except Exception:
        return None, HttpResponse(status = 400)
    
    return stripe_event, None







@method_decorator(csrf_exempt, name="dispatch")
class GithubWebhookView(View):

    def post(self, request):
        payload, error = parse_json(request)
        if error:
            return error

        external_event_id, error = validate_payload(payload)
        if error:
            return error

        try:
            db_event = Event.objects.create(
                source="github",
                external_event_id=external_event_id,
                raw_payload=payload,
            )
        except IntegrityError:
            return HttpResponse("duplicate", status=200)

        #this classification should be inside normalization layer
        db_event.status = classify_event(payload)
        db_event.save()

        return HttpResponse(db_event.status, status=201)


    def get(self, request):
        return HttpResponse(status=405)








def parse_json(request):
    try:  
        return json.loads(request.body), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "Invalid JSON"})


def validate_payload(payload):
    external_event_id = payload.get("id")
    if not external_event_id:
        return None, JsonResponse({"error": "event_id not found"}) 
    return external_event_id, None


def classify_event(payload):
    if payload.get("type") != "issue_opened":
        return Event.Status.UNSUPPORTED
    return Event.Status.VERIFIED






def events(request):
    events = Event.objects.all().order_by("created_at")

    data = [
        {
        "id": e.id,
        "source": e.source,
        "status": e.status,
        "created_at": e.created_at,
        }
        for e in events
    ]

    return JsonResponse(data, safe=False)