#!/bin/bash
icol=0
itab=0
iligne=0
icell=0
sedLine=0
icellee=0
icelleetemp=0
while read i; do
	sedLine=$((sedLine + 1))
	string=""
	string=$(echo $i | grep  '<tab')
	if [ ! -z "$string" ];then
		tab=""
		col=""
		ligne=""
		cell=""
		cellee=""
		tab=$(echo $i | grep '<tabtexte')
		col=$(echo $i | grep '<tabcol')
		ligne=$(echo $i | grep '<tabligne')
		cell=$(echo $i | grep '<tabcelluled')
		cellee=$(echo $i | grep '<tabcellulee')
		if [ ! -z "$tab" ]; then
			itab=$((itab + 1))
			icol=0
			iligne=0
			icell=0
			icellee=0
			icelleetemp=0
			sed -i "${sedLine}s/<tabtexte/<tabtexte id=\"tt${itab}\"/" $1
		elif [ ! -z "$col" ]; then
			icol=$((icol + 1))
			sed -i "${sedLine}s/<tabcol/<tabcol id=\"tt${itab}co${icol}\"/" $1
		elif [ ! -z "$ligne" ]; then
			# if case for first line, required in case of 2 cellulee line per table
			if [ "$icol" -gt 0 ];then
				icelleeTemp=$((icellee - icol))
			fi
			icol=0
			iligne=$((iligne + 1))
			sed -i "${sedLine}s/<tabligne/<tabligne id=\"tt${itab}li${iligne}\"/" $1

		elif [ ! -z "$cell" ]; then
			icol=$((icol + 1))
			icell=$((icell + 1))
			icelleeTemp=$((icelleeTemp + 1))
			sed -i "${sedLine}s/<tabcelluled/<tabcelluled id=\"tt${itab}td${icell}\" idcol=\"tt${itab}co${icol}\" idligne=\"tt${itab}li${iligne}\" identete=\"tt${itab}e${icelleeTemp}\"/" $1

		elif [ ! -z "$cellee" ]; then
			icol=$((icol + 1))
			icellee=$((icellee + 1))
			sed -i "${sedLine}s/<tabcellulee/<tabcellulee id=\"tt${itab}e${icellee}\" idcol=\"tt${itab}co${icol}\" idligne=\"tt${itab}li${iligne}\"/" $1
		fi
	fi
done < $1
