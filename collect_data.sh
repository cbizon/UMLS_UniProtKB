#!/bin/bash
user='your_username'
kubectl cp --context "$user@sterling" -n translator-dev babel:babel_downloads/UMLS/synonyms/ inputs/UMLS_synonyms
kubectl cp --context "$user@sterling" --retries 999 -n translator-dev babel:babel_outputs/compendia/Gene.txt inputs/Gene.txt
kubectl cp --context "$user@sterling" -n translator-dev babel:babel_outputs/conflation/GeneProtein.txt inputs/GeneProtein.txt
# The following are only needed if you are going to run the LLM QC
kubectl cp --context "$user@sterling" -n translator-dev babel:babel_downloads/UniProtKB/labels inputs/UniProtKB_labels
