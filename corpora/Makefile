.DEFAULT_GOAL := kcor-check
translit_file=old-translit-unbiased.hfst
main_file_prefix=merged

#################
# CORPUS CREATION
#################

%.xml: %.docx
	mkdir $*
	unzip $< -d $*
	cp "$*/word/document.xml" $@
	sed -i 's/\(<w:p \)/\n\1/g' $@
	sed -i '/\(Translation\|Sylfaen\|w:anchor\)/d' $@
	sed -i 's/\(<w:tab\/>\)/<w:t>\t<\/w:t>/g' $@
	sed -i 's/<w:br\/>/<\/w:p><w:p>/g' $@
	rm -r $*
%.parsed: %.xml
	python3 xmlparser.py -i $< -o $@
%.lat: %.parsed
	awk -F"," '{print $$1}' $< > $@
%.wordcol: %.parsed
	sed 's/\([^а-яА-Яёй]*\([а-яА-Яёй]*\).*\)/\1,\2/g' $< \
	| sed 's/,$$/,./g' > 

###################
# CORPUS PROCESSING
###################

%.analyzed: %.trans ../$(main_file_prefix).ana.hfst
	hfst-lookup -i $(word 2,$^) -I $< \
	| sed '/^$$/d' > $@
%.trans: %.lat ../translit/$(translit_file)
	cat $< \
	| hfst-lookup -I - -i $(word 2,$^) \
	| sed '/^$$/d' \
	| sed 's/\t/,/g' \
	| awk -F "," '{ print $$2 }' > $@
%.tr.analyzed: %.lat ../$(main_file_prefix).tr.hfst
	@hfst-lookup -i $(word 2,$^) -I $< \
	| sed '/^$$/d' > $@
%-check: %.tr.analyzed tr_stats.sh
	@bash tr_stats.sh $<
%-show-unrecog: %.tr.analyzed
	@grep "+" $< | sed "s/\t/,/g" | awk -F "," '{ print $$1 }' | sort | uniq -c | sort -nr

############
# MISC
############

gloss_mapping.hfst: gloss_mapping
	sed 's/$$/	1/g' <$< | hfst-strings2fst -j | hfst-repeat -o $@
../$(main_file_prefix).ana.hfst:
	cd ..; make merged.ana.hfst
../$(main_file_prefix).tr.hfst:
	cd ..; make merged.tr.hfst
