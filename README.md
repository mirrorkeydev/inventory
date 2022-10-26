<h1 align="center">
  <a href="https://mirrorkey.dev/Sprout/">
    <img width=400 src="https://user-images.githubusercontent.com/35010111/143727250-df1e6c14-696c-45ce-806c-4e579c62e700.jpg" alt="boxes"></a>
  <p>Personal Inventory Management CLI</p>
</h1>

A rudimentary inventory management system, allowing users to easily locate, add, remove, and generally organize personal belongings. Inspired by the many reused shipping boxes I use to hold my posessions, and my love of reorganizing them (and subsequent exasperation when I lose track of where I've put something).

This system is still a work in progress. Ideally, it hopes to fulfill the following user stories:
- I want to instantly find items
- I want to organize/relocate items
- I want to find items with certain attributes. For example, instantly identifying all expired medication and personal care products, so I can dispose of them and free up space.
- I want to be able to check the data from my phone
- I want to be able to send the data to a significant other without requiring them to use my system
- I don't want to spend too much time maintaining the system, but don't mind an initial setup cost

# Architecture

In its current form, the CLI just manipulates data stored in a Google Sheet in a CRUD fashion. Sheets was chosen because it allows:
- fast prototyping
- authentication through Google's OAuth flow 
- mobile access for when I'm not at my computer
- data sharing with anyone I share the sheet with
- easy rollbacks using version history

and because I didn't feel like hosting a real database or creating an account with yet another service. Yes, this means I had to write a bunch of de/serialization code. Also, I thought it might be fun to ~~mis~~use Sheets for something like this.

## Object relationships

There are two principal objects: `Container`s and `Item`s. A `Container` holds 0 or more `Container`s and 0 or more `Item`s. `Item`s cannot hold anything, and may only be related to a single `Container`. `Items` can be associated with arbitrary attributes, describing (for example) repetition or expiration date.

The `Container`s are arranged in a forest of n-ary trees, wherein root-level containers are closets, rooms, cabinets, etc., while leaf-level containers tend to be smaller shipping boxes.

## Design Constraints

- Don't want to have any sort of perpetual middleman server. As a result, new data is fetched for every command, and I can't use something like Elasticsearch to speed up keyword searches.
- Serialization cannot be too convoluted -- I want to keep the Google Sheet readable and editable by a human if necessary. Mass updates (such as initialization) are painful using the CLI anyhow, so keeping the Sheet accessible is important.

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

**Container**|**Parent Container**|**Contents (items)**
:-----:|:-----:|:-----:
HALLWAY CLOSET||
A|HALLWAY CLOSET|watercolor paper
B|HALLWAY CLOSET|watercolors {"count": 2}; checkbook
C|B|TI-84 graphing calculator
...|...|...

Currently there is no support for adding containers with the CLI, so you'll have to bootstrap your containers by hand, editing the Google Sheet (see [TODOs](#TODOs)). This is likely the more comfortable option for such a large operation anyway, and containers are unlikely to change frequently.

Contents cell should be formatted in the following format:
```
item 1; item 2; item 3 {<valid JSON contents>}; item 4
```

Note that the character sequences `; ` and `{}` are both reserved for delimiting items and their attributes, respectively.

If you want to check that you've initialized your inventory correctly, run `inventory --validate` after the last step to find any common errors in the Sheet setup, such as duplicate/missing containers or invalid attribute JSON.

### 2. Create a `secrets.json` in the `auth` directory:
Your sheet ID can be found in its URL: `docs.google.com/spreadsheets/d/<SHEET-ID>/`.
```json
{"SHEET_ID": "sheet-id"}
```

### 3. Set up GCP
Create a [GCP project](https://developers.google.com/workspace/guides/create-project), enabling the Sheets API with the 'https://www.googleapis.com/auth/spreadsheets' scope. [Generate Google Sheet API credentials](https://developers.google.com/workspace/guides/create-credentials), and store the resultant `credentials.json` in the `auth` directory.

### 4. Install dev dependencies
```
# If you don't already have pipenv, then:
# pip install pipenv
pipenv install
```

### 5. (Optional) Enable system-wide usage

```bash
pip3 install -e .
```

The `e` option keeps your installation editable. That is, if you edit any of the source files (e.g. by pulling latest changes), the `inventory` command will automatically use the new code. Feel free to omit the option if this behavior isn't appealing to you.

### 6. (Optional) Run tests
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
Item 'nasa sticker' moved to container C!
```
## Show inventory stats
```bash
$ inventory --stats
Your inventory stats:
  - 12 containers
  - 84 items
```
## Validate inventory setup
```bash
$ inventory --validate
Traceback (most recent call last):
  File "C:\...\Programs\Python\Python39\Scripts\inventory-script.py", line 33, in <module>
    sys.exit(load_entry_point('inventory', 'console_scripts', 'inventory')())
  File "c:\...\inventory\inventory\cli.py", line 33, in main
    containers, items, orphan_items = fetch_data(s)
  File "c:\...\inventory\inventory\service.py", line 57, in fetch_data
  File "c:\...\inventory\inventory\serialization.py", line 33, in deserialize_sheet
    raise Exception(f"duplicate container {container.name} in Sheet rows " +
Exception: duplicate container G in Sheet rows 8 and 9
```
After fixing:
```bash
$ inventory --validate
Looks good!
```

# TODOs
- [x] Refactor to use modules correctly
- [ ] Allow adding/removing containers
- [ ] Allow re-homing of containers
- [x] Decrease count of items when removing
- [x] Manage orphan items better (or not at all?)
- [x] Create convenience "move" operation (remove + add)
- [ ] Enable attributes when adding item
- [ ] Add command to output all recursive container contents
- [ ] Add ability to find expired items
- [ ] Expand validation functionality
