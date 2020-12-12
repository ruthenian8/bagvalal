.DEFAULT_GOAL := bagval_numbers.gen.hfst
%.lexd.hfst: %.lexd
	lexd $< | hfst-txt2fst -o $@
%.ana.hfst: %.gen.hfst
	hfst-invert $< -o $@
%.twol.hfst: %.twol
	hfst-twolc $< -o $@
%.gen.hfst: %.lexd.hfst %.twol.hfst
	hfst-compose-intersect $^ -o $@
check-ana: bagval_numbers.ana.hfst gold-standart.ana.txt
	bash compare.sh $^
check-gen: bagval_numbers.gen.hfst gold-standart.txt
	bash compare.sh $^
