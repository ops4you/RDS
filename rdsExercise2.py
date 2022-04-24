from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController, Ryu
from mininet.topolib import TreeTopo
from mininet.log import info
from mininet.log import setLogLevel
from mininet.link import TCLink
from subprocess import call
from mininet.cli import CLI



class RDSTopo( Topo ):
    "Topologia de Exercicio 2"

    def build( self ):
        "Desenvolvimento da topologia"
        
        net = Mininet( controller=RemoteController, switch=OVSSwitch, link=TCLink, waitConnected=True)
                   
                                   
       
        # Criação do Controlador para ligacao ao Switch principal de Layer 3
        
        c0 = net.addController( 'c0', port=6653, controller=RemoteController, ip='127.0.0.1', protocol='tcp')
        
        # Criação do Controlador para ligacao ao Switch principal de Layer 3
        
        c1 = net.addController( 's2', port=6633, controller=RemoteController, ip='127.0.0.1', protocol='tcp')
        c2 = net.addController( 's3', port=6633, controller=RemoteController, ip='127.0.0.1', protocol='tcp')
        c3 = net.addController( 's4', port=6633, controller=RemoteController, ip='127.0.0.1', protocol='tcp')


       # Criação de Utilizadores com respetivo ip e Switchs de Layer 3 e Layer 2
        
        l3Switch = self.addSwitch('s1')
        l2SwitchTwo = self.addSwitch( 's2' )
        l2SwitchThree = self.addSwitch( 's3' )
        l2SwitchFour = self.addSwitch( 's4' )
        
        hostOne = self.addHost( 'h1', ip='10.0.1.1', defaultRoute='via 10.0.1.254')
        hostTwo = self.addHost( 'h2', ip='10.0.1.2', defaultRoute='via 10.0.1.254')
        hostThree = self.addHost( 'h3', ip='10.0.1.3', defaultRoute='via 10.0.1.254')
        
        hostFour = self.addHost( 'h4', ip='10.0.2.1', defaultRoute='via 10.0.2.254')
        hostFive = self.addHost( 'h5', ip='10.0.2.6', defaultRoute='via 10.0.2.254' )
        hostSix = self.addHost( 'h6', ip='10.0.2.10', defaultRoute='via 10.0.2.254' )
        
        
        hostSeven = self.addHost( 'h7', ip='10.0.3.6', defaultRoute='via 10.0.3.254')
        hostEight = self.addHost( 'h8', ip='10.0.3.7', defaultRoute='via 10.0.3.254')
        hostNine = self.addHost( 'h9', ip='10.0.3.9', defaultroute='via 10.0.2.254')
        

        
        # Ligação entre Switchs
        
        self.addLink ( 's1', 's2', delay='5ms') # Ligação Switch layer 3 com primeiro switch de layer 2 e perdas de 5ms
        self.addLink ( 's1', 's3' ) # Ligação Switch layer 3 com segundo switch de layer 2
        self.addLink ( 's1', 's4' ) # Ligação Switch layer 3 com terceiro switch de layer 2
        
        
        # Ligação entre Switchs e Utilizadores Rede A
        
        self.addLink( 's2', 'h1' ) # Ligação Switch1 e Utilizador 1
        self.addLink( 's2', 'h2', bw=100 ) # Ligação Switch1 e Utilizador 2
        self.addLink( 's2', 'h3' ) # Ligação Switch1 e Utilizador 3
        
        # Ligação entre Switchs e Utilizadores Rede B
        
        self.addLink( 's3', 'h4' ) # Ligação Switch 2 e Utilizador 4
        self.addLink( 's3', 'h5' ) # Ligação Switch 2 e Utilizador 5
        self.addLink( 's3', 'h6', delay='5ms' ) # Ligação Switch 2 e Utilizador 6 com atrasos de 5ms
        
        # Ligação entre Switchs e Utilizadores Rede C
        
        self.addLink( 's4', 'h7' ) # Ligação Switch 3 e Utilizador 7
        self.addLink( 's4', 'h8' ) # Ligação Switch 3 e Utilizador 8
        self.addLink( 's4', 'h9', loss=10 ) # Ligação Switch 3 e Utilizador 9 com perdas em 10%

topos = { 'mytopo': ( lambda: RDSTopo() ) }
