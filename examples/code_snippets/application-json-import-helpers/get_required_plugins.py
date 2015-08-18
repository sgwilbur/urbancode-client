#!/usr/bin/env python
import os, sys
import json



def find_plugins_used( app_components ):
	plugins_used = {}

	for cur_component in app_components:
	#	print cur_component['name']

		cur_comp_processes = cur_component['processes']

		for cur_comp_process in cur_comp_processes:
	#		print "\t", cur_comp_process['name']

			if 'rootActivity' in cur_comp_process:
				children = cur_comp_process['rootActivity']['children']

				for cur_child in children:
					if 'pluginName' in cur_child:
						plugin_name = cur_child[ 'pluginName' ]
						plugin_version = cur_child[ 'pluginVersion']
	#					print "\t\t", plugin_name, ": ", plugin_version

						if plugin_name in plugins_used:

							if not plugin_version in plugins_used[ plugin_name ]:
								plugins_used[ plugin_name ].append( plugin_version )
								plugins_used[ plugin_name ] = sorted( plugins_used[ plugin_name ] )
						else:
							plugins_used[ plugin_name ] = [ plugin_version ]

	return plugins_used



#app_processes =  app_obj['processes']

#for process in app_processes:
#	print process['name']

export_json_file = sys.argv[1]

f = open( export_json_file, 'r')
json_contents = f.read()


# loads a json array with one item, so just return the first item
app_obj = json.loads( json_contents )

app_components =  app_obj['components']

print find_plugins_used( app_components )

# for comp in app_components:
# 	if 'name' in comp:
# 		print comp['name']
# 		continue
# 		for process in comp['processes']:
# 			print "\t\t", process['name']
