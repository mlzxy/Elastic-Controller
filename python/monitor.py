from flask import Flask,request,Response, jsonify
import Config as config
import util
Traffic_Data = {}
app = Flask(__name__)


global topo_inited
topo_inited = False

@app.route("/")
def hello():
    return "This is the Monitor Node!"


@app.route(config.MONITOR['METHODS']['STAT'][0], methods=[config.MONITOR['METHODS']['STAT'][1]])
def stat():    
    statDict = request.get_json()
    # TODO:    
    # argment the Traffic_Data here

    return jsonify(**{
        'success':True
    })

    



@app.route(config.MONITOR['METHODS']['FINISH_MIGRATION'][0], methods=[config.MONITOR['METHODS']['FINISH_MIGRATION'][1]])
def change_topo():
    content = request.get_json(silent=True)
    # TODO:
    # update the Topology here

    print content, type(content)



@app.route(config.MONITOR['METHODS']['TOPO_REPORT'][0],methods=[config.MONITOR['METHODS']['TOPO_REPORT'][1]])
def gen_topo():
    global topo_inited
    # print "TOPO_REPORT"
    content = request.get_json(silent=True)
    # print content
    Traffic_Data[content['ctrl']] = [{
        'switch_id':id,
        'traffic':{} ## TODO:
        ## Design the traffic structure
    }  for id in content['switches']]

    if len(Traffic_Data) == len(config.CONTROLLERS):
        for key in Traffic_Data:            
            util.Http_Request(key + config.CONTROLLER['METHODS']['INIT_ROLE'][0],config.SWITCHES[key])
            
        topo_inited = True
        print "Topology Inited"
        
    return jsonify(**{
        'success':True
    })



def monitor():
    # print "This is the monitor thread"
    if topo_inited:
        # TODO:
        # Implement the monitoring algorithm here, and notify controller use util.HTTP_Request
        pass
    else:
        # if the topology is not inited, then do nothing
        pass







# MAIN
# gen_topo()
util.Set_Interval(monitor,config.MONITOR['CHECK_INTERVAL'])
app.run(host='0.0.0.0', port=config.MONITOR['PORT'])
