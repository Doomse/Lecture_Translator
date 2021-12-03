#!/bin/bash -ex

javaBin=/usr/bin/java
lium_jar=./worker_scripts/LIUM_SpkDiarization-8.4.1.jar

tmpfile=$(mktemp /tmp/seg-audio.XXXXXX)

exec 3> "$tmpfile"
exec 4< "$tmpfile"
rm "$tmpfile"

sourcepath=$1
resultpath=$2
taskname=$3

${javaBin} -Xmx4096m -jar $lium_jar --fInputMask=$sourcepath --sOutputMask=/proc/$$/fd/3 --doCEClustering $taskname

cat <&4 | grep -v ";;" | awk '{print $1,$1,$3/100.,($3+$4)/100.}' > $resultpath

