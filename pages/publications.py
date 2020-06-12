#!/usr/bin/env python3

from __future__ import unicode_literals

import jinja2 as jinja
import logging
import os
from pybtex.database.input import bibtex
from pybtex.style.formatting.__init__ import * 
from pybtex.style.template import * 
from pybtex.style.formatting.unsrt import * 
from pybtex.backends.html import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Adapted from pybtex.style.formatting.unrst.py
class MyStyle (Style):
    
    # override default formatting to 
    # customize for our uses 

    def get_inproceedings_template(self, e):
        template = toplevel [
            self.format_title(e, 'title'),
            words [ 'By', sentence [self.format_names('author')],],
            words [
                'In',
                sentence [
                    optional[ self.format_editor(e, as_sentence=False) ],
                    self.format_btitle(e, 'booktitle', as_sentence=False),
                    self.format_volume_and_series(e, as_sentence=False),
                    optional[ pages ],
                ],
                self.format_address_organization_publisher_date(e),
            ],
            sentence [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template

    def get_article_template(self, e):
        volume_and_pages = first_of [
            # volume and pages, with optional issue number
            optional [
                join [
                    field('volume'),
                    optional['(', field('number'),')'],
                    ':', pages
                ],
            ],
            # pages only
            words ['pages', pages],
        ]
        template = toplevel [
            self.format_title(e, 'title'),
            words ['By', self.format_names('author'),],
            sentence [
                tag('em') [field('journal')],
                optional[ volume_and_pages ],
                date],
            sentence [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template

    def get_misc_template(self, e):
        template = toplevel [
            optional[ self.format_title(e, 'title') ],
            optional[ words ['By', sentence [self.format_names('author')] ]],
            sentence[
                optional[ field('howpublished') ],
                optional[ date ],
            ],
            sentence [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template

class MyBackend (Backend):
    symbols = {
        'ndash': u'&ndash;',
        'newblock': u'\n',
        'nbsp': u'&nbsp;'
    }

    ## HACK:  remove the \textbf from the author
    ## It actually merges with the previous author
    def format_str(self,text):
        if '\\textbf' in text:
            logger.debug('Replacing \\textbf ' + str(text))
            text = text.replace('\\textbf', '')
        if '\\' in text:
            logger.critical("Unprocessed Latex sequence: " + str(text) )
            raise Exception

        return super().format_str(text)

    ## HACK!
    ## the /textbf{} sequences seem to get tagged as "protected", so we
    ## just capture that and make it bold here
    def format_protected(self, text):
        return r'<bf>{}</bf>'.format(text)

class PubsBuilder:
    def __init__(this, bib_files):
        this.bib_strs = this._parseBibFiles(bib_files)

    def _parseBibFiles(this, bib_files):
        logger.info('Parsing Bib Files') 

        parser = bibtex.Parser()
        style = MyStyle()
        bib_strs = {}

        for bibfile in bib_files:
            logger.debug('Parsing: ' + str(bibfile))
            bib_data = parser.parse_file(bibfile)
            
        for bibkey,entry in bib_data.entries.items():
            logger.debug('formatting: ' + str(bibkey))
            #print (entry)
            # format into richtext
            bib_strs[bibkey] = style.format_entry( bibkey, entry).text
            #format into custom-html
            bib_strs[bibkey] = bib_strs[bibkey].render(MyBackend())

        return bib_strs

    def flatten(this, bib_strs=None): 
        bib_strs = bib_strs if bib_strs else this.bib_strs

        s = '' 
        for bibkey, bibstr in bib_strs.items():
           s += bibstr
           s += '<br/>\n\n'
        return s 


## Generates the page

def generate_page( jinja_env, html_folder):

    bib_files = ['conferences.bib', 'journals.bib', 'patents.bib', 'workshops.bib']
    bib_files = map(lambda x:  './cv/' + x, bib_files)
    pb = PubsBuilder(bib_files)
    content = pb.flatten()

    default_templ= jinja_env.get_template('default.html')
    name = 'publications'
    page = default_templ.render(title=name, content=content)
    with open(html_folder + '/' + name + '.html', 'w') as out:
        out.write(page)
