from collections import defaultdict
import json

print("Load UMLS Synonyms")
umls_synonyms = defaultdict(list)
with open("inputs/UMLS_synonyms","r") as inf:
    for line in inf:
        x = line.strip().split('\t')
        umls_synonyms[x[0]].append(x[2])


print("Load UniProtKB labels")
uniprot_labels = {}
with open("inputs/UniProtKB_labels","r") as inf:
    for line in inf:
        x = line.strip().split('\t')
        uniprot_labels[x[0]] = x[1]

print("Write UMLS_UniProtKB_labels")
with open("outputs/UMLS_UniProtKB.tsv","r") as inf, open("outputs/UMLS_UniProtKB_labels.jsonl","w") as outf:
    header = inf.readline()
    current_document = {"UMLS_id": None, "UMLS_Synonyms":[],  "UniProtKBs": []}
    for line in inf:
        x = line.strip().split('\t')
        umls_id = x[0]
        uniprot_id = x[3]
        uniprot_label = uniprot_labels[uniprot_id]
        if current_document["UMLS_id"] != umls_id:
            if current_document["UMLS_id"] is not None:
                outf.write(json.dumps(current_document) + "\n")
            current_document = {"UMLS_id": umls_id, "UMLS_Synonyms": umls_synonyms[umls_id], "UniProtKBs": [{"id": uniprot_id, "label": uniprot_label}]}
        else:
            current_document["UniProtKBs"].append({"UniProtKB": uniprot_id, "label": uniprot_label})
    outf.write(json.dumps(current_document) + "\n")