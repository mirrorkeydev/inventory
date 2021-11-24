from typing import List, Dict
from inventory.classes import Item, Container
from inventory.service import DELIM

def serialize_container_contents(items: List[Item]) -> str:
  return DELIM.join([f"{i.name}{(' ' + str(i.attributes)) if i.attributes != {} else ''}" for i in items])

def serialize_sheet(raw_values: List[List[str]]):
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
      items = [Item(s, container) for s in contents.split(DELIM)]
      for item in items:
        item_list.append(item)
        container.items.append(item)

  return containers, item_list, uncontainered_items

