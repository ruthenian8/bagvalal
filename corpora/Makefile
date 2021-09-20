.DEFAULT_GOAL := kcor-check
../merged.ana.hfst:
	cd ..; make merged.ana.hfst
../merged.tr.hfst:
	cd ..; make merged.tr.hfst
%.analyzed: %.cyr ../merged.ana.hfst
	hfst-lookup -i ../merged.ana.hfst -I $< -o $@
	grep . $@ > tmp.txt
	mv tmp.txt $@
%.trans: %.lat ../translit/translit.hfst
	hfst-lookup -i ../translit/translit.hfst -I $< -o $@
	sed -i 's/\t/,/g' $@
%.nel: %.trans
	cat $< | grep . > $@
%.cyr: %.nel
	awk -F "," '{ print $$2 }' $< | cat > $@
%.tr.analyzed: %.lat ../merged.tr.hfst
	hfst-lookup -i ../merged.tr.hfst -I $< -o $@
	grep . $@ > tmp.txt
	mv tmp.txt $@
%-check: %.tr.analyzed tr_stats.sh
	bash tr_stats.sh $<
%-show-unrecog: %.tr.analyzed
	grep "+" $< | sed "s/\t/,/g" | awk -F "," '{ print $$1 }' | sort | uniq -c | sort -nr
