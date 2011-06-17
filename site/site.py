from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from pyspades.site import get_servers
from pyspades.tools import make_server_number

UPDATE_INTERVAL = 10
PYSPADES_TIMEOUT = 2
INPUT = 'in.html'
OUTPUT = 'index.html'

SERVER_TEMPLATE = """
<tr>
<td>%(pyspades)s</td>
<td>%(ratio)s</td>
<td>%(ping)s</td>
<td>%(url)s</td>
<td>%(address)s</td>
</tr>
"""

LIST_TEMPLATE = """
<table>
<tbody>
<tr>
<td>pyspades</td>
<td>slots</td>
<td>ping</td>
<td>server</td>
<td>address</td>
</tr>
%(servers)s
</tbody>
</table>
"""

class QueryProtocol(DatagramProtocol):
    pyspades_set = None
    def startProtocol(self):
        self.update()
    
    def write_html(self, servers):
        f = open(INPUT, 'rb')
        data = f.read()
        f.close()
        html_servers = []
        for server in servers:
            address = 'aos://%s' % make_server_number(server.ip)
            html_servers.append(SERVER_TEMPLATE % {
                'pyspades' : ['No', 'Yes'][int(server.ip in self.pyspades_set)],
                'ratio' : '%s/%s' % (server.players, server.max),
                'ping' : server.ping,
                'url' : '<a href="%s">%s</a>' % (address, server.name),
                'address' : address
            })
        html = LIST_TEMPLATE % {'servers' : '\n'.join(html_servers)}
        data = data % {'servers' : '%s' % html}
        open(OUTPUT, 'wb').write(data)
        print 'done'
        self.pyspades_set = None
    
    def got_servers(self, servers):
        self.pyspades_set = set()
        for server in servers:
            self.transport.write('HELLO', (server.ip, 32887))
        reactor.callLater(PYSPADES_TIMEOUT, self.write_html, servers)
    
    def update(self):
        get_servers().addCallback(self.got_servers)
        reactor.callLater(UPDATE_INTERVAL, self.update)
    
    def datagramReceived(self, data, address):
        if self.pyspades_set is None or data != 'HI':
            return
        print 'yay'
        self.pyspades_set.add(address[0])
    
reactor.listenUDP(0, QueryProtocol())
reactor.run()