##read host file
import linecache
import json

#HOST_FILE = "./deployVMs/hosts"
HOST_FILE = "/mnt/storage/COMP90024-Proj2/harvester/hosts"

def readhost():
    couchdb = None
    analyser = None
    webserver = None
    harvester = None
    hdict = dict()
    
    with open (HOST_FILE,mode='r') as f:
        count = 0
        for line in f.readlines():
            
            if line.find("[couchdb]") >= 0:
                couchdb = linecache.getlines(HOST_FILE)[count+1].replace("\n","")
            elif line.find("[analyser]") >= 0:
                analyser = linecache.getlines(HOST_FILE)[count+1].replace("\n","")
            elif line.find("[webserver]") >= 0:
                webserver = linecache.getlines(HOST_FILE)[count+1].replace("\n","")
            elif line.find("[harvester]") >= 0:
                harvester = linecache.getlines(HOST_FILE)[count+1].replace("\n","")
            count = count + 1

    hdict["couchdb"] = couchdb
    hdict["analyser"] = analyser
    hdict["webserver"] = webserver
    hdict["harvester"] = harvester

    host_dict = json.dumps(hdict)
    return host_dict



