<h1 align="center">
  Personal Inventory Management CLI
</h1>

A rudimentary inventory management system, allowing users to easily locate, add, remove, and generally organize personal belongings. Inspired by the many reused shipping boxes I use to hold my posessions, and my love of rearranging them (and subsequent exasperation when I lose track of where I've put something).

# Architecture

In its current form, the CLI just manipulates data stored in a Google Sheet in a CRUD fashion. Sheets was chosen because it allows:
- fast prototyping
- authentication through Google's OAuth flow 
- mobile access for when I'm not at my computer
- data sharing with anyone I share the sheet with
- easy rollbacks using version history

and because I didn't feel like hosting a real database or creating an account with yet another service. Yes, this means I had to write a bunch of de/serialization code.

## Object relationships

There are two principle objects: `Container`s and `Item`s. A `Container` holds 0 or more `Container`s and 0 or more `Item`s. `Item`s cannot hold anything, and may only be related to a single `Container`. `Items` can attach arbitrary attributes to them, describing repetition or expiration date.

The `Container`s are arranged in a forest of n-ary trees, wherein root-level containers are closets, rooms, cabinets, etc., while leaf-level containers tend to be smaller shipping boxes.

## Constraints With Current Design

- New data is fetched for every command.
- Keyword search is performed as a linear search over all items with regex. With items in the hundreds, this is fine, but I expect performance will quickly degrade if trying to manage inventory with larger orders of magnitude.

# Setup

Given an example simplified inventory setup:
```bash
Hallway Closet/
├─ A/
├─ B/
│  ├─ C
│  ├─ D
Bedroom Closet/
├─ E/
Under Bed/
├─ Left Drawer/
│  ├─ F
├─ Right Drawer/
│  ├─ G
```

### 1. Create a Google Sheet of the form:

**Container**|**Parent Container**|**Contents (items)**|**Orphan Items**
:-----:|:-----:|:-----:|:-----:
HALLWAY CLOSET|||TBD
A|HALLWAY CLOSET|watercolor paper|
B|HALLWAY CLOSET|watercolors; checkbook| 
C|B|TI-84 graphing calculator| 
...|...|...|

Currently there is no support for adding containers with the CLI, so you'll have to bootstrap your containers by hand, editing the Google Sheet. See [TODOs](#TODOs).

### 2. Create a `secrets.json` in the `auth` directory:
```json
{"SHEET_ID": "your-sheet-id"} // From: docs.google.com/spreadsheets/d/<SHEET-ID>/
```

### 3. [Generate Google Sheet API credentials](https://developers.google.com/workspace/guides/create-credentials)
Store the resultant `credentials.json` in the `auth` directory.

### 4. Install dev dependencies
```
pipenv install
```

### 5. (Optional) Enable system-wide usage

```bash
pip3 install -e .
```

### 6. Run tests
```
pytest
```

# Usage

## Find item
```bash
$ inventory --find watercolor
searching 12 containers and 83 items...3 match(es)
  -'watercolor paper' in HALLWAY CLOSET -> A
  -'watercolors' in HALLWAY CLOSET -> B -> D
  -'homemade clay watercolor pan' in UNDER BED -> LEFT DRAWER -> F
```
## Add item
```bash
$ inventory --add "pride flag" F
Item 'pride flag' added to container F!
```
## Remove item
```bash
$ inventory --remove "calculator"
searching 12 containers and 84 items...3 match(es)
0: 'TI-84 graphing calculator' in HALLWAY CLOSET -> B -> C
1: 'pocket calculator' in UNDER BED -> RIGHT DRAWER -> G
2: 'casio scientific calculator' in UNDER BED -> RIGHT DRAWER -> G
Which item would you like to remove? (Enter 0-2): 1
Item 'pocket calculator' removed!
```
## Decrement item
```bash
$ inventory --remove "mason"
searching 12 containers and 84 items...1 match(es)
0: 'mason jars' {'count': 15} in UNDER BED -> RIGHT DRAWER -> G
Which item would you like to remove? (Enter 0-0): 0
Would you like to decrement this item or remove it completely? (Enter d# or r): d5
Item 'mason jars' decremented by 5!
```
## Move item
```bash
$ inventory --move "sticker" C
searching 12 containers and 84 items...2 match(es)
0: 'plant sticker' in HALLWAY CLOSET -> B -> C
1: 'nasa sticker' in UNDER BED -> RIGHT DRAWER -> G
Which item would you like to move? (Enter 0-1): 1
Item 'nasa sticker' moved to container 'C'!
```
# TODOs
- [x] Refactor to use modules correctly
- [ ] Allow adding/removing containers
- [ ] Allow re-homing of containers
- [x] Decrease count of items when removing
- [ ] Manage orphan items better (or not at all?)
- [x] Create convenience "move" operation (remove + add)
- [ ] Add command to output all recursive container contents
- [ ] Add ability to find expired items
