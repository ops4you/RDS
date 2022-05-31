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

hport_table = {"10.0.1.1": 1,
             "10.0.1.2": 1,
             "10.0.1.3": 1,
             "10.0.2.1": 2,
             "10.0.2.2": 2,
             "10.0.2.3": 2,
             "10.0.3.1": 3,
             "10.0.3.2": 3,
             "10.0.3.3": 3
             }

rport_table = { "10.0.1.254" : 1, "10.0.2.254" : 2 , "10.0.3.254" : 3}

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.L3SwitchMACs = {}
        self.ip_to_port = {}
        

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
        self.send_port_desc_stats_request(datapath)

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
        
    def arp_reply(self, datapath, eth, a, in_port):
        r = hport_table.get(a.src_ip)
        r1 = hport_table.get(a.dst_ip)
        r21 = rport_table.get(a.dst_ip)
        r22 = self.L3SwitchMACs.get(r21)
        if r:
            arp_resp = packet.Packet()
            arp_resp.add_protocol(ethernet.ethernet(ethertype=eth.ethertype,
                                  dst=eth.src, src=r22))
            arp_resp.add_protocol(arp.arp(opcode=arp.ARP_REPLY,
                                  src_mac=r22, src_ip=a.dst_ip,
                                  dst_mac=a.src_mac,
                                  dst_ip=a.src_ip))
                                  
            arp_resp.serialize()
            actions = []
            actions.append(datapath.ofproto_parser.OFPActionOutput(in_port))
            parser = datapath.ofproto_parser  
            ofproto = datapath.ofproto
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=arp_resp)
            datapath.send_msg(out)
        elif (a.dst_ip not in self.ip_to_port):
            self.ip_to_port.update({a.dst_ip : r1})
            arp_resp = packet.Packet()
            arp_resp.add_protocol(ethernet.ethernet(ethertype=eth.ethertype,
                                  dst=eth.src, src=r1))
            arp_resp.add_protocol(arp.arp(opcode=arp.ARP_REPLY,
                                  src_mac=r1, src_ip=a.dst_ip,
                                  dst_mac=a.src_mac,
                                  dst_ip=a.src_ip))
                                  
            arp_resp.serialize()
            actions = []
            actions.append(datapath.ofproto_parser.OFPActionOutput(in_port))
            parser = datapath.ofproto_parser  
            ofproto = datapath.ofproto
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=arp_resp)
            datapath.send_msg(out)
    
    def get_key_from_value(self, d, val):
           keys = [k for k, v in d.items() if v == val]
           if keys:
             return keys[0]
           return None

    def arp_request(self, datapath, eth, ic, in_port):
        if (ic.dst not in self.ip_to_port):
         r = hport_table.get(ic.dst) 
         r2 = self.get_key_from_value(rport_table, r)
         r3 = self.L3SwitchMACs.get(r)

        
         self.logger.info("Requested MAC %s ", r)
         arp_req = packet.Packet()
         arp_req.add_protocol(ethernet.ethernet(ethertype=ether_types.ETH_TYPE_ARP,
                                  dst="ff:ff:ff:ff:ff:ff", src=r3))
         arp_req.add_protocol(arp.arp(opcode=arp.ARP_REQUEST,
                                  src_mac=r3, src_ip=r2,
                                  dst_mac="ff:ff:ff:ff:ff:ff",
                                  dst_ip=ic.dst))
                                  
         arp_req.serialize()
         actions = []
         actions.append(datapath.ofproto_parser.OFPActionOutput(in_port))
         parser = datapath.ofproto_parser  
         ofproto = datapath.ofproto
         out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=arp_req)
         datapath.send_msg(out)
    
    def send_port_desc_stats_request(self, datapath):
       ofp_parser = datapath.ofproto_parser

       req = ofp_parser.OFPPortDescStatsRequest(datapath, 0)
       datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
       for p in ev.msg.body:
            self.L3SwitchMACs.update({p.port_no : p.hw_addr})
       print(self.L3SwitchMACs)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        if eth.ethertype == ether_types.ETH_TYPE_IPV6:
            # ignore ipv6
            return

        dst = eth.dst
        src = eth.src

        dpid = format(datapath.id, "d").zfill(16)
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port
        
        # Check whether is it arp packet
        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            self.logger.info("Received ARP Packet %s %s %s ", dpid, src, dst)
            a = pkt.get_protocol(arp.arp)
            self.arp_reply(datapath, eth, a, in_port)
            return

        
        self.logger.info("Received ICMP Packet %s %s %s ", dpid, src, dst)
        ic = pkt.get_protocol(ipv4.ipv4)
        if ic != None:
         self.arp_request(datapath, eth, ic, in_port)   

        print("aa")
        print(self.ip_to_port)

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD
        

        actions = [parser.OFPActionOutput(out_port)]

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

