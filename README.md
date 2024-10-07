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

This will create `outputs/UMLS_UniProtKB.tsv`, which contains the mappings described above.


