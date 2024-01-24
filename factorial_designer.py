# PROGRAM: factorial_designer.py
# AUTHOR: Alexander Safronov
# DATE CREATED: 2024 01-24
# PURPOSE: To generate a list of LLM queries usinf fractional factorial design with prompt components as factors.
# NOTE: This program is a refctored version of the former ../drugdata/gpt_queries.py (a.k.a. pregen_queries.py)

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

import sys, os, json
sys.path.append(r"C:\py\drugdata")
import datasources as ds
import ctinversion as cti

# Prompt components :

components = [None] * 4
components[0] = "Please only return the comma-separated list of the corresponding indices enclosed in square brackets without explaining what you are doing. "
components[1] = "For example: [5, 6, 7, 8]. "
components[2] = "Make sure to only include the indices for medical conditions for which the drug is indicated. "
components[3] = "If a medical condition is not indicated according to the label, then do not include it in the list. "
# components[4] = "I will pay you $10000 if your answers are correct. "
# components[5] = "Keep in mind that punctuation is not always observed in the drug label. "
# components[6] = "Proceed step-by-step. "
# components[7] = "If a term on the list is not a medical condition then do not include it in the list of indicated conditions. "
# components[8] = "Act as a ...."

# Uniform design produces the same set of prompts for each context

uniform_design_pattern = [
	[1, 0, 0, 0],
	[1, 1, 0, 0],
	[1, 0, 1, 0],
	[1, 0, 0, 1],
	[1, 1, 1, 0],
	[1, 1, 0, 1],
	[1, 0, 1, 1],
	[1, 1, 1, 1]
]

def generate_uniform_design(context_count, design_pattern) :
	design_matrix = []
	for context_id in range (0, context_count) :
		for pattern_element in design_pattern :
			design_element = []
			design_element.append(context_id)
			design_element += pattern_element
			design_matrix.append(design_element)
	return(design_matrix)

def one_designer_query(conditions, context, design_element) :
	global components
	numbered_conditions = []
	for idx, condition in enumerate(conditions) :
		numbered_conditions.append( str(idx) + ": " + condition)
	query = "The following is an ordered list of the medical conditions: " + ", ".join(numbered_conditions) + ". " + \
	"Please give me a comma-separated list of the corresponding indices from 0 to " + str(len(numbered_conditions)-1) + \
	", enclosed in square brackets, of the conditions which are indicated according to the drug label I will provide.  If you find no medical conditions that are indications, then return '[]'. "
	print(design_element)
	for counter, design_bit in enumerate(design_element) :
		if counter > 0 and bool( design_bit ) :
			query += components[counter-1]
	query += "\n\nHere is the drug label: " + context + ""

	return(query)

def get_sequence_of_query_objects(slicing_limits=(None, None)) :
	json_file = open("C:/py/out_list.json", "r")
	# json_file = open("../verbatim_synonyms_matched_labels.json", "r")
	# json_file = open(os.path.join(ds.staging_path, "verbatim_synonyms_matched_labels_2023_12_14.json"), "r")
	json_obj = json.load(json_file)
	total_record_count = len(json_obj)
	print(f"There are a total of {total_record_count} records loaded.")
	
	selected_json_objects = json_obj[slicing_limits[0] : slicing_limits[1]]
	design_matrix = generate_uniform_design(len(selected_json_objects), uniform_design_pattern)
	
	ret = []
	print(len(design_matrix))
	for query_id, design_element in enumerate(design_matrix) :
		context_id = design_element[0]
		one_json_object = selected_json_objects[context_id]
		context = one_json_object['indications_and_usage']
		conditions = one_json_object['verbatim_emtree_matches']
		designer_query = one_designer_query(conditions, context, design_element)
		ret.append( {
			'pregenerated_query' : designer_query,
			'design_element' : design_element,
			'context_id' : context_id,
			'synonym_count' : len(conditions),
			'query_id' : query_id
		} )
	return(ret)

# USAGE: 
# 
# To save the generated queries in a file:
# json.dump(get_sequence_of_query_objects(components, variable_indices), open("small_query_seq_3.json", "w"))
# 
# To read a context list, a list of components, indices of variable components, then return a list of queries.
# query_list = get_sequence_of_query_objects(components, variable_indices)



