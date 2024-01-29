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
		

def false_negative_verbatims(response, correct_answers, verbatim_matches) :
	false_verbatims = []
	for idx in correct_answers :
		if idx not in response :
			false_verbatims.append(verbatim_matches[idx])
	return(false_verbatims)

def false_positive_verbatims(response, correct_answers, verbatim_matches) :
	false_verbatims = []
	for idx in response :
		if idx not in correct_answers :
			# print(type(idx), "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
			false_verbatims.append(verbatim_matches[idx])
	return(false_verbatims)
	
def enumerated_list_string(list) :
	enumerated_list = []
	for counter, item in enumerate(list) :
		enumerated_list.append(str(counter) + ": " + item)
	return( ",   ".join(enumerated_list) + ".")

def valid_filenames_sorted_by_query_id(gpt_response_folder_path, fn_prefix_to_skip="INVALID_") :
	valid_file_names = [filename for filename in os.listdir(gpt_response_folder_path) if filename.endswith('.json') and not filename.startswith(fn_prefix_to_skip)]
	# Assuming the file name is formatted as "20240129_011233_722566_L000211.json" - sorting by "L000211" (query ID)
	sorted_file_names = sorted(valid_file_names, key=lambda x: x[24:32])
	return(sorted_file_names)
	# for item in sorted_file_names :
	#	print(f"{item} ={item[24:30]}=")

def read_responses_by_context(gpt_response_folder_path, fn_prefix_to_skip="INVALID_", correct_answers_file_path_name=None, verbatim_matches_file_path_name=None, query_list_filename=None) :
	json_file_names = valid_filenames_sorted_by_query_id(gpt_response_folder_path, fn_prefix_to_skip=fn_prefix_to_skip)
	
	dict_of_response_lists = {}
	
	correct_answers  = {}
	verbatim_matches = {}
	contexts         = {}
	tot_false_negative_verbatim_count = 0
	tot_false_positive_verbatim_count = 0
	tot_query_count = 0
	
	if correct_answers_file_path_name :
		correct_answers  = read_correct_answers(correct_answers_file_path_name)
		
	if query_list_filename :
		query_list       = read_query_list(query_list_filename)
		
	if verbatim_matches_file_path_name :
		verbatim_matches = read_verbatim_matches(verbatim_matches_file_path_name)
		contexts         = read_contexts        (verbatim_matches_file_path_name)
		
	context_counter = 0
	
	for counter, json_file_name in enumerate(json_file_names):
		if json_file_name.startswith(fn_prefix_to_skip) :
			continue
		else :
			with open(os.path.join(gpt_response_folder_path, json_file_name), encoding="utf-8") as json_file:
				json_obj = json.load(json_file)
				original_context_id = json_obj.get('original_context_id', "")
				if not original_context_id in dict_of_response_lists :
					dict_of_response_lists[original_context_id] = {
						'context' : contexts[original_context_id],
						'verbatim_matches' : verbatim_matches[original_context_id],
						'correct_answers' : correct_answers[original_context_id],
						'api_responses' : []
					}
					print("\n\n")
					print("(", str(context_counter).rjust(4), ")", original_context_id, "\n")
					context_counter += 1
					print(contexts[original_context_id], "\n")
					# print(verbatim_matches[original_context_id], "\n")
					print(enumerated_list_string(verbatim_matches[original_context_id]), "\n")
					print("\n                     Prompt Design       Classification of the verbatim terms")
					print(  "                     -------------       ---------------------------------")
				
				design_element_count = len(json_obj['design_element'])
				synonym_count = json_obj['synonym_count']
				query_idx = json_obj['query_idx']
				
				if synonym_count == 0 :
					print(str(counter).rjust(4), str(design_element_count).rjust(2), " ".join(str(x).rjust(2) for x in json_obj['design_element']), "    ", json_obj['synonym_count'], " <- Exception: no synonyms were supplied.")
					continue
				else :
					response_is_invalid = is_invalid_response(json_obj['response'], synonym_count)
					if response_is_invalid :
						print (response_is_invalid)
						continue
					# print(query_idx, " ===============================================================================================================================================")
					json_obj['false_negative_verbatims'] = false_negative_verbatims(json_obj['response'], correct_answers[original_context_id], verbatim_matches[original_context_id])
					json_obj['false_positive_verbatims'] = false_positive_verbatims(json_obj['response'], correct_answers[original_context_id], verbatim_matches[original_context_id])
					tot_false_negative_verbatim_count += len(json_obj['false_negative_verbatims'])
					tot_false_positive_verbatim_count += len(json_obj['false_positive_verbatims'])
					tot_query_count += 1
					
					dict_of_response_lists[original_context_id]['api_responses'].append(json_obj)
					response_indicators = [0] * synonym_count
					for response_item in json_obj['response'] :
						response_indicators[response_item] = 1
					# print(f"query_idx = {query_idx}, query = \n{query_list[query_idx] }\n\n")
					out_str = str(counter).rjust(4) + " " + original_context_id.rjust(9) + " " + str(design_element_count).rjust(2)+ " " + " ".join(str(x).rjust(2) for x in json_obj['design_element']) + \
						"    " + str(json_obj['synonym_count']).rjust(3) + "  " + " ".join(str(x) for x in response_indicators) + \
						"    FALSE_NEG : "  + ", ".join(json_obj['false_negative_verbatims']) + ". " + str(tot_false_negative_verbatim_count) + \
						"    FALSE_POS : "  + ", ".join(json_obj['false_positive_verbatims']) + ". " + str(tot_false_positive_verbatim_count)
					print(out_str)
	return(dict_of_response_lists)

