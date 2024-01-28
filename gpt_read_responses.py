# PROGRAM: gpt_read_responses.py
# DATE CREATED: 2023-11-24
# PURPOSE: To read GPT responses.
# AUDIENCE:

import  json, os

def is_invalid_response(response, synonym_count) :
	if not isinstance(response, list) :
		return("Exception: the response is not a list type.")
	else :
		for response_item in response :
			if response_item >= synonym_count :
				return ("Response index is out of range.")
		return(False)

def read_responses(gpt_response_folder_path, out_fn, fn_prefix_to_skip="INVALID_") :
	out_fh = open(out_fn, "w")
	json_file_names = [filename for filename in os.listdir(gpt_response_folder_path) if filename.endswith('.json')] # [0:75]
	multiple_study_objects = []
	for counter, json_file_name in enumerate(json_file_names):
		if json_file_name.startswith(fn_prefix_to_skip) :
			continue
		else :
			with open(os.path.join(gpt_response_folder_path, json_file_name), encoding="utf-8") as json_file:
				json_obj = json.load(json_file)
				design_element_count = len(json_obj['design_element'])
				context_id          = json_obj['context_id']
				original_context_id = json_obj.get('original_context_id', "")
				synonym_count = json_obj['synonym_count']
				response = json_obj['response']
				print(f"{counter} synonym_count = {synonym_count} context_id = {context_id} response = {response}", flush=True)
				if synonym_count == 0 :
					print(str(counter).rjust(4), str(design_element_count).rjust(2), " ".join(str(x).rjust(2) for x in json_obj['design_element']), "    ", json_obj['synonym_count'], " <- Exception: no synonyms were supplied.")
					continue
				else :
					response_is_invalid = is_invalid_response(response, synonym_count)
					if response_is_invalid :
						print (response_is_invalid)
						continue
					response_indicators = [0] * synonym_count
					for response_item in response :
						response_indicators[response_item] = 1
					out_str = str(counter).rjust(4) + " " + original_context_id.rjust(9) + " " + str(design_element_count).rjust(2)+ " " + " ".join(str(x).rjust(2) for x in json_obj['design_element']) + \
						"    " + str(json_obj['synonym_count']).rjust(3) + "  " + " ".join(str(x) for x in response_indicators) + "\n"
					out_fh.write(out_str)



def read_correct_answers(file_path_name) :
	with open(file_path_name, encoding="utf-8") as plain_file :
		while True:
			content=plain_file.readline()
			arr = content.split()
			if not content:
				break
			original_context_id = arr[0]
			context_id = int(arr[1])
			answer_list_c = arr[2:]
			answer_list_n = []
			for item in answer_list_c :
				answer_list_n.append(int(item))
			print(original_context_id, answer_list_n, end="\n")
		plain_file.close()
	return()


# read_responses("./20240128_011917_350660", "test.txt")
