.DEFAULT_GOAL := sampledAnas.txt

#######################
# MISC FUNCTIONS
#######################

../merged.tr.hfstol:
	cd ..; make merged.tr.hfstol;
clean:
	rm -r mag-*
	rm -r *.enum
	rm -r tmp*
	make clean_word
.PHONY: clean

#######################
# GENERIC FUNCTIONS
#######################

%.enum: %
	awk -F";" -v OFS=";" 'NR == 1 {print "0", $$0; next} {print (NR-1), $$0}' $< > $@
%-first: %.csv
	awk -F";" '{ print $$1 }' $< > $@
%-translit: %-first ../translit/%-translit.hfst
	hfst-lookup -i $(word 2,$^) -I $< > $@
	grep . $@ | awk -F "\t" '{ print $$2 }' > tmp.txt
	mv tmp.txt $@
%-translit.csv: %-translit.enum %.csv.enum
	join -t ";" -1 1 -2 1 $(word 1,$^) $(word 2,$^) \
	| cut -d ";" -f 2- \
	| grep -v "+?" > tmp3.txt
	mv tmp3.txt $@
lexicon/%.raw.lexd: lexicon/%.raw ../translit/kibrik-translit.hfst
	awk -F ":" '{print $$2}' $< | hfst-lookup ../translit/kibrik-translit.hfst \
	| grep -v -E -f ../translit/forbidden \
	| sed 's/\t/:/g'\
	| awk -F":" -v OFS=":" 'NR == 1 {print "0", $$0; next} {print (NR-1), $$0}' > tmp2.txt
	awk -F":" -v OFS=":" 'NR == 1 {print "0", $$0; next} {print (NR-1), $$0}' $< > tmp.txt
	join -t ":" -1 1 -2 1 tmp.txt tmp2.txt\
	| awk -F ":" -v OFS=":" '{print $$2, $$5}'
	> $@
	rm -r tmp.txt tmp2.txt

#######################
# PARSE DICTIONARIES
#######################

mag-pos: mag-translit.csv
	cat $< \
	| awk -F ";" '{print $$7}' \
	| sed 's/\([а-я]*\) .*/\1/' \
	| awk '!NF{$$0="."}1' \
	| pymorphy --tokenized parse \
	| sed 's/.*=\([A-Z]*\)[,} ].*/\1/' \
	> $@
.PHONY: mag-pos
magomedova-annot.csv: mag-pos.enum mag-translit.csv.enum
	join -t ";" -1 1 -2 1 $^ \
	| cut -d ";" -f 2- \
	| awk -F";" -v OFS=";" '{ print $$2, $$5, $$8, $$1 }' \
	> $@
# make Kibrik dict
kibrik.xml: bag.docx
	mkdir kibrik
	unzip $< -d kibrik
	cp kibrik/word/document.xml $@
	make clean_word
clean_word:
	rm -r kibrik
.PHONY: clean_word
kibrik.csv: document.xml
	python3 extract_kibrik.py --infile=$< --outfile=$@

#######################
# PARSE LEXICONS
#######################

lexicon/kibrik-pl-%.lexd: kibrik.csv
	grep -v "+?"  $<\
	| sed 's/\(.* pl \)\(.*\) || \(.*\)\(,.*\)/\1\2;\4\n\1\3;\4/'\
	| grep "pl $*"\
	| awk -F ";" -v OFS="" '{print $$1,"<n>:",$$1," # ",$$3}'\
	> $@
lexicon/kibrik-unique-pl.raw: kibrik.csv
	grep -v "+?" $<\
	| grep ' pl '\
	| sed 's/\(.* pl \)\(.*\) || \(.*\)\(,.*\)/\1\2;\4\n\1\3;\4/'\
	| sed 's/\(.* pl \)\(.*\) || \(.*\)\(,.*\)/\1\2;\4\n\1\3;\4/'\
	| sed 's/\(\);.* pl \(.*\),.*/\1<n>:\2/'\
	| grep -v -E -e ":[aāi].{0,1}$$" -e ":[jz]{0,1}.{0,1}bi" -e ":dari" -e ":a{0,1}[dl]i"\
	| sed 's/;//g'\
	> $@
# genitive plural forms of nouns make kibrik-pl-unique.raw.lexd | awk -F ":" '{print $2}' | hfst-lookup ../translit/kibrik-translit.hfst | awk 'NR==FNR {a[$1] = $1; next} {print $1 a[$1]}'
lexicon/kibrik-genpl-%.lexd: kibrik.csv
	grep -v "+?" $<\
	| grep "genpl" \
	| sed 's/\(.*genpl \)\(.*\) || \([a-zɬ=]*\)\(.*\)/\1\2;\4\n\1\3;\4/'\
	| sed 's/\(.*genpl \)\(.*\) || \([a-zɬ=]*\)\(.*\)/\1\2;\4\n\1\3;\4/'\
	| grep "genpl $*"\
	| awk -F ";" -v OFS="" '{print $$1,"<n>:",$$1," # ",$$3}'\
	> $@
lexicon/kibrik-unique-genpl.raw: kibrik.csv
	grep -v "+?"  $<\
	| grep "genpl" \
	| sed 's/\(.*genpl \)\(.*\) || \(.*\)$$/\1\2\n\1\3/'\
	| sed 's/\(.*genpl \)\(.*\) || \(.*\);/\1\2\n\1\3/'\
	| sed 's/\(\);.*genpl \([a-z’ɬʷ=χː]*\)/\1<n>:\2/'\
	| grep -v -E -e "[—⮊⇔]" -e ":dar.ɬ" -e ":.{0,3}ɬ" -e ":šːu=b" -e "d{0,1}[aāi][rl]u=b"\
	| sed 's/\(.*\):\(.*\) || \(.*\)/\1:\2\n\1:\3/'\
	| grep -v -E -e '[|;]'\
	> $@
# genitive forms of nouns
lexicon/kibrik-gen-%: kibrik.csv
	grep -v "+?"  $<\
	| sed 's/\(.*gen \)\(.*\) || \(.*\)\(,.*\)/\1\2;\4\n\1\3;\4/'\
	| sed 's/\(.*gen \)\(.*\) || \(.*\)\(,.*\)/\1\2;\4\n\1\3;\4/'\
	| grep "gen $*"\
	| awk -F ";" -v OFS="" '{print $$1,"<n>:",$$1," # ",$$3}'\
	> $@
lexicon/kibrik-unique-gen.raw: kibrik.csv
	cat  $<\
	| sed 's/\(.*gen \)\(.*\) || \(.*\)\(, pl.*\)/\1\2;\4\n\1\3;\4/'\
	| sed 's/\(.*gen \)\(.*\) || \(.*\)\(, pl.*\)/\1\2;\4\n\1\3;\4/'\
	| grep ";N;"\
	| grep -v -e "+?" -e "gen ɬ" -e "gen ɬiɬ" -e "gen .ɬ" -e "šːu=b"\
	| sed 's/\(\);.*gen \(.*\)[;,] pl.*/\1<n>:\2/'\
	| sed 's/;//g'
lexicon/kibrik-verbs: kibrik.csv
	cat $<\
	grep ";V;"
