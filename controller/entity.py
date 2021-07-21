class Entity():
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


class Entity_uas(Entity):
    def setExtraParams(self, extra_params):
        self.extra_params = extra_params

    def getExtraParams(self):
        return self.extra_params

class Entity_uac(Entity):
    def setExtraParams(self, extra_params):
        self.extra_params = extra_params

    def getExtraParams(self):
        return self.extra_params

class Entity_opensips(Entity):
    def __init__(self, extra_params, path_cfg, mount_point):
        self.extra_params = extra_params
        self.path_cfg = path_cfg
        self.mount_point = mount_point

    def setExtraParams(self, extra_params):
        self.extra_params = extra_paramsq

    def getExtraParams(self):
        return self.extra_params

    def setPathConfig(self, path_cfg):
        self.path_cfg = path_cfg

    def getPathConfig(self):
        return self.path_cfg

    def setMountPoint(self, mount_point):
        self.mount_point = mount_point

    def getMountPoint(self):
        return self.mount_point
