from inventory.classes import Item
from inventory.serialization import serialize_container_contents

def test_simple():
  items = [Item("some garbage", None)]
  want = "some garbage"
  got = serialize_container_contents(items)
  assert want == got
