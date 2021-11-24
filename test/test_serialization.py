from inventory.classes import Item
from inventory.serialization import deserialize_container_contents, serialize_container_contents

def test_simple_item_serialization():
  items = [Item("some garbage", None)]
  want = "some garbage"
  got = serialize_container_contents(items)
  assert want == got

def test_complex_item_serialization():
  items = [
    Item("some garbage", None).add_attr("count", 3).add_attr("expires", "nov 2022")
  ]
  want = r'some garbage {"count": 3, "expires": "nov 2022"}'
  got = serialize_container_contents(items)
  assert want == got

def test_multiple_item_serialization():
  items = [
    Item("other garbage w multiple,%&*@ symbols", None),
    Item("some garbage", None).add_attr("count", 2).add_attr("expires", "nov 2022")
  ]
  want = r'other garbage w multiple,%&*@ symbols; some garbage {"count": 2, "expires": "nov 2022"}'
  got = serialize_container_contents(items)
  assert want == got

def test_simple_item_deserialization():
  raw_items = "some garbage"
  got = deserialize_container_contents(raw_items, None)
  want = [Item("some garbage", None)]
  assert want == got

def test_complex_item_deserialization():
  raw_items = r'some garbage {"count": 3, "expires": "nov 2022"}'
  got = deserialize_container_contents(raw_items, None)
  want = [
    Item("some garbage", None).add_attr("count", 3).add_attr("expires", "nov 2022")
  ]
  assert want == got

def test_multiple_item_deserialization():
  raw_items = r'other garbage w multiple,%&*@ symbols; some garbage {"count": 2, "expires": "nov 2022"}'
  got = deserialize_container_contents(raw_items, None)
  want = [
    Item("other garbage w multiple,%&*@ symbols", None),
    Item("some garbage", None).add_attr("count", 2).add_attr("expires", "nov 2022")
  ]
  assert want == got
