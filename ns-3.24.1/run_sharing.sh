#for i in "0.5" "1" "2" "3" "4" "5" "6" "7" "8" "9" "10"
for i in "15" "20" "30" "40"
do
	./waf --run="scratch/lte_tcp -distance=10000 --goldUser=1 --silverUser=0 --dataRate=$i" > out.txt 2>&1
	tshark -r trace_log-1-1.pcap -z conv,tcp -q | grep "<->" >> trace_log_$i.out
done
