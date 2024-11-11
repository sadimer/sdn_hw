from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import RemoteController, Host

c = RemoteController("c", "0.0.0.0", 6633)
net = Mininet(topo=None, host=Host, controller=None)

h1 = net.addHost(
    "h1",
    cls=Host,
    ip="10.0.0.1/24",
    mac="10:00:00:00:00:01",
)
h2 = net.addHost(
    "h2",
    cls=Host,
    ip="10.0.0.2/24",
    mac="10:00:00:00:00:02",
)
h3 = net.addHost(
    "h3",
    cls=Host,
    ip="10.0.0.3/24",
    mac="10:00:00:00:00:03",
)

v1 = net.addHost(
    "v1",
    cls=Host,
    ip="20.0.0.1/24",  # "10.0.0.4/24",
    mac="20:00:00:00:00:01",
    defaultRoute="via 20.0.0.254",
)
v2 = net.addHost(
    "v2",
    cls=Host,
    ip="20.0.0.2/24",  # "10.0.0.5/24",
    mac="20:00:00:00:00:02",
    defaultRoute="via 20.0.0.254",
)
v3 = net.addHost(
    "v3",
    cls=Host,
    ip="20.0.0.3/24",  # "10.0.0.6/24",
    mac="20:00:00:00:00:03",
    defaultRoute="via 20.0.0.254",
)

s1 = net.addSwitch("s1", ip="192.168.0.1")
s2 = net.addSwitch("s2", ip="192.168.0.2")

net.addLink(h1, s1, addr2="10:00:00:00:00:01")
net.addLink(h2, s1, addr2="10:00:00:00:00:02")
net.addLink(h3, s2, addr2="10:00:00:00:00:03")

net.addLink(v1, s2, addr2="20:00:00:00:00:01")
net.addLink(v2, s2, addr2="20:00:00:00:00:02")
net.addLink(v3, s1, addr2="20:00:00:00:00:03")

net.addController(c)

for h in net.hosts:
    h.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
    h.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
    h.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

for sw in net.switches:
    sw.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
    sw.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
    sw.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

net.build()
s1.start([c])
s2.start([c])

CLI(net)
net.stop()

setLogLevel("debug")
