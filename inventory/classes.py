from __future__ import annotations

class Container:
  def __init__(self, name: str, parent: Container, row_num: str) -> None:
    self.name = name
    self.parent = parent
    self.items = []
    self.row_num = row_num
  def __str__(self) -> str:
    return (f'{self.parent} -> ' if self.parent != None else '') + f'{self.name}'
  def __repr__(self) -> str:
    return self.__str__()

class Item:
  def __init__(self, name: str, container: Container) -> None:
    self.name = name
    self.container = container
    self.attributes = {}
  def __str__(self) -> str:
    return f'\'{self.name}\'{" " + str(self.attributes) if self.attributes != {} else ""} in {self.container}'
  def __repr__(self) -> str:
    return str(self.__dict__)
  def __eq__(self, other) -> bool:
    return self.__dict__ == other.__dict__
  def add_attr(self, key, val) -> Item:
    self.attributes[key] = val
    return self

class InventoryException(Exception):
  pass
