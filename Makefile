mn:
	sudo ./python/mn.py
mn-test:
	sudo ./python/mn.py test

mn-clean:
	sudo mn -c

gui-topo:
	ryu run --observe-links ./python/tools/gui_topology/gui_topology.py


simple-net:
	sudo mn --topo single,3 --mac --switch ovsk --controller remote


ryu-hub-C1:
	echo "Controller 1 for Switches 1,2,3,4,5\n" &&	 \
	ryu-manager --wsapi-port 8081 --ofp-tcp-listen-port 6633 \
		./python/Samples/simpleSwitchHub.py

ryu-hub-C2:
	echo "Controller 2 for Switches 6,7,8\n" &&  \
	ryu-manager --wsapi-port 8080 --ofp-tcp-listen-port 6634 \
		./python/Samples/simpleSwitchHub.py

