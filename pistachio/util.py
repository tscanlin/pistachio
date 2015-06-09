def merge_dicts(d1, d2):
  """
  Recursively update a dict
  Merges d2 into d1
  Any conflicts override d1
  """
  for key in d2:
    if key in d1 and isinstance(d1[key], dict) and isinstance(d2[key], dict):
      merge_dicts(d1[key], d2[key])
    else:
      d1[key] = d2[key]
  return d1

def truthy(string_or_bool):
  """ Takes a string or bool as an argument, and returns a bool """
  if string_or_bool == True:
    return True
  elif string_or_bool == False:
    return False
  else:
    return str(string_or_bool).lower() in ['true']
