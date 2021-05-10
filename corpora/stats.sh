#!/bin/sh
# initial corpus is presumably latin-based
if [ $1 ];
then
target="$1"
else
target="2shepherds.analyzed"
fi
overall=`sort $target | sort | uniq | wc -l`
rec=`grep -v --regexp="inf" $target | sort | uniq | wc -l`
echo "Number of transliterated tokens";
echo "(includes abundant forms due to transliteration ambiguity):";
echo "$overall";
echo "Number of recognized forms (including duplicates):"
echo "$rec";
exit 0;