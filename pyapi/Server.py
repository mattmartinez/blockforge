from BaseHTTPServer import BaseHTTPRequestHandler
from CommonKeys import *
from ErrorCodes import *
import BaseHTTPServer
import GpuInfo
import sgminerapi
import json,os,time
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

	# Dev, so lets wipe these to start off
	if r.keys("*") > 1:
		r.flushall()
	
	gst = gpu_statuses
	for i in range(len(gst)):
        time = strftime("%m_%d_%Y-%H_%M_%S")
		r.set("gpu_" + str(i) + "_hashrate", gst[int(i)]['hashrate'])
		r.set("gpu_" + str(i) + "_temp", gst[int(i)]['temperature'])
		r.set("gpu_" + str(i) + "_sacc", gst[int(i)]['shares_accepted'])
		r.set("gpu_" + str(i) + "_srej", gst[int(i)]['shares_rejected'])
		r.set("gpu_" + str(i) + "_lastw", gst[int(i)]['time_since_last_valid_work'])
	
				

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
