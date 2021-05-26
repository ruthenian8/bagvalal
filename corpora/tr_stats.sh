#!/bin/sh
if [ $1 ];
then
target="$1"
else
target="k_newline.tr.analyzed"
fi
sed 's/\t/,/g' $target > temp.txt
awk -F "," '{ print $1 }' temp.txt > t2.txt
overall=`sort t2.txt | uniq | wc -l`
rm temp.txt t2.txt
unrec=`grep --regexp="+" $target | sort | uniq | wc -l`
echo "Number of unique tokens: $overall";
nanalyzed=`grep -v --regexp=="+" $target | wc -l`
rec=`echo "scale=2; $overall - $unrec" | bc`
echo "Number of recognized unique tokens: $rec";
percent=`echo "scale=2; $rec / $overall * 100" | bc`
mamb=`echo "scale=2; $nanalyzed / $rec" | bc`
echo "Percentage of recognized forms: $percent"
echo "Mean ambiguity: $mamb"
exit 0;