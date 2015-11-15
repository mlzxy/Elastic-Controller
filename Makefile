mn:
	sudo ./python/mn.py
mn-test:
	sudo ./python/mn.py test

mn-clean:
	sudo mn -c

gui-topo:
	ryu run --observe-links ./python/tools/gui_topology/gui_topology.py
