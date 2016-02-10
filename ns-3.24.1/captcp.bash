for i in {0..3}
do
  captcp throughput -s 1.0 -i -f 1.1 -o cap dynamic_weight_$i.pcap
  cd cap
  make png
  cp throughput.png ~/Dropbox/$i\_mobility.png
  cd ..
done
