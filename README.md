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
