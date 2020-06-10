#!/usr/bin/env python3

import os
from pybtex.database.input import bibtex

import logger 


class Paper:
    def __init__(this, bibkey, entry):
        this.bibkey = bibkey
        this.authors = this.build_authors(entry)
        print (bibkey)
        print (entry)
        raise 
    def build_authors(this, entry):
        for author in entry.persons['author']:
            print (author)
        raise

def get_name (person):
	name = ''
	first   = person.get_part_as_text('first')
	middle  = person.get_part_as_text('middle')
	last    = person.get_part_as_text('last')
	lineage = person.get_part_as_text('lineage')

	name += first
	if middle:
		if name:
			name += '~' + middle
		else:
			name += middle
	if last:
		if name:
			name += '~' + last
		else:
			name += last
	if lineage:
		name += ',~' + lineage
	return name


class PubsBuilder:
    def __init__(this, ):
        pass

    def parseBibFiles(this, bib_files):

        parser = bibtex.Parser()

        for bibfile in bib_files:

            logger.info('Parsing: ' + str(bibfile))
            bib_data = parser.parse_file(bibfile)
            
            for bibkey,entry in bib_data.entries.items():
                Paper(bibkey, entry) 
                

pb = PubsBuilder()
bib_files = ['conferences.bib', 'journals.bib', 'patents.bib', 'workshops.bib']
bib_files = map(lambda x:  './cv/' + x, bib_files)
bibdata = pb.parseBibFiles(bib_files)
for bibkey,entry in bib_data.entries.items():
    print (bibkey)
       

