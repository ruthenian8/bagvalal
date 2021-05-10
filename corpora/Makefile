.DEFAULT_GOAL := 2shepherds.analyzed
.PHONY: count
%.analyzed: %.cyr
	hfst-lookup -i ../merged.ana.hfst -I $< -o $@
%.trans: %.lat
	hfst-lookup -i ../translit/translit.hfst -I $< -o $@
	sed -i 's/\t/,/g' $@
	cat $@ | grep . | cat > $@
%.cyr: %.trans
	awk -F "," '{ print $$2 }' $< | cat > $@