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
  def __str__(self) -> str:
    return f'\'{self.name}\' in {self.container}'
  def __repr__(self) -> str:
    return self.__str__()
