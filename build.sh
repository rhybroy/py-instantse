#!/bin/bash 

mkdir ./output

for i in `ls`
do
    if [ $i == "output" ]
    then
        continue
    elif [ -d $i ]
    then
        cp -r $i ./output/
    else
        cp $i ./output/
    fi
done

cd ./output

find . -type d -name ".svn" | xargs rm -rf

cd ..

mv ./output search

tar zfc search.tar.gz search

rm -rf search
