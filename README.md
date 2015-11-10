# pyIOS
A NETCONF Implementation for Cisco IOS

To enable NETCONF over SSH on Cisco IOS
```
crypto key generate rsa usage-keys modulus 1024
ip ssh version 2
netconf max-sessions 16
netconf lock-time 300
netconf ssh
line vty 0 15
 transport input ssh
```

This library is currently experemental and is not a functiional library. All that it currently does is receive a hello from the NETCONF enabled network device, then responds with a hello. There is still quite a bit of work that needs to happen to be able to send commands via NETCONF.
