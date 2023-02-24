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
