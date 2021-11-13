"""IIT KGP sample topology

"""

from mininet.topo import Topo
from mininet.link import TCLink

class MyTopo( Topo ):


    def build( self ):

        # Add hosts and switches
        simHost = self.addHost( 'H0' )
        hostel1H1 = self.addHost( 'H1' )
        hostel1H2 = self.addHost( 'H2' )
        hostelSwitch1 = self.addSwitch( 'S1' )
        hostel2H3 = self.addHost( 'H3' )
        hostel2H4 = self.addHost( 'H4' )
        hostelSwitch2 = self.addSwitch( 'S2' )
        hostel3H5 = self.addHost( 'H6' )
        hostel3H6 = self.addHost( 'H5' )
        hostelSwitch3 = self.addSwitch( 'S3' )
        dpid = 256 
        aggSwitch1 = self.addSwitch( 'AS1', dpid='%x' % dpid  )
        
        acad1H7 = self.addHost( 'H7' )
        acad1H8 = self.addHost( 'H8' )
        acadSwitch1 = self.addSwitch( 'S4' )
        acad2H9 = self.addHost( 'H7' )
        acad2H10 = self.addHost( 'H8' )
        acadSwitch2 = self.addSwitch( 'S5' )
        dpid = dpid + 16
        aggSwitch2 = self.addSwitch( 'AS2', dpid='%x' % dpid )
        
        resH11 = self.addHost( 'H11' )
        resH12 = self.addHost( 'H12' )
        resSwitch = self.addSwitch( 'S6' )
        
        dpid = dpid + 16
        cicCoreSwitch = self.addSwitch( 'CIC', dpid='%x' % dpid )
        
        # Add links in hostel 1
        self.addLink( hostel1H1, hostelSwitch1, cls=TCLink, bw=30, delay='2ms' )
        self.addLink( hostel1H2, hostelSwitch1, cls=TCLink, bw=10, delay='2ms' )
        self.addLink( hostelSwitch1, aggSwitch1, cls=TCLink, bw=20, delay='2ms' )
        # Add links in hostel 2
        self.addLink( hostel2H3, hostelSwitch2, cls=TCLink, bw=10, delay='2ms' )
        self.addLink( hostel2H4, hostelSwitch2, cls=TCLink, bw=10, delay='2ms' )
        self.addLink( hostelSwitch2, aggSwitch1, cls=TCLink, bw=10, delay='2ms' )
        # Add links in hostel 3
        self.addLink( hostel3H5, hostelSwitch3, cls=TCLink, bw=10, delay='2ms' )
        self.addLink( hostel3H6, hostelSwitch3, cls=TCLink, bw=10, delay='2ms' )
        self.addLink( hostelSwitch3, aggSwitch1, cls=TCLink, bw=10, delay='2ms' )
        # Add links in academic area 1
        self.addLink( acad1H7, acadSwitch1, cls=TCLink, bw=10, delay='2ms' )
        self.addLink( acad1H8, acadSwitch1, cls=TCLink, bw=10, delay='2ms' )
        self.addLink( acadSwitch1, aggSwitch2, cls=TCLink, bw=20, delay='2ms' )
        # Add links in academic area 2
        self.addLink( acad2H9, acadSwitch2, cls=TCLink, bw=10, delay='2ms' )
        self.addLink( acad2H10, acadSwitch2, cls=TCLink, bw=10, delay='2ms' )
        self.addLink( acadSwitch2, aggSwitch2, cls=TCLink, bw=20, delay='2ms' )
        # Add links in residential area
        self.addLink( resH11, resSwitch, cls=TCLink, bw=10, delay='2ms' )
        self.addLink( resH12, resSwitch, cls=TCLink, bw=10, delay='2ms' )
        
        # Add links to CIC core switch
        self.addLink( resSwitch, cicCoreSwitch, cls=TCLink, bw=20, delay='2ms' ) 
        self.addLink( aggSwitch1, cicCoreSwitch, cls=TCLink, bw=30, delay='2ms' )
        self.addLink( aggSwitch2, cicCoreSwitch, cls=TCLink, bw=40, delay='2ms' )   
        self.addLink( simHost, cicCoreSwitch, cls=TCLink, bw=50, delay='2ms' )   

topos = { 'mytopo': ( lambda: MyTopo() ) }