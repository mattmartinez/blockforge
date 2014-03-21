from BaseHTTPServer import BaseHTTPRequestHandler
from CommonKeys import *
from ErrorCodes import *
import BaseHTTPServer
import GpuInfo
import sgminerapi
import json
import os
import time
import redis

api = sgminerapi.api()
GpuInfo = GpuInfo.GpuInfo()


class Handler(BaseHTTPRequestHandler):

# Talk to sgminer
    def do_GET(self):
        timestamp = int(round(time.time()))
        api_data = api.call()
        devs = api.getDevsArray(api_data)
        http_code = 200

        if not api.isValidReponse(api_data):
            print "Could not get valid api result!"
            res = {CommonKeys.REQUEST_STATUS : ErrorCodes.BAD_SGMINER}
            http_code = 500
        elif len(devs) < 1:
            print "config is busted"
            res = {CommonKeys.REQUEST_STATUS : ErrorCodes.CONFIG_ERROR}
        else:
            when = api.getServerTime(api_data)
            gpu_statuses = GpuInfo.processDevs(devs, when)
            res = {
                CommonKeys.REQUEST_STATUS : ErrorCodes.OK,
                CommonKeys.GPUS_STATUS : gpu_statuses
            }
		
	#redis
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
	
	gst = gpu_statuses
	for i in range(len(gst)):
		r.set("gpu_" + str(i) + "_hashrate", gst[int(i)]['hashrate'])
		r.set("gpu_" + str(i) + "temp", gst[int(i)]['temperature'])


        # send response (render it)

        self.send_response(http_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(res))

def serve_on_port(port):
    print "Serving port %s" % str(port)

    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class(("", port), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print "Server stopped"


if __name__ == "__main__":
    serve_on_port(1337)
