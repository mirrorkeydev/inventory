from inventory.classes import Item, Container
from inventory.serialization import deserialize_container_contents, serialize_container_contents


def test_simple_item_serialization():
  c = Container("dummy container", "1", None)
  items = [Item("some garbage", c)]
  want = "some garbage"
  got = serialize_container_contents(items)
  assert want == got

def test_complex_item_serialization():
  c = Container("dummy container", "1", None)
  items = [
    Item("some garbage", c).add_attr("count", 3).add_attr("expires", "nov 2022")
  ]
  want = r'some garbage {"count": 3, "expires": "nov 2022"}'
  got = serialize_container_contents(items)
  assert want == got

def test_multiple_item_serialization():
  c = Container("dummy container", "1", None)
  items = [
    Item("other garbage w multiple,%&*@ symbols", c),
    Item("some garbage", c).add_attr("count", 2).add_attr("expires", "nov 2022")
  ]
  want = r'other garbage w multiple,%&*@ symbols; some garbage {"count": 2, "expires": "nov 2022"}'
  got = serialize_container_contents(items)
  assert want == got

def test_simple_item_deserialization():
  c = Container("dummy container", "1", None)
  raw_items = "some garbage"
  got = deserialize_container_contents(raw_items, c)
  want = [Item("some garbage", c)]
  print(got)
  print(want)
  assert want == got

def test_complex_item_deserialization():
  c = Container("dummy container", "1", None)
  raw_items = r'some garbage {"count": 3, "expires": "nov 2022"}'
  got = deserialize_container_contents(raw_items, c)
  want = [
    Item("some garbage", c).add_attr("count", 3).add_attr("expires", "nov 2022")
  ]
  assert want == got

def test_multiple_item_deserialization():
  c = Container("dummy container", "1", None)
  raw_items = r'other garbage w multiple,%&*@ symbols; some garbage {"count": 2, "expires": "nov 2022"}'
  got = deserialize_container_contents(raw_items, c)
  want = [
    Item("other garbage w multiple,%&*@ symbols", c),
    Item("some garbage", c).add_attr("count", 2).add_attr("expires", "nov 2022")
  ]
  assert want == got
