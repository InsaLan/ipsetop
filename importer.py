import threading
import time
from netcontrol.managed import Net
from random import randint
import sys


class Importer:
    def __init__(self):
        self.code = randint(0, 2**32)
        self.config = {
            "max_user": 100*1024**2,
            "max_total": 1024**3,
            "sort_by": ("1s","down"),
            "hide" : [], #local, port, remote
        }
        self.ipset = Net()
        self.data = [self.ipset.get_all_flows()]
        def run(x):
            while True:
                time.sleep(1)
                users = x.ipset.get_all_flows()
                x.data = x.data[-60:]+[users]

        t = threading.Thread(target=run, args=(self,))
        t.start()

    def update_sort(self, dire=None, time=None):
        t,d = self.config["sort_by"]
        if dire == "u":
            d = "up"
        elif dire == "d":
            d = "down"
        if time == "1":
            t == "1m"
        elif time == "2":
            t == "15s"
        elif time == "3":
            t == "1s"
        self.config["sort_by"] = t,d
        

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

            (down_prev, up_prev) = users_usage.get(name, ((0,0,0), (0,0,0)))
            def update(old, measure):
                return tuple(o+m for o,m in zip(old, measure))
            users_usage[name] = (update(down_prev, down), update(up_prev, up))
            total_down,total_up = update(total_down, down),update(total_up, up)

        total = "total", self.bar(total_down, self.config["max_total"]), self.bar(total_up, self.config["max_total"])
        data = {}
        data["users"] = [self.user_to_line(user)  for user in sorted(users_usage, key=lambda x: self.cmp(x))]

        if self.config["max_user"] is None:
            max_bw = 0
        else:
            max_bw = self.config["max_user"]
        data["max"] = max_bw
        return data

    def bar(self, x, max_val):
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

    def cmp(self, x):
        _,dire = self.config["sort_by"]
        if dire == "down":
            d = users_usage[x][0]
        elif dire == "up":
            d = users_usage[x][1]
        return self.bar(d, -1)[0:1] + tuple(-v for v in self.bar(d, 1)[:0:-1])

    def user_to_line(self, user):
        data = users_usage[user]
        return user, self.bar(data[0], self.config["max_user"]), self.bar(data[1], self.config["max_user"])
