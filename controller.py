import docker
from docker.api import container
import docker

# return a client configured from environment variables.
client = docker.from_env()

# return a container 
uas = client.containers.run("ctaloi/sipp","-sn uas", detach=True)
print(uas.status)

# list with all containers
containers_list = client.containers.list()[0]

# if the container is still working, stop it
while(1):
    if uas.status == "running" or uas.status == "created":
        continue
    else:
        break

print(uas.status)
