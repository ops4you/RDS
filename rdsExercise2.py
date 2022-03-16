from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.topolib import TreeTopo
from mininet.log import setLogLevel

"c8 = RemoteController( 'c8', ip='127.0.0.1', port=6633 )"


class RDSTopo( Topo ):
    "Topologia de Exercicio 2"

    def build( self ):
        "Criação da Topologia do Exercicio 2 "
        
              
    net = Mininet( controller=OpenFlow, switch=OVSSwitch,
                   waitConnected=True )
                   
 
        # Criação de Utilizadores e Switch
        
        l3SwitchOne = self.addSwitch( 's1' )
        l2SwitchOne = self.addSwitch( 's2' )
        l2SwitchTwo = self.addSwitch( 's3' )
        l2SwitchThree = self.addSwitch( 's4' )
        
        hostOne = self.addHost( 'h1' )
        hostTwo = self.addHost( 'h2' )
        hostThree = self.addHost( 'h3' )
        
        hostFour = self.addHost( 'h4' )
        hostFive = self.addHost( 'h5' )
        hostSix = self.addHost( 'h6' )
        
        
        hostSeve = self.addHost( 'h7' )
        hostEight = self.addHost( 'h8' )
        hostNine = self.addHost( 'h9' )
        
      
      
        # Ligação entre Switchs
        
        self.addLink ( l3SwitchOne, l2SwitchOne )
        self.addLink ( l3SwitchOne, l2SwitchTwo )
        self.addLink ( l3SwitchOne, l2SwitchThree )
        
        
        # Ligação entre Switchs e Utilizadores Seccao A
        
        self.addLink( l2SwitchOne, hostOne ) # Ligação Switch1 e Utilizador 1
        self.addLink( l2SwitchOne, hostTwo ) # Ligação Switch1 e Utilizador 2
        self.addLink( l2SwitchOne, hostThree ) # Ligação Switch1 e Utilizador 3
        
        # Ligação entre Switchs e Utilizadores Seccao B
        
        self.addLink( l2SwitchTwo, hostFour ) # Ligação Switch 2 e Utilizador 4
        self.addLink( l2SwitchTwo, hostFive ) # Ligação Switch 2 e Utilizador 5
        self.addLink( l2SwitchTwo, hostSix ) # Ligação Switch 2 e Utilizador 6
        
        # Ligação entre Switchs e Utilizadores Seccao C
        
        self.addLink( l2SwitchThree, hostSeven ) # Ligação Switch 3 e Utilizador 7
        self.addLink( l2SwitchThree, hostEight ) # Ligação Switch 3 e Utilizador 8
        self.addLink( l2SwitchThree, hostNine ) # Ligação Switch 3 e Utilizador 9
  
  info( "*** Criação do Controlador a fim de ser chamado nos Switchs da Topologia\n" )
  
	    c1 = net.addController( 'c1', port=6633 )
	    c2 = net.addController( 'c2', port=6634 )
	    c3 = net.addController( 'c3', port=6635 )
	    c4 = net.addController( 'c4', port=6636 )
	    
	    info( "*** Inicializar a rede\n" )
		    net.build()
		    c1.start()
		    c2.start()
		    c3.start()
		    c4.start()
			    s1.start( [ c1 ] )
			    s2.start( [ c2 ] )
			    s3.start( [ c3 ] )
			    s4.start( [ c4 ] )
			    
    "c8 = RemoteController( 'c1', ip='127.0.0.1', port=6633 )"
    "c8 = RemoteController( 'c2', ip='127.0.0.2', port=6634 )"
    "c8 = RemoteController( 'c3', ip='127.0.0.3', port=6635 )"
    "c8 = RemoteController( 'c4', ip='127.0.0.4', port=6636 )"
    
    info( "*** Teste de Rede\n" )
    net.pingAll()


    info( "*** Paragem\n" )
    net.stop()
        
         

topos = { 'mytopo': ( lambda: RDSTopo() ) }
