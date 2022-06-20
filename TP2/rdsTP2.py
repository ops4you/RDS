#coding=utf-8

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import info
from mininet.log import setLogLevel
from mininet.link import TCLink
from subprocess import call


def topo():
        "Desenvolvimento da topologia"
        
        net = Mininet( controller=RemoteController, switch=OVSSwitch)

                                   
       
        #Criação do Controlador para ligacao ao Switch principal de Layer 3
        
        c0 = net.addController( 'c0',  ip='127.0.0.1', port=6653, protocols='OpenFlow13')
        
        # Criação do Controlador para ligacao aos Switchs de Layer 2
        
        c1 = net.addController( 'c1', port=6633, ip='127.0.0.1', protocols='OpenFlow13')
        

        s1 = net.addSwitch( 's1', dpid='0000000000000005', protocols='OpenFlow13' ) # Switch Secundário de Layer2 Rede A
        s2 = net.addSwitch( 's2', dpid='0000000000000006', protocols='OpenFlow13' ) # Switch Secundário de Layer2 Rede B
        s3 = net.addSwitch( 's3', dpid='0000000000000007', protocols='OpenFlow13' ) # Switch Secundário de Layer2 Rede C


       # Adição de Switchs
        
        r1 = net.addSwitch( 'r1', dpid='0000000000000001', protocols='OpenFlow13') # Switch/Router Principal de Layer3 Rede A
        r2 = net.addSwitch( 'r2', dpid='0000000000000002', protocols='OpenFlow13') # Switch/Router Principal de Layer3 Rede B
        r3 = net.addSwitch( 'r3', dpid='0000000000000003', protocols='OpenFlow13') # Switch/Router Principal de Layer3 Rede C
        


	# Criação de Utilizadores com respetivo ip e Switchs de Layer 3 e Layer 2
        
        # Rede A
        
        h1 = net.addHost( 'h1', ip='10.0.1.1/24', mac='00:00:00:00:00:01', defaultRoute='via 10.0.1.254')
        h2 = net.addHost( 'h2', ip='10.0.1.2/24', mac='00:00:00:00:00:02', defaultRoute='via 10.0.1.254')
        h3 = net.addHost( 'h3', ip='10.0.1.3/24', mac='00:00:00:00:00:03', defaultRoute='via 10.0.1.254')
        
        # Rede B
        
        h4 = net.addHost( 'h4', ip='10.0.2.1/24', mac='00:00:00:00:00:04', defaultRoute='via 10.0.2.254')
        h5 = net.addHost( 'h5', ip='10.0.2.2/24', mac='00:00:00:00:00:05', defaultRoute='via 10.0.2.254' )
        h6 = net.addHost( 'h6', ip='10.0.2.3/24', mac='00:00:00:00:00:06', defaultRoute='via 10.0.2.254' )
        
        # Rede C
        
        h7 = net.addHost( 'h7', ip='10.0.3.1/24', mac='00:00:00:00:00:07', defaultRoute='via 10.0.3.254')
        h8 = net.addHost( 'h8', ip='10.0.3.2/24', mac='00:00:00:00:00:08', defaultRoute='via 10.0.3.254')
        h9 = net.addHost( 'h9', ip='10.0.3.3/24', mac='00:00:00:00:00:09', defaultRoute='via 10.0.3.254')
        
        # Ligação entre Routers e Switchs
        
        net.addLink ( r1, s1) # Ligação Switch/Router layer 3 com Switch Layer 2 Rede A
        net.addLink ( r2, s2 ) # Ligação Switch/Router layer 3 com Switch Layer 2 Rede B
        net.addLink ( r3, s3 ) # Ligação Switch/Router layer 3 com Switch Layer 2 Rede C

        # Ligação entre Routers Principais
        
        net.addLink ( r1, r2) # Ligação Switch/Router layer 3 Rede A com Rede B
        net.addLink ( r1, r3, delay='5ms') # Ligação Switch/Router layer 3 Rede A com Rede C
        net.addLink ( r2, r3 ) # Ligação Switch/Router layer 3 Rede B com Rede C
        
        # Ligação entre Switchs e Utilizadores Rede A
        
        net.addLink( s1, h1 , bw=100) # Ligação Switch1 e Utilizador 1 e bandwidth de 100
        net.addLink( s1, h2 ) # Ligação Switch1 e Utilizador 2
        net.addLink( s1, h3 ) # Ligação Switch1 e Utilizador 3
        
        # Ligação entre Switchs e Utilizadores Rede B
        
        net.addLink( s2, h4 ) # Ligação Switch 2 e Utilizador 4
        net.addLink( s2, h5 ) # Ligação Switch 2 e Utilizador 5
        net.addLink( s2, h6, delay='5ms' ) # Ligação Switch 2 e Utilizador 6 com atrasos de 5ms
        
        # Ligação entre Switchs e Utilizadores Rede C
        
        net.addLink( s3, h7 ) # Ligação Switch 3 e Utilizador 7
        net.addLink( s3, h8 ) # Ligação Switch 3 e Utilizador 8
        net.addLink( s3, h9, loss=10) # Ligação Switch 3 e Utilizador 9 com perdas em 10%
        
        
        net.build()
        
	# Inicialização Switchs(Routers) Layer 3
        r1.start([c0])
        r2.start([c0])
        r3.start([c0])
        
        # Inicialização Switchs(Routers) Layer 2
        s1.start([c1])
        s2.start([c1])
        s3.start([c1])
        
        
        CLI(net)
        net.stop()

if __name__ == '__main__':
   setLogLevel ('info')
   topo()
