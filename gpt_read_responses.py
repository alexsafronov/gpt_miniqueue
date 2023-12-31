# PROGRAM: gpt_miniqueue.py
# DATE CREATED: 2023-11-24
# PURPOSE: This module creates queues of GPT API requests, manages them be restarting
# outstanding queues and saves results in the file system.
# AUTHOR: Alexander Safronov
# AUDIENCE: This package is designed for data analysis utilizing GPT API on small and medium-sized datasets by researchers
# as a quick and low cost solution for text analysis.

# The config file and the key must be in the folder above from where the main program is located

import  json, os

sleep_seconds = 0.5
queue_timestamp = ""


def read_responses(gpt_response_folder_path, out_fn) :
	out_fh = open(out_fn, "w")
	json_file_names = [filename for filename in os.listdir(gpt_response_folder_path) if filename.endswith('.json')] # [0:75]
	multiple_study_objects = []
	for counter, json_file_name in enumerate(json_file_names):
		with open(os.path.join(gpt_response_folder_path, json_file_name), encoding="utf-8") as json_file:
			json_obj = json.load(json_file)
			design_element_count = len(json_obj['design_element'])
			response = json_obj['response']
			if json_obj['synonym_count'] == 0 :
				print(str(counter).rjust(4), str(design_element_count).rjust(2), " ".join(str(x).rjust(2) for x in json_obj['design_element']), "    ", json_obj['synonym_count'], " <- Exception: no synonyms were supplied.")
				continue
			elif not isinstance(response, list) :
				print("Exception: the response is not a list type.")
			else :
				response_indicators = [0] * json_obj['synonym_count']
				for response_item in response :
					response_indicators[response_item] = 1
				out_str = str(counter).rjust(4) + " " + str(design_element_count).rjust(2)+ " " + " ".join(str(x).rjust(2) for x in json_obj['design_element']) + \
					"    " + str(json_obj['synonym_count']).rjust(3) + "  " + " ".join(str(x) for x in response_indicators) + "\n"
				# print(out_str)
				out_fh.write(out_str)

read_responses("./20231230_224919_081804", "test.txt")






