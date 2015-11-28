mn:
	sudo ./python/mn.py
mn-test:
	sudo ./python/mn.py test

mn-clean:
	sudo mn -c

gui-topo:
	ryu run --observe-links ./python/tools/gui_topology/gui_topology.py


simple-net:
	sudo mn --topo single,3 --mac --switch ovsk,protocols=openflow13 --controller remote


ryu-hub-C1:
	echo "Controller 1 for Switches 1,2,3,4,5\n" &&	 \
	ryu-manager --wsapi-port 8081 --ofp-tcp-listen-port 6633 \
		./python/Samples/simpleSwitchHub.py

ryu-hub-C2:
	echo "Controller 2 for Switches 6,7,8\n" &&  \
	ryu-manager --wsapi-port 8080 --ofp-tcp-listen-port 6634 \
		./python/Samples/simpleSwitchHub.py



update-requirements:
	rm -f ./requirements.txt &&  pip freeze > ./requirements.txt

install-requirements:
	pip install -r ./requirements.txt

# following is start the real program

controller_1:
	echo "Controller 1 for Switches 1,2,3,4,5\n" &&	 \
	ryu-manager --wsapi-port 8081 --ofp-tcp-listen-port 6633 \
		./python/controller.py

controller_2:
	echo "Controller 2 for Switches 6,7,8\n" &&  \
	ryu-manager --wsapi-port 8080 --ofp-tcp-listen-port 6634 \
		./python/controller.py	
monitor:
	python ./python/monitor.py


sample-rest-api:
	ryu-manager ./python/Samples/restApi.py


shutdown:
	sudo killall -KILL python ryu-manager mn make
