import json

def go():
    prompt_tokens = 0
    completion_tokens = 0
    with open("outputs/batch_qc.jsonl","r") as inf, open("outputs/batch_qc.tsv","w") as outf:
        for line in inf:
            result = json.loads(line)
            input_score = result["custom_id"].split("-")[-1]
            try:
                response = json.loads(result["response"]["body"]["choices"][0]["message"]["content"])
            except:
                print("badline",line)
                continue
            for up in response["UniProtKBs"]:
                row = (f"{response['UMLS_id']}\t{up['UniProtKB_id']}\t{up['match_score']}\t{input_score}\n")
                outf.write(row)
            usage = result["response"]["body"]["usage"]
            prompt_tokens += usage["prompt_tokens"]
            completion_tokens += usage["completion_tokens"]
            print(prompt_tokens,completion_tokens )
    # The cost of this model is $0.075 / 1M input tokens and $0.300 / 1M output tokens
    print(f"Cost: ${0.075 * prompt_tokens / 1e6 + 0.3 * completion_tokens / 1e6}")

if __name__ == "__main__":
    go()