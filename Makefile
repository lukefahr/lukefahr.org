
all: local 


local:
	python3 website.py

	

clean: 
	rm -rf html

.PHONY:  all local clean	


