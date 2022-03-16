from mininet.topo import Topo

class RDSTopo( Topo ):
    "Topologia de Exercicio 1"

    def build( self ):
        "Desenvolvimento da topologia"

        # Criação de Utilizadores e Switch
        
        hostOne = self.addHost( 'h1' )
        hostTwo = self.addHost( 'h2' )
        hostThree = self.addHost( 'h3' )
        hostFour = self.addHost( 'h4' )
        l2Switch = self.addSwitch( 's1' )

        # Ligação entre Switch e Hosts
        
        self.addLink( hostOne, l2Switch ) # Ligação Utilizador 1 e Switch 
        self.addLink( hostTwo, l2Switch ) # Ligação Utilizador 2 e Switch
        self.addLink( hostThree, l2Switch ) # Ligação Utilizador 3 e Switch
        self.addLink( hostFour, l2Switch ) # Ligação Utilizador 4 e Switch


topos = { 'mytopo': ( lambda: RDSTopo() ) }
