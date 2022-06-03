%translit.hfst: %translit %translit-initial.hfst
	sed 's/$$/	1/g' <$< | hfst-strings2fst -j | hfst-repeat | hfst-concatenate $(word 2,$^) - -o $@
.PHONY: translit.hfst
%translit-initial.hfst: %translit-initial
	sed 's/$$/	1/g' <$< | hfst-strings2fst -j -o $@
.PHONY: translit-initial.hfst
%translit-unbiased.hfst: %translit.hfst %forbidden.hfst
	hfst-compose -F -1 $< -2 $(word 2,$^) -o $@
%forbidden.hfst: %forbidden.regex
	hfst-regexp2fst -o $@ < $<
