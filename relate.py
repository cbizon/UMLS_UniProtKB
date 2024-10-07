from collections import defaultdict

def read_ids(filename):
    ids = set()
    with open(filename, "r") as f:
        for line in f:
            ids.add(line.split('\t')[0].split(':')[1])
    return ids

def read_UMLS_protein_ids():
    return read_ids("inputs/UMLS_protein_ids")

def read_UMLS_gene_ids():
    return read_ids("inputs/UMLS_gene_ids")

def build_UMLS_protein_to_gene(UMLS_proteins, UMLS_genes):
    #MRREL.RRF contains relations for everything in UMLS :O
    #We only want the relations between proteins and genes but we gotta look through all of em
    # The subject is in field 4 and the object is in field 0 and the predicate is in field 3
    p2g = defaultdict(set)
    g2p = defaultdict(set)
    with open("inputs/MRREL.RRF","r") as inf:
        for line in inf:
            fields = line.split('|')
            if fields[4] in UMLS_proteins and fields[0] in UMLS_genes and fields[3] == "RO":
                p2g[fields[4]].add(fields[0])
                g2p[fields[0]].add(fields[4])
    return p2g, g2p

def go():
    UMLS_proteins = read_UMLS_protein_ids()
    UMLS_genes = read_UMLS_gene_ids()
    UMLS_protein_to_gene, UMLS_gene_to_protein = build_UMLS_protein_to_gene(UMLS_proteins, UMLS_genes)
    print("Number of proteins: ", len(UMLS_proteins))
    print("Number of proteins with gene relations: ", len(UMLS_protein_to_gene))
    print("Number of proteins linked to more than one gene: ", len([k for k in UMLS_protein_to_gene if len(UMLS_protein_to_gene[k]) > 1]))
    with open("outputs/UMLS_no_genes","w") as f:
        for protein in UMLS_proteins:
            if protein not in UMLS_protein_to_gene:
                f.write(protein + "\n")
    with open("outputs/UMLS_protein_to_gene","w") as f:
        for protein in UMLS_protein_to_gene:
            f.write(protein + "\t" + ",".join(UMLS_protein_to_gene[protein]) + "\n")

if __name__ == "__main__":
    go()