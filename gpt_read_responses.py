# PROGRAM: gpt_read_responses.py
# DATE CREATED: 2023-11-24
# PURPOSE: To read GPT responses.
# AUDIENCE:

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
			context_id          = json_obj['context_id']
			original_context_id = json_obj['original_context_id']
			synonym_count = json_obj['synonym_count']
			response = json_obj['response']
			print(f"{counter} synonym_count = {synonym_count} context_id = {context_id} response = {response}", flush=True)
			if synonym_count == 0 :
				print(str(counter).rjust(4), str(design_element_count).rjust(2), " ".join(str(x).rjust(2) for x in json_obj['design_element']), "    ", json_obj['synonym_count'], " <- Exception: no synonyms were supplied.")
				continue
			elif not isinstance(response, list) :
				print("Exception: the response is not a list type.")
			else :
				response_indicators = [0] * synonym_count
				for response_item in response :
					if response_item >= synonym_count :
						print("INVALID RESPONSE") # , end=" ")
						break
					response_indicators[response_item] = 1
				out_str = str(counter).rjust(4) + " " + original_context_id.rjust(9) + " " + str(design_element_count).rjust(2)+ " " + " ".join(str(x).rjust(2) for x in json_obj['design_element']) + \
					"    " + str(json_obj['synonym_count']).rjust(3) + "  " + " ".join(str(x) for x in response_indicators) + "\n"
				# print(out_str)
				out_fh.write(out_str)

read_responses("./20240127_013912_672162", "test.txt")








