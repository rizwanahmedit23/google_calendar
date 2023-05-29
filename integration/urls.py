from django.urls import path
from .views import GoogleCalendarInitView, GoogleCalendarRedirectView

urlpatterns = [
    path('init/', GoogleCalendarInitView.as_view(), name='google-calendar-init'),
    path('redirect/', GoogleCalendarRedirectView.as_view(), name='google-calendar-redirect'),
]
