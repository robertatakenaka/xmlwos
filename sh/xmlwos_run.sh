. xmlwos_config.sh

echo "Script running with CISIS version:"
$cisis_dir/mx what

colls=`ls -1 ../iso`
#rm -f ../databases/*

#for coll in $colls;
#do
#    echo "Creating now "$coll" master files"
#    isos=`ls -1 ../iso/$coll/`
#    for iso in $isos;
#    do
#        echo "Creating master files for "$iso
#        dot_iso=`expr index "$iso" 1.`-1
#        database_name=${iso:0:$dot_iso}
#        $cisis_dir/mx iso=../iso/$coll/$iso append=../databases/$database_name -all now
#    done
#done

#echo "Indexing databases according to FSTs"
#$cisis_dir/mx ../databases/artigo  fst="@../fst/artigo.fst"  fullinv/ansi=../databases/artigo  tell=1000  -all now
#$cisis_dir/mx ../databases/title   fst="@../fst/title.fst"   fullinv/ansi=../databases/title   tell=10    -all now
#$cisis_dir/mx ../databases/bib4cit fst="@../fst/bib4cit.fst" fullinv/ansi=../databases/bib4cit tell=10000 -all now

echo "Creating articles processing list"
from=$1
count=$2

range=""
if [[ $from != "" ]]; then
    range="from="$from
fi

if [[ $count != "" ]]; then
    range=$range" count="$count
fi

articles_processing_list="aplf"$from"c"$count".txt"
$cisis_dir/mx ../databases/artigo "pft=if p(v880) then,v880,fi,/" $range -all now > ../tmp/$articles_processing_list

#echo "Reading and generating XML file for each article_pid in processing list"
#rm -f ../output/*.xml
#total_pids=`wc -l ../tmp/$articles_processing_list`
#from=1
#for pid in `cat ../tmp/$articles_processing_list`;
#do
#    echo $from"/"$total_pids "-" $pid
#    from=$(($from+1))
#    echo '<article xmlns:xlink="http://www.w3.org/1999/xlink">'   > ../output/$pid.xml
#    echo "<front>"     >> ../output/$pid.xml
#    $cisis_dir/mx ../databases/artigo "btell=0" pid=$pid "lw=0" "pft=@../pft/xmlwos_front.pft"  -all now >> ../output/$pid.xml
#    echo "</front>"    >> ../output/$pid.xml
#    echo "<back>"      >> ../output/$pid.xml
#    echo "<ref-list>"  >> ../output/$pid.xml
#    $cisis_dir/mx ../databases/bib4cit "btell=0" $pid"$" "lw=0" "pft=@../pft/xmlwos_back.pft"  -all now >> ../output/$pid.xml
#    echo "</ref-list>" >> ../output/$pid.xml
#    echo "</back>"     >> ../output/$pid.xml
#    echo "</article>"  >> ../output/$pid.xml
#done

echo "Creating json files for each article"
mkdir -p ../output/isos/
total_pids=`wc -l ../tmp/$articles_processing_list`
from=1
for pid in `cat ../tmp/$articles_processing_list`;
do
    echo $from"/"$total_pids "-" $pid
    from=$(($from+1))

    loaded=`curl -s -X GET "http://localhost:8888/api/v1/is_loaded?code="$pid`
    if [[ $loaded == "False" ]]; then
        mkdir -p ../output/isos/$pid
        $cisis_dir/mx ../databases/artigo  btell="0" pid=$pid   iso=../output/isos/$pid/$pid"_artigo.iso" -all now
        $cisis_dir/mx ../databases/title   btell="0" ${pid:1:9} iso=../output/isos/$pid/$pid"_title.iso" -all now
        $cisis_dir/mx ../databases/bib4cit btell="0" $pid"$"    iso=../output/isos/$pid/$pid"_bib4cit.iso" -all now

        python isis2json.py ../output/isos/$pid/$pid"_artigo.iso" -c -p v -t 3 > ../output/isos/$pid/$pid"_artigo.json"
	python json2mongodb.py ../output/isos/$pid/$pid"_artigo.iso"
        python isis2json.py ../output/isos/$pid/$pid"_title.iso" -c -p v -t 3 > ../output/isos/$pid/$pid"_title.json"
        python json2mongodb.py ../output/isos/$pid/$pid"_title.iso"
        python isis2json.py ../output/isos/$pid/$pid"_bib4cit.iso" -c -p v -t 3 > ../output/isos/$pid/$pid"_bib4cit.json"
        python json2mongodb.py ../output/isos/$pid/$pid"_bib4cit.iso"
        rm -rf ../output/isos/$pid/*.iso
	curl -X POST "http://localhost:8888/api/v1/article?code="$pid
    else
        echo "article alread processed!!!"
    fi
done

#echo "Validating Against Schema"
#source ../xmlwos-env/bin/activate
#xml_files=`ls -1 ../output/*.xml`
#for xml_file in $xml_files;
#do
#    python validate_xml.py $xml_file
#done

deactivate
