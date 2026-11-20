## Docker Image for SIPssert

This image can be used to run the [SIPssert](https://github.com/OpenSIPS/SIPssert) tool for a test set provided by the user.
Build the image with the following command:

```bash
docker build -t opensips/sipssert .
```

Due to the fact that the SIPssert containers are actually started from the host environment, we need to provide the host's relative path to the scenarios. Since this is unknown in the SIPssert's container environment, we need match the exact host's filesystem layout for the tests directory.
So, go to your test directory and run the following command:

```bash
docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd):$(pwd) -w $(pwd) opensips/sipssert .
```

### Tracing from a container

The tracer runs `tcpdump` in the controller environment. When SIPssert itself
runs in a container (as in the example above), `tcpdump -i any` only sees the
controller container's own network namespace, so the resulting capture does
not contain the traffic of the scenario tasks, which runs over the Docker
bridge networks that live in the host network namespace.

To make tracing work, run the controller with `--net=host`:

```bash
docker run --rm -it --net=host -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):$(pwd) -w $(pwd) opensips/sipssert .
```

Sources of this docker image can he found on [GitHub](https://github.com/OpenSIPS/SIPssert/tree/main/docker).
