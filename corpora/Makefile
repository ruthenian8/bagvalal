.DEFAULT_GOAL := 2shepherds.analyzed
.PHONY: count
%.analyzed: %.cyr
	hfst-lookup -i ../merged.ana.hfst -I $< -o $@
	grep . $@ > tmp.txt
	mv tmp.txt $@
%.trans: %.lat
	hfst-lookup -i ../translit/translit.hfst -I $< -o $@
	sed -i 's/\t/,/g' $@
%.nel: %.trans
	cat $< | grep . > $@
%.cyr: %.nel
	awk -F "," '{ print $$2 }' $< | cat > $@
%.tr.analyzed: %.lat
	hfst-lookup -i ../merged.tr.hfst -I $< -o $@
	grep . $@ > tmp.txt
	mv tmp.txt $@
%-check: %.tr.analyzed
	bash tr_stats.sh $<
%-show-unrecog: %.tr.analyzed
	grep "+" $< | sed "s/\t/,/g" | awk -F "," '{ print $$1 }' | sort | uniq -c | sort -nr
