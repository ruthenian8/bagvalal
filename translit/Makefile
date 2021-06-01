translit.hfst: translit translit.multi translit-initial.hfst
#	sed 's/$$/	1/g' <$< | hfst-strings2fst -j -m $<.multi | hfst-repeat | hfst-concatenate translit-initial.hfst - | hfst-fst2fst -w -o translit.hfst
#	sed 's/$$/	1/g' <$< | hfst-strings2fst -j -m $<.multi | hfst-repeat | hfst-concatenate translit-initial.hfst - -o translit.hfst
	sed 's/$$/	1/g' <$< | hfst-strings2fst -j | hfst-repeat | hfst-concatenate translit-initial.hfst - -o translit.hfst
translit-initial.hfst: translit-initial
	sed 's/$$/	1/g' <$< | hfst-strings2fst -j -o $@
