import threading
import time
from netcontrol.managed import Net

class Importer:
    def __init__(self):
        self.config = {
            "max_user": 100*1024**2,
            "max_vpn": 300*1024**2,
            "max_total": 1024**3,
            "sort_by": ("1s","down"),
            "vpnlist": None,
        }
        self.ipset = Net()
        self.data = [self.ipset.get_all_connected()]
        self.vpnlist = {}
        threading.Thread(target=lambda s: s.__run, args=(self,)).start

    def __run(self):
        while True:
            time.sleep(1)
            users = self.ipset.get_all_connected()
            self.data = self.data[-60:]+[users]

    @property
    def vpn_map(self):
        if self.config["vpnlist"]:
            return self.config["vpnlist"]
        else:
            users = self.data[-1]
            if len(users):
                start_vpn = min((users[k] for k in users), key=lambda u: u.mark if u.mark is not None else 2**32).mark
                end_vpn = max((users[k] for k in users), key=lambda u: u.mark if u.mark is not None else 0).mark
                return {mark: "vpn{}".format(i) for i,mark in enumerate(range(start_vpn, end_vpn+1))}
            else:
                return {}



    def get_data(self):
        data = {}
        data["users"] = []

        [
            ("player1", (0.3,1,2,81.2*1024**2), (0.9, 3,4,17.1*1024**2), "vpn0"),
            ("player2", (0.2,5,6,45.2*1024), (0.1, 7,8,2000), "vpn1")
        ]
        data["vpn"] = [(vpn, (0,0,0,0), (0,0,0,0)) for vpn in self.vpn_map.values()] + [("total", (0,0,0,0), (0,0,0,0))]
        [
            ("vpn0", (0.3, 1,2,81.2*1024**2), (0.8, 3,4,17.1*1024**2)),
            ("vpn1", (0.2, 5,6,45.2*1024), (0.1, 7,8,2000)),
            ("total", (0.5, 7,8,81.2*1024**2), (0.8,10,12,17.1*1024**2))
        ]
        data["max"] = 0
        return data
