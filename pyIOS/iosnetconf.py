from os.path import expanduser

import xml.etree.ElementTree as ET

import sys
import pexpect

from exceptions import InvalidInputError


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
            hello = xml_tree.remove(session)

        """ Send 'hello' back to remote device """
        client_hello = '{0}]]>]]>'.format(hello)
        host.sendline(client_hello)

    def close(self):
        pass

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
