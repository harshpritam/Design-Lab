from mininet.topo import Topo
from mininet.util import irange

class MyTopo( Topo ):

    def build( self , racks=2, numHosts=2, numSwitches=2):
 
        self.levels = []
        rootSwitches = []
        lastRootSwitch = None
        for i in irange( 1, numSwitches ):
            rootSwitch = self.addSwitch( 's%s' % i )
            rootSwitches.append( rootSwitch )
 
            if lastRootSwitch:
                self.addLink( lastRootSwitch, rootSwitch )
 
            lastRootSwitch = rootSwitch
 
        # Make the final link from the last switch to the first switch
        if numSwitches > 1:
            self.addLink( lastRootSwitch, rootSwitches[0] )
 
        for i in irange( 1, racks ):
            level = self.buildLevel( i, numHosts=numHosts,
                                   numSwitches=numSwitches )
            self.levels.append( level )
 
            for j in range( numSwitches ):
                self.addLink( rootSwitches[j], level[j] )
                
    def buildLevel( self, loc, numHosts, numSwitches ):
 
        switches = []
        for n in irange( 1, numSwitches ):
            dpid = ( loc * 16 ) + n
            switch = self.addSwitch( 's%sr%s' % (n, loc), dpid='%x' % dpid )
            switches.append( switch )
 
        for n in irange( 1, numHosts ):
            host = self.addHost( 'h%sr%s' % ( n, loc ) )
 
            # Add a link from every top switch to the host
            for switch in switches:
                self.addLink( switch, host )
 
        # Return list of top switches for this level
        return switches
        


topos = { 'mytopo': MyTopo }