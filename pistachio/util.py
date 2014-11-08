# Recursively update a dict
# Merges d2 into d1
# Any conflicts override d1
def merge_dicts(d1, d2):
  for key in d2:
    if key in d1 and isinstance(d1[key], dict) and isinstance(d2[key], dict):
      merge_dicts(d1[key], d2[key])
    else:
      d1[key] = d2[key]
  return d1
