# PROGRAM: gpt_miniqueue.py
# DATE CREATED: 2023-11-24
# PURPOSE: This is an example of using the module gpt_miniqueue.py (see the module description)
# AUTHOR: Alexander Safronov

import threading, time, sys, keyboard, json, os
from datetime import datetime
from gpt_miniqueue import *

fn = "..\\..\\subselected_fda_labels.json"
json_list = json.load(open(fn, encoding="utf-8"))
sleep_seconds = 0.5

if len(sys.argv) < 5 :
    print("Not enough arguments to the command line call.")
    exit()

l_limit   = int(sys.argv[1])
u_limit   = int(sys.argv[2])
prompt_idx =     sys.argv[3]
rep_idx    = int(sys.argv[4])

def never(string) :
    return (False)
def always(string) :
    return (True)

def trivial_query(context_idx, rep_idx) :
    text = """
        Tell me how many words are there in the following drug label ($ ... $),
        but only return one number in the round brackets, without explaining
        hat you were doing. For example, if the drug label is $the drug is being used for cough, perspiration, and running nose$,
        then your response must be '(11)' because there are 11 words in the drug label.
        A series of consequtive white space and punctuation is always treated one delimiter.
        Here is the drug label: $ """ + context_list[context_idx] + " $"
    return (text)

def trivial_query2(context_idx, rep_idx) :
    text = """
        Extract all medical words from the following drug label and list them comma separated.
        Only return that list in the round brackets, without explaining
        what you were doing. For example, if the drug label is $the drug is being used for cough, perspiration, and running nose$,
        then your response must be '(cough, perspiration, and running nose)'.
        Here is the drug label: $ """ + context_list[context_idx] + " $"
    return (text)

# queue_all(l_limit, u_limit, rep_idx, query_fn= .... , response_is_valid_fn_arg = always)
queue_all(l_limit, u_limit, rep_idx, query_fn=trivial_query2, response_is_valid_fn_arg = always)


