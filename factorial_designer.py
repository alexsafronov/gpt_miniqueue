# PROGRAM: factorial_designer.py
# AUTHOR: Alexander Safronov
# DATE CREATED: 2024 01-24
# PURPOSE: To generate a list of LLM queries usinf fractional factorial design with prompt components as factors.
# NOTE: This program is a refctored version of the former ../drugdata/gpt_queries.py (a.k.a. pregen_queries.py)
# INSTALLATION OF MODULES: TO be able to use doe_box module, run this: "pip install doe-toolbox"
# INPUT FORMAT:

'''
[
  {
    "label_number": "BLA125387",
    "app_nbr_6d": "125387",
    "brand_name": "EYLEA",
    "indications_and_usage": "1 INDICATIONS AND USAGE EYLEA is indicated for the treatment of: EYLEA is a vascular endothelial growth factor (VEGF) inhibitor indicated for the treatment of patients with: Neovascular (Wet) Age-Related Macular Degeneration (AMD) ( 1.1 ) Macular Edema Following Retinal Vein Occlusion (RVO) ( 1.2 ) Diabetic Macular Edema (DME) ( 1.3 ) Diabetic Retinopathy (DR) ( 1.4 ) Retinopathy of Prematurity (ROP) ( 1.5 ) 1.1 Neovascular (Wet) Age-Related Macular Degeneration (AMD) 1.2 Macular Edema Following Retinal Vein Occlusion (RVO) 1.3 Diabetic Macular Edema (DME) 1.4 Diabetic Retinopathy (DR) 1.5 Retinopathy of Prematurity (ROP)",
    "verbatim_emtree_matches": [
      "retinopathy",
      "diabetic",
      "vein occlusion",
      "retinal vein occlusion",
      "diabetic macular edema",
      "occlusion",
      "degeneration",
      "edema",
      "prematurity",
      "retinopathy of prematurity",
      "diabetic retinopathy",
      "macular edema",
      "macular degeneration"
    ]
  },
  {
    "label_number": "NDA021920",
    "app_nbr_6d": "021920",
    "brand_name": "Naproxen Sodium",
    "indications_and_usage": "Uses temporarily relieves minor aches and pains due to: minor pain of arthritis muscular aches backache menstrual cramps headache toothache the common cold temporarily reduces fever",
    "verbatim_emtree_matches": [
      "backache",
      "cramps",
      "fever",
      "headache",
      "common cold",
      "arthritis",
      "toothache"
    ]
  }
]
'''

import sys, os, json, doe_box
sys.path.append(r"C:\py\drugdata")
# import datasources as ds
# import ctinversion as cti


ascii_code_a = 97
minimum_design_resolution = 3

def get_stat_factor_string(factor_count) :
	terms = "";
	for factor_idx in range(factor_count) :
		ascii_code = factor_idx + ascii_code_a
		terms += (chr(ascii_code) + " ")
	return(terms)

def get_design_pattern(factor_count, design_resolution = minimum_design_resolution) :
	terms = get_stat_factor_string(factor_count)
	generator_string = doe_box.fracfactgen(terms=terms, resolution=design_resolution)
	# print(f"terms = {terms}")
	print(f"factor_count = {factor_count}")
	print(f"design_resolution = {design_resolution}")
	# print(f"generator_string = {generator_string}\n")
	design_matrix = doe_box.fracfact(generator_string)
	return_matrix = []
	for row in design_matrix:
		return_row = []
		for item in row :
			return_row.append(1 if item == 1 else 0)
		return_matrix.append(return_row)
	return( return_matrix )

def print_design_pattern(design_pattern) :
	factor_count = len(design_pattern[0])
	print(str(' ').rjust(4), "     ", end = "")
	for factor_idx in range(factor_count) :
		ascii_code = factor_idx + ascii_code_a
		print(chr(ascii_code).rjust(2) + "  ", end = "")
	print("\n" + "-" * (9 + factor_count * 4) + "\n" )
	
	for counter, row in enumerate(design_pattern):
		print(str(counter).rjust(4), " |   ", end = "")
		for item in row :
			print(str(item).rjust(2) + "  ", end = "")
		print()
'''
factor_count = 5 # int(sys.argv[1])
design_pattern = get_design_pattern(factor_count)
print_design_pattern(design_pattern)
exit()
'''

# Prompt components :
'''
components = [None] * 4
components[0] = "Please only return the comma-separated list of the corresponding indices enclosed in square brackets without explaining what you are doing. "
components[1] = "For example: [5, 6, 7, 8]. "
components[2] = "Make sure to only include the indices for medical conditions for which the drug is indicated. "
components[3] = "If a medical condition is not indicated according to the label, then do not include it in the list. "
'''

'''
components = []
components.append("Please only return the comma-separated list of the corresponding indices enclosed in square brackets without explaining what you are doing. ") 
components.append("For example: [5, 6, 7, 8]. ") 
components.append("Make sure to only include the indices for medical conditions for which the drug is indicated. ") 
components.append("If a medical condition is not indicated according to the label, then do not include it in the list. ") 
'''

'''
components.append(" 1") 
components.append(" 2") 
components.append(" 3") 
components.append(" 4") 
'''

# components[4] = "I will pay you $10000 if your answers are correct. "
# components[5] = "Keep in mind that punctuation is not always observed in the drug label. "
# components[6] = "Proceed step-by-step. "
# components[7] = "If a term on the list is not a medical condition then do not include it in the list of indicated conditions. "
# components[8] = "Act as a ...."

# Uniform design produces the same set of prompts for each context
# It is generated based on the the variable_index_string.
# E.g. "1 . . ." means that the first component is always present, and the remaning three components are variables according to the fractional factorial design
# Step one - generate a uniform_design_pattern based on the  variable_index_string

