# PROGRAM: gpt_miniqueue.py
# DATE CREATED: 2023-11-24
# PURPOSE: This module creates queues of GPT API requests, manages them be restarting
# outstanding queues and saves results in the file system.
# AUTHOR: Alexander Safronov
# AUDIENCE: This package is designed for data analysis utilizing GPT API on small and medium-sized datasets by researchers
# as a quick and low cost solution for text analysis.

import openai
import threading, time, sys, json, os
import ast
from datetime import datetime

sleep_seconds = 0.5
queue_timestamp = ""

pregenerated_query_list = None
design_element_list = None
context_id_list = None
original_context_id_list = None
synonym_count_list = None
outfolder_name = None
api_key_file = None

def populate_lists() :
	global design_element_list
	global context_id_list
	global original_context_id_list
	global synonym_count_list
	design_element_list = []
	context_id_list = []
	original_context_id_list = []
	synonym_count_list = []
	for counter, item in enumerate(pregenerated_query_list) :
		design_element_list.append(item['design_element'])
		context_id_list.append(counter)
		original_context_id_list.append(item['context_original_id'])
		synonym_count_list.append(item['synonym_count'])


is_completed = {}
start_time = {}
global prompt_id
global rep_id
global query_fn_static

def res_is_valid(response) :
    try:
        file_data = json.loads(response)
        if len(file_data['non_indications']) > 1 :
            return (False)
    except:
        return (False)
    return (True)

def fetch_raw_API_response_asis(query):
	global api_key_file
	openai.api_key = open(api_key_file, "r").read().strip('\n')
	print()
	query_str = query['pregenerated_query']
	sys.stdout.buffer.write(query_str.encode('utf8'))
	print()
	completion = openai.chat.completions.create(
	model = "gpt-3.5-turbo",
		messages = [{"role": "user", "content": query_str}]
	)
	result = completion.choices[0].message.content
	return result

def dict_to_save(query_idx, queue_timestamp, out_fn, prompt_idx, rep_id, request_st_time, request_en_time, response) :
    duration_s = round((request_en_time-request_st_time).total_seconds(), 1)
    ret = {
         'query_idx' : query_idx
        ,'prompt_idx' : prompt_idx
        ,'request_st_time' : str(request_st_time)[0:19]
        ,'request_en_time' : str(request_en_time)[0:19]
        ,'duration_s' : duration_s
        ,'query_length' : len(pregenerated_query_list[query_idx])
        ,'response'             : response
        ,'design_element'       : design_element_list      [query_idx]
        ,'context_id'           : context_id_list          [query_idx]
        ,'original_context_id'  : original_context_id_list [query_idx]
        ,'synonym_count'        : synonym_count_list       [query_idx]
    }
    #    ,'query'      : pregenerated_query_list[query_idx]
    return(ret)

def response_is_valid_always(response) :
    return (True)
def response_is_valid_never(response) :
    return (False)

response_is_valid_fn = response_is_valid_always

def procure_valid_raw_API_response(query_idx, queue_timestamp, out_fn, prompt_idx, rep_id, response_is_valid_fn = response_is_valid_always) :
    request_st_time = datetime.now()
    query = query_fn_static(query_idx, rep_id)
    raw_response = fetch_raw_API_response_asis(query)
    request_en_time = datetime.now()
    is_valid = response_is_valid_fn(raw_response)
    
    if not is_valid :
        out_fn = "INVALID_" + out_fn
    
    print(f"\n query_idx = {query_idx}  RESPONSE : {raw_response}\n" )
    try :
        response = json.loads(raw_response)
        to_out = dict_to_save(query_idx, queue_timestamp, out_fn, prompt_idx, rep_id, request_st_time, request_en_time, response)
    except :
        to_out = dict_to_save(query_idx, queue_timestamp, out_fn, prompt_idx, rep_id, request_st_time, request_en_time, raw_response)
    
    json.dump(to_out, open(os.path.join(".", queue_timestamp, out_fn), "w"))
    return(is_valid)


