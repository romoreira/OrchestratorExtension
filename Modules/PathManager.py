'''
Created on Aug 6, 2018

@author: rodrigo
'''

#Class imports - QoS Enforcement Rest API
from flask import Flask, request, abort
from flask_restful import Api, Resource, reqparse
import threading
import json
import requests
import re

from ryu.base import app_manager
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link, get_host
from ryu.controller import dpset
from wheel import paths


#class Flow(ControllerBase):
#    
#    _CONTEXTS = {
#        'dpset': dpset.DPSet
#    }
#    
#    def __init__(self, *args, **kwargs):
#        super(Flow, self).__init__(*args, **kwargs)
#        self.dpset = ['dpset']
#        print("Construtor")

#    def _my_handler(self):
#        dpid = 1
#        dp = self.dpset.get(dpid)
#        if dp is None:
#            print("No SUCH DATAPATH WITH ITS ID")
    
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
        '''
        Given QoS Mechanism Status - BAM, RDM and Others
        '''
        return json.dumps({QoS.BANDWIDTH_SCHEME: QoS.QoS_ENABLED}, sort_keys=True, indent=4)


    @app.route("/qos/switch_ip/<string:find_dpid>",methods=['GET'])
    def get_switch_ip(self,find_dpid):
        '''
        Search switch <IP> by considering <dpid>
        '''
        
        #Raise an error if URL parameter is null
        if find_dpid is None:
            return json.dumps({"":""},sort_keys=True, indent=4)
        
        #Create LSP object to retrieve swtiches
        lsp = LSP("","","","")
        switch_list = lsp.get_switches()
        switch_ip = ""
        for switch in switch_list:
            if str(find_dpid) == str(switch.dp.id):
                switch_ip = switch.dp.address
                break

        #Return JSON null if there are no switch with same given <dpid>           
        if str(switch_ip) is None:
            return json.dumps({"":""},sort_keys=True, indent=4)
        
        #Return JSON with <dpid> and <ip>
        return json.dumps({find_dpid: switch_ip})
        
    @app.route("/qos/apply",methods=['POST'])
    def apply_qos():
        '''
        Performs Bandwidth reservation by considering end-to-end Path of Two Hosts - POST content is JSON data
        '''
        
        #Perform verifications before create QoS PATH
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
                
        #Create LSP to perform QoS policies
        lsp = LSP(ip_src, ip_dst, required_bandwidth, reservation_mode)
        return json.dumps({"":lsp.perform_qos()}),501

class PATH(app_manager.RyuApp):
    
    def __init__(self, ingress, egress, dpid):
        self.ingress = ingress
        self.egress = egress
        self.dpid = dpid
        
