import time
import os
import json
#from collections import defaultdict
from pathlib import Path
from typing import Optional
from random import random, choice
from openai import OpenAI
import requests

api_key = os.environ.get("OPENAI_LITCOIN_KEY")


def write_query(text):
    prompt = f""" 
    This JSON structure contains a UMLS term for a protein, along with its lexical synonyms.  
    It also lists one or more UniProtKB terms for that protein with their label.  
    You must decide whether the UMLS term refers to the same protein as each of the UniProtKB terms.  
    Return your results in only the following JSON format with no extraneous text:
    {{
     "UMLS_id": <input umls id>
    "UniProtKBs": [
      {{ "UniProtKB_id": <uniprotkb_id>, 
        "explanation": <text explaining the match score>,
        "match_score" <0-5, 5 being the best>
    }} ]}}

    {text}
    """
    return prompt
def run_qc(text, out_file_path: Optional[str | Path] = None):
    # Define the Prompt
    prompt = write_query(text)
    results = query(prompt)


def query(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    content = response.json()["choices"][0]["message"]["content"]
    chunk = content[content.index("["):(content.rindex("]")+1)]
    output = json.loads(chunk)
    return output

def go():
    with open("outputs/UMLS_UniProtKB") as f:
        for line in f:
            run_qc(line.strip())
            break

def create_good_batch_line(line,count):
    p = write_query(line)
    d = {"custom_id": f"request-{count}-good", "method": "POST", "url": "/v1/chat/completions",
         "body": {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": p }], "max_tokens": 1000}}
    return json.dumps(d)

def create_bad_batch_line(line1,line2,count):
    newblob = json.loads(line1)
    newblob["UniProtKBs"] = json.loads(line2)["UniProtKBs"]
    p = write_query(json.dumps(newblob))
    d = {"custom_id": f"request-{count}-bad", "method": "POST", "url": "/v1/chat/completions",
         "body": {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": p }], "max_tokens": 1000}}
    return json.dumps(d)

def build_batch_file(n=0, error_rate=0.1):
    count = 0
    with open("outputs/UMLS_UniProtKB_labels.jsonl") as f:
        lines = f.readlines()
    with open("outputs/batch_file.jsonl", "w") as outf:
        for line in lines:
            count += 1
            oline = create_good_batch_line(line,count)
            outf.write(oline+"\n")
            if random() < error_rate:
                count += 1
                line1 = choice(lines)
                line2 = choice(lines)
                oline = create_bad_batch_line(line1, line2, count)
                outf.write(oline + "\n")
            if (n > 0) and (count >= n):
                break

def upload_batch_file():
    client = OpenAI(api_key=api_key)
    batch_input_file = client.files.create(
        file=open("outputs/batch_file.jsonl", "rb"),
        purpose="batch"
    )
    batch_input_file_id = batch_input_file.id

    batch = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": "QC"
        }
    )
    return batch

def retrieve_query(batch):
    client = OpenAI(api_key=api_key)
    batch_id = batch.id
    batch = client.batches.retrieve(batch_id)
    print(json.dumps(batch.to_dict(),indent=4))
    status = batch.status
    while status in ['validating', 'in_progress', 'finalizing']:
        time.sleep(5*60)
        batch_id = batch.id
        batch = client.batches.retrieve(batch_id)
        print(json.dumps(batch.to_dict(), indent=4))
        status = batch.status

    file_response = client.files.content(batch.output_file_id)
    with open("outputs/batch_qc.jsonl","w") as f:
        f.write(file_response.text)

def get_batch():
    client = OpenAI(api_key=api_key)
    batches = client.batches.list(limit=10)
    batch = batches.data[0]
    return batch

def go_batch():
    build_batch_file(0,0.1)
    batch = upload_batch_file()
    #print(batch)
    #batch=get_batch()
    retrieve_query(batch)

if __name__ == "__main__":
    go_batch()