def get_extract(query_idx) :
    start_time[query_idx] = datetime.now()
    print(f"st idx: {query_idx}, st time = {str(start_time[query_idx])[0:19]}", flush=True)
    
    timestamp = str(datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    dummy_prompt_id = "0" # ("prompt_id" is a legacy parameter)
    out_fn = "" + timestamp + "_L" + str(query_idx).zfill(6) + "_P" + dummy_prompt_id.zfill(3) + "_R" + str(rep_id).zfill(3) + ".json"
    
    is_completed[query_idx] = procure_valid_raw_API_response(query_idx, queue_timestamp, out_fn, dummy_prompt_id, rep_id,  response_is_valid_fn = response_is_valid_fn)
    
    request_en_time = datetime.now()
    print(f"en idx: {query_idx}, en time = {request_en_time}, out_fn = {out_fn}", flush=True)


def pregenerated_query(query_idx, rep_idx) :
	ret = pregenerated_query_list[query_idx] # ['pregenerated_query']
	# print(f"pregenerated_query_list[...] ============ {ret}")
	return (ret)

def queue_range_pregenerated(l_lim, u_lim, api_key_fn_path="../openai_key.txt", source_pregen_query_path_fn="some_query_seq.json") :
	global pregenerated_query_list
	global api_key_file
	api_key_file = api_key_fn_path
	pregenerated_query_list = json.load(open(source_pregen_query_path_fn, encoding="utf-8")) 
	populate_lists()
	queue_range(l_lim, u_lim, 0, query_fn=pregenerated_query)

def queue_range(l_lim, u_lim, rep, query_fn=pregenerated_query, response_is_valid_fn_arg = response_is_valid_always) :
	l_lim = 0 if l_lim == None else l_lim
	u_lim = len(pregenerated_query_list) if u_lim == None else u_lim
	global response_is_valid_fn
	global rep_id
	global queue_timestamp
	global query_fn_static
	query_fn_static = query_fn
	response_is_valid_fn = response_is_valid_fn_arg
	rep_id = rep
	global is_completed
	global start_time
	is_completed = {}
	start_time = {}
	print('*' * 100)
	print(f"Total list size = {len(pregenerated_query_list)}. Only {u_lim - l_lim} items will be queued with indices {l_lim} to < {u_lim}. ")
	queue_timestamp = str(datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
	global outfolder_name
	outfolder_name = queue_timestamp
	print(f"A new queue started with queue_timestamp = {queue_timestamp}")
	if not os.path.exists(queue_timestamp):
		# Create a new directory because it does not exist
		os.makedirs(queue_timestamp)
	for idx in range(l_lim, u_lim) :
		is_completed[idx] = False
		threading.Thread(target=get_extract, daemon=True, args=(idx, )).start()
		time.sleep(sleep_seconds)
	restart_outstanding()

def is_all_completed(bool_dict) :
    ret = {}
    for idx_key in bool_dict.keys() :
        if not bool_dict[idx_key] :
            return(False)
    return(True)

def elapsed_seconds(time_dict) :
    ret = {}
    for idx_key in time_dict.keys() :
        ret[idx_key] = round((datetime.now() - time_dict[idx_key]).total_seconds(), 1 )
    return(ret)

def print_and_resend_outstanding() :
    elapsed = elapsed_seconds(start_time)
    width_of_column = 8
    for idx_key in is_completed :
        if not is_completed[idx_key] :
            print('-' * width_of_column, end=" ")
    print(flush=True)
    for idx_key in is_completed :
        if not is_completed[idx_key] :
            print(str(idx_key).rjust(width_of_column), end=" ")
    print(flush=True)
    for idx_key in is_completed :
        if not is_completed[idx_key] :
            print(str(elapsed[idx_key]).rjust(width_of_column), end=" ")
    print(flush=True)

def restart_outstanding() :
    # During the following loop too much RAM is used if over 20 queries are queued.
    while not is_all_completed(is_completed):
        elapsed = elapsed_seconds(start_time)
        for idx_key in is_completed.keys() :
            if elapsed[idx_key] > 15 and not is_completed[idx_key] :
                print_and_resend_outstanding()
                print(f"RESTARTING index {idx_key}")
                threading.Thread(target=get_extract, daemon=True, args=(idx_key, )).start()
        time.sleep(5)

# queue_range_pregenerated (None, None) # (0,  240)

'''
def read_responses() :
	json_file_names = [filename for filename in os.listdir(queue_timestamp) if filename.endswith('.json')]
	
	multiple_study_objects = []
	for counter, json_file_name in enumerate(json_file_names):
		with open(os.path.join(queue_timestamp, json_file_name), encoding="utf-8") as json_file:
			json_obj = json.load(json_file)
			response = json_obj['response']
			if isinstance(response, list) : 
				print(response)
				response_indicators = [0] * json_obj['synonym_count']
				print(response_indicators)
				for response_item in response :
					response_indicators[response_item] = 1
			else :
				print("Exception: the response is not a list type.")
			print(*json_obj['design_element'], "    ", json_obj['synonym_count'], *response_indicators)

# read_responses()
'''

