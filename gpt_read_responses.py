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

def read_responses(folder_path) :
	json_file_names = [filename for filename in os.listdir(folder_path) if filename.endswith('.json')]
	multiple_study_objects = []
	for counter, json_file_name in enumerate(json_file_names):
		with open(os.path.join(folder_path, json_file_name), encoding="utf-8") as json_file:
			json_obj = json.load(json_file)
			design_element_count = len(json_obj['design_element'])
			response = json_obj['response']
			if isinstance(response, list) :
				# print(response)
				response_indicators = [0] * json_obj['synonym_count']
				# print(response_indicators)
				for response_item in response :
					response_indicators[response_item] = 1
			else :
				print("Exception: the response is not a list type.")
			print(design_element_count, *json_obj['design_element'], "    ", json_obj['synonym_count'], *response_indicators)

read_responses("./20231230_214056_704798")