class LSP(app_manager.RyuApp):
    
    '''
    Label-Switched Path (LSP) - Specifies the <Path> with QoS metrics
    '''
      
    PATHS = []   
        
    def __init__(self, ip_src, ip_dst, required_bandwidth, reservation_mode):
        '''
        Constructor
        '''
        print("Label-Switched Path (LSP) - Constructor - Multiple Parameters")
        super(LSP, self).__init__()
        self.ip_src = ip_src
        self.ip_dst = ip_dst
        self.required_bandwidth = required_bandwidth
        self.reservation_mode = reservation_mode
    
    def update_topology(self):
        '''
        If eventually raises some events the topology information should be updated
        '''
        print("Topologia Deve Ser atualizada")
        
    
    def get_switches(self):
        '''
        Function to get <switch> lis from RYU core - It is necessary because this object can belongs to the context 
        '''
        return get_switch(self, None)
    
    def get_topology(self):
        '''
        This function brings the links of current topology
        '''
        
        switch_list = self.get_switches()
        switches = [switch.dp.id for switch in switch_list]
        
        #for switch in switch_list:
        #    print("SWITCH IP: "+str(switch.dp.address))
        
        links_list = get_link(self, None)
        links = [[link.src.dpid,link.dst.dpid,link.src.port_no] for link in links_list]
        host_list = get_host(self, None)
        hosts = [host.port.name for host in host_list]
        return links
    
    def walk_on_flows(self,dpid, src_host_mac, dst_host_mac, src_interface_sw_mac, dst_interface_sw_mac):
        
        #print("PROCURANDO EM: "+str(dpid) + " HOST-A: " + str(src_host_mac) + " HOST-B: " + str(dst_host_mac) + " HOSTA-A NA INTERFACE: " + str(src_interface_sw_mac) + " HOST-B NA INTERFACE: " + str(dst_interface_sw_mac))
        
        rest_link = 'http://10.0.0.100:8080/stats/flow/'
        rest_link = rest_link + str(dpid)
        flows = requests.get(rest_link)
        flows = flows.json()
        flows = str(flows).replace("'",'"')
        flows = json.loads(flows)
        
        for flow in flows[str(dpid)]:
            per_flow = flow['match']
            #print("PER FLOW: "+str(per_flow))
            if len(per_flow) > 2:
                
                #Verifica que sossui Flow Match no dpid atual
                if per_flow['dl_src'] == src_host_mac and per_flow['dl_dst'] == dst_host_mac:
                    
                    #PEGO O NUMERO DA INTERFACE QUE O FLOW MANDA SEGUIR
                    #print("IR PARA A PROXIMA ENTIDADE QUE TA NA PORTA: "+str(flow['actions']))
                    destination_port_number = str(flow['actions'])
                    destination_port_number = re.findall("\d+", destination_port_number)[0]
                    #print("IR PARA ->: "+str(destination_port_number))
                    
                    #CHAMADA DOS DESCRITORES DE PORTA DE CADA SWITCH
                    rest_link = 'http://10.0.0.100:8080/stats/portdesc/'
                    rest_link = rest_link + str(dpid)
                    port_desc = requests.get(rest_link)
                    port_desc = port_desc.json()
                    port_desc = str(port_desc).replace("'",'"')
                    port_desc = json.loads(port_desc)
                    
                    #PEGAR O MAC DA INTERFACE QUE O FLOW MANDA SEGUIR
                    for x in port_desc[str(dpid)]:
                        if str(x['port_no']) == destination_port_number:
                            destination_port_name = str(x['hw_addr'])
                            break;
                    
                    #print("FLOW MANDA SEGUIR PARA ESSA INTERFACE. MAC: "+str(destination_port_name))
                    
                    
                    #O DESTINO ESTA NO PROPRIO SWITCH?
                    for x in port_desc[str(dpid)]:
                        #print(" O DESTINO ESTA NO PROPRIO SWTICH? ")
                        destination_port_name = str(x['hw_addr'])
                        if destination_port_name == dst_interface_sw_mac:
                            #print("SIM O DESTINO ESTA NO SWITCH o/ o/")
                            path = PATH(src_interface_sw_mac,destination_port_name,dpid)
                            self.PATHS.append(path)
                            #ENCOUNTROU A INTERFACE DO SW DE ULTIMO SALTO PARA O DESTINO
                            return
                    
                    #PEGAR DOS LINKS O PROXIMO DATAPATH QUE A INTERFACE DA REGRA MANDA SEGUIR
                    #print("NAO O DESTINO FINAL NAO ESTA NESSE SWITCH")
                    #print("CONSIDERANDO A TOPOLOGIA: "+str(self.get_topology()))
                    links = self.get_topology()
                    i = 0
                    while i < len(links):
                        #print("ONDE ESTOU dpid: "+str(links[i][0]) + " ONDE DEVERIA ESTAR: "+str(dpid) + " IR PARA "+str(links[i][2]) + " POIS: " + str(destination_port_number))
                        if str(links[i][0]) == dpid and str(links[i][2]) == destination_port_number:
                            #print("DEVO SAIR PELA: " + str(links[i][2]))
                            path = PATH(src_interface_sw_mac,destination_port_name,dpid)
                            self.PATHS.append(path)
                            self.walk_on_flows(links[i][1], src_host_mac, dst_host_mac, src_interface_sw_mac, dst_interface_sw_mac)
                            return
                        i = i + 1
                    
                #Nao possui flow match no dpid atual e outros flows mandaram o buscador pra ca, portando o caminho nao existe
                else:
                    print("Destination Unreachable - <Host-B> from <Host-A>")
                    return
                
                
    def perform_qos(self):
        
        print("Reserving Bandwidth")
        switch_list = get_switch(self, None)
        host_list = get_host(self, None)
        
        if len(host_list) == 0:
            print("Topology has not any Hosts")
            return 501,"Topology has not any Hosts"
                        
        #Source Information
        for host in host_list:
            print(host.ipv4[0])
            if host.ipv4[0] == self.ip_src:
                switch_src = host.port.hw_addr #MAC of conected Switch
                port_src_no = host.port.port_no #PORT Number of connected Host on Switch
                port_src_name = host.port.name #PORT Name of connected Host on Switch
                port_src_name = re.findall('''(?<=')\s*[^']+?\s*(?=')''', str(port_src_name))
        
        #Destination Information
        for host in host_list:
            if host.ipv4[0] == self.ip_dst:
                switch_dst = host.port.hw_addr
                port_dst_no = host.port.port_no
                port_dst_name = host.port.name
                port_dst_name = re.findall('''(?<=')\s*[^']+?\s*(?=')''', str(port_dst_name))
       
        
        
        print("SRC - NOME DA PORTA DO SWITCH QUE O HOST SRC TA CONECTADO: "+str(port_src_name[0]))
        print("SRC - NUMERO DA PORTA QUE O SRC TA CONECTADO: " + str(port_src_no))
        print("SRC - MAC DO PORTA DO SWITCH QUE O HOST TA CONECTADO: " + str(switch_src))
        
        
        print("DST - NOME DA PORTA DO SWITCH QUE O HOST DST TA CONECTADO: "+str(port_dst_name[0]))
        print("DST - NUMERO DA PORTA QUE O DST TA CONECTADO: " + str(port_dst_no))
        print("DST - MAC DO PORTA DO SWITCH QUE O HOST DST TA CONECTADO: " + str(switch_dst))
        
        
        #PROCURE O DPID QUE O HOST ESTA CONECTADO
        find = False
        sw_list = requests.get('http://10.0.0.100:8080/stats/switches')
        sw_list = sw_list.json()
        for switch in sw_list:
            rest_link = 'http://10.0.0.100:8080/stats/portdesc/'
            rest_link = rest_link + str(switch)
            port_desc = requests.get(rest_link)
            port_desc = port_desc.json()
            port_desc = str(port_desc).replace("'",'"')
            port_desc = json.loads(str(port_desc))
            find_dpid = ""
            for key,value in port_desc.items():
                for i in range(len(value)):
                    hw_addr = value[i]['hw_addr']
                    hw_addr = str(hw_addr)
                    if hw_addr == switch_src:
                        find = True
                        find_dpid = str(key)
                        break
                if find == True:
                    break
            if find == True:
                break
        
        #SRC - NOME DA PORTA DO SWITCH QUE O HOST SRC TA CONECTADO: vnet0
        #SRC - NUMERO DA PORTA QUE O SRC TA CONECTADO: 2
        #SRC - MAC DO PORTA DO SWITCH QUE O HOST TA CONECTADO: a6:c0:32:2b:89:b1
        #DST - NOME DA PORTA DO SWITCH QUE O HOST DST TA CONECTADO: enp2s4
        #DST - NUMERO DA PORTA QUE O DST TA CONECTADO: 2
        #DST - MAC DO PORTA DO SWITCH QUE O HOST DST TA CONECTADO: 00:e0:7d:db:18:d4
        
        print("DATAPATH ID QUE O HOST SOURCE ESTA CONECTADO: "+ find_dpid)
        self.walk_on_flows(find_dpid, "08:00:27:2c:5c:ff", "08:00:27:0f:df:de",switch_src,switch_dst)
        for path in self.PATHS:
            print("HOST-A VINDO DE: " + str(path.dpid) + " INGRESS: " + str(path.ingress) + " EGRESS: " + str(path.egress))
        
        #By considering path list, make OVS QoS command to each Ingress and Egress port
            
        return "QoS Path Created",201
    