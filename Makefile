analyser=./merged.tr.hfstol
main_file_prefix=merged
translit_file=old-translit-unbiased.hfst
tests=tests.csv
test_sources=$(shell sed -s 1d $(tests) | cut -d, -f4 | sort -u)
test_len=$(shell wc -l $(tests))

.DEFAULT_GOAL := $(analyser)

###############################################################################
## TRANSLITERATOR RULES
###############################################################################

translit/$(translit_file):
	cd translit; make $(translit_file)

###############################################################################
## PREPROCESSING RULES
###############################################################################

preprocessing/mag-translit.csv: translit/mag-translit.hfst
	cd preprocessing; make mag-translit.csv

###############################################################################
## BILINGUAL ANALYZER RULES
###############################################################################

# bilingual/%.gen.hfst: bilingual/%.lexd $(main_file_prefix).twol.hfst
# 	lexd $< | hfst-txt2fst | hfst-compose-intersect - $(word 2,$^) -o $@
bilingual/$(main_file_prefix).ana.%.hfst: $(main_file_prefix).ana.hfst bilingual/%.lexd.hfst
	hfst-compose -1 $< -2 $(word 2,$^) -o $@
bilingual/$(main_file_prefix).tr.%.hfst: translit/$(translit_file) bilingual/$(main_file_prefix).ana.%.hfst
	hfst-compose  $^ -o $@
test-bilingual: corpora/Kibrik_texts.parsed bilingual/$(main_file_prefix).tr.bag_rus.hfst
	@awk -F',' '{print $$2}' $< | sed 's/[^а-яёЁйЙА-Я]*\([а-яёЁйЙА-Я]\+\).*/\1/' | sort | uniq > tmp1
	@awk -F',' '{print $$1}' $< | hfst-lookup $(word 2,$^) | grep -E -e "[а-яА-Я]+" | sed 's/[^а-яёЁйЙА-Я]*\([а-яёЁйЙА-Я]\+\).*/\1/' | sort | uniq > tmp2
	@echo -e "\nUnique Russian words: $$(wc -l tmp1)"
	@echo "Recognized Russian words: $$(comm -1 -2 tmp1 tmp2 | wc -l)"
	@rm -r tmp1 tmp2
.PHONY: test-bilingual

###############################################################################
## MORPHOLOGICAL ANALYZER RULES
###############################################################################
# hfst-compose merged.ana.hfst bag_rus.lexd.hfst -o merged.bilingual.hfst
%.tr.hfst: translit/$(translit_file) %.ana.hfst 
	hfst-compose $^ -o $@
%.lexd.hfst: %.lexd
	lexd $< | hfst-txt2fst -o $@
%.lexd.hfstol: %.lexd.hfst
	hfst-fst2fst --optimized-lookup-unweighted $< -o $@
%.ana.hfst: %.gen.hfst
	hfst-invert $< -o $@
%.twol.hfst: %.twol
	hfst-twolc $< -o $@
%.gen.hfst: %.lexd.hfst %.twol.hfst
	hfst-compose-intersect $^ -o $@
%.tr.hfstol: %.tr.hfst
	hfst-fst2fst --optimized-lookup-unweighted -i $< -o $@
%.hfstol: %.hfst
	echo '?::0' | hfst-regexp2fst | hfst-repeat | hfst-compose -F $< - | hfst-minimise -E | hfst-fst2fst -w -o $@

speller/spellrelax.hfst: speller/spellrelax.regex
	hfst-regexp2fst -o $@ < $<
%.relaxed.ana.hfst: speller/spellrelax.hfst %.ana.hfst
	hfst-compose-intersect -1 $< -2 $(word 2,$^) -o $@


###############################################################################
## COVERAGE CHECKS
###############################################################################

check-coverage-stats: corpora $(analyser) stats
	@ cd corpora; find * -name "*.lat" -print0 | xargs -0 ../stats ../$(analyser)
check-coverage-unrecog: corpora $(analyser) unrecog
	@ find corpora -name "*.lat" -print0 | xargs -0 ./unrecog $(analyser)
check-coverage: corpora $(analyser) stats unrecog
	@ echo aggregate coverage:
	@ (make -s check-coverage-stats; find corpora -name "*.lat" -exec cat {} \; | ./stats -q $(analyser) -) | column -t
	@ echo
	@ echo unrecognised words:
	@ make -s check-coverage-unrecog | tail -n20

%.pass.txt: $(tests)
	awk -F, '$$4 == "$*" && $$3 == "pass" {print $$1 ":" $$2}' $^ | sort -u > $@
%.ignore.txt: $(tests)
	awk -F, '$$4 == "$*" && $$3 == "ignore" {print $$1 ":" $$2}' $^ | sort -u > $@
check-gen: merged.gen.hfst $(foreach t,$(test_sources),$(t).pass.txt $(t).ignore.txt)
	for t in $(test_sources); do echo $$t; bash compare.sh $< $$t.ignore.txt; bash compare.sh $< $$t.pass.txt || exit $$?; done;
check: check-gen
.PHONY: check

testing/analyses.csv: testing/gudtexts.txt
	python3 asynccsv.py --input-file=$< --output_file=$@
testing/chosen.csv: testing/analyses.csv
	python3 sampleWords.py $<
testing/sampledAnas.txt: testing/chosen.csv merged.tr.hfstol
	awk -F, '{ print $$1 }' $< \
	| hfst-proc $(word 2,$^) > $@
	sed 's/^[^/]*\///g' $@ > /tmp/temp.txt
	mv /tmp/temp.txt > $@

###############################################################################
## MORPHOLOGICAL GUESSER RULES
###############################################################################

