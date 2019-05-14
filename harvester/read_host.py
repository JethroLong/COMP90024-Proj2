
import json
import sys
sys.path.append("/mnt/storage/COMP90024-Proj2-master/")
sys.path.append("/Users/jethrolong/pyCharmProjects/COMP90024-Proj2/")


class ReadHost:

    @staticmethod
    def read():
        with open("/Users/jethrolong/pyCharmProjects/COMP90024-Proj2/harvester/hosts", mode='r') as f:
            found = False
            for line in f:
                if found:
                    if line.endswith("\n"):
                        return line[:-1]
                    else:
                        return line
                if line.find("[harvester]") >= 0:
                    found = True
        return None


