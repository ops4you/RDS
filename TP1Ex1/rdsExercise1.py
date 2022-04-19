from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController, Ryu
from mininet.topolib import TreeTopo
from mininet.log import setLogLevel
from mininet.cli import CLI

class RDSTopo( Topo ):
    "Topologia de Exercicio 1"

    def build( self ):
        "Desenvolvimento da topologia"

        net = Mininet( controller=RemoteController, switch=OVSSwitch,
                   waitConnected=True )


        # Criação de Utilizadores e Switch
        
        l2Switch = self.addSwitch( 's1' )
        hostOne = self.addHost( 'h1' )
        hostTwo = self.addHost( 'h2' )
        hostThree = self.addHost( 'h3' )
        hostFour = self.addHost( 'h4' )
        
        # Criação do Controlador para ligacao ao Switch de Layer 2
        
        c1 = net.addController( 's1', port=6653)
        c8 = RemoteController( 'c1', ip='127.0.0.1')


        # Ligação entre Switch e Hosts
        
        self.addLink( 's1', 'h1' ) # Ligação Utilizador 1 e Switch Layer 2
        self.addLink( 's1', 'h2' ) # Ligação Utilizador 2 e Switch Layer 2
        self.addLink( 's1', 'h3' ) # Ligação Utilizador 3 e Switch Layer 2
        self.addLink( 's1', 'h4' ) # Ligação Utilizador 4 e Switch Layer 2


topos = { 'mytopo': ( lambda: RDSTopo() ) }
