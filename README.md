# gpt_miniqueue
The gpt_miniqueue Python module creates and manages small queues of API requests for LLM analysis in a time-efficient automated way. It is designed as a tool enabling a data analyst or a researcher in prompt engineering so to save time and credits while using third-party API for LLM data analysis.

Using the kit:
---------------------------------------------------------------------------------------------------------------------
import sys, json
sys.path.append(r".\gpt_miniqueue")
import factorial_designer as fd
import gpt_miniqueue as mq
import gpt_read_responses as rr


query_list_filename = "./small_query_seq_test.json"
context_input = "./a_prematched_list_of_druglabels.json"

query_structure = "The following is an ordered list of medical conditions: {numbered_comma_separated_matches}. " \
	+ "Please give me a comma-separated list of the indices from 0 to {match_count} for the medical conditions from the drug label, enclosed in square brackets. " \
	+ "Do not explain what you are doing. " \
	+ " {masked_component_sequence}. If you find no medical conditions that are indications, then return '[]'. \n\nHere is the drug label: {context}. "

components = []
components.append("Only include conditions that match the drug label. ")
components.append("Only include the indications. Do not include conditions that are not indicated according to the drug label .")
components.append("Be extra careful. ")
components.append("Act as my physician. ")

def show_stat(manual_grade_filename, gpt_response_folder_path) :
	responses = rr.read_responses_by_context(gpt_response_folder_path, correct_answers_file_path_name=manual_grade_filename, verbatim_matches_file_path_name=context_input, query_list_filename=query_list_filename, verbose = True)
	rr.display_4_way_anova(responses)

json.dump(fd.get_sequence_of_query_objects(context_input, components, context_id_list = ['NDA021342', 'NDA019034', 'NDA209388'], persistent_component=query_structure ), open(query_list_filename, "w"))
gpt_response_folder_path = mq.queue_range_pregenerated (None, None, api_key_fn_path="./openai_key.txt", source_pregen_query_path_fn=query_list_filename, base_output_folder=".")
show_stat("./gpt_miniqueue/manualy_graded/manual_grades_with_ids.txt", gpt_response_folder_path)
---------------------------------------------------------------------------------------------------------------------
