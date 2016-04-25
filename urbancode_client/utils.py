import datetime
import time
import json


def write_file( fname, contents):
  with open( fname, 'w') as f:
    f.write( contents )

def write_pretty_json( fname, contents):
  write_file( fname, json.dumps( contents, sort_keys=True, indent=4, separators=(',', ': ')))

'''
 Convert to Unix epoch by removing the ms portion, then convert to GMT before
 printing
'''
def javats_tostr( ts ):
  return ts_tostr( ts/1000 )

def ts_tostr( ts ):
  return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(ts) )
