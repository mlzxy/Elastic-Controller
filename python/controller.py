from webob import Response
import Config as config
import ryu



import util
import json
import logging
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from datetime import datetime


from ryu import cfg
CONF = cfg.CONF
CONTROLLER_ADDR = 'http://127.0.0.1:' + str(CONF['wsapi_port'])

# import pdb
# pdb.set_trace()

def http_send_stat(x):
    return util.Http_Request('http:127.0.0.1:'+config.MONITOR['PORT']+config.MONITOR['METHODS']['STAT'][0],x)
    


class OurController(app_manager.RyuApp):

    _CONTEXTS = { 'wsgi': WSGIApplication }
    def __init__(self, *args, **kwargs):
        super(OurController, self).__init__(*args, **kwargs)
        wsgi = kwargs['wsgi']
        wsgi.register(OurServer, {'controller' : self})

        # submit results
        self.stat = {
            'from':util.Now_Str(),
            'ip':CONTROLLER_ADDR,
            'data':[]
        };
        
        
        util.Set_Interval(self.submit_stat,config.CONTROLLER['STAT_SUBMIT_INTERVAL']);

    def submit_stat(self):
        self.stat['to'] = util.Now_Str()
        data_to_send = self.stat.copy()    
        self.stat['from'] = util.Now_Str()
        self.stat['data'] = []        
        res = http_send_stat(data_to_send)
        # submit the result
        
    def collect_stat(self,ev):
        # TODO:
        # Collect the temporary stat
        pass
        

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser        
        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
        
        self.collect_stat(ev)
        
        out = ofp_parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port,
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
        

    @route('OurController', config.CONTROLLER['METHODS']['START_MIGRATION'][0], methods=[config.CONTROLLER['METHODS']['START_MIGRATION'][1]])
    def start_migrate(self, req, **kwargs):
        # TODO:
        # Start Migrating                
        return Response(content_type='text/plain', body='helloworld')

        



    
