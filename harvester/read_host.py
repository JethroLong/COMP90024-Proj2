
import json
import sys
sys.path.append("/mnt/storage/COMP90024-Proj2-master/")


class ReadHost:

    @staticmethod
    def read():
        with open("./harvester/hosts", mode='r') as f:
            found = False
            for line in f:
                if found:
                    return line[:-1]
                if line.find("[harvester]") >= 0:
                    found = True
        return None


