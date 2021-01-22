
all: local 


local:
	python3 website.py

remote: local
	rsync -a -v html/ lukefahr@silo.soic.indiana.edu:~/cgi-pub/ 
	
clean: 
	rm -rf html

.PHONY:  all local remote clean	


