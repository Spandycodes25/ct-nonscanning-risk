import os
from Bio import Entrez

Entrez.email = "surdas.s@northeastern.edu"
Entrez.api_key = os.environ.get("NCBI_API_KEY")

handle = Entrez.esearch(db="pubmed", term="computed tomography radiation risk", retmax=0)
record = Entrez.read(handle)
handle.close()

print("Total PubMed hits for 'computed tomography radiation risk':", record["Count"])