#!/bin/bash
if [ $# -ne 1 ]
then
	echo "Need a version number to create zip..."
	exit 65
fi
zip ./script.service.xbmal-$1.zip -r ./script.service.xbmal
