from json.decoder import JSONDecodeError
from typing import List, Dict
from inventory.classes import Item, Container, InventoryException
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
      raise InventoryException(f"failed to deserialize container items: {raw_item}")
    item = Item(match[1], container)
    if match[2] != None:
      try:
        item.attributes = json.loads(match[2])
      except JSONDecodeError as e:
        raise InventoryException(f"JSON attributes for item '{item.name}' in container '{item.container}'"
        f"(row {item.container.row_num}) were misformatted. See above stack trace for details.") from e
    items.append(item)
  return items

def deserialize_sheet(raw_values: List[List[str]]):
  item_list: List[Item] = []
  uncontainered_items: str = raw_values[0][3]
  containers: Dict[str, Container] = {}

  # Grab all container names and create Containers
  for i, row in enumerate(raw_values):
    row_num = i + 2
    container_name = row[0]
    if container_name is None or container_name == '':
      raise InventoryException(f"container in Sheet row {row_num} must have a name")
    container = Container(container_name, None, row_num)
    if container.name in containers:
      raise InventoryException(f"duplicate container '{container.name}' in Sheet rows "
      f"{containers[container.name].row_num} and {row_num}")
    containers[container.name] = container

  # In second run-through, set parent relationships to Containers
  # Has to be done in second run-through because children might
  # come before their parents, and we can't reference an object
  # we haven't encountered yet.
  for row in raw_values:
    container_name = row[0]
    parent_name = row[1] if len(row) > 1 else None
    contents = row[2] if len(row) > 2 else None

    container = containers[container_name]
    if parent_name != None:
      parent_container = containers.get(parent_name)
      if parent_container == None:
        raise Exception(f"container {container.name}'s (row {container.row_num}) parent"
        f" '{parent_name}' does not exist (typo?)")
      container.parent = parent_container

    if contents:
      items = deserialize_container_contents(contents, container)
      for item in items:
        item_list.append(item)
        container.items.append(item)

  return containers, item_list, uncontainered_items
