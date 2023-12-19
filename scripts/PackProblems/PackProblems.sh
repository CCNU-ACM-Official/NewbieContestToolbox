#!/bin/env bash
# version 2.1 
# last update: bugfix of file exist if statement
#			   bugfix of import problems to domjudge 7.3.4 -- old version also works! ヾ(≧▽≦*)o
#			   auto detect markdown converter
#              special judge is supported now

tmp='Temp'
spjtmp='ExeTemp'
tar='Problems'
spj='Executables'
basedir=`pwd`

Compress(){

	salt=`head /dev/urandom | tr -dc A-Za-z | head -c 5`
	# add salt to permit ERROR 500
	dirname=`echo $1 | cut -d/ -f1`
	pid=`echo $dirname | cut -d. -f1`
	filename=`echo $dirname | cut -d. -f2`

	newdirname=${dirname/ /_}
	if [ "$newdirname" != "$dirname" ]
	then echo "[Warning]:Space exist in dirname"
	fi

	pdir=$tmp/$filename
	spjdir=$spjtmp/$filename

	mkdir -pv $pdir/data/secret
	mkdir -pv $pdir/submissions
	mkdir -pv $spjdir

	memLimit=`sed '/^memLimit=/!d;s/.*=//' "$dirname/config.ini"`
	cpuLimit=`sed '/^cpuLimit=/!d;s/.*=//' "$dirname/config.ini"`
	optLimit=`du -s -B M $1 | cut -f1 | sort -nr | head -n1`
	if [ $optLimit == "0M" ]
		then optLimit="1M"
	fi 

	# make domjudge-problem.ini
	echo "probid='$pid'" >> $pdir/domjudge-problem.ini
	echo "name='$filename'" >> $pdir/domjudge-problem.ini
	echo "allow_submit='1'" >> $pdir/domjudge-problem.ini
	echo "allow_judge='1'" >> $pdir/domjudge-problem.ini
	echo "timelimit='$cpuLimit'" >> $pdir/domjudge-problem.ini
    
	# make problem.yaml
	echo "name: '$filename'" >> $pdir/problem.yaml
	echo "limits: " >> $pdir/problem.yaml
	echo "    memory: '$memLimit'" >> $pdir/problem.yaml
	echo "    output: '$optLimit'" >> $pdir/problem.yaml
	echo "    compilation_time: 10" >> $pdir/problem.yaml
	echo "    compilation_memory: 512" >> $pdir/problem.yaml

	if [ -e "$dirname/$dirname.pdf" ] 
	then
		cp "$dirname/$dirname.pdf" $pdir/problem.pdf
	elif [ -e "$dirname/$dirname.html" ] 
	then
		cp "$dirname/$dirname.html" $pdir/problem.html
	else		
		echo "pdf and html not found, converting md..."
		pandoc ${dirname}/${dirname}.md -o ${pdir}/problem.pdf --latex-engine=xelatex -V CJKmainfont="微软雅黑"
	fi

	cp ${1}std*.cpp $pdir/submissions
	cp ${1}*.in $pdir/data/secret

	outputs=`ls ${1}|grep .*\.out`
	for file in $outputs
	do
		filename=`echo $file | cut -d. -f1`.ans
		tr -d '\r' <${1}/$file >$pdir/data/secret/$filename
		# fix Windows CRLF line endings
	done

	outputs=`ls ${1}|grep .*\.ans`
	for file in $outputs
	do
		tr -d '\r' <${1}/$file >$pdir/data/secret/$file 
		# fix Windows CRLF line ending
	done

	if [ -e "$dirname/spj.cpp" ]
	then
		cp "$dirname/spj.cpp" "$spjdir/spj.cpp"
		cp "$basedir/testlib.h" "$spjdir/testlib.h"

		echo "special_compare='`echo $1 | tr -dc A-Za-z | cut -d/ -f1`spj'" >> $pdir/domjudge-problem.ini
		
		filename=`echo $1 | tr -dc A-Za-z | cut -d/ -f1`spj.zip
		cd $spjdir/
		zip -r $basedir/$spj/$filename ./*
		cd $basedir
	fi

	# Just add salt here
	filename=`echo $1 | cut -d/ -f1`_$salt.zip
	cd $pdir/
	zip -r $basedir/$tar/$filename ./*
	cd $basedir
}

if ! [ -x "$(command -v pandoc)" ]; then
	sudo apt install pandoc
fi

rm -rf $tmp
rm -rf $tar
rm -rf $spj
rm -rf $spjtmp

problems=`ls -F | grep "/$"`
mkdir $tmp
mkdir $tar
mkdir $spj
mkdir $spjtmp
for problem in $problems
do
	Compress $problem
done
rm -rf $tmp
rm -rf $spjtmp