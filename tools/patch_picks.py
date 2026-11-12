"""Pick overrides that survive a rescan: python tools/patch_picks.py  (applies PATCH to tools/photo-picks.json)."""
import json, os
PATCH = {'v-walk': 6, 'v-feel': 2, 'v-stick': 5, 'v-teach': 8, 'v-end': 8}      # walk: a traveller with a backpack on a road (user's choice); feel: fingers touching the face; stick: a glue stick; teach: a robot teacher at a blackboard; end: asphalt road ending in dirt
f = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'photo-picks.json')
p = json.load(open(f)); p.update(PATCH)
json.dump(p, open(f, 'w'), indent=0, sort_keys=True)
# second look at the words that had no photo before (politicians and broken thumbnails excluded)
PATCH2 = {'n-politics': 1, 'n-senator': 8, 'n-pan': 0, 'n-stick': 5, 'n-neighbor': 5, 'n-outline': 8, 'n-pursuit': 5,
          'n-publisher': 3, 'n-lid': 0, 'n-throat': 0, 'n-tension': 4, 'n-doll': 1, 'n-policy': 2,
          'n-devil': 5, 'n-handle': 4, 'n-insect': 3, 'n-jeans': 4, 'n-habit': 5, 'n-clue': 1, 'n-consideration': 0,
          'n-gentleman': 1, 'n-desk': 4, 'n-margin': 2, 'n-rod': 6}
p.update(PATCH2)
json.dump(p, open(f, 'w'), indent=0, sort_keys=True)
