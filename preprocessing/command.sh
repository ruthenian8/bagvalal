awk -F, '{ print $1 }' chosen.csv | hfst-proc ../merged.tr.hfstol > ./sampledAnas.txt
sed 's/^[^/]*\///g' sampledAnas.txt > /tmp/temp.txt
cat /tmp/temp.txt > ./sampledAnas.txt
rm /tmp/temp.txt
