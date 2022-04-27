from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController, Ryu
from mininet.topolib import TreeTopo
from mininet.log import info
from mininet.log import setLogLevel
from mininet.node import Node
from subprocess import call
from mininet.cli import CLI
from mininet.link import TCLink, Intf



class RDSTopo( Topo ):
    "Topologia de Exercicio 2"

    def build( self ):
        "Desenvolvimento da topologia"
        
        net = Mininet( controller=RemoteController, switch=OVSSwitch, link=TCLink, waitConnected=True)

                                   
       
        # Criação do Controlador para ligacao ao Switch principal de Layer 3
        
        c0 = net.addController( 'c0',  ip='127.0.0.1', port=6653, controller=RemoteController, mac='00:00:00:00:00:04', protocol='tcp')
        
        # Criação do Controlador para ligacao aos Switchs de Layer 2
        
        c1 = net.addController( 'c1', port=6633, controller=RemoteController, ip='127.0.0.1', mac='00:00:00:00:00:05', protocol='tcp')
        "c2 = net.addController( 's3', port=6633, controller=RemoteController, ip='127.0.0.1', protocol='tcp')"
        "c3 = net.addController( 's4', port=6633, controller=RemoteController, ip='127.0.0.1', protocol='tcp')"
        cmap = { 's1': c1, 's2': c1, 's3': c1, 's4': c1}
        

       # Criação de Utilizadores com respetivo ip e Switchs de Layer 3 e Layer 2
        
        l3Switch = self.addSwitch('s1')
        l2SwitchTwo = self.addSwitch( 's2' )
        l2SwitchThree = self.addSwitch( 's3' )
        l2SwitchFour = self.addSwitch( 's4' )
        
        # Rede A
        
        h1 = self.addHost( 'h1', ip='10.0.1.1', mac='10:00:00:00:00:01', defaultRoute='via 10.0.1.254')
        h2 = self.addHost( 'h2', ip='10.0.1.2', mac='10:00:00:00:00:02', defaultRoute='via 10.0.1.254')
        h2 = self.addHost( 'h3', ip='10.0.1.3', mac='10:00:00:00:00:03', defaultRoute='via 10.0.1.254')
        
        # Rede B
        
        h4 = self.addHost( 'h4', ip='10.0.2.1', mac='20:00:00:00:00:01', defaultRoute='via 10.0.2.254')
        h5 = self.addHost( 'h5', ip='10.0.2.6', mac='20:00:00:00:00:02', defaultRoute='via 10.0.2.254' )
        h6 = self.addHost( 'h6', ip='10.0.2.10', mac='20:00:00:00:00:03', defaultRoute='via 10.0.2.254' )
        
        # Rede C
        
        h7 = self.addHost( 'h7', ip='10.0.3.6', mac='30:00:00:00:00:01', defaultRoute='via 10.0.3.254')
        h8 = self.addHost( 'h8', ip='10.0.3.7', mac='30:00:00:00:00:02', defaultRoute='via 10.0.3.254')
        h9 = self.addHost( 'h9', ip='10.0.3.9', mac='30:00:00:00:00:03', defaultroute='via 10.0.2.254')
        


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
        
        
        net.build()
        
        c0.start()
        c1.start()
        

topos = { 'mytopo': ( lambda: RDSTopo() ) }
