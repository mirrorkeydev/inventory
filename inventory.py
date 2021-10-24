from __future__ import annotations
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from secrets import SHEET_ID, SHEET_RANGE
from typing import Dict, List
import argparse
import re
import sys

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class Container:
  def __init__(self, name: str, parent: Container) -> None:
    self.name = name
    self.parent = parent
  def __str__(self) -> str:
    return (f"{self.parent} -> " if self.parent != None else "") + f"{self.name}"
  def __repr__(self) -> str:
    return self.__str__()

class Item:
  def __init__(self, name: str, container: Container) -> None:
    self.name = name
    self.container = container
  def __str__(self) -> str:
    return f"'{self.name}' in {self.container}"
  def __repr__(self) -> str:
    return self.__str__()

def fetch_data() -> List[Item] | None:
  # So we can run this script from any directory but still reference the
  # credentials.json file inside it, navigate to the script's location.
  os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
      token.write(creds.to_json())

  service = build('sheets', 'v4', credentials=creds)

  # Call the Sheets API
  sheet = service.spreadsheets()
  result = sheet.values().get(spreadsheetId=SHEET_ID, range=SHEET_RANGE).execute()
  values: List[List[str]] = result.get('values', [])

  if not values:
    return None
  else:
    item_list: List[Item] = []
    containers: Dict[str, Container] = {}

    # Grab all container names and create Containers
    for row in values:
      container_name = row[0]
      container = Container(container_name, None)
      containers[container.name] = container

    # In second run-through, set parent relationships to Containers
    for row in values:
      container_name, parent_name, contents = row

      container = containers[container_name]
      parent_container = containers.get(parent_name)
      if parent_container != None:
        container.parent = parent_container

      items = [Item(s.strip(), container) for s in contents.split(";")]
      for item in items:
        item_list.append(item)

  return item_list

def search_items(search_term: str, items: List[Item]) -> List[Item]:
  results: List[Item] = []
  for item in items:
    if re.search(search_term, item.name, flags=re.I):
      results.append(item)
  return results

def remove_item(item: Item) -> bool:
  pass

def main():
  parser = argparse.ArgumentParser(prog="Inventory CLI")
  parser.add_argument("-f", "--find", dest="f", type=str, help="find an item")
  parser.add_argument("-r", "--remove", dest="r", type=str, help="remove an item")
  args = parser.parse_args()

  items = fetch_data()
  if items == None:
    print("Data source is empty!")
    return
  print(f"searching {len(items)} items...")

  search_term = [x for x in [args.f, args.r] if x != None][0]
  
  results = search_items(search_term, items)
  if not len(results):
    print("No results found :(")

  if args.f != None:
    for item in results:
      print(item)
    return
  
  if args.r != None:
    for i, item in enumerate(results):
      print(f"{i}: {item}")
    item_num = input(f"Which item would you like to remove? (Enter #0-{len(results)-1}): ")
    remove_item(results[item_num])

if __name__ == '__main__':
  main()
