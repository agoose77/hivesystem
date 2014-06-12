"""
Code to test _nodeioarray with Silk
syntax:
silk --schema _nodeioarray.json -I <current directory> -m nodeio --form _nodeioarray_silk form
or
silk --schema _advnodeioarray.json -I <current directory> -m nodeio --form _nodeioarray_silk advform
"""

def form(f):
  f.val.length = 10
  f.val.count_from_one = True
  f.val.form = "soft"
  f.val.arraymanager = "dynamic"
  
def advform(f):
  f.val.length = 10
  f.val.count_from_one = True
  f.val.form = "soft"  
  f.val.arraymanager = "dynamic"