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

                                   
       
        # Criação do Controlador para ligacao ao Switch principal de Layer 3
        
        c0 = net.addController( 'c0',  ip='127.0.0.1', port=6653, protocols='OpenFlow13')
        
        # Criação do Controlador para ligacao aos Switchs de Layer 2
        
        c1 = net.addController( 'c1', port=6633, ip='127.0.0.1', protocols='OpenFlow13')
        "cmap = { 's1': c0, 's2': c1, 's3': c1, 's4': c1}"
        

       # Criação de Utilizadores com respetivo ip e Switchs de Layer 3 e Layer 2
        
        s1 = net.addSwitch('s1', dpid='0000000000000001', protocols='OpenFlow13')
        s2 = net.addSwitch( 's2', dpid='0000000000000002', protocols='OpenFlow13' )
        s3 = net.addSwitch( 's3', dpid='0000000000000003', protocols='OpenFlow13' )
        s4 = net.addSwitch( 's4', dpid='0000000000000004', protocols='OpenFlow13' )

       # Criação de Routers e ligação entre eles
        
        rRedeA = net.addRouter('rA', ip='10.0.1.1/24', protocols='OpenFlow13')
        rRedeB = net.addRouter( 'rB', ip='10.0.2.1/24', protocols='OpenFlow13')
        rRedeC = net.addRouter( 'rC', ip='10.0.3.1/24', protocols='OpenFlow13')
        
        r1r3 = net.addLink ( 'rA', 'rC', delay='5ms') # Ligação entre Router Rede A e Router Rede C
        r1r2 = net.addLink ( 'rA', 'rB') # Ligação entre Router Rede A e Router Rede B
        r2r3 = net.addLink ( 'rB', 'rC') # Ligação entre Router Rede A e Router Rede C
        
        # Rede A
        
        h1 = net.addHost( 'h1', ip='10.0.1.5/24', mac='00:00:00:00:00:01', defaultRoute='via 10.0.1.254')
        h2 = net.addHost( 'h2', ip='10.0.1.8/24', mac='00:00:00:00:00:02', defaultRoute='via 10.0.1.254')
        h3 = net.addHost( 'h3', ip='10.0.1.10/24', mac='00:00:00:00:00:03', defaultRoute='via 10.0.1.254')
        
        # Rede B
        
        h4 = net.addHost( 'h4', ip='10.0.2.6/24', mac='00:00:00:00:00:04', defaultRoute='via 10.0.2.254')
        h5 = net.addHost( 'h5', ip='10.0.2.8/24', mac='00:00:00:00:00:05', defaultRoute='via 10.0.2.254' )
        h6 = net.addHost( 'h6', ip='10.0.2.10/24', mac='00:00:00:00:00:06', defaultRoute='via 10.0.2.254' )
        
        # Rede C
        
        h7 = net.addHost( 'h7', ip='10.0.3.6/24', mac='00:00:00:00:00:07', defaultRoute='via 10.0.3.254')
        h8 = net.addHost( 'h8', ip='10.0.3.9/24', mac='00:00:00:00:00:08', defaultRoute='via 10.0.3.254')
        h9 = net.addHost( 'h9', ip='10.0.3.10/24', mac='00:00:00:00:00:09', defaultroute='via 10.0.3.254')
        


        # Ligação entre Switchs
        
        l1 = net.addLink ( 's1', 's2', delay='5ms') # Ligação Switch layer 3 com primeiro switch de layer 2 e perdas de 5ms
        l2 = net.addLink ( 's1', 's3' ) # Ligação Switch layer 3 com segundo switch de layer 2
        l3 = net.addLink ( 's1', 's4' ) # Ligação Switch layer 3 com terceiro switch de layer 2
        
        # Ligação entre Routers e Switchs
        
        r1l1 = net.addLink ( 'rA', 's1') # Ligação entre Router da rede A e Switch da R&D Division
        r1l2 = net.addLink ( 'rB', 's2') # Ligação entre Router da rede B e Switch da Divisao Executiva
        r1l3 = net.addLink ( 'rC', 's3') # Ligação entre Router da rede B e Switch da Divisao Executiva
        
        
        
        # Ligação entre Switchs e Utilizadores Rede A
        
        net.addLink( 's2', 'h1' ) # Ligação Switch1 e Utilizador 1
        net.addLink( 's2', 'h2', bw=100 ) # Ligação Switch1 e Utilizador 2
        net.addLink( 's2', 'h3' ) # Ligação Switch1 e Utilizador 3
        
        # Ligação entre Switchs e Utilizadores Rede B
        
        net.addLink( 's3', 'h4' ) # Ligação Switch 2 e Utilizador 4
        net.addLink( 's3', 'h5' ) # Ligação Switch 2 e Utilizador 5
        net.addLink( 's3', 'h6', delay='5ms' ) # Ligação Switch 2 e Utilizador 6 com atrasos de 5ms
        
        # Ligação entre Switchs e Utilizadores Rede C
        
        net.addLink( 's4', 'h7' ) # Ligação Switch 3 e Utilizador 7
        net.addLink( 's4', 'h8' ) # Ligação Switch 3 e Utilizador 8
        net.addLink( 's4', 'h9', loss=10 ) # Ligação Switch 3 e Utilizador 9 com perdas em 10%
        
        
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
