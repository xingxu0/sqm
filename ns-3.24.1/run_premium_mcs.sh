#for i in "0.025" "0.05" "0.1" "0.15" "0.20" "0.25" "0.3" "0.35" "0.4" "0.45" "0.5"
#for i in "0.6" "0.65" "0.7" "0.75" "0.8" "0.85" "0.9" "0.95"
#for i in "0.125" "0.25" "0.5" "0.6" "1" "1.25" "1.5" "1.75" "2" "2.25" "2.5" "3" "3.25" "3.5" "3.75" "4" "4.25" "4.5" "4.75" "5" "7.5" "10"
for i in 5000 10000 15000 20000 30000 40000
do
	echo $i
	for p in 0
	do
		./waf --run="scratch/lte_tcp_nonsharing --nodes=10 --premium_distance=$i --goldUser=$p --silverUser=0 --dataRate=100" > out.txt 2>&1
		for j in {0..9}
		do
			tshark -r trace_nonsharing_$j.pcap -z conv,tcp -q | grep "<->" >> trace_log_$i\_$p.out
		done
	done
done
