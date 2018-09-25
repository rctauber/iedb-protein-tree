#!/usr/bin/env python3

import csv
import sys

# files to use
parents = "dependencies/parent-proteins.csv"
ttl_out = "build/iedb-proteins.ttl"

# protein database IRI bases
uniprot = "http://www.uniprot.org/uniprot/{0}"
genpept = "https://www.ncbi.nlm.nih.gov/protein/{0}"

# Turtle templates
ttl_header = """@prefix iedb: <http://iedb.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

[ rdf:type owl:Ontology
 ] .

"""

# expects: IRI, parent IRI, accession ID, database name
ttl_template_lite = """
<{0}> rdf:type owl:Class ;
	rdfs:subClassOf <{1}> ;
	iedb:has-accession \"{2}\" ;
	iedb:has-accession-iri <{0}> ;
	iedb:has-source-database \"{3}\" .
"""

# expects: IRI, parent IRI, label, accession ID, database name
ttl_template = """
<{0}> rdf:type owl:Class ;
	rdfs:subClassOf <{1}> ;
	rdfs:label \"{2}\" ;
	iedb:has-accession \"{3}\" ;
	iedb:has-accession-iri <{0}> ;
	iedb:has-source-database \"{4}\" .
"""

# expects: IRI, parent IRI, label, synonym, accession ID, database name
ttl_template_full = """
<{0}> rdf:type owl:Class ;
	rdfs:subClassOf <{1}> ;
	rdfs:label \"{2}\" ;
	iedb:protein-synonym \"{3}\" ;
	iedb:has-accession \"{4}\" ;
	iedb:has-accession-iri <{0}> ;
	iedb:has-source-database \"{5}\" .
"""

def main(args):
	in_file = args[1]
	out_file = args[2]
	lines = []
	with open(in_file, mode='r') as f:
		reader = csv.DictReader(f, delimiter='\t')
		# skip headers
		next(reader)
		# use rows to create ttl
		for row in reader:
			lines.append(parse_row(row))
	# write to file
	with open(out_file, 'w') as f:
		f.write(ttl_header)
		for l in lines:
			f.write(l)

def parse_row(row):
	# create an IRI from Accession and Database cells
	database = row["Database"]
	id_num = row["Accession"]
	iri = format_iri(database, id_num)
	if iri is None:
		return ""
	# build a class
	label = format_label(row["Title"])
	synonym = format_synonym(row["Name"])
	parent = format_parent(row["Proteome Label"])
	if label == "":
		# missing label, check if there is a synonym
		if synonym == "":
			return ttl_template_lite.format(iri, parent, id_num, database)
		else:
			return ttl_template.format(iri, parent, synonym, id_num, database)
	elif synonym == "":
		# only label, no synonym
		return ttl_template.format(iri, parent, label, id_num, database)
	else:
		# all fields present
		return ttl_template_full.format(
			iri, parent, label, synonym, id_num, database)

def format_iri(database, id_num):
	if database == "GenPept":
		return genpept.format(id_num)
	elif database == "UniProt":
		return uniprot.format(id_num)
	else:
		print "Unknown database: {0}".format(database)
		return None

def format_label(title):
	if title == "":
		return ""
	words = title.split(" ")
	label_words = []
	for w in words:
		if '|' in w:
			continue
		if '=' in w:
			break
		label_words.append(w)
	return " ".join(label_words)

def format_parent(proteome):
	if proteome == "":
		return "http://purl.obolibrary.org/obo/PRO_000000001"
	parent_id = proteome.split('-')[0]
	return "http://purl.obolibrary.org/obo/NCBITaxon_{0}".format(parent_id)

def format_synonym(name):
	if name == "":
		return ""
	return name.split('|')[-1]

if __name__ == '__main__':
	main(sys.argv)