def statistics(dict_of_response_lists) :
	tot_false_negative_verbatim_count = 0
	tot_false_positive_verbatim_count = 0
	tot_query_count = 0
	for key in dict_of_response_lists :
		for response in dict_of_response_lists[key]['api_responses'] :
			tot_false_negative_verbatim_count += len(response['false_negative_verbatims'])
			tot_false_positive_verbatim_count += len(response['false_positive_verbatims'])
			tot_query_count += 1
	print(f"tot_false_negative_verbatim_count = {tot_false_negative_verbatim_count}")
	print(f"tot_false_positive_verbatim_count = {tot_false_positive_verbatim_count}")
	print(f"tot_query_count = {tot_query_count}")

def read_responses(gpt_response_folder_path, out_fn, fn_prefix_to_skip="INVALID_", correct_answers_file_path_name=None, verbatim_matches_file_path_name=None) :
	out_fh = open(out_fn, "w")
	json_file_names = [filename for filename in os.listdir(gpt_response_folder_path) if filename.endswith('.json')] # [0:75]
	correct_answers  = {}
	verbatim_matches = {}
	
	if correct_answers_file_path_name :
		correct_answers  = read_correct_answers(correct_answers_file_path_name)
		
	if verbatim_matches_file_path_name :
		verbatim_matches = read_verbatim_matches(verbatim_matches_file_path_name)
		contexts         = read_contexts        (verbatim_matches_file_path_name)
		
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
				correct_answer      = correct_answers.get(original_context_id)
				verbatim_match_list = verbatim_matches.get(original_context_id)
				context             = contexts.get(        original_context_id)
				print(f"{str(counter).rjust(5)} {original_context_id} syn_cnt = {synonym_count} context_id = {context_id} response = {response} correct_ans = {correct_answer} verbat_matches = {verbatim_match_list}", flush=True)
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
	correct_answers = {}
	with open(file_path_name, encoding="utf-8") as plain_file :
		counter = 0
		while True:
			content = plain_file.readline()
			arr = content.split()
			if not content:
				break
			original_context_id = arr[0]
			context_id = int(arr[1])
			answer_list_c = arr[2:]
			answer_list_n = []
			for item in answer_list_c :
				answer_list_n.append(int(item))
			print(str(counter).rjust(3), original_context_id, answer_list_n, end="\n")
			correct_answers[original_context_id] = answer_list_n
			counter += 1;
		plain_file.close()
	return(correct_answers)


def read_verbatim_matches(file_path_name, verbatim_match_field_name = 'verbatim_emtree_matches', original_context_id_name = 'label_number') :
	verbatims = {}
	with open(file_path_name, encoding="utf-8") as json_file :
		dict_obj = json.load(json_file)
		# print(dict_obj)
		for marked_item in dict_obj :
			# print(marked_item[verbatim_match_field_name])
			verbatims[marked_item[original_context_id_name]] = marked_item[verbatim_match_field_name]
	return(verbatims)

def read_contexts(file_path_name, context_field_name = 'indications_and_usage', original_context_id_name = 'label_number') :
	contexts = {}
	with open(file_path_name, encoding="utf-8") as json_file :
		dict_obj = json.load(json_file)
		# print(dict_obj)
		for marked_item in dict_obj :
			# print(marked_item[context_field_name])
			contexts[marked_item[original_context_id_name]] = marked_item[context_field_name]
	return(contexts)
	
def read_query_list(query_list_filename, query_field_name = 'pregenerated_query', query_id_name = 'query_id') :
	queries = {}
	with open(query_list_filename, encoding="utf-8") as json_file :
		dict_obj = json.load(json_file)
		# print(dict_obj)
		for marked_item in dict_obj :
			# print(marked_item[context_field_name])
			queries[marked_item[query_id_name]] = marked_item[query_field_name]
	return(queries)


