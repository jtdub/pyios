from os.path import expanduser

import xml.etree.ElementTree as ET

import sys
import pexpect


class IOS(object):

    def __init__(self, hostname, username, password, port=22, timeout=120):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout

    def open(self):
        """
        To establish a NETCONF session, we do so utilizing ssh via:

        ssh -s -p {{ port }} {{ username }}@{{ hostname }} netconf

        The -s flag allows us to invoke the netconf subsystem on the remote
        system.

        The remote network device will immediately send a 'hello' xml command.
        We take the 'hello' xml command, remove the system-id element and
        send the 'hello' back to the remote network device. Once this
        handshake is complete, the NETCONF session is established and ready
        to do work.
        """
        host = pexpect.spawn('ssh -o ConnectTimeout={} -s -p {} {}@{} netconf'
                             .format(self.timeout, self.port, self.username,
                                     self.hostname))
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
        host.expect([']]>]]>', pexpect.EOF], timeout=self.timeout)
        server_hello = host.before
        server_hello = server_hello.lstrip()
        with open(expanduser('~/.server_hello.netconf'), 'w') as f:
            f.write(server_hello)
        xml_tree = ET.parse(expanduser('~/.server_hello.netconf'))
        xml_root = xml_tree.getroot()
        session = xml_tree.find('session-id')
        xml_root.remove(session)
        xml_tree.write(expanduser('~/.client_hello.netconf'))
        with open(expanduser('~/.client_hello.netconf'), 'r') as f:
            hello = f.read()
        client_hello = '<?xml version="1.0" encoding="UTF-8"?>{0}]]>]]>'\
            .format(hello)

        host.sendline(client_hello)

    def close(self):
        self.host.close()

    def get_config(self, format='json'):
        pass

    def load_running_config(self):
        pass

    def load_candidate_config(self, filename=None, config=None):
        pass

    def compare_config(self):
        pass

    def replace_config(self, config=None, force=None):
        pass

    def rollback(self):
        pass
