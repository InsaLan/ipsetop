import sys
import threading
import time
from random import randint

from managed import Net


class Importer:
    def __init__(self, interfaces, reverse, code=None):
        if code:
            self.code = code
        else:
            self.code = str(randint(0, 2**32))
        self.ipset = Net(self.code, interfaces, reverse)
        self.data = [self.ipset.get_all_flows()]
        def run(x):
            while True:
                time.sleep(1)
                flows = x.ipset.get_all_flows()
                x.data = x.data[-60:]+[flows]

        t = threading.Thread(target=run, args=(self,))
        t.start()

    def get_data(self):
        if len(self.data) > 15:
            self.time = [-len(self.data), -16, -2]
        elif len(self.data) > 1:
            self.time = [-len(self.data)]*2+[-2]
        else:
            self.time = [-1]*3

        now = self.data[-1]
        measurements = [self.data[t] for t in self.time]

        flows_usage = {}
        total_down,total_up = (0,0,0),(0,0,0)
        for flow in now:
            flow_now = now[flow]
            flow_id = (flow_now.source, flow_now.port, flow_now.destination)
            down_now = flow_now.down
            up_now = flow_now.up
            def delta(user):
                if user is None:
                    return (down_now, up_now)
                else:
                    return (down_now - user.down, up_now - user.up)
            down, up = zip(*[delta(m.get(flow)) for m in measurements])

            flows_usage[flow_id] = down, up

        return flows_usage
