'''
Created on Aug 6, 2018

@author: rodrigo
'''

#Class imports - QoS Enforcement Rest API
from flask import Flask, request, abort
from flask_restful import Api, Resource, reqparse
import threading
import json

from ryu.base import app_manager
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link, get_host

class QoS(threading.Thread):

    app = Flask(__name__)
    app.config["DEBUG"] = True
    QoS_ENABLED = False
    BANDWIDTH_SCHEME = "MAM"
    LSP_LIST = []
     
    def __init__(self,thread_numbering,QoSModule):
        self.thread_numbering = thread_numbering
        threading.Thread.__init__(self)
   
    def run(self):
        print("QoS Listener is Running!")
        self.app.run(host='0.0.0.0', port=8081,debug=False)
    
    @app.route("/qos/status", methods=['GET'])
    def get_qos_status():
        return json.dumps({QoS.BANDWIDTH_SCHEME: QoS.QoS_ENABLED}, sort_keys=True, indent=4)
        
    @app.route("/qos/apply",methods=['POST'])
    def apply_qos():
        
        '''
        Performs JSON validation before apply QoS
        '''
        if not request.json or not 'ip_src' in request.json or not 'ip_dst' in request.json or not 'required_bandwidth' in request.json or not 'reservation_mode' in request.json:
            return json.dumps({'ip_src': "IP", 'ip_dst': "IP",'required_bandwidth': 10, 'reservation_mode': "MAM"}, sort_keys=True, indent=4)
            abort(400)
        else:
            ip_src = request.json['ip_src']
            ip_dst = request.json['ip_dst']
            required_bandwidth = request.json['required_bandwidth']
            reservation_mode = request.json['reservation_mode']
            
            try:
                required_bandwidth = float(required_bandwidth)
            except ValueError:
                return "Required Bandwidth should be in number format"
                abort(400)
            if isinstance(required_bandwidth, str) or required_bandwidth < 0:
                return "Required Bandwidth should be Zero or Positive Number"
                abort(400)
                
        '''
        Performs QoS enforcement to LSP 
        '''
        lsp = LSP(ip_src, ip_dst, required_bandwidth, reservation_mode)
        lsp.apply_qos()
        return str(request.json), 201
        
        
class LSP(app_manager.RyuApp):
    
    '''
    Label-Switched Path (LSP) - Specifies the <Path> with QoS metrics
    '''
        
    def __init__(self, ip_src, ip_dst, required_bandwidth, reservation_mode):
        '''
        Constructor
        '''
        print("Label-Switched Path (LSP) - Constructor - Multiple Parameters")
        super(LSP, self).__init__()
    
    def update_topology(self):
        print("Topologia Deve Ser atualizada")
        
        
    def get_topology(self):
        switch_list = get_switch(self, None)
        switches = [switch.dp.id for switch in switch_list]
        links_list = get_link(self, None)
        links = [(link.src.dpid,link.dst.dpid,{'port':link.src.port_no}) for link in links_list]
        host_list = get_host(self, None)
        print("HOSTS: "+ str(host_list))
        print(links)
        
    
    def apply_qos(self):
        print("Reserving Bandwidth")
        self.get_topology()
        
    