"""
Provisions a G Suite account for a person
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

from django.conf import settings
from django.utils import crypto

SCOPES = ["https://www.googleapis.com/auth/admin.directory.user"]


def create_user(username, first_name, last_name):
    creds = service_account.Credentials.from_service_account_file(
        settings.GSUITE_SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
        subject=settings.GSUITE_AUTH_EMAIL,
    )

    service = build("admin", "directory_v1", credentials=creds)

    body = {
        "primaryEmail": "{}@{}".format(username, settings.GSUITE_DOMAIN),
        "password": crypto.get_random_string(
            50
        ),  # Required in request, but we will never use it
        "name": {
            "givenName": first_name,
            "familyName": last_name,
        },
    }

    try:
        service.users().insert(body=body).execute()
    except HttpError as e:
        if e.resp.status == 409:
            print("Google user {} already exists".format(username))
        else:
            raise e
