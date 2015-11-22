from webob import Response
import Config as config
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

class OurController(app_manager.RyuApp):

    _CONTEXTS = { 'wsgi': WSGIApplication }
    def __init__(self, *args, **kwargs):
        super(OurController, self).__init__(*args, **kwargs)        
        wsgi = kwargs['wsgi']
        wsgi.register(OurServer, {'controller' : self})

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser        
        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
        
        # TODO:
        # Collect the temporary stat
        
        out = ofp_parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions)
        dp.send_msg(out)

    # TODO:
    # Migrating Logic
        


class OurServer(ControllerBase):    
    def __init__(self, req, link, data, **config):
        super(OurServer, self).__init__(req, link, data, **config)
        self.controller = data['controller']
        

    @route('OurController', config.CONTROLLER['METHODS']['START_MIGRATION'][0], methods=[config.CONTROLLER['METHODS']['START_MIGRATION'][1]])
    def helloworld(self, req, **kwargs):
        # TODO:
        # Start Migrating
        return Response(content_type='text/plain', body='helloworld')

        



    
