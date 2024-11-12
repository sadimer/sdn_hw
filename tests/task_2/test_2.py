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
        "h4",
        cls=Host,
        ip="10.0.0.4/24",
        mac="10:00:00:00:00:04",
    )
    h5 = net.addHost(
        "h5",
        cls=Host,
        ip="10.0.0.5/24",
        mac="10:00:00:00:00:05",
    )
    h6 = net.addHost(
        "h6",
        cls=Host,
        ip="10.0.0.6/24",
        mac="10:00:00:00:00:06",
    )

    info("*** Adding switches\n")
    s1 = net.addSwitch("s1")
    info("*** Adding links\n")
    net.addLink(h1, s1, addr2="10:00:00:00:00:01")
    net.addLink(h2, s1, addr2="10:00:00:00:00:02")
    net.addLink(h3, s1, addr2="10:00:00:00:00:03")
    net.addLink(h4, s1, addr2="10:00:00:00:00:04")
    net.addLink(h5, s1, addr2="10:00:00:00:00:05")
    net.addLink(h6, s1, addr2="10:00:00:00:00:06")

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
    yield net, s1, h1, h2, h3, h4, h5, h6
    for mnobj in net, s1, h1, h2, h3, h4, h5, h6:
        mnobj.stop()


@pytest.fixture(scope="module")
def controller():
    pid = os.fork()
    if pid == 0:
        os.execlp(
            "/usr/local/bin/osken-manager", "osken-manager", "tasks/task_2/task.py"
        )
    yield
    os.kill(pid, 9)


def test_connectivity_1(mininet, controller):
    net, s1, h1, h2, h3, h4, h5, h6 = mininet
    r1 = net.ping([h1, h2])
    r2 = net.ping([h1, h6])
    r3 = net.ping([h2, h6])

    assert r1 == 0, r1
    assert r2 == 0, r2
    assert r3 == 0, r3


def test_connectivity_2(mininet, controller):
    net, s1, h1, h2, h3, h4, h5, h6 = mininet
    n1 = net.ping([h1, h3], timeout=1)
    n2 = net.ping([h1, h4], timeout=1)
    n3 = net.ping([h1, h5], timeout=1)

    assert n1 == 100, n1
    assert n2 == 100, n2
    assert n3 == 100, n3


def test_connectivity_3(mininet, controller):
    net, s1, h1, h2, h3, h4, h5, h6 = mininet
    n4 = net.ping([h2, h3], timeout=1)
    n5 = net.ping([h2, h4], timeout=1)
    n6 = net.ping([h2, h5], timeout=1)

    assert n4 == 100, n4
    assert n5 == 100, n5
    assert n6 == 100, n6


def test_connectivity_4(mininet, controller):
    net, s1, h1, h2, h3, h4, h5, h6 = mininet
    n7 = net.ping([h6, h3], timeout=1)
    n8 = net.ping([h6, h4], timeout=1)
    n9 = net.ping([h6, h5], timeout=1)

    assert n7 == 100, n7
    assert n8 == 100, n8
    assert n9 == 100, n9


def test_connectivity_5(mininet, controller):
    net, s1, h1, h2, h3, h4, h5, h6 = mininet
    r4 = net.ping([h3, h4])
    r5 = net.ping([h3, h5])
    r6 = net.ping([h4, h5])

    assert r4 == 0, r4
    assert r5 == 0, r5
    assert r6 == 0, r6


def test_mac_table(mininet, controller):
    assert filecmp.cmp("tests/task_2/test_2.out", "task_2.out") == True


def test_arp_scan_1(mininet, controller):
    net, s1, h1, h2, h3, h4, h5, h6 = mininet

    r = h1.cmdPrint("arp-scan -t 3000 10.0.0.0/24")
    print(r)
    assert "10.0.0.2" in r
    assert "10.0.0.3" not in r
    assert "10.0.0.4" not in r
    assert "10.0.0.5" not in r
    assert "10.0.0.6" in r


def test_arp_scan_2(mininet, controller):
    net, s1, h1, h2, h3, h4, h5, h6 = mininet

    r = h2.cmdPrint("arp-scan -t 3000 10.0.0.0/24")
    print(r)
    assert "10.0.0.1" in r
    assert "10.0.0.3" not in r
    assert "10.0.0.4" not in r
    assert "10.0.0.5" not in r
    assert "10.0.0.6" in r


def test_arp_scan_3(mininet, controller):
    net, s1, h1, h2, h3, h4, h5, h6 = mininet

    r = h6.cmdPrint("arp-scan -t 3000 10.0.0.0/24")
    print(r)
    assert "10.0.0.2" in r
    assert "10.0.0.3" not in r
    assert "10.0.0.4" not in r
    assert "10.0.0.5" not in r
    assert "10.0.0.1" in r


def test_arp_scan_4(mininet, controller):
    net, s1, h1, h2, h3, h4, h5, h6 = mininet

    r = h3.cmdPrint("arp-scan -t 3000 10.0.0.0/24")
    print(r)
    assert "10.0.0.5" in r
    assert "10.0.0.1" not in r
    assert "10.0.0.2" not in r
    assert "10.0.0.6" not in r
    assert "10.0.0.4" in r


def test_arp_scan_5(mininet, controller):
    net, s1, h1, h2, h3, h4, h5, h6 = mininet

    r = h4.cmdPrint("arp-scan -t 3000 10.0.0.0/24")
    print(r)
    assert "10.0.0.5" in r
    assert "10.0.0.1" not in r
    assert "10.0.0.2" not in r
    assert "10.0.0.6" not in r
    assert "10.0.0.3" in r


def test_arp_scan_6(mininet, controller):
    net, s1, h1, h2, h3, h4, h5, h6 = mininet

    r = h5.cmdPrint("arp-scan -t 3000 10.0.0.0/24")
    print(r)
    assert "10.0.0.4" in r
    assert "10.0.0.1" not in r
    assert "10.0.0.2" not in r
    assert "10.0.0.6" not in r
    assert "10.0.0.3" in r
