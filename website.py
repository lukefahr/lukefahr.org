#!/usr/bin/env python3
# vim: set 

import importlib
import os
import shutil

import jinja2 as jinja
import markdown

jinja_env = jinja.Environment(loader=jinja.FileSystemLoader('templates'))

#standard_templ = jinja_env.get_template('standard.html')
default_templ= jinja_env.get_template('default.html')

STATIC = 'static/'
HTML='html/'

shutil.rmtree(HTML, ignore_errors=True)
os.makedirs( HTML)

for src in os.listdir('pages'): 
    if ( src[-3:] == '.md'):
        name = src[:-3]
        md = open('pages/'+src, 'r') 
        content = markdown.markdown(md.read(), extensions=['extra'])
        page = default_templ.render(title=name.title(), content=content)
        with open(HTML + name + '.html', 'w') as out:
            out.write(page)
    elif (src[-3:] == '.py'):
        # import the python file, and call "generate_page" on it. 
        mod = importlib.import_module('pages.'+ src[:-3]) 
        mod.generate_page(jinja_env, HTML)

    else:
        print ('Ignoring: ' + str(src))

shutil.copytree( STATIC +'css', HTML + 'css')      
shutil.copytree( STATIC +'images', HTML + 'images')      
shutil.copytree( STATIC +'papers', HTML + 'papers')      
shutil.copytree( STATIC +'slides', HTML + 'slides')      

# HACK

