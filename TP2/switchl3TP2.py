# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import threading
import time
import code
from pickletools import markobject
from requests import request
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4
from ryu.lib.packet import in_proto
from ryu.lib.packet import icmp 
from ryu.lib.packet import tcp  
from ryu.lib.packet import udp
from ryu.lib.packet import arp
from ryu.ofproto import ether

hport_table = {  "10.0.1.1": 1,
                 "10.0.1.2": 1,
                 "10.0.1.3": 1,
                 "10.0.2.1": 2,
                 "10.0.2.2": 2,
                 "10.0.2.3": 2,
                 "10.0.3.1": 3,
                 "10.0.3.2": 3,
                 "10.0.3.3": 3}                          

gport_table = { 1: "10.0.1.254", 2: "10.0.2.254" , 3: "10.0.3.254"}

class Switchl3(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Switchl3, self).__init__(*args, **kwargs)
        self.router_ports = {}
        self.router_ports_state = {}
        self.ip_to_mac = {}
        self.message_queue = {}
        

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        
        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        match = parser.OFPMatch(eth_type = ether_types.ETH_TYPE_IPV6)
        actions = []
        self.add_flow(datapath, 1, match, actions)
        x = threading.Thread(target=self.send_port_desc_stats_request(datapath), args=(1,))
        x.start()
        time.sleep(1)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    def get_key_from_value(self, d, val):
           keys = [k for k, v in d.items() if v == val]
           if keys:
             return keys[0]
           return None    
        
    def arp_reply(self, datapath, dpid, eth_p, arp_p, in_port):
        
        mg = self.router_ports[dpid].get(1)
            
        arp_rep = packet.Packet()
        arp_rep.add_protocol(ethernet.ethernet(ethertype=eth_p.ethertype,
                                  dst=eth_p.src, src=mg))
        arp_rep.add_protocol(arp.arp(opcode=arp.ARP_REPLY,
                                  src_mac=mg, src_ip=arp_p.dst_ip,
                                  dst_mac=arp_p.src_mac,
                                  dst_ip=arp_p.src_ip))

        parser = datapath.ofproto_parser  
        ofproto = datapath.ofproto                         
        arp_rep.serialize()
        actions = [datapath.ofproto_parser.OFPActionOutput(in_port)]
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=arp_rep)
        datapath.send_msg(out)

        return

    def arp_request_network(self,datapath,dpid,ipv4_p):
        port2 = 2
        port3 = 3
        ip_source = gport_table.get(dpid)
        mac_source2 = self.router_ports[dpid].get(port2)
        mac_source3 = self.router_ports[dpid].get(port3)


        arp_req2 = packet.Packet()
        arp_req2.add_protocol(ethernet.ethernet(ethertype=ether.ETH_TYPE_ARP,
                                           dst='ff:ff:ff:ff:ff:ff',
                                           src=mac_source2))
        arp_req2.add_protocol(arp.arp(opcode=arp.ARP_REQUEST,
                                 src_mac=mac_source2,
                                 src_ip=ip_source,
                                 dst_mac='ff:ff:ff:ff:ff:ff',
                                 dst_ip=ipv4_p.dst))

        parser = datapath.ofproto_parser  
        ofproto = datapath.ofproto
        arp_req2.serialize()
        actions = [datapath.ofproto_parser.OFPActionOutput(port2)]
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=arp_req2.data)
        datapath.send_msg(out)

        arp_req3 = packet.Packet()
        arp_req3.add_protocol(ethernet.ethernet(ethertype=ether.ETH_TYPE_ARP,
                                           dst='ff:ff:ff:ff:ff:ff',
                                           src=mac_source3))
        arp_req3.add_protocol(arp.arp(opcode=arp.ARP_REQUEST,
                                 src_mac=mac_source3,
                                 src_ip=ip_source,
                                 dst_mac='ff:ff:ff:ff:ff:ff',
                                 dst_ip=ipv4_p.dst))

        parser = datapath.ofproto_parser  
        ofproto = datapath.ofproto
        arp_req3.serialize()
        actions = [datapath.ofproto_parser.OFPActionOutput(port3)]
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=arp_req3.data)
        datapath.send_msg(out)

    def arp_request(self,datapath,dpid,arp_p):
        ip_source = gport_table.get(dpid)
        mac_source = self.router_ports[dpid].get(1)


        arp_req = packet.Packet()
        arp_req.add_protocol(ethernet.ethernet(ethertype=ether.ETH_TYPE_ARP,
                                           dst='ff:ff:ff:ff:ff:ff',
                                           src=mac_source))
        arp_req.add_protocol(arp.arp(opcode=arp.ARP_REQUEST,
                                 src_mac=mac_source,
                                 src_ip=ip_source,
                                 dst_mac='ff:ff:ff:ff:ff:ff',
                                 dst_ip=arp_p.dst_ip))

        parser = datapath.ofproto_parser  
        ofproto = datapath.ofproto
        arp_req.serialize()
        actions = [datapath.ofproto_parser.OFPActionOutput(1)]
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=arp_req.data)
        datapath.send_msg(out)
        return


    def icmp_reply(self, datapath, dpid, eth_p, icmp_p, ipv4_p, in_port):
        
        if icmp_p.type != icmp.ICMP_ECHO_REQUEST:
            return

        gp = gport_table.get(dpid)
        mg = self.router_ports[dpid].get(1)

        self.logger.info("Requested ICMP in %s from %s", ipv4_p.dst,ipv4_p.src)

        icmp_rep = packet.Packet()
        icmp_rep.add_protocol(ethernet.ethernet(ethertype=eth_p.ethertype,
                                  dst=eth_p.src, src=mg))
        icmp_rep.add_protocol(ipv4.ipv4(proto=ipv4_p.proto,
                                  src=ipv4_p.dst,
                                  dst=ipv4_p.src))
        icmp_rep.add_protocol(icmp.icmp(type_=icmp.ICMP_ECHO_REPLY,
                                code=icmp.ICMP_ECHO_REPLY_CODE,
                                csum=0,
                                data=icmp_p.data))
        
        parser = datapath.ofproto_parser  
        ofproto = datapath.ofproto
        icmp_rep.serialize()
        actions = [datapath.ofproto_parser.OFPActionOutput(in_port)]
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=icmp_rep.data)
        datapath.send_msg(out)

        self.logger.info('Send ICMP reply to %s.', ipv4_p.src)

    def icmp_unreachable(self, datapath, dpid, eth_p, icmp_p, ipv4_p, in_port):

        
        icmp_data = icmp.dest_unreach()

        if icmp_p.type != icmp.ICMP_ECHO_REQUEST:
            return

        port = hport_table.get(ipv4_p.src)
        gateway = self.get_key_from_value(gport_table,port)
        mg = self.router_ports[dpid].get(gateway)

        icmp_unr = packet.Packet()
        icmp_unr.add_protocol(ethernet.ethernet(ethertype=eth_p.ethertype,
                                  dst=eth_p.src, src=mg))
        icmp_unr.add_protocol(ipv4.ipv4(proto=ipv4_p.proto,
                                  src=gateway,
                                  dst=ipv4_p.src))
        icmp_unr.add_protocol(icmp.icmp(type_=icmp.ICMP_DEST_UNREACH,
                                   code=1,
                                   csum=0,
                                   data=icmp_data))
        
        parser = datapath.ofproto_parser  
        ofproto = datapath.ofproto
        icmp_unr.serialize()
        actions = [datapath.ofproto_parser.OFPActionOutput(in_port)]
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=icmp_unr.data)
        datapath.send_msg(out)
    
    def send_port_desc_stats_request(self, datapath):
       ofp_parser = datapath.ofproto_parser

       req = ofp_parser.OFPPortDescStatsRequest(datapath, 0)
       datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
        dpid = ev.msg.datapath.id
        self.router_ports.setdefault(dpid, {})
        self.router_ports_state.setdefault(dpid, {})
        for p in ev.msg.body:
         if(p.port_no<50):
          self.router_ports[dpid].update({p.port_no : p.hw_addr})
          self.router_ports_state[dpid].update({p.port_no : p.state})
        print(self.router_ports)
        print(self.router_ports_state)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth_p = pkt.get_protocols(ethernet.ethernet)[0]

        if eth_p.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        if eth_p.ethertype == ether_types.ETH_TYPE_IPV6:
            # ignore ipv6
            return

        dst = eth_p.dst
        src = eth_p.src

        print(self.ip_to_mac)

        dpid = datapath.id
        
        # Check whether is it arp packet
        arp_p = pkt.get_protocol(arp.arp)

        if arp_p:
            if arp_p.dst_ip == gport_table.get(dpid) and arp_p.opcode == arp.ARP_REQUEST:
                self.ip_to_mac.setdefault(dpid, {})
                self.ip_to_mac[dpid].update({arp_p.src_ip : arp_p.src_mac})
                self.logger.info("Received ARP Packet %s %s %s ", dpid, src, dst)
                self.arp_reply(datapath,dpid, eth_p, arp_p, in_port)
            if arp_p.dst_ip in hport_table and arp_p.opcode == arp.ARP_REQUEST:
                self.logger.info("Received ARP broadcast Packet in router %s from %s to %s ", dpid, arp_p.src_ip , arp_p.dst_ip)
                self.arp_request(datapath,dpid,arp_p)
            elif arp_p.dst_ip == gport_table.get(dpid) and arp_p.opcode == arp.ARP_REPLY:
                self.ip_to_mac.setdefault(dpid, {})
                self.ip_to_mac[dpid].update({arp_p.src_ip : arp_p.src_mac})
                for m in self.message_queue[arp_p.src_ip]:      
                    p = packet.Packet(m.data)
                    p_eth = pkt.get_protocol(ethernet.ethernet)
                    out_port = 1
                    p_eth.src = self.router_ports[dpid].get(out_port)
                    p_eth.dst = self.ip_to_mac[dpid].get(arp_p.src_ip)
                    parser = datapath.ofproto_parser  
                    ofproto = datapath.ofproto
                    p.serialize()
                    actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
                    out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                    in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=p.data)
                    datapath.send_msg(out)
                return
            else:
                return    
                

        ipv4_p = pkt.get_protocol(ipv4.ipv4)

        if ipv4_p:
         if ipv4_p.dst == gport_table.get(dpid):
              icmp_p = pkt.get_protocol(icmp.icmp)
              if icmp_p:
                self.icmp_reply(datapath, dpid, eth_p, icmp_p, ipv4_p, in_port) 
                return
         else:
            if ipv4_p.dst in hport_table:
              self.ip_to_mac.setdefault(dpid,{})
              dpid_dst = hport_table.get(ipv4_p.dst)
              if ipv4_p.dst in self.ip_to_mac[dpid]:
                port = 1
                eth_p.src = self.router_ports[dpid].get(port)
                eth_p.dst = self.ip_to_mac[dpid].get(ipv4_p.dst)
                parser = datapath.ofproto_parser  
                ofproto = datapath.ofproto
                pkt.serialize()
                actions = [datapath.ofproto_parser.OFPActionOutput(port)]
                out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=pkt.data)
                datapath.send_msg(out)
                return  

              elif (ipv4_p.dst not in self.ip_to_mac[dpid]) and (dpid_dst in self.ip_to_mac) and (ipv4_p.dst in self.ip_to_mac[dpid_dst]):
                if (dpid == 1 and hport_table.get(ipv4_p.dst) == 2): 
                 port = 2
                 eth_p.src = self.router_ports[dpid].get(port)
                 eth_p.dst = self.router_ports[2].get(port)
                 parser = datapath.ofproto_parser  
                 ofproto = datapath.ofproto
                 pkt.serialize()
                 actions = [datapath.ofproto_parser.OFPActionOutput(port)]
                 out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=pkt.data)
                 datapath.send_msg(out)
                 return

                if (dpid == 2 and hport_table.get(ipv4_p.dst) == 1):
                 port = 2
                 eth_p.src = self.router_ports[dpid].get(port)
                 eth_p.dst = self.router_ports[1].get(port)
                 parser = datapath.ofproto_parser  
                 ofproto = datapath.ofproto
                 pkt.serialize()
                 actions = [datapath.ofproto_parser.OFPActionOutput(port)]
                 out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=pkt.data)
                 datapath.send_msg(out)   
                 return   

                if (dpid == 2 and hport_table.get(ipv4_p.dst) == 3): 
                 port = 3
                 eth_p.src = self.router_ports[dpid].get(port)
                 eth_p.dst = self.router_ports[3].get(port)
                 parser = datapath.ofproto_parser  
                 ofproto = datapath.ofproto
                 pkt.serialize()
                 actions = [datapath.ofproto_parser.OFPActionOutput(port)]
                 out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=pkt.data)
                 datapath.send_msg(out)
                 return

                if (dpid == 3 and hport_table.get(ipv4_p.dst) == 2):
                 port = 3
                 eth_p.src = self.router_ports[dpid].get(port)
                 eth_p.dst = self.router_ports[2].get(port)
                 parser = datapath.ofproto_parser  
                 ofproto = datapath.ofproto
                 pkt.serialize()
                 actions = [datapath.ofproto_parser.OFPActionOutput(port)]
                 out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=pkt.data)
                 datapath.send_msg(out)    
                 return

                if (dpid == 3 and hport_table.get(ipv4_p.dst) == 1):
                 port = 2
                 eth_p.src = self.router_ports[dpid].get(port)
                 eth_p.dst = self.router_ports[1].get(3)
                 parser = datapath.ofproto_parser  
                 ofproto = datapath.ofproto
                 pkt.serialize()
                 actions = [datapath.ofproto_parser.OFPActionOutput(port)]
                 out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=pkt.data)
                 datapath.send_msg(out) 
                 return

                if (dpid == 1 and hport_table.get(ipv4_p.dst) == 3):
                 port = 3
                 eth_p.src = self.router_ports[dpid].get(port)
                 eth_p.dst = self.router_ports[3].get(2)
                 parser = datapath.ofproto_parser  
                 ofproto = datapath.ofproto
                 pkt.serialize()
                 actions = [datapath.ofproto_parser.OFPActionOutput(port)]
                 out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=pkt.data)
                 datapath.send_msg(out) 
                 return

              else:
                #Send ARP Request
                self.message_queue.setdefault(ipv4_p.dst,[])
                self.message_queue[ipv4_p.dst].append(msg)
                self.arp_request_network(datapath,dpid,ipv4_p)
                return

        