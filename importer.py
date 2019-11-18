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
                if start_vpn is not None:
                    return {mark: "vpn{}".format(i) for i,mark in enumerate(range(start_vpn, end_vpn+1))}
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
        vpn_usage = {}
        total_down,total_up = (0,0,0),(0,0,0)
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
            (vpn_down, vpn_up) = vpn_usage.get(user_now.mark, ((0,0,0), (0,0,0)))
            def update(old, measure):
                return tuple(o+m for o,m in zip(old, measure))
            vpn.add(user_now.mark)
            users_usage[name] = (update(down_prev, down), update(up_prev, up), vpn)
            vpn_usage[user_now.mark] = (update(vpn_down, down), update(vpn_up, up))
            total_down,total_up = update(total_down, down),update(total_up, up)

        def bar(x, max_val):
            t,_ = self.config["sort_by"]
            scalled = tuple(x[i]/(-1-time[i] or 1) for i in range(3))
            if t == "1m":
                p = scalled[0]/max_val
            elif t == "15s":
                p = scalled[1]/max_val
            elif t == "1s":
                p = scalled[2]/max_val
            if p>1:
                p=0.99
            return (p, scalled[0], scalled[1], scalled[2])

        def cmp(x):
            _,dire = self.config["sort_by"]
            if dire == "down":
                d = users_usage[x][0]
            elif dire == "up":
                d = users_usage[x][1]
            return bar(d, -1)[0:1] + tuple(-v for v in bar(d, 1)[:0:-1])

        vpn_map = self.vpn_map
        def user_to_line(user):
            data = users_usage[user]
            vpnstr = "&".join(vpn_map.get(vpn, "<no_vpn>") for vpn in data[2])
            return user, bar(data[0], self.config["max_user"]), bar(data[1], self.config["max_user"]), vpnstr
        def vpn_to_line(vpn, total=False):
            max_val = self.config["max_vpn"]
            name = vpn_map.get(vpn, "<no_vpn>")
            return name, bar(vpn_usage[vpn][0], max_val), bar(vpn_usage[vpn][1], max_val)
        total = "total", bar(total_down, self.config["max_total"]), bar(total_up, self.config["max_total"])
        data = {}
        data["users"] = [user_to_line(user)  for user in sorted(users_usage, key=cmp)]
        data["vpn"] = sorted([vpn_to_line(vpn) for vpn in vpn_usage]) + [total]

        if self.config["max_user"] is None:
            max_bw = 0
        else:
            max_bw = self.config["max_user"]
        data["max"] = max_bw
        return data
