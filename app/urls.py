from django.urls import path
from .views import StripeWebhookView, GithubWebhookView, events, dashboard

urlpatterns = [
    path("stripe/", StripeWebhookView.as_view()),
    path("github/", GithubWebhookView.as_view()),
    path("events/", events),
    path("dashboard/", dashboard, name="dashboard"),
]