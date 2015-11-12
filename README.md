# pyIOS

A NETCONF API Implementation for Cisco IOS

To enable NETCONF over SSH on Cisco IOS
```
crypto key generate rsa usage-keys modulus 1024
ip ssh version 2
netconf max-sessions 16
netconf lock-time 60
netconf ssh
line vty 0 15
 transport input ssh
```

This library is inspired by [pyIOSXR](https://github.com/fooelisa/pyiosxr), [pyEOS](https://github.com/spotify/pyeos), and [NAPALM](https://github.com/spotify/napalm) in general. The purpose of this library is to take advantage of the [NETCONF](http://www.netconfcentral.org/) API that is present in most modern implementations of Cisco IOS and follows a very similar structure to the NAPALM structure.

NOTE: This code isn't ready for production use.

* The commit_config function doesn't like writing large chunks of configuration changes. Small, targeted configuration changes appear to work, however.
* I need to test the lock and unlock functionality to lock a device from being configured by a third party at the same time that work is being performed via NETCONF.
* I need to implement discard and rollback functions
* I need to implement an API call in commit_config to write changes to startup.



To utilize this library. You must first import the class.

```
>>> from pyIOS.iosnetconf import IOS
``` 

Then you define the parameters for the device that you want to connect to.

```
>>> router = IOS(hostname='router1', username='someuser', password='somepassword', timeout=120)
```

Next, establish a connection to the device. The data-plane is established over SSH. The SSH connection calls the NETCONF subsystem. The remote device will immediately send a ```<hello>``` xml message. We strip the session-id off the ```<hello>``` and reply back with the same xml message. This effectively establishes the NETCONF session to the remote device.

```
>>> router.open()
```

Once the NETCONF session is established, we're able to make API calls to interact with the device. To get the running configuration of the device, call the load_running_config() function.

```
>>> running = router.load_running_config()
```

Now you can load a candidate configuration into memory locally, with the load_candidate_config().

```
>>> candidate = router.load_candidate_config(filename='replace.cfg')
```

With a running config and candidate config loaded into memory, you can compare the differences between the configurations.

```
>>> compare = router.compare_config()
>>> print compare
--- 
+++ 
@@ -349,8 +349,7 @@
  spanning-tree bpdufilter enable
 !
 interface GigabitEthernet1/0/1
- no switchport
- ip address 192.168.3.1 255.255.255.0
+ switchport
 !
 interface GigabitEthernet1/0/2
 !
@@ -445,7 +444,7 @@
  exec-timeout 0 0
  transport input ssh
 !
-ntp clock-period 36030421
+ntp clock-period 36029820
 ntp server 172.16.0.2 prefer
 ntp server 172.16.0.2 source Loopback0
 netconf max-sessions 16
``` 

If you're satisfied with the intended configuration from the candidate, you can commit the changes to the remote device.

```
>>> router.commit_config(filename='replace.cfg')
```

Finally, when you're done, you can close the connection.

```
>>> router.close()
```
