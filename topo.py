#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.node import RemoteController
from mininet.link import TCLink
from time import sleep
TEST_TIME = 300 #seconds
TEST_TYPE = "attack" #normal, attack

class SingleSwitchTopology(Topo):
    "Single switch connected to 10 hosts."
    def build(self):
        switch1 = self.addSwitch('s1')
        for i in range(1,11):
          macId = "00:00:00:00:00:"
          host = self.addHost('h'+str(i), ip='10.1.1.'+str(i)+'/24', mac=macId+str(i).zfill(2),defaultRoute="via 10.1.1.10")
          self.addLink(host, switch1, cls=TCLink, bw=5)


def generateNormalTraffic(TEST_TIME, net):
    print ("Generating NORMAL traffic........." )
    for i in range(1,11):
         host = net.get('h'+str(i))
         command = "bash normal.sh &"
         host.cmd(command)
    sleep(TEST_TIME)
    net.stop()

def generateAttackTraffic(TEST_TIME, net):
    print ("Generating ATTACK traffic.........")
    h1 = net.get('h1')
    cmd1 = "bash attack.sh &"
    h1.cmd(cmd1)

    sleep(TEST_TIME)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topo = SingleSwitchTopology()
    c1 = RemoteController('c1', ip='127.0.0.1')
    net = Mininet(topo=topo, controller=c1)
    net.start()

    if TEST_TYPE == "normal":
        generateNormalTraffic(TEST_TIME, net)

    elif TEST_TYPE == "attack":
        generateAttackTraffic(TEST_TIME, net)
