"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo
from mininet.util import irange

class MyTopo( Topo ):

    def build( self ):
        self.levels = []
        rootSwitch = self.addSwitch( 's1' )
        for i in irange( 1, 4 ):
            level = self.buildLevel( i )
            self.levels.append( level )
            for switch in level:
                self.addLink( rootSwitch, switch )
 
    def buildLevel( self, loc ):
 
        dpid = ( loc * 16 ) + 1
        switch = self.addSwitch( 's1r%s' % loc, dpid='%x' % dpid )
 
        for n in irange( 1, 4 ):
            host = self.addHost( 'h%sr%s' % ( n, loc ) )
            self.addLink( switch, host )
 
        # Return list of top-of-rack switches for this rack
        return [switch]  


topos = { 'mytopo': ( lambda: MyTopo() ) }