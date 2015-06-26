#!/usr/bin/env python
import os, sys
import json

'''
 Parse the the resultant object loaded from json to help find structure
'''
def read_obj( obj ):

	if type( obj ) is list or type( obj ) is dict:
		for item in obj:
			print "--> item: ", item
			if type( item ) is dict:
				print "\t", read_obj( obj[item] )
			else:
				if type( item ) is list:
					print item
#			print "\t", read_obj( obj[item] )
	else:
		return obj


# Accept one parameter being the json file to read
read_json_file = sys.argv[1]

f = open( read_json_file, 'r')
json_contents = f.read()

# loads a json array with one item, so just return the first item
app_obj = json.loads( json_contents )
#print app_obj

read_obj( app_obj )

# Do not overwrite input file, just create a new one with .out extension
write_json_file = read_json_file + ".out"
