from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController, Ryu
from mininet.topolib import TreeTopo
from mininet.log import setLogLevel
from mininet.cli import CLI


def topo():
        "Desenvolvimento da topologia"

        net = Mininet( controller=RemoteController, switch=OVSSwitch,
                   waitConnected=True )


        # Criação de Utilizadores e Switch
        
        l2Switch = net.addSwitch( 's1' )
        hostOne = net.addHost( 'h1' )
        hostTwo = net.addHost( 'h2' )
        hostThree = net.addHost( 'h3' )
        hostFour = net.addHost( 'h4' )
        
        # Criação do Controlador para ligacao ao Switch de Layer 2
        
        c0 = net.addController( 'c0',  ip='127.0.0.1', port=6653, protocols='OpenFlow13')

        # Ligação entre Switch e Hosts
        
        net.addLink( 's1', 'h1' ) # Ligação Utilizador 1 e Switch Layer 2
        net.addLink( 's1', 'h2' ) # Ligação Utilizador 2 e Switch Layer 2
        net.addLink( 's1', 'h3' ) # Ligação Utilizador 3 e Switch Layer 2
        net.addLink( 's1', 'h4' ) # Ligação Utilizador 4 e Switch Layer 2

        
        net.build()
        
        c0.start()
        l2Switch.start([c0])

        CLI(net)
        net.stop()



if __name__ == '__main__':
   setLogLevel ('info')
   topo()
