import docker

# return a client configured from environment variables.
client = docker.from_env()

# return a container 
uas = client.containers.run("ctaloi/sipp", "-sn uas", detach=True)
print(uas.status)

# list with all containers
containers_list = client.containers.list()[0]

# if the container is still working, stop it
while(1):
    # updateing status
    uas.reload()
    if uas.status == "created":
        print("container just created, wait for changeing status")
        continue
    elif uas.status == "exited":
        print("container terminated")
        break
    # container still running
    else:
        print("the container will stop")
        uas.stop()

uas.reload()
print(uas.status)
