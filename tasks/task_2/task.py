import yaml
from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from os_ken.controller.handler import set_ev_cls
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet
from os_ken.lib.packet import ethernet
from os_ken.lib.packet import ether_types
from os_ken.ofproto.ofproto_v1_3 import OFPPS_LIVE

VLAN_MAPPING = {
    "10:00:00:00:00:01": 1,
    "10:00:00:00:00:02": 1,
    "10:00:00:00:00:06": 1,
    "10:00:00:00:00:03": 2,
    "10:00:00:00:00:04": 2,
    "10:00:00:00:00:05": 2,
}


class SimpleSwitch(app_manager.OSKenApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)
        self.mac_table = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        # WRITE YOUR CODE HERE
        pass

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # WRITE YOUR CODE HERE
        with open("task_2.out", "w") as file:
            print(f"MAC TABLE:\n{yaml.dump(self.mac_table)}", file=file)
