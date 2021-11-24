from __future__ import annotations
import googleapiclient
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from typing import Dict, List, Tuple
from inventory.classes import Item, Container
from inventory.serialization import deserialize_sheet, serialize_container_contents
from pathlib import Path
import json

from inventory.serialization import deserialize_container_contents

SHEET_RANGE = 'A2:D1000'
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
AUTH_DIR = Path(__file__).joinpath('../../auth')
SECRETS = json.loads(AUTH_DIR.joinpath('secrets.json').read_text())
SHEET_ID: str = SECRETS['SHEET_ID']

def create_service():
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  token = AUTH_DIR.joinpath('token.json')
  if token.is_file():
    creds = Credentials.from_authorized_user_file(str(token), SCOPES)

  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    success = False
    if creds and creds.expired and creds.refresh_token:
      try:
        creds.refresh(Request())
        success = True
      except:
        token.unlink()
    if not success:
      flow = InstalledAppFlow.from_client_secrets_file(str(AUTH_DIR.joinpath('credentials.json')), SCOPES)
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    token.write_text(creds.to_json())

  service = build('sheets', 'v4', credentials=creds)
  return service

def fetch_data(service) -> Tuple[List[Item], List[Item], str] | None:
  sheet = service.spreadsheets()
  result = sheet.values().get(spreadsheetId=SHEET_ID, range=SHEET_RANGE).execute()
  values: List[List[str]] = result.get('values', [])

  if not values:
    return None
  else:
    return deserialize_sheet(values)

def orphanize_item(service, item: Item, orphan_items: str) -> None:
  request = service.spreadsheets().values().update(
    spreadsheetId=SHEET_ID, range=f'D2', valueInputOption='USER_ENTERED',
    body={
      'range': f'D2',
      'values': [[orphan_items + f'; {item.name}']]
    }
  )
  request.execute()

def remove_item(service, item: Item) -> None:
  remaining_items: List[Item] = [x for x in item.container.items if x is not item]
  request = service.spreadsheets().values().update(
    spreadsheetId=SHEET_ID, range=f'C{item.container.row_num}',
    valueInputOption='USER_ENTERED',
    body={
      'range': f'C{item.container.row_num}',
      'values': [[serialize_container_contents(remaining_items)]]
    }
  )
  request.execute()

def update_item(service, item: Item) -> None:
  request = service.spreadsheets().values().update(
    spreadsheetId=SHEET_ID, range=f'C{item.container.row_num}',
    valueInputOption='USER_ENTERED',
    body={
      'range': f'C{item.container.row_num}',
      'values': [[serialize_container_contents(item.container.items)]]
    }
  )
  request.execute()

def add_item(service, item: Item) -> None:
  request = service.spreadsheets().values().update(
    spreadsheetId=SHEET_ID, range=f'C{item.container.row_num}',
    valueInputOption='USER_ENTERED',
    body={
      'range': f'C{item.container.row_num}',
      'values': [[serialize_container_contents(item.container.items + [item])]]
    }
  )
  request.execute()