guesser/guess-filter.hfst: guesser/guess-filter
	hfst-regexp2fst -o $@ < $<
guesser/%-guess.lexd: %.lexd decltypes.lexd
	@cat $^ > $@
	@sed -i 's/^\([a-zA-Z]*adjSingle[][a-zA-Z_-]* \)/\1DeclType[TypeAdj] /g' $@
	@sed -i 's/^\(agrInitial[][a-zA-Z_-]\+ [][a-zA-Z_-]\+ \)/\1DeclType[Type2xAdj] /g' $@
	@sed -i 's/^\(Noun[][a-zA-Z_-]\+ \)/\1DeclType[TypeNom] /g' $@
# @sed -i 's/^\(Potentialis\|Prateritum\|Prohibitive\|Imperfect\)/\1 DeclType[TypeVerb]/g' $@
	@sed -i 's/\(VerbStem\[Idecl,\([AB],\)\{0,1\}-\{0,1\}AgrInit\] \[:>\] \)/\1DeclType[TypeVerb] /g' $@
	@sed -i 's/\(VerbStem\[IIdecl,\([AB],\)\{0,1\}-\{0,1\}AgrInit\] \[:>\] \)/\1DeclType[TypeVerb] /g' $@
	@sed -i 's/\(VerbStem\[IIIdecl,\([AB],\)\{0,1\}-\{0,1\}AgrInit\] \[:>\] \)/\1DeclType[TypeVerb] /g' $@
	@sed -i 's/\(VerbStem\[IVdecl,\([AB],\)\{0,1\}-\{0,1\}AgrInit\] \[:>\] \)/\1DeclType[TypeVerb] /g' $@
	@sed -i 's/\(VerbStem\[Vdecl,\([AB],\)\{0,1\}-\{0,1\}AgrInit\] \[:>\] \)/\1DeclType[TypeVerb] /g' $@
guesser/%-guess.ana.hfst: guesser/%-guess.lexd %.twol.hfst
	lexd $< | hfst-txt2fst | hfst-compose-intersect - $(word 2,$^) | hfst-invert - -o $@
guesser/%-guess.ana.subst.hfst: guesser/%-guess.ana.hfst
	hfst-summarize -v $< \
	| grep -A1 'sigma set:' \
	| tail -1 \
	| sed 's/, /\n/g' \
	| grep -E '<Type.+>'\
	| sed 's/<Type\(.\+\)>/&\t[GUESS_CATEGORY=\1]/'\
	| hfst-substitute -F - -o $@ $<
guesser/%-guess.filtered: guesser/%-guess.ana.subst.hfst guesser/guess-filter.hfst
	hfst-compose -F -1 $< -2 $(word 2,$^) | hfst-minimize > $@
guesser/%.guesser.hfst: guesser/%-guess.filtered
	hfst-guessify -v  $< > $@
test-guesser: tests.csv guesser/$(main_file_prefix).guesser.hfst
	@echo "Overall test cases: $$(wc -l $<)"
	@sed 's/^\([^\<]*<[^\<]\{1,5\}>\).*/\1/g' $< | sort | uniq > guesser/test_stems
	@awk -F"," '{print $$2}' $< | hfst-guess $(word 2,$^) | sed 's/.*\t\(.*\)\[.*/\1/' | sort | uniq > guesser/guessed_stems
	@echo "Succesfully guessed stems: $$(comm -1 -2 guesser/test_stems guesser/guessed_stems | wc -l | cat)" 
	@rm -r guesser/test_stems guesser/guessed_stems
.PHONY: test-guesser

###############################################################################
## Spell checker
###############################################################################

check-speller-num-%: tests.csv $(main_file_prefix).zhfst # use with 1 or 2 instead of the wildcards
	awk -F"," '{print $$2}' $< \
	| sed 's/[аоуэеи]/я/' \
	| hfst-ospell -S $(word 2,$^) \
	| grep $* 
# | wc -l


$(main_file_prefix).zhfst: .deps/acceptor.default.hfst .deps/errmodel.default.hfst speller/index.xml
	rm -f $@
	zip -j $@ $^

.deps/editdist.default.att: speller/editdist.default.txt .deps/acceptor.default.hfst
	apertium-editdist -v -s -d 1 -e '@0@' -i speller/editdist.default.txt -a .deps/acceptor.default.hfst > $@
.deps/editdist.default.hfst: .deps/editdist.default.att
	hfst-txt2fst -e '@0@' $< -o $@
.deps/editstrings.default.hfst: .deps/strings.default.hfst .deps/editdist.default.hfst
	hfst-disjunct $^ | hfst-minimise | hfst-repeat -f 1 -t 2 -o $@
.deps/errmodel.default.hfst: .deps/words.default.hfst .deps/editstrings.default.hfst
	hfst-disjunct $^ | hfst-fst2fst -f olw -o $@
.deps/words.default.hfst: speller/words.default.txt
	grep -v -e "^#" -e "^$$" $< | hfst-strings2fst  -j -o $@
.deps/strings.default.hfst: speller/strings.default.txt .deps/anystar.hfst
	grep -v -e "^#" -e "^$$" $< | hfst-strings2fst  -j | hfst-concatenate .deps/anystar.hfst - |\
	hfst-concatenate - .deps/anystar.hfst -o $@
.deps/anystar.hfst:
	echo "?*;" | hfst-regexp2fst -S -o $@
.deps/acceptor.default.hfst: $(main_file_prefix).gen.hfst
	cat $< | hfst-fst2fst -t | hfst-project --project=lower | hfst-minimise | hfst-fst2fst  -f olw -o $@

# echo "рьабда" | hfst-ospell -S merged.zhfst | grep 1 | awk '{print $1;}' | hfst-proc merged.ana.hfstol