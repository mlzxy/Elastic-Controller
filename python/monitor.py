from flask import Flask,request,Response
import Config as config
import util
Traffic_Data = {}
Topology = {}
app = Flask(__name__)




@app.route("/")
def hello():
    return "This is the Monitor Node!"


@app.route(config.MONITOR['METHODS']['STAT'][0], methods=[config.MONITOR['METHODS']['STAT'][1]])
def stat():    
    statDict = request.get_json()
    # TODO:    
    # argment the Traffic_Data here

    return Response("1")
    
    



@app.route(config.MONITOR['METHODS']['FINISH_MIGRATION'][0], methods=[config.MONITOR['METHODS']['FINISH_MIGRATION'][1]])
def change_topo():
    content = request.get_json(silent=True)
    # TODO:
    # update the Topology here

    print content, type(content)



topo_inited = False
@app.route(config.MONITOR['METHODS']['TOPO_REPORT'][0],methods=config.MONITOR['METHODS']['TOPO_REPORT'][1])
def gen_topo():
    # TODO:
    # generate initial topology from config information
    pass



def monitor():
    print "This is the monitor thread"
    if topo_inited:
        # TODO:
        # Implement the monitoring algorithm here, and notify controller use util.HTTP_Request
        pass
    else:
        # if the topology is not inited, then do nothing
        pass







# MAIN
gen_topo()
util.Set_Interval(monitor,config.MONITOR['CHECK_INTERVAL'])
app.run(host='0.0.0.0', port=config.MONITOR['PORT'])
