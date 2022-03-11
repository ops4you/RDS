from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        hostOne = self.addHost( 'h1' )
        hostTwo = self.addHost( 'h2' )
        hostThree = self.addHost( 'h3' )
        hostFour = self.addHost( 'h4' )
        l2Switch = self.addSwitch( 's1' )

        # Add links
        self.addLink( hostOne, l2Switch )
        self.addLink( hostTwo, l2Switch )
        self.addLink( hostThree, l2Switch )
        self.addLink( hostFour, l2Switch )


topos = { 'mytopo': ( lambda: MyTopo() ) }
