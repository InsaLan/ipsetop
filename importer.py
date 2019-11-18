import threading
import time
from netcontrol.managed import Net
import sys


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
        def run(x):
            while True:
                time.sleep(1)
                users = x.ipset.get_all_connected()
                x.data = x.data[-60:]+[users]

        t = threading.Thread(target=run, args=(self,))
        t.start()



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
        if len(self.data) > 15:
            time = [-len(self.data), -16, -2]
        elif len(self.data) > 1:
            time = [-len(self.data)]*2+[-2]
        else:
            time = [-1]*3

        now = self.data[-1]
        measurements = [self.data[t] for t in time]

        users_usage = {}
        for ip in now:
            user_now = now[ip]
            name = user_now.name or ip
            down_now = user_now.down
            up_now = user_now.up
            def delta(user):
                if user is None:
                    return (down_now, up_now)
                else:
                    return (down_now - user.down, up_now - user.up)
            down, up = zip(*[delta(m.get(ip)) for m in measurements])

            (down_prev, up_prev, vpn) = users_usage.get(name, ((0,0,0), (0,0,0),set()))
            def update(old, measure):
                return tuple(o+m for o,m in zip(old, measure))
            vpn.add(user_now.mark)
            users_usage[name] = (update(down_prev, down), update(up_prev, up), vpn)

        max_val = self.config["max_user"]
        def bar(x):
            t,_ = self.config["sort_by"]
            scalled = tuple(x[i]/(-1-time[i] or 1) for i in range(3))
            if t == "1m":
                p = scalled[0]/max_val
            elif t == "15s":
                p = scalled[1]/max_val
            elif t == "1s":
                p = scalled[2]/max_val
            return (p, scalled[0], scalled[1], scalled[2])


        def cmp(x):
            _,dire = self.config["sort_by"]
            if dire == "down":
                d = users_usage[x][0]
            elif dire == "down":
                d = users_usage[x][1]
            return -bar(d)[0]




        vpn_map = self.vpn_map
        def entry_to_line(user):
            data = users_usage[user]
            vpnstr = "&".join(vpn_map[vpn] for vpn in data[2])
            return user, bar(data[0]), bar(data[1]), vpnstr
        user_lines = [entry_to_line(user)  for user in sorted(users_usage, key=cmp)]

        data = {}
        data["users"] = user_lines
        data["vpn"] = [(vpn, (0,0,0,0), (0,0,0,0)) for vpn in self.vpn_map.values()] + [("total", (0,0,0,0), (0,0,0,0))]

        [
            ("player1", (0.3,1,2,81.2*1024**2), (0.9, 3,4,17.1*1024**2), "vpn0"),
            ("player2", (0.2,5,6,45.2*1024), (0.1, 7,8,2000), "vpn1")
        ]
        [
            ("vpn0", (0.3, 1,2,81.2*1024**2), (0.8, 3,4,17.1*1024**2)),
            ("vpn1", (0.2, 5,6,45.2*1024), (0.1, 7,8,2000)),
            ("total", (0.5, 7,8,81.2*1024**2), (0.8,10,12,17.1*1024**2))
        ]

        if self.config["max_user"] is None:
            max_bw = 0
        else:
            max_bw = self.config["max_user"]
        data["max"] = max_bw
        return data
