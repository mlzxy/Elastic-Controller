from flask import Flask,request,Response, jsonify
import Config as config
import util
Traffic_Data = {}
app = Flask(__name__)

global topo_inited, changing_topo
changing_topo = False
topo_inited = False

SWITCHES_ROLE = {}
Switch_traffic = {}

@app.route("/")
def hello():
    return "This is the Monitor Node!"


@app.route(config.MONITOR['METHODS']['STAT'][0], methods=[config.MONITOR['METHODS']['STAT'][1]])
def stat():
    # Switch_traffic = [0] * len(config.)
    statDict = request.get_json()
    # TODO:    
    # argment the Traffic_Data here
    # print "******"
    # print statDict
    # print "******"
    # format of statDict:
    # {u'ip': u'http://127.0.0.1:8080', u'traffic': {u'1': 9, u'3': 9, u'2': 9}}

    # copy traffic info from statDict to Switch_traffic
    # format of Switch_traffic:
    # {controller_ip: {switch_id: number,},}
    #if len(Switch_traffic) == len(config.CONTROLLERS):
    #    Switch_traffic = {}
    Switch_traffic[statDict['ip']] = statDict['traffic']


    return jsonify(**{
        'success':True
    })
    



@app.route(config.MONITOR['METHODS']['FINISH_MIGRATION'][0], methods=[config.MONITOR['METHODS']['FINISH_MIGRATION'][1]])
def change_topo():
    content = request.get_json(silent=True)
    global changing_topo
    changing_topo = False
    # TODO:
    # after migration, update the Topology here
    # source controller, destination controler, switch id
    # SWITCHES_ROLE[source_ctrl][switch_id] = 's' ? 'm' : 's'
    # SWITCHES_ROLE[destination_ctrl][switch_id] = 's' ? 'm' : 's'
    print content, type(content)



@app.route(config.MONITOR['METHODS']['TOPO_REPORT'][0],methods=[config.MONITOR['METHODS']['TOPO_REPORT'][1]])
def gen_topo():
    global topo_inited, Switch_traffic
    # print "TOPO_REPORT"
    content = request.get_json(silent=True)

    # format of Switch_traffic:
    # Switch_traffic = {controller_ip: {switch_id: in package number},}
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
    ctrls = Switch_traffic.keys()   
    # print "In the Monitor, Switch_Traffic",Switch_traffic
    if topo_inited and len(ctrls) == len(config.CONTROLLERS) and not changing_topo:
        # TODO:
        # Implement the monitoring algorithm here, and notify controller use util.HTTP_Request
        # {controller_ip: {switch_id: number,},}
        sum1 = 0
        sum2 = 0
        # print Switch_traffic


        controller_ip_1 = ctrls[0]
        controller_ip_2 = ctrls[1]
        for key in Switch_traffic[controller_ip_1]:
            sum1 += Switch_traffic[controller_ip_1][key]
        for key in Switch_traffic[controller_ip_2]:
            sum2 += Switch_traffic[controller_ip_2][key]

        delta = abs(sum1 - sum2)
        if sum1 > sum2:
            source_ctrl_ip = controller_ip_1
            dest_ctrl_ip = controller_ip_2
            smaller = sum2
        else:
            source_ctrl_ip = controller_ip_2
            dest_ctrl_ip = controller_ip_1
            smaller = sum1

        if (delta + 0.0) / smaller > -0.5:        
            # migrate
            nearest_switch_id = ''
            minimum = 9999
            for key in Switch_traffic[source_ctrl_ip]:
                distance = abs(Switch_traffic[source_ctrl_ip][key] - delta / 2)
                if minimum > distance:
                    nearest_switch_id = key
                    minimum = distance
            # start migration
            obj = {
                'source':source_ctrl_ip,
                'dest':dest_ctrl_ip,
                'switch':nearest_switch_id
            }
            print 'migrating: ',obj
            util.Http_Request(source_ctrl_ip + config.CONTROLLER['METHODS']['START_MIGRATION'][0], obj)
            changing_topo = True
            # for testing
            # topo_inited = False
        
    else:
        # if the topology is not inited, then do nothing
        pass







# MAIN
# gen_topo()
util.Set_Interval(monitor,config.MONITOR['CHECK_INTERVAL'] * 2)
app.run(host='0.0.0.0', port=config.MONITOR['PORT'])
