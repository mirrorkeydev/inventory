from __future__ import annotations
import googleapiclient
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from typing import Dict, List, Tuple
from auth.secrets import SHEET_ID
from classes import Item, Container
import os
import sys

SHEET_RANGE = 'A2:D1000'
DELIM = '; '
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def create_service():
  # Navigate to the script's location, so we can run this script from any
  # directory but still reference the credentials.json file inside it.
  os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))
  os.chdir("./auth")

  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    success = False
    if creds and creds.expired and creds.refresh_token:
      try:
        creds.refresh(Request())
        success = True
      except:
        os.remove('token.json')
    if not success:
      flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
      token.write(creds.to_json())

  service = build('sheets', 'v4', credentials=creds)
  return service

def fetch_data(service) -> Tuple[List[Item], List[Item], str] | None:
  sheet = service.spreadsheets()
  result = sheet.values().get(spreadsheetId=SHEET_ID, range=SHEET_RANGE).execute()
  values: List[List[str]] = result.get('values', [])

  if not values:
    return None
  else:
    item_list: List[Item] = []
    uncontainered_items: str = values[0][3]
    containers: Dict[str, Container] = {}

    # Grab all container names and create Containers
    for i, row in enumerate(values):
      container_name = row[0]
      container = Container(container_name, None, i+2)
      containers[container.name] = container

    # In second run-through, set parent relationships to Containers
    for row in values:
      container_name = row[0]
      parent_name = row[1] if len(row) > 1 else None
      contents = row[2] if len(row) > 2 else None

      container = containers[container_name]
      parent_container = containers.get(parent_name)
      if parent_container != None:
        container.parent = parent_container

      if contents:
        items = [Item(s, container) for s in contents.split(DELIM)]
        for item in items:
          item_list.append(item)
          container.items.append(item)

  return containers, item_list, uncontainered_items

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
      'values': [[DELIM.join([i.name for i in remaining_items])]]
    }
  )
  request.execute()

def add_item(service, item_name: str, container_name: str, containers: dict[str, Container]) -> None:
  container = containers[container_name]
  request = service.spreadsheets().values().update(
    spreadsheetId=SHEET_ID, range=f'C{container.row_num}',
    valueInputOption='USER_ENTERED',
    body={
      'range': f'C{container.row_num}',
      'values': [[DELIM.join([i.name for i in container.items]) + DELIM + item_name]]
    }
  )
  request.execute()