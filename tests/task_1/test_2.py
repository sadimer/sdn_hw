import os
import filecmp

import pytest

from mininet.log import setLogLevel, info
from mininet.net import Mininet
from mininet.node import RemoteController, Host


@pytest.fixture(scope="module")
def mininet():
    c = RemoteController("c", "0.0.0.0", 6633)
    net = Mininet(topo=None, host=Host, controller=None)
    info("*** Adding hosts\n")
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
    h4 = net.addHost(
        "h3",
        cls=Host,
        ip="10.0.0.4/24",
        mac="10:00:00:00:00:04",
    )
    info("*** Adding switches\n")
    s1 = net.addSwitch("s1")
    info("*** Adding links\n")
    net.addLink(h1, s1, addr2="10:00:00:00:00:01")
    net.addLink(h2, s1, addr2="10:00:00:00:00:02")
    net.addLink(h3, s1, addr2="10:00:00:00:00:03")
    net.addLink(h4, s1, addr2="10:00:00:00:00:04")

    info("*** Adding controller\n")
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
    setLogLevel("debug")
    s1.start([c])
    yield net, s1, h1, h2, h3, h4
    for mnobj in net, s1, h1, h2, h3, h4:
        mnobj.stop()


@pytest.fixture(scope="module")
def controller():
    pid = os.fork()
    if pid == 0:
        os.execlp(
            "/usr/local/bin/osken-manager", "osken-manager", "tasks/task_1/task.py"
        )
    yield
    os.kill(pid, 9)


def test_connectivity(mininet, controller):
    net, s1, h1, h2, h3, h4 = mininet
    r1 = net.ping([h1, h2])
    r2 = net.ping([h1, h3])
    r3 = net.ping([h1, h4])
    r4 = net.ping([h2, h3])
    r5 = net.ping([h2, h4])
    r6 = net.ping([h3, h4])

    assert r1 == 0, r1
    assert r2 == 0, r1
    assert r3 == 0, r1
    assert r4 == 0, r1
    assert r5 == 0, r1
    assert r6 == 0, r1


def test_mac_table(mininet, controller):
    assert filecmp.cmp("tests/task_1/test_2.out", "task_1.out") == True
