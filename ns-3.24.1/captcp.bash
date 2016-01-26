for i in {0..11}
do
  captcp throughput -s 0.3 -i -f 1.1 -o cap dynamic_weight_$i.pcap
  cd cap
  make png
  cp throughput.png ~/Dropbox/$i\_requirement.png
  cd ..
done
