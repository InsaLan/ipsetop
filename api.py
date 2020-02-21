from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json

hostName = "0.0.0.0"
hostPort = 1312


class Api(BaseHTTPRequestHandler):
    importer = None
    def do_GET(self):
        path = urlparse(self.path)
        if path.path != "/":
            self.send_response(404)
            self.end_headers()
            return
        group,filt,err = self.parse_query(path.query)
        if err:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(bytes(err, "utf-8"))
            return
        filtered = self.filter(filt)
        grouped = self.group(group, filtered)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(grouped), "utf-8"))

    def group(self, group, data):
        res = {}
        def add(lhs, rhs):
            #TODO si quelqu'un a la foi, il faudrait rendre ça moins sale
            res = ((lhs[0][0]+rhs[0][0],lhs[0][1]+rhs[0][1],lhs[0][2]+rhs[0][2]),
                   (lhs[1][0]+rhs[1][0],lhs[1][1]+rhs[1][1],lhs[1][2]+rhs[1][2]))
            return res
        for (source, port, dest) in data:
            key = []
            if "sip" in group:
                key.append(source)
            if "port" in group:
                key.append(port)
            if "dip" in group:
                key.append(dest)
            key = ",".join(key)
            old = res.get(key, ((0,0,0),(0,0,0)))
            res[key] = add(old, data[(source, port, dest)])
        for key in res:
            down,up = res[key]
            res[key] = {'down': {'1m': down[0]*8//60, '15s': down[1]*8//15, '1s': down[2]*8}, 'up':{'1m': up[0]*8//60, '15s': up[1]*8//15, '1s': up[2]*8}}
        return res

    def parse_query(self, query):
        group = None
        filt = []
        for qp in query.split("&"):
            if not qp:
                continue
            cmd, val = qp.split("=")
            if cmd == "group-by":
                if group:
                    return None,None,"Only one group-by is allowed"
                group = [k for k in set(val.split(","))]
                for k in group:
                    if not k in ["sip", "port", "dip"]:
                        return None,None,"Unknown group by : " + k
            elif cmd == "filter":
                f = []
                for v in val.split(","):
                    kind, value = v.split(":",1)
                    if not kind in ["sip", "port", "dip"]:
                        return None,None,"Unknown filer : " + kind
                    f.append((kind,value))
                filt.append(f)
            else:
                return None,None,"Unknown parameter : " + cmd
        if group is None:
            group = ["sip","port","dip"]
        return group,filt,None

    def filter(self, filt):
        res = {}
        data = Api.importer.get_data()
        for (source, port, dest) in data:
            if len(filt) == 0:
                res[(source, port, dest)] = data[(source, port, dest)]
            for f in filt:
                for kind,value in f:
                    if kind == "sip":
                        if value != source:
                            break
                    elif kind == "dip":
                        if value != dest:
                            break
                    else:
                        if value != port:
                            break
                else:
                    res[(source, port, dest)] = data[(source, port,dest)]
                    break
        return res

def run_api(importer):
    Api.importer = importer
    myServer = HTTPServer((hostName, hostPort), Api)

    myServer.serve_forever()
    myServer.server_close()
