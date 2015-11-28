#!/usr/bin/python

"""
This Python generate an 8-switch openflow network,
with 2 controllers.  The switches are connected
in a cube manner.

The distribution of switches for controller,
and the number of nodes under each switch are
configured in Config.py.
"""

from mininet.net import Mininet
from mininet.node import RemoteController, Controller, OVSSwitch, OVSController
from mininet.cli import CLI
from mininet.log import setLogLevel
import traceback
import sys



CustomController = None



# Setup
import Config
config = {
    'NODE_NUMBER_PER_SWITCH':Config.NODE_NUMBER_PER_SWITCH,
    'CONTROLLERS':Config.CONTROLLERS,
    'SWITCH_NUMBER':8,             # S1-S8
    'TOPO':Config.TOPO,
    'USE_TOPO':Config.USE_TOPO
}
setLogLevel( 'info' )  # for CLI output


def GenController(net,cfg):
    ctrl = net.addController(cfg['name'],port=cfg['port'], ip=cfg['ip'])
    return ctrl


def CubeLink(net,switches):
    connects = config['TOPO'][config['USE_TOPO']]
    for c in connects:
        print "***** Linking Switch "+ str(c[0]) + " and Switch " + str(c[1])
        net.addLink(switches[c[0]-1],switches[c[1]-1])


        

def gnet():
    net = Mininet( controller=CustomController, switch=OVSSwitch )
    C1 = None
    C2 = None
    switches = []
    Threshold = config['CONTROLLERS'][0]['sn']
    C1 = GenController(net, config['CONTROLLERS'][0])
    C2 = GenController(net, config['CONTROLLERS'][1])    
    
    
    print "*** Creating Switches and Hosts"
    for i in range(1,config['SWITCH_NUMBER']+1):        
        swchName = 'S'+str(i)
        print "***** Creating Switch: " + swchName
        s = net.addSwitch(swchName)
        switches.append(s)
        hosts = [ net.addHost((swchName +'_H%d') % n )
                  for n in
                  range(1,config['NODE_NUMBER_PER_SWITCH']+1) ]
        for h in hosts:
            net.addLink( s, h )

            
    print "*** Linking Switches in a cube manner"
    CubeLink(net,switches)
    
    print "*** Starting network"
    print "***** Starting Controller"
    net.build()
    C1.start()
    C2.start()


    print "***** Starting Switches"
    counter = 1
    for swch in switches:
        # if counter <= Threshold:
        swch.start([C1,C2])
        # else:
        # swch.start([C2])
        # counter+=1
                
    print "*** Testing network"
    # net.pingAll()
     
    print "*** Running CLI"
    CLI( net )

    print "*** Stopping network"
    net.stop()
        
    
    
    
if __name__ == '__main__':    
    try:
        if len(sys.argv) < 2:            
            CustomController = RemoteController
            gnet()
        elif sys.argv[1] == 'test':
            CustomController = Controller
            gnet()
    except Exception as err:
        print "=========================================="
        print err.args[0]
        print "=========================================="
        traceback.print_exc()
        
