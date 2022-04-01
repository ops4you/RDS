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
        
        l3SwitchOne = self.addSwitch('s1')
        l2SwitchTwo = self.addSwitch( 's2' )
        l2SwitchThree = self.addSwitch( 's3' )
        l2SwitchFour = self.addSwitch( 's4' )
        
        hostOne = self.addHost( 'h1', ip='127.0.1.1'  )
        hostTwo = self.addHost( 'h2' )
        hostThree = self.addHost( 'h3' )
        
        hostFour = self.addHost( 'h4' )
        hostFive = self.addHost( 'h5' )
        hostSix = self.addHost( 'h6' )
        
        
        hostSeven = self.addHost( 'h7' )
        hostEight = self.addHost( 'h8' )
        hostNine = self.addHost( 'h9' )
        
      
      
        # Ligação entre Switchs
        
        self.addLink ( l3SwitchOne, l2SwitchTwo, delay='5ms' )
        self.addLink ( l3SwitchOne, l2SwitchThree )
        self.addLink ( l3SwitchOne, l2SwitchFour )
        
        
        # Ligação entre Switchs e Utilizadores Seccao A
        
        self.addLink( l2SwitchTwo, hostOne ) # Ligação Switch1 e Utilizador 1
        self.addLink( l2SwitchTwo, hostTwo ) # Ligação Switch1 e Utilizador 2
        self.addLink( l2SwitchTwo, hostThree ) # Ligação Switch1 e Utilizador 3
        
        # Ligação entre Switchs e Utilizadores Seccao B
        
        self.addLink( l2SwitchThree, hostFour ) # Ligação Switch 2 e Utilizador 4
        self.addLink( l2SwitchThree, hostFive ) # Ligação Switch 2 e Utilizador 5
        self.addLink( l2SwitchThree, hostSix ) # Ligação Switch 2 e Utilizador 6
        
        # Ligação entre Switchs e Utilizadores Seccao C
        
        self.addLink( l2SwitchFour, hostSeven ) # Ligação Switch 3 e Utilizador 7
        self.addLink( l2SwitchFour, hostEight ) # Ligação Switch 3 e Utilizador 8
        self.addLink( l2SwitchFour, hostNine ) # Ligação Switch 3 e Utilizador 9
        
       
        ("*** Criação do Controlador a fim de ligar nos Switchs")
        
        c1 = net.addController( 's1', port=6653 )
        "c2 = net.addController( 's2')"
        "c3 = net.addController( 's3')"
        "c4 = net.addController( 's4')"
        
        c8 = RemoteController( 'c1',  ip='127.0.1.0')
        "c9 = RemoteController( 'c2')"
        
   
        


   
topos = { 'mytopo': ( lambda: RDSTopo() ) }
