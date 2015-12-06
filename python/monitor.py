from flask import Flask,request,Response, jsonify
import Config as config
import util
from collections import deque
Traffic_Data = {}
app = Flask(__name__)

global topo_inited, changing_topo
changing_topo = False
topo_inited = False

SWITCHES_ROLE = {}
Switch_traffic = {}
traffic_queue_ctrl1 = deque([], maxlen = config.MONITOR['CHECK_INTERVAL'] / config.CONTROLLER['STAT_SUBMIT_INTERVAL'])
traffic_queue_ctrl2 = deque([], maxlen = config.MONITOR['CHECK_INTERVAL'] / config.CONTROLLER['STAT_SUBMIT_INTERVAL'])


@app.route("/")
def hello():
    return "This is the Monitor Node!"


@app.route(config.MONITOR['METHODS']['STAT'][0], methods=[config.MONITOR['METHODS']['STAT'][1]])
def stat():
    statDict = request.get_json()
    # format of statDict:
    # {u'ip': u'http://127.0.0.1:8080', u'traffic': {u'1': 9, u'3': 9, u'2': 9}}

    # copy traffic info from statDict to two deque

    if statDict['ip'] == config.SWITCHES.keys()[0]:
        # controller 1
        traffic_queue_ctrl1.append(statDict['traffic'])
    elif statDict['ip'] == config.SWITCHES.keys()[1]:
        # controller 2
        traffic_queue_ctrl2.append(statDict['traffic'])
    
    return jsonify(**{'success':True})




@app.route(config.MONITOR['METHODS']['FINISH_MIGRATION'][0], methods=[config.MONITOR['METHODS']['FINISH_MIGRATION'][1]])
def change_topo():
    content = request.get_json(silent=True)
    global changing_topo

    # after migration, update the Topology here
    source_ctrl = content['sourceController']
    dest_ctrl = content['targetController']
    switch_id = content['targetSwitch']
    if SWITCHES_ROLE[source_ctrl][int(switch_id)] == 's':
        SWITCHES_ROLE[dest_ctrl][int(switch_id)] = 'm'
    elif SWITCHES_ROLE[source_ctrl][int(switch_id)] == 'm':
        SWITCHES_ROLE[dest_ctrl][int(switch_id)] = 's'


@app.route(config.MONITOR['METHODS']['TOPO_REPORT'][0],methods=[config.MONITOR['METHODS']['TOPO_REPORT'][1]])
def gen_topo():
    global topo_inited, Switch_traffic
    content = request.get_json(silent=True)

    Switch_traffic = {}

    Traffic_Data[content['ctrl']] = [{
        'switch_id':id,
        'traffic':{} ## TODO:
        ## Design the traffic structure
    }  for id in content['switches']]


    if len(Traffic_Data) == len(config.CONTROLLERS):
        for key in Traffic_Data:
            SWITCHES_ROLE[key] = config.SWITCHES[key]
            util.Http_Request(key + config.CONTROLLER['METHODS']['INIT_ROLE'][0],config.SWITCHES[key])
            
        topo_inited = True
        print "Topology Inited"
        
    return jsonify(**{
        'success':True
    })



def monitor():
    global topo_inited, changing_topo
    print "this is the monitor"
    # print "This is the monitor thread"
    if topo_inited and not changing_topo:
        # Implement the monitoring algorithm here, and notify controller use util.HTTP_Request
        # {controller_ip: {switch_id: number,},}
        sum1 = 0
        sum2 = 0

        controller_ip_1 = config.SWITCHES.keys()[0]
        controller_ip_2 = config.SWITCHES.keys()[1]
        # calculate the traffic sum for two controllers
        controller_traffic_1 = {}
        controller_traffic_2 = {}

        for i in range(0, len(traffic_queue_ctrl1)):
            for key in traffic_queue_ctrl1[i]:
                if controller_traffic_1.has_key(key):
                    controller_traffic_1[key] += traffic_queue_ctrl1[i][key]
                else:
                    controller_traffic_1[key] = traffic_queue_ctrl1[i][key]
        
        for i in range(0, len(traffic_queue_ctrl2)):
            for key in traffic_queue_ctrl2[i]:
                if controller_traffic_2.has_key(key):
                    controller_traffic_2[key] += traffic_queue_ctrl2[i][key]
                else:
                    controller_traffic_2[key] = traffic_queue_ctrl2[i][key]

        for key in controller_traffic_1:
            sum1 += controller_traffic_1[key]
        for key in controller_traffic_2:
            sum2 += controller_traffic_2[key]
        
        delta = abs(sum1 - sum2)
        nearest_switch_id = ''
        minimum = 9999
        if sum1 > sum2 * 1.5:
            for key in controller_traffic_1:
                distance = abs(controller_traffic_1[key] - delta/2)
                if distance < minimum:
                    nearest_switch_id = key
                    minimum = distance
            obj = {
                'source' : controller_ip_1,
                'dest' : controller_ip_2,
                'switch' : nearest_switch_id
            }
            print obj
            util.Http_Request(controller_ip_1 + config.CONTROLLER['METHODS']['START_MIGRATION'][0], obj)
            changing_topo = True

        elif sum2 > sum1 * 1.5:
            for key in controller_traffic_2:
                distance = abs(controller_traffic_2[key] - delta/2)
                if distance < minimum:
                    nearest_switch_id = key
                    minimum = distance
            obj = {
                'source' : controller_ip_2,
                'dest' : controller_ip_1,
                'switch' : nearest_switch_id
            }
            print obj
            util.Http_Request(controller_ip_2 + config.CONTROLLER['METHODS']['START_MIGRATION'][0], obj)
            changing_topo = True
            # for testing
            # topo_inited = False
        
    else:
        # if the topology is not inited, then do nothing
        pass


# MAIN
# gen_topo()
# util.Set_Interval(monitor,config.MONITOR['CHECK_INTERVAL'])
app.run(host='0.0.0.0', port=config.MONITOR['PORT'])
