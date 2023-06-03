from analisadorlexico import * 
from asyncio.windows_events import NULL
import pandas as pd


# lista dos terminais da gramatica
terminal = ['ID', 'Numero','char','int','float','function','se', 'entao','senao','enquanto','faca','repita','ate','<','<=', '==','<>','>','>=','+','-','*','/','^', '=','(',')','{','}',';',':',',','$']


#Realiza a leitura da tabela de analise sintatica, campo "names" são as colunas que contem os terminais no arquivo tabelaAnalise.xlsx
tabelaAnalise = pd.read_excel('tabelaAnalise.xlsx', names= terminal)

# Realiza a leitura da tabela de produções, campo "names[Producoes]" é a coluna que contem as produções no arquivo tabelaProducoes.xlsx.
producoes = pd.read_excel('tabelaProducoes.xlsx', names =['Producoes'])



#Lê o arquivo de código
file = open("codigo.txt", "r")

def lex(token):
    (nome, atr, (linha, coluna)) = getToken(file, token)
    global i
    i += 1
    file.seek(0, 0)
    if atr == NULL:
        atr = '-'
    if nome == 'ERRO':
        print(
            f"Erro no caractere {atr} \nEncontrado na linha {linha} e coluna {coluna}")
        exit()
    if nome == '$':
        return ('$', 'EOF', (linha, coluna))
    return (nome, atr, (linha, coluna))


class Arvore:
    def __init__(self, chave=None):
        self.chave = list(reversed(chave))
        self.lista = []

    def definir_subarvore(self):
        return '%s\n %s' % (self.chave, self.lista)
    
    
def estrutura_floresta(floresta):
    if floresta:
        for j in range(0, len(floresta)):
            print(floresta[j])
    



def removeListaVazia():
  ### remove lista vazia da pilha ###
    if pilha and not pilha[-1]:
        pilha.pop()


def analisePreditiva():
    global proxToken, pilha, floresta
    while pilha:
        X = pilha[-1]

        # Se o topo da pilha está no terminal
        if X[-1] in terminal:
            #verifica se ele é o token correspondente: Se sim-> remove o topo e passa para o proximo token / Se não-> erro. 
            if (X[-1] == proxToken[0] or X[-1] == proxToken[1]):
                pilha[-1].pop()
                removeListaVazia()
                proxToken = lex(i)
            else:
                print('Erro: Caractere ' + proxToken[0] + ' inesperado na Linha ' + str(proxToken[2][0]) + ' Coluna ' + str(proxToken[2][1]))
                break
        else:
            # Verifica na tabela preditiva se há uma produção para o token no não-terminal X[-1] (topo da pilha)
            if (proxToken[0] == 'RELOP' or proxToken[0] == 'Operador Aritimético') and tabelaAnalise.loc[X[-1], proxToken[1]] == -1: #se não tiver retorna erro
                print('Erro: Produção (' +  str(X[-1]) + ', ' + proxToken[1] + ' ) inesperada! Linha ' + str(proxToken[2][0]) + ' Coluna ' + str(proxToken[2][1]))
                break
            elif (proxToken[0] != 'RELOP' and proxToken[0] != 'Operador Aritimético') and tabelaAnalise.loc[X[-1], proxToken[0]] == -1: #se não tiver retorna erro
                print(pilha)
                print('Erro: Produção (' +  str(X[-1]) + ', ' + proxToken[0] + ' ) inesperada! Linha ' + str(proxToken[2][0]) + ' Coluna ' + str(proxToken[2][1]))
                break
            
            else:
                sub_arvore = Arvore(pilha[-1])

                # Pega o valor da produção do Não-terminal, terminal
                if proxToken[0] == 'RELOP' or proxToken [0] == 'Operador Aritimético':
                    valor = tabelaAnalise.loc[X[-1], proxToken[1]]

                    # procura o valor na tabela de produções
                    resultado = producoes.iloc[int(valor)-1, :]

                    # transforma o resultado em uma lista contendo uma unica string
                    transforma = resultado.values

                    # transforma a lista de uma unica string em uma lista de strings
                    producaoinversa = transforma[0].split()
                else:
                    valor = tabelaAnalise.loc[X[-1], proxToken[0]]
                    # procura o valor na tabela de produções
                    resultado = producoes.iloc[int(valor)-1, :]

                    # transforma o resultado em uma lista contendo uma unica string
                    transforma = resultado.values

                    # transforma a lista de uma unica string em uma lista de strings
                    producaoinversa = transforma[0].split()

                for k in range(0, len(producaoinversa)):
                    sub_arvore.lista.append(producaoinversa[k])

                floresta.append(sub_arvore.definir_subarvore())

                # remove o topo da lista
                pilha[-1].pop()

                #se após isso ficar uma lista vazia, remova-a da pilha
                removeListaVazia()

                # se a produção inversa for diferente de epsolon
                if (producaoinversa[-1] != 'ε'):
                    # coloque a produção de forma inversa na pilha
                    pilha.append(list(reversed(producaoinversa)))
                else: #caso seja, não coloque o epsolon na pilha
                    pass

    if len(pilha) == 0 and proxToken[0] == '$':
        print('Cadeia aceita!')
        return floresta
    else:
        print('Cadeia rejeitada!')
                

          
############# "MAIN" ############
i=1
floresta = []
pilha = []
pilha.append(['Programa'])
proxToken = lex(i)
floresta = analisePreditiva()
estrutura_floresta(floresta)