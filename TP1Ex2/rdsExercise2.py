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
                   waitConnected=True)


       # Criação de Utilizadores com respetivo ip e Switchs de Layer 3 e Layer 2
        
        l3Switch = self.addSwitch('s1')
        l2Switch = self.addSwitch( 's2' )
        l2Switch = self.addSwitch( 's3' )
        l2Switch = self.addSwitch( 's4' )
        
        hostOne = self.addHost( 'h1', ip='10.0.1.1')
        hostTwo = self.addHost( 'h2', ip='10.0.1.2' )
        hostThree = self.addHost( 'h3', ip='10.0.1.3')
        
        hostFour = self.addHost( 'h4', ip='10.0.2.1' )
        hostFive = self.addHost( 'h5', ip='10.0.2.6' )
        hostSix = self.addHost( 'h6', ip='10.0.2.10' )
        
        
        hostSeven = self.addHost( 'h7', ip='10.0.3.6' )
        hostEight = self.addHost( 'h8', ip='10.0.3.7' )
        hostNine = self.addHost( 'h9', ip='10.0.3.9')
        
                
       
        # Criação do Controlador para ligacao ao Switch principal de Layer 3
        
        c1 = net.addController( 's1', port=6653)
        c8 = RemoteController( 'c1', ip='127.0.0.1')
        
      
        # Ligação entre Switchs
        
        self.addLink ( 's1', 's2', delay='5ms') # Ligação Switch layer 3 com primeiro switch de layer 2 e perdas de 5ms
        self.addLink ( 's1', 's3' ) # Ligação Switch layer 3 com segundo switch de layer 2
        self.addLink ( 's1', 's4' ) # Ligação Switch layer 3 com terceiro switch de layer 2
        
        
        # Ligação entre Switchs e Utilizadores Seccao A
        
        self.addLink( 's2', 'h1' ) # Ligação Switch1 e Utilizador 1
        self.addLink( 's2', 'h2', bw=100 ) # Ligação Switch1 e Utilizador 2
        self.addLink( 's2', 'h3' ) # Ligação Switch1 e Utilizador 3
        
        # Ligação entre Switchs e Utilizadores Seccao B
        
        self.addLink( 's3', 'h4' ) # Ligação Switch 2 e Utilizador 4
        self.addLink( 's3', 'h5' ) # Ligação Switch 2 e Utilizador 5
        self.addLink( 's3', 'h6', delay='5ms' ) # Ligação Switch 2 e Utilizador 6 com atrasos de 5ms
        
        # Ligação entre Switchs e Utilizadores Seccao C
        
        self.addLink( 's4', 'h7' ) # Ligação Switch 3 e Utilizador 7
        self.addLink( 's4', 'h8' ) # Ligação Switch 3 e Utilizador 8
        self.addLink( 's4', 'h9', loss=10 ) # Ligação Switch 3 e Utilizador 9 com perdas em 10%

        
        "c2 = net.addController( 's2')"
        "c3 = net.addController( 's3')"
        "c4 = net.addController( 's4')"
        "c9 = RemoteController( 'c2')"
           
topos = { 'mytopo': ( lambda: RDSTopo() ) }
