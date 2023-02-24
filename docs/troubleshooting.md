# SIPssert Testing Framework Troubleshooting

This page contains information about possibilities of troubleshooting a
particular scenario. It is by no means a complete troubleshooting guide, but
rather aims to present you the tools the framework offers you.

## Logs

Framework logging is definitely a useful tool for troubleshooting. For a
better understanding of the process, you should first familiarize yourself with
the [logging](logging.md) structure of the SIPssert Testing Framework.

## Tracing

For each scenario that is being run, the framework captures a `pcap` file, and
stores it in the `SCENDIR` directory, `capture.pcap` file. Check out the
[tracing](tracing.md) file for more information.

## Process

Troubleshooting should be initially narrowed down to a scenario you want to
check. The first step would be to check whether all the tasks within the
scenario have been successfully executed. To do that, look into the `SCENDIR`
directory and check that you have the `.status` and `.logs` file for all the
tasks that should have run for that scenario. If any of them is missing, it is
very likely that the controller did not even tried to start them, or their
execution failed. To check this, you should be checking the controller's logs
(located in the `RUNDIR/controller.log`, or wherever the configuration was
pointing it).

If you have statuses and logs for all the tasks, you should either check the
`capture.pcap` file resulted by the scenario. That should give you a quick idea
of what is the component/task that misbehaves.

At this point, you should have narrowed down the troublesome component - you
should now check the task's logs, located in the `SCENDIR/task.log` file.
