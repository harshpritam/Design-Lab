"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo
from mininet.link import TCLink

class MyTopo( Topo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        leftHost = self.addHost( 'h1' )
        rightHost = self.addHost( 'h2' )
        guestHost1 = self.addHost( 'gh1' )
        #guestHost2 = self.addHost( 'gh2' )
        leftSwitch = self.addSwitch( 's1' )
        rightSwitch = self.addSwitch( 's2' )

        # Add links
        #linkopts = dict(bw=10, delay='2ms', loss=0, use_htb=True)
        self.addLink( leftHost, leftSwitch, cls=TCLink, bw=10, delay='2ms' )
        self.addLink( leftSwitch, rightSwitch )
        self.addLink( rightSwitch, rightHost, cls=TCLink, bw=10, delay='2ms' )
        self.addLink( leftHost, rightHost, cls=TCLink, bw=10, delay='2ms' )
        #self.addLink( guestHost1, leftHost )
        self.addLink( guestHost1, leftSwitch )


topos = { 'mytopo': ( lambda: MyTopo() ) }