# SIPssert Testing Framework Scenarios Guide

The scenarios are essentially the place where you describe the behavior of your
tests; in scenario you define the networking mode you want to run with, the
applications you want to run, the pre-requisites you need, and the way all
these interact with each other. That is why it is very important to pay
attention when developing a new test/scenario.

This page aims to offer a few guidelines on how a scenario should be designed,
organized and implemented.

## Organizing

When designing a particular test suite, you should take into account how often
a set of scenarios should be run together, or individually. If a set of tasks
is very often run as a whole, you should store all of them in a tests set.
Basically, every new feature should be a tests set, and within it, each
scenario should test a particular functionality of the feature.

For example, if you want to test registrations and calls for your platform, you
may have a tests-set for registration, and one for calls. One for transfers,
and so on, and so forth.

A different approach for spreading scenarios within tests set would be based on
components. Lets say for example that you have a platform and you have a
complex VoIP platform, that consists of multiple components, such as an SBC, a
Core engine, and a set of Media Servers. A good approach would be to write a
tests set for each component - this way you can easily filter whatever tests
suite you want to run.

Of course, combining both is possible, but at a higher level. For example, you
may write a shell script that triggers the `sipssert` tool for each component,
where each component has multiple tests sets organized per feature.

## Defines

[Defines](../config/define.md) are used to specify certain configuration
settings in a single place as variables, and then use those variables along the
tests set and scenario. If, for example, you have a setting that should be
shared among multiple tasks, it is a good idea to define a variable for that
setting, and then use it along the scenarios as variable, instead of hard-coded
values.

Try to minimize the scope of the defines - if for example you are using a
variable only for a specific scenario, do not declare it in the tests set, as
that would unnecessarily expand the tests set defines. Instead, define it in
the scenario and use it there. If however you need the same setting among
multiple scenarios, then it is a good idea to define it in tests set defines.

## Defaults

[Defaults](../config/tests-set.md#defaults) are used to keep the specification
of tasks within scenarios shorter, by defining a set of default settings for
specific tasks types. Using defaults as much as possible is always recommended.

## Tips

A few recommendations to take into account when writing tests/scenarios:

 * Do not try to condense multiple functionalities in a single scenario; simply
write a scenario for each functionality you are trying to test.
 * A scenario should be as small as possible, and should test as little
functionality as possible. The more complex it is, the harder would be to
troubleshoot in case something is not working as expected.
 * Due to the same considerings, tasks should perform small operations; if a
specific tasks you are planning to use seems to complex, try writing your
own tasks (should not be that hard, check out the [Tasks](tasks.md) page).
 * Pay attention to dependencies and the way tasks are executed; since they are
executed in parallel, if dependencies are not properly set, some tasks may
fail because their prerequisites have not been completed yet.
 * Use as much as possible definitions, to avoid duplicating information across
tests sets and scenarios
