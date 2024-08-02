## Docker Image for SIPssert

This image can be used to run the SIPssert tool for a test set provided by the user.
Build the image with the following command:

```bash
docker build -t opensips/sipssert .
```

Due to the fact that the SIPssert containers are actually started from the host environment, we need to provide the host's relative path to the scenarios. Since this is unknown in the SIPssert's container environment, we need match the exact host's filesystem layout for the tests directory.
So, go to your test directory and run the following command:

```bash
docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd):$(pwd) -w $(pwd) opensips/sipssert .
```
