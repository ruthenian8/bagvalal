.DEFAULT_GOAL := rus2.ana.hfst
%.lexd.hfst: %.lexd
	lexd $< | hfst-txt2fst -o $@
%.ana.hfst: %.gen.hfst
	hfst-invert $< -o $@
%.twol.hfst: %.twol
	hfst-twolc $< -o $@
%.gen.hfst: %.lexd.hfst %.twol.hfst
	hfst-compose-intersect $^ -o $@

