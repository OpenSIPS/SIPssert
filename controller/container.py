class Container():
    def __init__(self, name, type, image, ports, ip):
        self.name = name
        self.type = type
        self.image = image
        self.ports = ports
        self.ip = ip

    def getName(self):
        return self.name

    def getType(self):
        return self.type

    def getImage(self):
        return self.image

    def getPorts(self):
        return self.ports

    def getIp(self):
        return self.ip


class Uas(Container):
    def setExtraParams(self, extra_params):
        self.extra_params = extra_params

    def getExtraParams(self):
        return self.extra_params

class Uac(Container):
    def __init__(self, extra_params):
        self.extra_params = extra_params
    
    def getExtraParams(self):
        return self.extra_params

class Opensips(Container):
    def __init__(self, extra_params, path_cfg, mount_point):
        self.extra_params = extra_params
        self.path_cfg = path_cfg
        self.mount_point = mount_point

    def getExtraParams(self):
        return self.extra_params

    def getPathConfig(self):
        return self.path_cfg

    def getMountPoint(self):
        return self.mount_point
