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
        

       # Adição de Switchs
        
        s1 = net.addSwitch( 's1_P', dpid='0000000000000001', protocols='OpenFlow13') # Switch Principal de Layer3
        s2 = net.addSwitch( 's2_A', dpid='0000000000000002', protocols='OpenFlow13' ) # Switch Secundário de Layer2 Rede A
        s3 = net.addSwitch( 's3_B', dpid='0000000000000003', protocols='OpenFlow13' ) # Switch Secundário de Layer2 Rede B
        s4 = net.addSwitch( 's4_C', dpid='0000000000000004', protocols='OpenFlow13' ) # Switch Secundário de Layer2 Rede C


	# Criação de Utilizadores com respetivo ip e Switchs de Layer 3 e Layer 2
        
        # Rede A
        
        h1 = net.addHost( 'h1_A', ip='10.0.1.1/24', mac='00:00:00:00:00:01', defaultRoute='via 10.0.1.254')
        h2 = net.addHost( 'h2_A', ip='10.0.1.2/24', mac='00:00:00:00:00:02', defaultRoute='via 10.0.1.254')
        h3 = net.addHost( 'h3_A', ip='10.0.1.3/24', mac='00:00:00:00:00:03', defaultRoute='via 10.0.1.254')
        
        # Rede B
        
        h4 = net.addHost( 'h4_B', ip='10.0.2.1/24', mac='00:00:00:00:00:04', defaultRoute='via 10.0.2.254')
        h5 = net.addHost( 'h5_B', ip='10.0.2.2/24', mac='00:00:00:00:00:05', defaultRoute='via 10.0.2.254' )
        h6 = net.addHost( 'h6_B', ip='10.0.2.3/24', mac='00:00:00:00:00:06', defaultRoute='via 10.0.2.254' )
        
        # Rede C
        
        h7 = net.addHost( 'h7_C', ip='10.0.3.1/24', mac='00:00:00:00:00:07', defaultRoute='via 10.0.3.254')
        h8 = net.addHost( 'h8_C', ip='10.0.3.2/24', mac='00:00:00:00:00:07', defaultRoute='via 10.0.3.254')
        h9 = net.addHost( 'h9_C', ip='10.0.3.3/24', mac='00:00:00:00:00:08', defaultRoute='via 10.0.3.254')
        


        # Ligação entre Switchs
        
        net.addLink ( s1, s2, delay='5ms') # Ligação Switch layer 3 com primeiro switch de layer 2 e perdas de 5ms
        net.addLink ( s1, s3 ) # Ligação Switch layer 3 com segundo switch de layer 2
        net.addLink ( s1, s4 ) # Ligação Switch layer 3 com terceiro switch de layer 2
        
        
        # Ligação entre Switchs e Utilizadores Rede A
        
        net.addLink( s2, h1 , bw=100) # Ligação Switch1 e Utilizador 1 e bandwidth de 100
        net.addLink( s2, h2 ) # Ligação Switch1 e Utilizador 2
        net.addLink( s2, h3 ) # Ligação Switch1 e Utilizador 3
        
        # Ligação entre Switchs e Utilizadores Rede B
        
        net.addLink( s3, h4 ) # Ligação Switch 2 e Utilizador 4
        net.addLink( s3, h5 ) # Ligação Switch 2 e Utilizador 5
        net.addLink( s3, h6, delay='5ms' ) # Ligação Switch 2 e Utilizador 6 com atrasos de 5ms
        
        # Ligação entre Switchs e Utilizadores Rede C
        
        net.addLink( s4, h7 ) # Ligação Switch 3 e Utilizador 7
        net.addLink( s4, h8 ) # Ligação Switch 3 e Utilizador 8
        net.addLink( s4, h9, loss=10) # Ligação Switch 3 e Utilizador 9 com perdas em 10%
        
        
        net.build()
        
        c0.start()
        c1.start()

        s1.start([c0])
        s2.start([c1])
        s3.start([c1])
        s4.start([c1])

        CLI(net)
        net.stop()

if __name__ == '__main__':
   setLogLevel ('info')
   topo()
