# SIPssert Testing Framework UAC SIPP Stir and Shaken Task

This is a particularization of the [SIPp](sipp.md) task for running a UAC
[SIPp](https://sipp.sourceforge.net/) scenario.

## Behavior

Executes the `sipp` command in UAC mode.

## Defaults

The variables overwritten by default by the task are:

* `image`: the default image to run is `allomediadocker/sipp:3.7.1`

## Settings

This task uses all the [SIPp task settings](sipp.md#settings)
Additional settings that can be passed to the task:

* `proxy`: represents the outbound proxy; mandatory if `remote` is not present
* `remote`: remote destination - if present, sets the remote destination; if
`proxy` is missing, it may take `proxy`'s place
* `caller`: the identity of the caller, passed as the `caller` `key` to the
`sipp` XML scenario
* `destination`: the destination username; this is an alias to the `sipp`
`service` node
* `config_file`: if missing and no `sipp.xml` file in the scenario directory,
the UAC default scenario is run.
* `stir_shaken_private_key`: In PEM format, default
```
-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIIOvgr23lbJ5rIOhiF+LR/VU4piEc1EYLT1CF5SN5HtZoAoGCCqGSM49
AwEHoUQDQgAEuyQP0hteN1oKDUxo/2zvTp+0ppJ2IntNSdu36QFsUPDsCWlr4iTU
MsjPtD+XQ58xQEf6n/zTE9cwZhs46NJWdA==
-----END EC PRIVATE KEY-----
```
* `stir_shaken_info`: default `https://certs.example.org/cert.pem`
* `stir_shaken_alg`: default `ES256`
* `stir_shaken_ppt`: default `shaken`
* `stir_shaken_typ`: default `passport`
* `stir_shaken_attest`: default `A`
* `stir_shaken_origid`: default `4437c7eb-8f7a-4f0e-a863-f53a0e60251a`

## Example

Execute a UAC scenario:
```
 - name: SIPP UAC Stir and Shaken
    type: uac-sipp-stir-shaken
    service: "+33987654321"
    config_file: scripts/uac.xml
    remote: {{ uas_ip }}:{{ uas_port }}
    caller: "+33612345678"
    duration: 10000
    stir_shaken_private_key: "-----BEGIN EC PRIVATE KEY-----
    MHcCAQEEIIOvgr23lbJ5rIOhiF+LR/VU4piEc1EYLT1CF5SN5HtZoAoGCCqGSM49
    AwEHoUQDQgAEuyQP0hteN1oKDUxo/2zvTp+0ppJ2IntNSdu36QFsUPDsCWlr4iTU
    MsjPtD+XQ58xQEf6n/zTE9cwZhs46NJWdA==
    -----END EC PRIVATE KEY-----"
    stir_shaken_info: "https://certs.example.org/cert.pem"
    stir_shaken_alg: "ES256"
    stir_shaken_ppt: "shaken"
    stir_shaken_typ: "passport"
    stir_shaken_attest: "A"
    stir_shaken_origid: "4437c7eb-8f7a-4f0e-a863-f53a0e60251a"
```
