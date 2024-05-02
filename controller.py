import time

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import (CONFIG_DISPATCHER, MAIN_DISPATCHER,
                                    set_ev_cls)
from ryu.lib import hub
from ryu.lib.packet import arp, ether_types, ethernet, ipv4, packet
from ryu.ofproto import ofproto_v1_3

import csv_utils
from svm import SVM

APP_TYPE = 1    #set 0 data collection for test and train,set to 1 ddos detection

TEST_TYPE = 0   #0  normal traffic, 1 attack traffic  #TEST_TYPE is used only for data collection

PREVENTION = 0  # ddos prevention

INTERVAL = 2    #data collection time interval in seconds

gflows = []

old_ssip_len = 0
previousFlowCount = 0

FLOW_SERIAL_NO = 0
iteration = 0

def getFlowNumber():
    global FLOW_SERIAL_NO
    FLOW_SERIAL_NO = FLOW_SERIAL_NO + 1
    return FLOW_SERIAL_NO

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.flow_thread = hub.spawn(self._flow_monitor)
        self.datapaths = {}
        self.mitigation = 0
        self.svmobj = None
        self.arpIpToPort = {}

        if APP_TYPE == 1:
            self.svmobj = SVM()

    def _flow_monitor(self):
        #inital delay
        hub.sleep(5)
        while True:
            for dp in self.datapaths.values():
                self.requestFlowMetrics(dp)
            hub.sleep(INTERVAL)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        self.datapaths[datapath.id] = datapath

        flow_serial_no = getFlowNumber()

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.addFlow(datapath, 0, match, actions, flow_serial_no)

        csv_utils.init_portcsv(datapath.id)
        csv_utils.init_flowcountcsv(datapath.id)

    def requestFlowMetrics(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        req = ofp_parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)


    def _speedOfFlowEntries(self, flows):
        global previousFlowCount
        currentFlowCount = 0
        for flow in flows:
            currentFlowCount += 1
        sfe = currentFlowCount - previousFlowCount
        previousFlowCount = currentFlowCount
        return sfe


    def _speedOfSourceIp(self, flows):
        global old_ssip_len
        ssip = []
        for flow in flows:
            m = {}
            for i in flow.match.items():
                key = list(i)[0]
                val = list(i)[1]
                if key == "ipv4_src":
                    if val not in ssip:
                        ssip.append(val)
        cur_ssip_len = len(ssip)
        ssip_result = cur_ssip_len - old_ssip_len
        old_ssip_len = cur_ssip_len

        return ssip_result


    def _ratioOfFlowpair(self, flows):
        #determine total number of flows and  collaborative flows
        flow_count = 0
        for flow in flows:
            flow_count += 1
        flow_count -= 1

        collaborative_flows = {}
        for flow in flows:
            m = {}
            srcip = dstip = None
            for i in flow.match.items():
                key = list(i)[0]  # match key
                val = list(i)[1]  # match value
                if key == "ipv4_src":
                    srcip = val
                if key == "ipv4_dst":
                    dstip = val
            if srcip and dstip:
                fwdflowhash = srcip + "_" + dstip
                revflowhash = dstip + "_" + srcip
                if not fwdflowhash in collaborative_flows:
                    #check you have reverse flowhash exists?
                    if not revflowhash in collaborative_flows:
                        collaborative_flows[fwdflowhash] = {}
                    else:
                        collaborative_flows[revflowhash][fwdflowhash] = 1
        #to identify number of collaborative flows
        onesideflow = iflow = 0
        for key in collaborative_flows:
            if collaborative_flows[key] == {}:
                onesideflow += 1
            else:
                iflow +=2
        if flow_count != 0 :
            rfip = float(iflow) / flow_count
            return rfip
        return 1.0

    @set_ev_cls([ofp_event.EventOFPFlowStatsReply], MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        global gflows, iteration
        t_flows = ev.msg.body
        flags = ev.msg.flags
        dpid = ev.msg.datapath.id
        gflows.extend(t_flows)

        if flags == 0:
            sfe  = self._speedOfFlowEntries(gflows)
            ssip = self._speedOfSourceIp(gflows)
            rfip = self._ratioOfFlowpair(gflows)

            self.detectAttackOrNormalTraffic(dpid, sfe, ssip, rfip)
            gflows = []


            #update the flowcount csv file
            t = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime())
            csv_utils.update_flowcountcsv(dpid, [t, str(previousFlowCount)])

    def detectAttackOrNormalTraffic(self, dpid, sfe, ssip, rfip):
        if APP_TYPE == 1:
            result = self.svmobj.classify([sfe,ssip,rfip])
            if  '1' in result:
                print("Attack Traffic Is Detected")
                self.mitigation = 1
                if PREVENTION == 1 :
                     print("Mitigation Started")

            if '0' in result:
                print("It Is A Normal Traffic")

        else:
            t = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime())
            row = [t, str(sfe), str(ssip), str(rfip)]
            self.logger.info(row)

            csv_utils.update_portcsv(dpid, row)
            csv_utils.update_resultcsv([str(sfe), str(ssip), str(rfip)],str(TEST_TYPE))

    def addFlow(self, datapath, priority, match, actions,serial_no, buffer_id=None, idletime=0, hardtime=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, cookie=serial_no, buffer_id=buffer_id,
                                    idle_timeout=idletime, hard_timeout=hardtime,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, cookie=serial_no, priority=priority,
                                    idle_timeout=idletime, hard_timeout=hardtime,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)


    def block_port(self, datapath, portnumber):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(in_port=portnumber)
        actions = []
        flow_serial_no = getFlowNumber()
        self.addFlow(datapath, 100, match, actions, flow_serial_no, hardtime=130)

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

            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        self.arpIpToPort.setdefault(dpid, {})
        self.arpIpToPort[dpid].setdefault(in_port, [])
        #self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        #if ARP Request packet , log the IP and MAC Address from that port
        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            a = pkt.get_protocol(arp.arp)
            if a.opcode == arp.ARP_REQUEST or a.opcode == arp.ARP_REPLY:
                if not a.src_ip in self.arpIpToPort[dpid][in_port]:
                    self.arpIpToPort[dpid][in_port].append(a.src_ip)



        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:

            # check IP Protocol and create a match for IP
            if eth.ethertype == ether_types.ETH_TYPE_IP:
                ip = pkt.get_protocol(ipv4.ipv4)
                srcip = ip.src
                dstip = ip.dst
                protocol = ip.proto


                if self.mitigation and PREVENTION:
                    if not (srcip in self.arpIpToPort[dpid][in_port]):
                        print("Attack detected from port ", in_port)
                        print("Block the port ", in_port)
                        self.block_port(datapath, in_port)
                        return

                match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=srcip, ipv4_dst=dstip)

                flow_serial_no = getFlowNumber()
                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self.addFlow(datapath, 1, match, actions, flow_serial_no,  buffer_id=msg.buffer_id)
                    return
                else:
                    self.addFlow(datapath, 1, match, actions, flow_serial_no)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
