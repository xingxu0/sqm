#for i in "0.025" "0.05" "0.1" "0.15" "0.20" "0.25" "0.3" "0.35" "0.4" "0.45" "0.5"
#for i in "0.6" "0.65" "0.7" "0.75" "0.8" "0.85" "0.9" "0.95"
#for i in "0.125" "0.25" "0.5" "0.6" "1" "1.25" "1.5" "1.75" "2" "2.25" "2.5" "3" "3.25" "3.5" "3.75" "4" "4.25" "4.5" "4.75" "5" "7.5" "10"
for i in `seq 50 10 80`
do
	ii="$(echo $i/4 | bc -l)"
	./waf --run="scratch/lte_tcp_nonsharing --nodes=2 --distance=10000 --goldUser=1 --silverUser=0 --dataRate=$ii" > out.txt 2>&1
	for j in {0..3}
	do
		tshark -r trace_nonsharing_$j.pcap -z conv,tcp -q | grep "<->" >> trace_log_$ii.out
	done
done
