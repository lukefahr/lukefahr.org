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
import typing 

logging.basicConfig(
    level=logging.DEBUG)

logger = logging    

# Adapted from pybtex.style.formatting.unrst.py
class MyStyle (Style):
    
    # override default formatting to 
    # customize for our uses 

    def get_inproceedings_template(self, e):
        template = toplevel [
            tag('h4') [self.format_title(e, 'title')],
            words [ 'By', sentence [self.format_names('author')]],
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
            tag('h4') [self.format_title(e, 'title')],
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
            optional[ tag('h4') [self.format_title(e, 'title')]],
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

    def format_tag(self, tag, text):
        return r'<{0}>{1}</{0}>'.format(tag, text) if text else u''

    ## HACK!
    ## the /textbf{} sequences seem to get tagged as "protected", so we
    ## just capture that and make it bold here
    def format_protected(self, text):
        return r'<b><em>{}</em></b>'.format(text)

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
            #print (entry)
            # format into richtext
            bib_strs[bibkey] = style.format_entry( bibkey, entry).text
            #format into custom-html
            bib_strs[bibkey] = bib_strs[bibkey].render(MyBackend())

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

def generate_page( jinja_env, html_folder):

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


    default_templ= jinja_env.get_template('default.html')
    name = 'publications'
    page = default_templ.render(title=name, content=content)
    with open(html_folder + '/' + name + '.html', 'w') as out:
        out.write(page)