# 
# 		[1, 0, 0, 0],
# 		[1, 1, 0, 0],
# 		[1, 0, 1, 0],
def uniform_design_pattern(components) :
	factor_count = len(components)
	return(get_design_pattern(factor_count))
	'''
	return([
		[1, 0, 0, 1],
		[1, 1, 1, 0],
		[1, 1, 0, 1],
		[1, 0, 1, 1],
		[1, 1, 1, 1]
	])
	'''
	
'''
print_design_pattern(uniform_design_pattern())
for line in uniform_design_pattern() :
	print(line)
'''

def generate_uniform_design(context_count, design_pattern) :
	design_matrix = []
	for context_id in range (0, context_count) :
		for pattern_element in design_pattern :
			design_element = []
			design_element.append(context_id)
			design_element += pattern_element
			design_matrix.append(design_element)
	return(design_matrix)

def one_designer_query(components, verbatim_matches, context, design_element, persistent_component = "") :
	numbered_matches = []
	for idx, verbatim_match in enumerate(verbatim_matches) :
		numbered_matches.append( str(idx) + ": " + verbatim_match)
	query = ""
	query = "The following is an ordered list of the medical conditions: " + ", ".join(numbered_matches) + ". " \
		+ "Please give me a comma-separated list of the corresponding indices from 0 to " + str(len(numbered_matches)-1) \
		+ ", enclosed in square brackets, of the conditions which are indicated according to the drug label I will provide. " \
		+ " If you find no medical conditions that are indications, then return '[]'. " + persistent_component
	print(design_element)
	for counter, design_bit in enumerate(design_element) :
		if counter > 0 and bool( design_bit ) :
			query += components[counter-1]
	query += "\n\nHere is the drug label: " + context + ""
	return(query)

def get_sequence_of_query_objects(context_input, components, context_index_list = None, context_id_list = None, context_id_name = 'label_number', persistent_component="") : # variable_indices, slicing_limits=(None, None)) :
	if isinstance(context_input, str) :
		json_file = open(context_input, "r")
		json_obj_raw = json.load(json_file)
		# json_file = open("../verbatim_synonyms_matched_labels.json", "r")
		# json_file = open(os.path.join(ds.staging_path, "verbatim_synonyms_matched_labels_2023_12_14.json"), "r")
	elif isinstance(context_input, list):
		json_obj_raw = context_input
	else :
		print()
		type_of_arg = type(context_input)
		exit(f"ERROR: Unexpected context_input type : {type_of_arg}")
	
	if context_index_list :
		selected_json_objects = [json_obj_raw[i] for i in context_index_list]
	elif context_id_list :
		selected_json_objects = [item for item in json_obj_raw if item[context_id_name] in context_id_list]
	else :
		selected_json_objects = json_obj_raw
	
	selected_record_count = len(selected_json_objects)
	print(f"There are a total of {selected_record_count} contexts loaded.")
	
	# selected_json_objects = json_obj[slicing_limits[0] : slicing_limits[1]]
	design_matrix = generate_uniform_design(len(selected_json_objects), uniform_design_pattern(components))
	
	ret = []
	print(f"len(design_matrix) = {len(design_matrix)} ")
	for query_id, design_element in enumerate(design_matrix) :
		context_id = design_element[0]
		one_json_object = selected_json_objects[context_id]
		context = one_json_object['indications_and_usage']
		verbatim_matches = one_json_object['verbatim_emtree_matches']
		designer_query = one_designer_query(components, verbatim_matches, context, design_element, persistent_component=persistent_component)
		ret.append( {
			'pregenerated_query' : designer_query,
			'design_element' : design_element,
			'synonym_count' : len(verbatim_matches),
			'query_id' : query_id,
			'context_id' : context_id,
			'context_original_id' : selected_json_objects[context_id][context_id_name],
			'brand_name' : selected_json_objects[context_id]['brand_name']
		} )
	return(ret)

'''
json_obj = json.load(open(context_input, "r"))
good_indices = range(0, 10) # [0, 1]
good_indices = [0, 1, 3, 5, 11, 16]
json_obj_sel = [json_obj[i] for i in good_indices]
for obj in json_obj_sel :
	print(obj['label_number'], obj['brand_name'])
'''

'''
context_input = "C:/py/out_list.json"
json.dump(get_sequence_of_query_objects(context_input, components, context_id_list = ['NDA021342', 'NDA019034', 'NDA209388']), open("small_query_seq_TEST_3.json", "w"))
'''

'''
# MUST DEFINE COMPONENTS BEFORE USING the function get_sequence_of_query_objects(.....)
components = []
components.append("Please only return the comma-separated list of the corresponding indices enclosed in square brackets without explaining what you are doing. ") 
components.append("For example: [5, 6, 7, 8]. ") 
components.append("Make sure to only include the indices for medical conditions for which the drug is indicated. ") 
components.append("If a medical condition is not indicated according to the label, then do not include it in the list. ") 
'''

# USAGE:
# 
# To save the generated queries in a file:
# json.dump(get_sequence_of_query_objects(components), open("small_query_seq_3.json", "w"))
# 
# To read a context list, a list of components, indices of variable components, then return a list of queries.
# query_list = get_sequence_of_query_objects(components)
# json.dump(get_sequence_of_query_objects(context_input, components, context_id_list = ['NDA021342', 'NDA019034', 'NDA209388']), open("small_query_seq_TEST_3.json", "w"))
# json.dump(get_sequence_of_query_objects(context_input, components, context_index_list = [0, 1]), open("small_query_seq_TEST_3.json", "w"))

