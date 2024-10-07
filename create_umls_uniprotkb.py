from collections import defaultdict
import json, ast

proteins = defaultdict(set)
genes = defaultdict(set)
with open("inputs/UMLS_synonyms") as f:
    for line in f:
        x = line.strip().split('\t')
        synonym = x[2]
        cui = x[0]
        if synonym.endswith("protein, human"):
            text = synonym[:-15]
            proteins[text].add(cui)
        if synonym.endswith("gene"):
            text = synonym[:-5]
            genes[text].add(cui)

#Map UMLS Proteins to UMLS genes
p2g = defaultdict(set)
for text in proteins:
    if text in genes:
        for p in proteins[text]:
            p2g[p].update(genes[text])

allgenes = set()
for x in p2g.values():
    allgenes.update(x)

# Now we want to know which of these genes have an entry in our Genes concordance and get the NCBIGeneID for them
umlsgene_to_ncbigene = {}
with open("inputs/Gene.txt","r") as f:
    for line in f:
        if "UMLS" not in line:
            continue
        clique = json.loads(line)
        canonical_id = clique["identifiers"][0]["i"]
        for ident in clique["identifiers"]:
            iid = ident["i"]
            if iid.startswith("UMLS:"):
                if iid in allgenes:
                    umlsgene_to_ncbigene[iid] = canonical_id

ncbi2uniprot = {}
# Now that we have that, we want to use the GeneProtein concordance to get the relevant UniProt for each NCBIGene
with open("inputs/GeneProtein.txt","r") as f:
    for line in f:
        x = ast.literal_eval(line.strip())
        ncbi2uniprot[x[0]] = x[1:]

#NOW we want to get the UniProt for each UMLS protein
with open("outputs/UMLS_UniProtKB.tsv","w") as f:
    f.write("UMLS_protein\tUMLS_gene\tNCBI_gene\tUniProtKB\n")
    for umlsprotein,umlsgenes in p2g.items():
        for umlsgene in umlsgenes:
            if umlsgene in umlsgene_to_ncbigene:
                ncbigene = umlsgene_to_ncbigene[umlsgene]
                if ncbigene in ncbi2uniprot:
                    for uniprot in ncbi2uniprot[ncbigene]:
                        f.write(f"{umlsprotein}\t{umlsgene}\t{ncbigene}\t{uniprot}\n")
