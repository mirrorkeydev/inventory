from typing import List, Dict
from inventory.classes import Item, Container
import json
import re

DELIM = '; '

def serialize_container_contents(items: List[Item]) -> str:
  return DELIM.join([f"{i.name}{(' ' + json.dumps(i.attributes)) if i.attributes != {} else ''}" for i in items])

def deserialize_container_contents(raw_items: str, container: Container) -> List[Item]:
  items: List[Item] = []
  for raw_item in raw_items.split(DELIM):
    match = re.match(r"^([^{}]+)(?: ({.+}))?$", raw_item)
    if not match:
      raise Exception(f"failed to deserialize object {raw_item}")
    item = Item(match[1], container)
    if match[2] != None:
      item.attributes = json.loads(match[2])
    items.append(item)
  return items

def deserialize_sheet(raw_values: List[List[str]]):
  item_list: List[Item] = []
  uncontainered_items: str = raw_values[0][3]
  containers: Dict[str, Container] = {}

  # Grab all container names and create Containers
  for i, row in enumerate(raw_values):
    container_name = row[0]
    container = Container(container_name, None, i+2)
    containers[container.name] = container

  # In second run-through, set parent relationships to Containers
  for row in raw_values:
    container_name = row[0]
    parent_name = row[1] if len(row) > 1 else None
    contents = row[2] if len(row) > 2 else None

    container = containers[container_name]
    parent_container = containers.get(parent_name)
    if parent_container != None:
      container.parent = parent_container

    if contents:
      items = deserialize_container_contents(contents, container)
      for item in items:
        item_list.append(item)
        container.items.append(item)

  return containers, item_list, uncontainered_items

