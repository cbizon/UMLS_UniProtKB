# UMLS_UniProtKB
Create a UMLS/UniProtKB table

The problem with UMLS Protein entities is that many of them only link to MeSH, and there's no links to other protein identifiers. So we want to find a way to generically connect UMLS to UniProtKB.

We're going to rely on some work that has been done in Babel, but this particular part doesn't slot into that work very well, because the workflow is a bit circular.  To generate a UMLS/UniProt mapping, we're going to rely on already having a Gene/Protein conflation generated, as well as a Gene and Protein concordance.

We are relying on the fact that for most human gene/protein pairs, there appear to be in UMLS a GeneID that has at least one lexical entry of "<something> gene, human" along with a corresponding protein ID that has at least one lexical entry of "<something> protein".  We use these to join UMLS Proteins to Genes (at least for humans), then use Babel's Gene/Protein conflation to get back to UniProtKB identifiers.

## Generate the UMLS/UniProtKB table

To run this, you need to put the following Babel files into `/inputs`, changing their name to fit the following:

| File | local name         |
|------|--------------------|
| UMLS synonyms            | UMLS\_synonyms     |
| UniProtKB labels  |  UniProtKB\_labels  |
| Gene Protein Conflation |  Gene\_Protein\_Conflation |
| Gene Concordance |  Gene\_Concordance |

If you are running at RENCI and have access to the `translator-dev` namespace on Sterling, you can run `collect_data.sh` to get the files you need.

Create the output mappings:
```
python create_umls_uniprotkb.py
```

This will create `outputs/UMLS_UniProtKB.tsv`, which contains the mappings described above. Note that there can be multiple UniProtKB mappings for a single UMLS Protein.

## QC

We generate mappings for over 13000 UMLS Proteins.  To check the mappings, we use an LLM to inspect the labels of the mapped proteins.

First, convert the tsv to a jsonl and add the UMLS and UniProtKB labels:
```
python add_labels.py
```

Then, run the LLM:
```
export OPENAI_LITCOIN_KEY=<your key>
python run_qc.py
python parse_qc.py
```

This is going to run the QC on the mappings in batch mode using gpt-4o-mini.  In addition to generating a call for each UMLS/UniProtKB pair, it will also generate a specfied fraction of calls by permuting UMLS and UniProtKB identifiers. This allows us to see whether the QC is able to differntiate between (putatively) correct and (known) incorrect mappings.

Now the noteboook `analyze_qc.ipynb` can be used to analyze the results of the QC.  In particular we can look at the distribution of scores for correct and incorrect mappings:

| score | bad  | good |
|-----|----|------|             
|0  |      846 |    22 |
|1  |      375 |    64 |
|2  |       34 |    45 |
|3  |       12 |    25 |
|4  |       17 |   113 |
|5  |       23 | 13478 |

So the vast majority of putatively good mappings gat a score of 5 and the vast majority of known bad mappings get a score of 0 or 1.  Hand inspection of putatively good mappings with low scores appears to be due to the LLM failing rather than the mapping procedure.

