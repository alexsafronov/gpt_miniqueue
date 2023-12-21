# PROGRAM: gpt_miniqueue.py
# DATE CREATED: 2023-11-24
# PURPOSE: This module creates queues of GPT API requests, manages them be restarting
# outstanding queues and saves results in the file system.
# AUTHOR: Alexander Safronov
# AUDIENCE: This package is designed for data analysis utilizing GPT API on small and medium-sized datasets by researchers
# as a quick and low cost solution for text analysis.

# The config file and the key must be in the folder above from where the main program is located

import openai
from openai.error import OpenAIError, RateLimitError
import threading, time, sys, keyboard, json, os
import ast
from datetime import datetime

sleep_seconds = 0.5
queue_timestamp = ""

config_fn = None
context_list = None
pregenerated_query_list = None

def config(fn) :
    global config_fn
    config_fn = fn
    config_data = json.load(open(config_fn, encoding="utf-8"))
    global context_list
    context_list = get_context_list(source_path_fn())
    global pregenerated_query_list
    pregenerated_query_list = get_pregenerated_query_list(source_pregen_query_path_fn())

def config_data() :
    return ( json.load(open(config_fn, encoding="utf-8")) )

def source_path_fn() :
    config_data = json.load(open(config_fn, encoding="utf-8"))
    return(config_data.get('source_path_fn'))

def source_pregen_query_path_fn() :
    config_data = json.load(open(config_fn, encoding="utf-8"))
    # print(config_data, flush=True)
    return(config_data.get('source_pregen_query_path_fn'))

def get_context_list(json_filename) :
    ret = []
    with open(os.path.join(".", json_filename), encoding="utf-8") as json_file:
        for one_json_obj in json.load(json_file) :
            label = one_json_obj
            try:
                ret.append(label.get('indications_and_usage', [])[0:16000])
            except IndexError:
                ret.append('')
    l = len(ret)
    return(ret)

def get_pregenerated_query_list(json_filename) :
    ret = []
    print(f"json_filename = {json_filename}\n", flush=True)
    with open(os.path.join(".", json_filename), encoding="utf-8") as json_file:
        for one_json_obj in json.load(json_file) :
            label = one_json_obj # .encode('utf-8')
            # print(label, flush=True)
            try:
                ret.append(label.get('pregenerated_query', [])[0:16000])
            except IndexError:
                ret.append('')
    l = len(ret)
    return(ret)

def load_context_data() :
    pass


is_completed = {}
start_time = {}
global prompt_id
global rep_id
global query_fn_static

def TA_query(context_idx, rep_idx) :
    text = """
        Please return a short description of a therapuetic area for which the drug is indicated
        enclosed in square brackets. For example "[cardiovascular]" or "[pulmonary]" or "[oncology]".
        The drug label you will find below inside the pair of the dollar sighs ($ ... $).
        Only return the description of a therapuetic area within square brackets, without explaining
        what you are doing. For example, if the drug label is $the drug is being used for cough, perspiration, and running nose$,
        then your response must be "[respiratory diseases]". Here is the drug label: $
    """ + context_list[context_idx] + "$"
    # print(f"from trivial_query =================={context_idx}=================================")
    return (text)

def res_is_valid(response) :
    try:
        # print(f"TRYING : \n {response} \n",)
        file_data = json.loads(response)
        # print("file_data : ", file_data)
        # print("NONINDIC : ", file_data['non_indications'])
        if len(file_data['non_indications']) > 1 :
            return (False)
    except:
        return (False)
    return (True)

def fetch_raw_API_response_asis(query):
    openai.api_key = open("../openai_key.txt", "r").read().strip('\n')
    print(f"\n{query}\n")
    completion = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [{"role": "user", "content": query}]
    )
    result = completion.choices[0].message.content
    # result_json = json.loads(result)
    return result

def dict_to_save(context_idx, context, queue_timestamp, out_fn, prompt_idx, rep_id, request_st_time, request_en_time, response) :
    duration_s = round((request_en_time-request_st_time).total_seconds(), 1)
    ret = {
         'context_idx' : context_idx
        ,'prompt_idx' : prompt_idx
        ,'request_st_time' : str(request_st_time)[0:19]
        ,'request_en_time' : str(request_en_time)[0:19]
        ,'duration_s' : duration_s
        ,'context_length' : len(context)
        ,'response' : response
    }
    return(ret)

def response_is_valid_always(response) :
    return (True)
def response_is_valid_never(response) :
    return (False)

response_is_valid_fn = response_is_valid_always

def procure_valid_raw_API_response(context_idx, context, queue_timestamp, out_fn, prompt_idx, rep_id, response_is_valid_fn = response_is_valid_always) :
    request_st_time = datetime.now()
    query = query_fn_static(context_idx, rep_id)
    raw_response = fetch_raw_API_response_asis(query)
    request_en_time = datetime.now()
    is_valid = response_is_valid_fn(raw_response)
    
    if not is_valid :
        out_fn = "INVALID_" + out_fn
    
    print(f"\n context_idx = {context_idx}  RESPONSE : {raw_response}\n" )
    try :
        response = json.loads(raw_response)
        to_out = dict_to_save(context_idx, context, queue_timestamp, out_fn, prompt_idx, rep_id, request_st_time, request_en_time, response)
    except :
        to_out = dict_to_save(context_idx, context, queue_timestamp, out_fn, prompt_idx, rep_id, request_st_time, request_en_time, raw_response)
    
    json.dump(to_out, open(os.path.join(".", queue_timestamp, out_fn), "w"))
    return(is_valid)


def get_extract(context_idx) :
    start_time[context_idx] = datetime.now()
    print(f"st idx: {context_idx}, st time = {str(start_time[context_idx])[0:19]}", flush=True)
    
    timestamp = str(datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    dummy_prompt_id = "0" # ("prompt_id" is a legacy parameter)
    out_fn = "" + timestamp + "_L" + str(context_idx).zfill(6) + "_P" + dummy_prompt_id.zfill(3) + "_R" + str(rep_id).zfill(3) + ".json"
    
    is_completed[context_idx] = procure_valid_raw_API_response(context_idx, context_list[context_idx], queue_timestamp, out_fn, dummy_prompt_id, rep_id,  response_is_valid_fn = response_is_valid_fn)
    
    request_en_time = datetime.now()
    print(f"en idx: {context_idx}, en time = {request_en_time}, out_fn = {out_fn}", flush=True)


def pregenerated_query(context_idx, rep_idx) :
    return (pregenerated_query_list[context_idx])

def queue_range_pregenerated(l_lim, u_lim) :
    queue_range(l_lim, u_lim, 0, query_fn=pregenerated_query)

# def queue_all(l_lim, u_lim, rep, query_fn=trivial_query, response_is_valid_fn_arg = response_is_valid_always) :
def queue_range(l_lim, u_lim, rep, query_fn=TA_query, response_is_valid_fn_arg = response_is_valid_always) :
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
    print(f"Total list size = {len(context_list)}. Only {u_lim - l_lim} items will be queued with indices {l_lim} to < {u_lim}. ")
    queue_timestamp = str(datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
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

config("../ddconfig.json")
queue_range_pregenerated( 100,  102)
