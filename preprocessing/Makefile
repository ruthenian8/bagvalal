.DEFAULT_GOAL := sampledAnas.txt

../merged.tr.hfstol:
	cd ..; make merged.tr.hfstol;

Kibrik_dict.xlsx:
	python3 extractKibrik.py save

analyses.csv: gudtexts.txt
	python3 asynccsv.py

chosen.csv: analyses.csv
	python3 sampleWords.py $<

sampledAnas.txt: chosen.csv ../merged.tr.hfstol
	awk -F, '{ print $$1 }' chosen.csv | hfst-proc ../merged.tr.hfstol > $@
	sed 's/^[^/]*\///g' sampledAnas.txt > /tmp/temp.txt
	cat /tmp/temp.txt > $@
	rm /tmp/temp.txt
