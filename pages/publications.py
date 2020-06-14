#!/usr/bin/env python3

from __future__ import unicode_literals
import logging
import os
from pybtex.database.input import bibtex
from pybtex.style.formatting.__init__ import * 
from pybtex.style.template import * 
from pybtex.style.formatting.unsrt import * 
from pybtex.backends.html import *
from pybtex.style.names.plain import NameStyle
import typing 

logging.basicConfig(
    level=logging.DEBUG)

logger = logging    

class MyNameStyle(NameStyle):

    # HACK:
    # scan the author names for \textbf.  
    # If found, highlight the entire author's name
    # I should have done this for each name, but ran out of time
    def format(self, person, abbr=False):
        highlight = False
        for namefield in ['first_names', 'middle_names', 'prelast_names', 
                        'last_names', 'lineage_names']:
            names = getattr(person,namefield)
            for nidx, name in enumerate(names):
                if '\\textbf' in name: 
                    logger.debug('Found a \\textbf, highlighting name')
                    highlight = True
                    newstr = names[nidx].replace('\\textbf{', '')
                    newstr = newstr.replace('}','', 1)
                    names[nidx] = newstr
        normal = super().format(person, abbr)
        if highlight:
            return join[ tag('b') [ tag('em') [normal]]]
        else: 
            return normal            


# Adapted from pybtex.style.formatting.unrst.py
class MyStyle (Style):

    # override default name formatting
    # to use the \textbf name-bolding style
    def __init__(self, label_style=None, name_style=None, 
            sorting_style=None , abbreviate_names=False, 
                min_crossrefs=2, **kwargs):    
        super(MyStyle,self).__init__(label_style, name_style, 
                        sorting_style, abbreviate_names,
                        min_crossrefs, **kwargs)
        self.name_style = MyNameStyle()
        self.format_name =self.name_style.format

    # override default formatting to 
    # customize for our uses 

    def get_inproceedings_template(self, e):
        template = toplevel [
            tag('h4') [ field('title')],
            words [ 'By', sentence [self.format_names('author')]],
            words [ Symbol('linebreak'), 
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
            tag('h4') [ field('title')],
            words ['By', self.format_names('author'),],
            words[ Symbol('linebreak'),
                'In', 
                tag('em') [field('journal')],
                optional[ volume_and_pages ],
                date],
            sentence [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template

    def get_misc_template(self, e):
        template = toplevel [
            tag('h4') [ field('title')],
            optional[ words ['By', 
                        sentence [self.format_names('author')] ]],
            words [ Symbol('linebreak'), 
                        sentence [optional_field('note')]],
            sentence[ 
                optional[ field('howpublished') ],
                optional[ date ],
            ],

            self.format_web_refs(e),
        ]
        return template

# based off backends/html.py
class MyBackend (Backend):

    # Add a new 'linebreak' symbol to insert a
    # HTML <br \>  as desired
    symbols = {
         'ndash': u'&ndash;',
         'newblock': u'\n', 
         'linebreak': u'<br \>\n', # force line break
         'nbsp': u'&nbsp;'
    }

class PubsBuilder:
    def __init__(this, bib_files):


        bib_strs = this._parseBibFiles(bib_files)
        this.bib_strs = this._addUrls(bib_strs)


    def _parseBibFiles(this, bib_files):
        logger.info('Parsing Bib Files') 
        
        #handle strings or lists of strings
        if isinstance(bib_files, str):
            bib_files = [bib_files]

        parser = bibtex.Parser()
        style = MyStyle()
        bib_strs = {}

        for bibfile in bib_files:
            logger.debug('Parsing: ' + str(bibfile))
            bib_data = parser.parse_file(bibfile)
            
        for bibkey,entry in bib_data.entries.items():
            logger.debug('formatting: ' + str(bibkey))
            # format into richtext
            richFormat = style.format_entry( bibkey, entry).text
            logger.debug('Rich formatting: ' + str(richFormat))
            #format into custom-html
            bib_strs[bibkey] = richFormat.render(MyBackend())

        return bib_strs
    
    def _addUrls(this, bib_strs, static_path='./../static/'):
        class Link(typing.NamedTuple):
            path: str
            label: str
            
        logger.info('Adding URLs')
        
        my_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.abspath(my_dir + static_path ) + '/'

        for bibkey, bibstr in bib_strs.items():
            logger.debug('Processing ' + str(bibkey))
            urls = []

            paper = Link( 'papers/'+ bibkey + '.pdf', 'Paper')
            pptx = Link('slides/' + bibkey + '.pptx', 'Slides')
            pdf = Link('slides/' + bibkey + '.pdf', 'Slides')
            links = [paper,pptx,pdf]
            
            for link in links:
                logger.debug('Lookup: ' + str(base_dir + link.path))
                if os.path.exists( base_dir + link.path):
                    urls.append('<a href="' + link.path + '">' + 
                                link.label + '</a>')
                else:
                    logger.debug(link.label + ' not found')
            
            if urls:
                logger.debug('Adding reference links')
                refLinks = '\n<br />[' + ' | '.join(urls) + ']'
                bib_strs[bibkey] +=refLinks 

        return bib_strs 

    def flatten(this, bib_strs=None): 
        bib_strs = bib_strs if bib_strs else this.bib_strs
        
        s = ''
        for bibkey, bibstr in bib_strs.items():
           s += bibstr 
           s += '<br /><br />\n\n'
        return s 


## Generates the page

def generate_content(): 

    bib_files = {'Conference Papers': 'conferences.bib',
                'Journal Papers': 'journals.bib', 
                'Patents': 'patents.bib', 
                'Workshops': 'workshops.bib'}
    
    content = ''
    for title,bibfile in bib_files.items():
        bibfile= os.path.abspath('./cv/' +  bibfile)
        print (bibfile)
        pb = PubsBuilder(bibfile)
        content +=  '<h2>' + title + '</h2>\n' + \
                        pb.flatten()

    return content 

    
