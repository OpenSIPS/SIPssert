# SIPssert Testing Framework Tracing

This page describes the way the framework traces networking traffic for
each scenario being run.

For each scenario, the framework takes a pcap capture of the communication for
that scenario and stores it in the `capture.pcap` file in the scenario's logs
directory.

The data that is being captured depends on the networking mode the scenario
runs with. If it is using a `host` network adapter, then the entire traffic of
the host is traced. Otherwise, if a `bridged` adaptor is being used, then only
the traffic going through the bridge network device is being traced.

By default tracer is always on. You can change this behavior by disabling 
tracer on global, test_set or scenario level with desc order priority.
Disabling tracer on global level has highest priority.


1. To disable tracer on global level by passing command line arg, use:

`-x|--no-trace` - do not trace call

2. To disable tracer on global level by defining configuration parameter in config file, edit:

run.yml
```yaml
tracer: off
```

3. To disable tracer on test_set level, edit config.yml on test_set level:

config.yml
```yaml
tracer: off
```

4. To disable tracer on scenario level, edit scenario.yml:

scenario.yml
```yaml
tracer: off
```
