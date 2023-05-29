from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.urls import reverse
from django.views import View
from google.auth.transport import requests
from google.oauth2 import id_token
import requests as google_requests
import logging
from django.shortcuts import render
import json

GOOGLE_OAUTH2_CLIENT_ID = "622199708954-bpmfbukpabrk9g2dtplbhneb7bq1b91m.apps.googleusercontent.com"
GOOGLE_OAUTH2_CLIENT_SECRET = "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"
GOOGLE_OAUTH2_REDIRECT_URI = "http://localhost:8000/rest/v1/calendar/redirect/"


class GoogleCalendarInitView(View):
    def get(self, request):
        # Step 1 of OAuth: Redirect the user to Google's OAuth 2.0 consent screen
        authorization_url = f"https://accounts.google.com/o/oauth2/auth?client_id={GOOGLE_OAUTH2_CLIENT_ID}&redirect_uri={GOOGLE_OAUTH2_REDIRECT_URI}&response_type=code&scope=https://www.googleapis.com/auth/calendar.readonly"
        return HttpResponseRedirect(authorization_url)


class GoogleCalendarRedirectView(View):
    def get(self, request):
        # Step 2 of OAuth: Handle the redirect request from Google with the authorization code
        code = request.GET.get("code")
        # print("Received code:", code)
        try:
            # Exchange the authorization code for an access token
            token_url = "https://oauth2.googleapis.com/token"
            token_payload = {
                "code": code,
                "client_id": GOOGLE_OAUTH2_CLIENT_ID,
                "client_secret": GOOGLE_OAUTH2_CLIENT_SECRET,
                "redirect_uri": GOOGLE_OAUTH2_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
            token_response = google_requests.post(token_url, data=token_payload)

            # Check if the token response was successful
            if token_response.status_code != 200:
                return HttpResponse("Token exchange failed.")

            token_data = token_response.json()
            access_token = token_data.get("access_token")

            # Debug statement to inspect access_token value
            # print("Access Token:", access_token)
            # print("Token Response:", token_response)
            # print("Token Data:", token_data)

            # Check if the access token is available
            if access_token is None:
                raise ValueError("Access token is None")

            # Use the access token to fetch events from the user's calendar
            calendar_url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
            headers = {"Authorization": f"Bearer {access_token}"}
            calendar_response = google_requests.get(calendar_url, headers=headers)
            calendar_data = calendar_response.json()

            # Process the calendar events data
            events = []
            for item in calendar_data.get("items", []):
                event = {
                    "summary": item.get("summary"),
                    "start": item.get("start").get("dateTime"),
                    "end": item.get("end").get("dateTime"),
                }
                events.append(event)

            # Render a template to display the events
            context = {
                "events": events,
            }
            return render(request, "events.html", context)
            # Display the events or perform any desired action
            # return HttpResponse(f"Events: {events}")
        except Exception as e:
            logging.exception("An error occurred while processing the redirect: %s", str(e))
            return HttpResponse("An error occurred while processing the redirect.")
