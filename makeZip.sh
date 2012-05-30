#!/bin/bash
if [ $# -ne 1 ]
then
	echo "Need a version number to create zip..."
	exit 65
fi
zip ./script.xbmal-$1.zip -r ./script.xbmal
