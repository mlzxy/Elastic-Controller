from webob import Response
import Config as config
import ryu



import util
import json
import logging

from ryu.lib.mac import haddr_to_bin
from ryu import ofproto
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet, ether_types
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
# from attrdict import AttrDict
# from datetime import datetime


from ryu import cfg
CONF = cfg.CONF
CONTROLLER_ADDR = 'http://127.0.0.1:' + str(CONF['wsapi_port'])

import pdb
#

def http_send_stat(x):
    return util.Http_Request('http://127.0.0.1:'+str(config.MONITOR['PORT'])+str(config.MONITOR['METHODS']['STAT'][0]),x)

def http_send_switches_report(data):
    return util.Http_Request('http://127.0.0.1:'+str(config.MONITOR['PORT'])+config.MONITOR['METHODS']['TOPO_REPORT'][0],
                             {
                                 'ctrl':CONTROLLER_ADDR,
                                'switches':data
                             })

def respond_json(data):
    return Response(content_type='application/json', body=json.dumps(data))


# CONSTANT

Constant = {
    'Role':{
        'Equal':ofproto.ofproto_v1_3.OFPCR_ROLE_EQUAL,
        'Master':ofproto.ofproto_v1_3.OFPCR_ROLE_MASTER,
        'Slave':ofproto.ofproto_v1_3.OFPCR_ROLE_SLAVE
    }
}

def get_role(i):
    if i == "s":
        return Constant['Role']['Slave']
    elif i == "m":
        return Constant['Role']['Master']
    elif i == "e":
        return Constant['Role']['Equal']




class OurController(app_manager.RyuApp):

    _CONTEXTS = { 'wsgi': WSGIApplication }


    def __init__(self, *args, **kwargs):
        super(OurController, self).__init__(*args, **kwargs)
        wsgi = kwargs['wsgi']
        wsgi.register(OurServer, {'controller' : self})

        self.switches = {} # datapathId: datapathInstance
        self.switches_reported = False
        # submit results
        self.stat = {
            'from':util.Now_Str(),
            'ip':CONTROLLER_ADDR,
            'data':[]
        }
        # switch traffic: in-package number
        self.switch_traffic = {}
        self.mac_to_port = {}
        self.role_inited = False
        
        util.Set_Interval(self.submit_stat,config.CONTROLLER['STAT_SUBMIT_INTERVAL']);

    def send(self,dpid, opfmsg):
        self.switches[dpid].send_msg(opfmsg)

        
    def send_role_request(self, dpid, role):        
        datapath = self.switches[dpid]
        print "set role: " + str(role) + " for dpid " + str(dpid)
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser        
        req = ofp_parser.OFPRoleRequest(datapath, role, 0)
        datapath.send_msg(req)

    def init_role(self, arr):
        for i in range(0,8):            
            self.send_role_request(i+1,arr[i])
        self.role_inited = True
        
        
    def submit_stat(self):
        if(len(self.switches) < config.SWITCH_NUMBER):
            print "switch info has not been sent to controller yet!!"
            pass
        else:
            if self.role_inited:
                data_to_send = self.switch_traffic.copy()
                res = http_send_stat(data_to_send)
                self.switch_traffic = {}
                """
                self.stat['to'] = util.Now_Str()
                data_to_send = self.stat.copy()
                self.stat['from'] = util.Now_Str()
                self.stat['data'] = []
                res = http_send_stat(data_to_send)
                """
            else:
                #print "switch role is not assigned!!"
                #pass
                k = self.switches.keys()
               # print k
                http_send_switches_report(k)
               # result =  r.json()
               # self.switches_reported = result['success']
               # self.switches_reported = True


        # submit the result
        
    def collect_stat(self,ev):
        if(len(self.switches) < config.SWITCH_NUMBER):
            pass
            # don't know all the switch id, so don't collect data
        else:
            if self.role_inited:
                msg = ev.msg
                dp = msg.datapath
                dpid = dp.id
                if self.switch_traffic.has_key(dpid):
                    self.switch_traffic[dpid] = self.switch_traffic[dpid] + 1
                else:
                    self.switch_traffic[dpid] = 1
            else:
                # role not assigned, not neccessary to collect data
                pass

        
    def add_flow(self, datapath, in_port, dst, actions):
        ofproto = datapath.ofproto
        match = datapath.ofproto_parser.OFPMatch(
            in_port=in_port, dl_dst=haddr_to_bin(dst))

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)
        datapath.send_msg(mod)
        
    def get_actions(self,ev):
        # get a good action
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        pkt = packet.Packet(msg.data)
        dpid = dp.id;
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth.ethertype == ether_types.ETH_TYPE_LLDP: # ignore lldp packet     
            return
        dst = eth.dst
        src = eth.src        
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = msg.match['in_port']
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofp.OFPP_FLOOD
        actions = [ofp_parser.OFPActionOutput(out_port)]
        # if out_port != ofp.OFPP_FLOOD:
        #     self.add_flow(dp, msg.in_port, dst, actions)
        return actions
        
        
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp_parser = dp.ofproto_parser
        

        dpid = dp.id;
        if not self.switches.has_key(dpid):
            self.switches[dpid] = dp;
        
        self.collect_stat(ev)

        # get a good action
        actions = self.get_actions(ev)
        # if out_port != ofp.OFPP_FLOOD:
        #     self.add_flow(dp, msg.in_port, dst, actions)
        
        out = ofp_parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id, in_port=msg.match['in_port'],
            actions=actions)
        dp.send_msg(out)

        
        

    def migrate(self, *args, **kargs):        
        # TODO:
        # Migrating Logic
        pass



class OurServer(ControllerBase):    
    def __init__(self, req, link, data, **config):
        super(OurServer, self).__init__(req, link, data, **config)
        self.controller = data['controller']

    @route('OurController', config.CONTROLLER['METHODS']['INIT_ROLE'][0], methods=[config.CONTROLLER['METHODS']['INIT_ROLE'][1]])
    def init_role(self, req, **kwargs):
        # TODO:
        # print req.method,req.POST,kwargs
        
        self.controller.init_role([get_role(i)
                                   for i in req.json])
        
        return respond_json({'success':True})

        

        

    @route('OurController', config.CONTROLLER['METHODS']['START_MIGRATION'][0], methods=[config.CONTROLLER['METHODS']['START_MIGRATION'][1]])
    def start_migrate(self, req, **kwargs):
        # TODO:
        # Start Migrating                
        return Response(content_type='text/plain', body='helloworld')

        

    @route('OurController', config.CONTROLLER['METHODS']['MIGRATION_BEGIN'][0], methods=[config.CONTROLLER['METHODS']['MIGRATION_BEGIN'][1]])
    def migration_begin(self, req, **kwargs):
        # TODO
        return Response(content_type='text/plain', body='migration_begin')



    @route('OurController', config.CONTROLLER['METHODS']['MIGRATION_READY'][0], methods=[config.CONTROLLER['METHODS']['MIGRATION_READY'][1]])
    def migration_ready(self, req, **kwargs):
        # TODO
        return Response(content_type='text/plain', body='migration_ready')



    @route('OurController', config.CONTROLLER['METHODS']['MIGRATION_END'][0], methods=[config.CONTROLLER['METHODS']['MIGRATION_END'][1]])
    def migration_end(self, req, **kwargs):
        # TODO
        return Response(content_type='text/plain', body='migration_end')


#
# API
# req.json -> get json request
# util.Http_Request(url,json) -> send json request
# respond_json(json) -> reply a json


