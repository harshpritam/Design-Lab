from mininet.topo import Topo
from mininet.util import irange

class MyTopo( Topo ):

    def build( self , rows=2, columns=2):
        self.levels = []
        rootSwitch = self.addSwitch( 's1' )
        for i in irange( 1, rows ):
            level = self.buildLevel( i, columns=columns )
            self.levels.append( level )
            for switch in level:
                self.addLink( rootSwitch, switch )
 
    def buildLevel( self, loc, columns ):
 
        dpid = ( loc * 16 ) + 1
        switch = self.addSwitch( 's1r%s' % loc, dpid='%x' % dpid )
 
        for n in irange( 1, columns ):
            host = self.addHost( 'h%sr%s' % ( n, loc ) )
            self.addLink( switch, host )
 
        # Return list of top switches for this rack
        return [switch]
        


topos = { 'mytopo': MyTopo }