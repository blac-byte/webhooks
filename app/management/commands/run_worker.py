# app/management/commands/run_worker.py

import time
from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import Event
from app.services import process_event


class Command(BaseCommand):
    help = "Run event processing worker"

    def handle(self, *args, **options):
        self.stdout.write("Worker started...")

        while True:
            event = None

            with transaction.atomic():
                event = (
                    Event.objects
                    .select_for_update(skip_locked=True)
                    .filter(status=Event.Status.VERIFIED)
                    .order_by("created_at")
                    .first()
                )

                if event:
                    process_event(event)

            if not event:
                time.sleep(2)