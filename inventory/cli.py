from typing import List
from inventory.classes import Item
from inventory.service import (
  fetch_data,
  create_service,
  remove_item,
  add_item,
  orphanize_item,
  update_item
)
import argparse
import re

def search_items(search_term: str, items: List[Item]) -> List[Item]:
  results: List[Item] = []
  for item in items:
    if re.search(search_term, item.name, flags=re.I):
      results.append(item)
  return results

def main() -> None:
  parser = argparse.ArgumentParser(prog='Inventory CLI')
  parser.add_argument('-f', '--find', dest='find_term', type=str, help='find an item')
  parser.add_argument('-r', '--remove', dest='remove_term', type=str, help='remove an item')
  parser.add_argument('-a', '--add', dest='add_term', type=str, help='add an item and specify a container.', nargs=2)
  parser.add_argument('-m', '--move', dest='move_term', type=str, help='specify an item and specify a destination container.', nargs=2)
  args = parser.parse_args()

  s = create_service()
  containers, items, orphan_items = fetch_data(s)
  if containers == None or items == None:
    print('Data source is empty!')
    return

  if args.find_term != None:
    print(f'searching {len(containers)} containers and {len(items)} items...', end='')
    results = search_items(args.find_term, items)
    print(f'{len(results)} match(es)')
    for item in results:
      print(f'  - {item}')
    return
  
  if args.remove_term != None:
    print(f'searching {len(containers)} containers and {len(items)} items...', end='')
    results = search_items(args.remove_term, items)
    print(f'{len(results)} match(es)')
    if not len(results):
      print('Make sure that the item you want to remove exists.')
      return
    for i, item in enumerate(results):
      print(f'{i}: {item}')
    item_num = int(input(f'Which item would you like to remove? (Enter #0-{len(results)-1}): '))
    if item_num < 0 or item_num >= len(results):
      print('You entered an invalid item.')
      return
    item = results[item_num]
    if item.attributes.get("count") != None:
      choice = input("Would you like to decrement this item or remove it completely? (Enter d# or r): ")
      if (match := re.match(r"^d(\d+)$", choice)):
        item.attributes["count"] = item.attributes.get("count") - int(match[1])
        if item.attributes["count"] > 0:
          update_item(s, item)
          print(f"Item \'{item.name}\' decremented by {match[1]}!")
          return
        print("Decrementing to 0 items, removing the item.")
    remove_item(s, item)
    orphanize_item(s, item, orphan_items)
    print(f'Item \'{item.name}\' removed!')
    return

  if args.add_term != None:
    item_name, container_name = args.add_term
    container = containers[container_name]
    add_item(s, Item(item_name, container))
    print(f'Item \'{item_name}\' added to container {container_name}!')
    return

  if args.move_term != None:
    item_name, container_name = args.move_term
    print(f'searching {len(containers)} containers and {len(items)} items...', end='')
    results = search_items(item_name, items)
    print(f'{len(results)} match(es)')
    if not len(results):
      print('Make sure that the item you want to move exists.')
      return
    for i, item in enumerate(results):
      print(f'{i}: {item}')
    item_num = int(input(f'Which item would you like to move? (Enter #0-{len(results)-1}): '))
    item = results[item_num]

    remove_item(s, item)
    item.container = containers[container_name]
    add_item(s, item)
    print(f'Item \'{item_name}\' moved to container \'{container_name}\'!')
    return

if __name__ == '__main__':
  main()
