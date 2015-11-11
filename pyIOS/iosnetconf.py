import xml.etree.ElementTree as ET

import pexpect
import re
import difflib

from exceptions import InvalidInputError


def __execute_netconf__(device, rpc_command, timeout):
    rpc = '''<?xml version="1.0" encoding="UTF-8"?>
    <rpc message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
     {0}
    </rpc>]]>]]>\n'''.format(rpc_command)
    device.sendline(rpc)
    device.expect("<rpc-reply.*</rpc-reply>]]>]]>", timeout=timeout)

    return device.after


class IOS(object):

    def __init__(self, hostname, username, password, port=22, timeout=120):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout

    def open(self):
        """
        To establish a NETCONF session, we utilize ssh via:

        ssh -s -p {{ port }} {{ username }}@{{ hostname }} netconf

        The -s flag allows us to invoke the netconf subsystem on the remote
        system.

        The remote network device will immediately send a 'hello' xml command.
        We take the 'hello' xml command, remove the system-id element and
        send the 'hello' back to the remote network device. Once this
        handshake is complete, the NETCONF session is established and ready
        to do work.
        """

        """ Establishing a connection and logging in """
        host = pexpect.spawn('ssh -o ConnectTimeout={} -s -p {} {}@{} netconf'
                             .format(self.timeout, self.port, self.username,
                                     self.hostname))
        self.host = host
        index = host.expect(['\(yes\/no\)\?', '[Pp]assword:', pexpect.EOF],
                            timeout=self.timeout)
        if index == 0:
            host.sendline('yes')
            index = host.expect(['\(yes\/no\)\?', '[Pp]assword:', pexpect.EOF],
                                timeout=self.timeout)
        if index == 1:
            host.sendline(self.password)
        elif index == 2:
            pass

        """ Receive 'hello' from remote device """
        host.expect(']]>]]>', timeout=self.timeout)
        server_hello = host.before
        server_hello = server_hello.lstrip()
        xml_tree = ET.fromstring(server_hello)

        """ Find and remove 'session-id' from remote hello """
        for session in xml_tree.findall('session-id'):
            xml_tree.remove(session)

        """ Send 'hello' back to remote device """
        hello = ET.tostring(xml_tree)
        client_hello = '<?xml version="1.0" encoding="UTF-8"?>{0}]]>]]>\n'\
            .format(hello)
        host.sendline(client_hello)
        host.expect(']]>]]>', timeout=self.timeout)

        """ Make the host variable callable by other functions """
        self.host = host

    def close(self):
        """ Close the connection to the remote device """
        self.host.close()

    def get_running_config(self):
        """ Get the live running config from a remote device """
        live = __execute_netconf__(self.host, '<get></get>',
                                   timeout=self.timeout)
        running = re.sub('<.+>', '', live)
        running = re.sub('\r', '', running)

        return running 

    def load_running_config(self, config=None):
        """ Get configuration section to be replaced """
        xml_encap = '''<get-config>
         <source>
          <running/>
         </source>
         <filter>
          <config-format-text-block>
          <text-filter-spec> {0} </text-filter-spec>
          </config-format-text-block>
         </filter>
        </get-config>'''.format(config)

        live = __execute_netconf__(self.host, xml_encap,
                                   timeout=self.timeout)
        running = re.sub('<.+>', '', live)
        running = re.sub('\r', '', running)

        return running

    def load_replace_config(self, filename=None, config=None):
        """ Load a candidate config in to memory """
        configuration = ''

        if filename is None:
            configuration = config
        else:
            with open(filename, 'r') as f:
                configuration = f.read()

        return configuration

    def compare_config(self, running=None, candidate=None):
        """ Compare a running configuration with a candidate configuration """
        running_config = running
        candidate_config = candidate
        
        diff = difflib.unified_diff(running_config.splitlines(1)[2:-2],
                                    candidate_config.splitlines(1)[2:-2])
        diff = ''.join([x.replace('\r', '') for x in diff])

        return diff

    def commit_config(self, filename=None, config=None):
        """ Push a configuration to a device """
        configuration = ''
        encap_config = ''

        if filename:
            with open(filename, 'r') as f:
                configuration = f.read()
        else:
            configuration = config

        for line in configuration.split('\n'):
            encap_config += '<cmd>{0}</cmd>'.format(line)

        xml_encap = '''<edit-config>
         <target>
          <running/>
         </target>
          <config>
           <cli-config-data>
            {0}
           </cli-config-data>
          </config>
         </edit-config>'''.format(encap_config)

        live = __execute_netconf__(self.host, rpc_command=xml_encap,
                                   timeout=self.timeout)
        return live
