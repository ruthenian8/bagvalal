analyser=./merged.tr.hfstol
.DEFAULT_GOAL := $(analyser)
tests=tests.csv
test_sources=$(shell sed -s 1d $(tests) | cut -d, -f4 | sort -u)
.PHONY: check

translit/translit.hfst: translit/translit translit/translit.multi translit/translit-initial.hfst
	cd translit; make translit.hfst
translit/translit-initial.hfst: translit/translit-initial
	cd translit; make translit-initial.hfst
%.tr.hfst: translit/translit.hfst %.ana.hfst 
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
%.pass.txt: $(tests)
	awk -F, '$$4 == "$*" && $$3 == "pass" {print $$1 ":" $$2}' $^ | sort -u > $@
%.ignore.txt: $(tests)
	awk -F, '$$4 == "$*" && $$3 == "ignore" {print $$1 ":" $$2}' $^ | sort -u > $@
check-gen: merged.gen.hfst $(foreach t,$(test_sources),$(t).pass.txt $(t).ignore.txt)
	for t in $(test_sources); do echo $$t; bash compare.sh $< $$t.ignore.txt; bash compare.sh $< $$t.pass.txt || exit $$?; done;
check: check-gen
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
%.hfstol: %.hfst
	echo '?::0' | hfst-regexp2fst | hfst-repeat | hfst-compose -F $< - | hfst-minimise -E | hfst-fst2fst -w -o $@