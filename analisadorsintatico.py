from analisadorlexico import *
import pandas as pd

# Lista dos terminais da gramatica
terminal = ['ID', 'Numero', 'char', 'int', 'float', 'function', 'se', 'entao', 'senao', 'enquanto', 'faca', 'repita', 'ate', '<', '<=', '==', '<>', '>', '>=', '+', '-', '*', '/', '^', '=', '(', ')', '{', '}', ';', ':', ',', '$']

# Realiza a leitura da tabela de analise sintatica, campo "names" são as colunas que contem os terminais no arquivo tabelaAnalise.xlsx
tabelaAnalise = pd.read_excel('tabelaAnalise.xlsx', names=terminal)

# Realiza a leitura da tabela de produções, campo "names[Producoes]" é a coluna que contem as produções no arquivo tabelaProducoes.xlsx.
tabelaProducoes = pd.read_excel('tabelaProducoes.xlsx', names=['Producoes'])

# Lê o arquivo de código
arquivo = open("codigo.txt", "r")

# Tabela de Símbolo
tabela = open("tabela-simbolo.txt", "r+")

def lex(token):
    (nome, atr, (linha, coluna)) = getToken(arquivo, token)
    global i
    i += 1
    arquivo.seek(0, 0)
    if atr == NULL:
        atr = '-'
    if nome == 'ERRO':
        print(f"Erro no caractere {atr} \nEncontrado na linha {linha} e coluna {coluna}")
        exit()
    if nome == '$':
        return ('$', 'EOF', (linha, coluna))
    return (nome, atr, (linha, coluna))


class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def imprimir_arvore(self, deep=0):
        indent = "| " * deep # Multiplica pela profundidade do nó para criar identação correta
        print(f"{indent}|- {self.value}")
        for child in self.children:
            child.imprimir_arvore(deep + 1) # Chamada recursiva para cada filho, aumentando profundidade

def removeListaVazia(pilha):
    while pilha and not pilha[-1]:
        pilha.pop()

# Pegar os símbolos terminais com produções válidas para o não-terminal do topo da pilha 
def getSimbolosFromErro(topo):
    linha = tabelaAnalise.loc[topo, :]
    colunas = linha[linha > 0] # Apenas produções válidas
    simbolos = []
    for y in range(0, len(colunas)):
        simbolos.append(colunas.index[y])
        
    return simbolos

# Recebe o numero da linha da tabela de simbolos e retorna o lexema
def getTokenFromTabelaSimbolo(linha):
    tabela.seek(0, 0)
    # Percorre o arquivo da tabela a partir da linha 1 procurando a linha do parâmetro
    for num, row in enumerate(tabela, start=1):
        if num == linha:
            objeto = json.loads(row)
            return objeto['Lexema']


def analisePreditiva():
    global proxToken, pilha, arvore, lastToken
    while pilha:        
        X = pilha[-1] 
        # Se o topo da pilha está no terminal
        if X[-1] in terminal:
            # Verifica se ele é o token correspondente: Se sim-> remove o topo e passa para o proximo token / Se não-> erro.
            if (X[-1] == proxToken[0] or X[-1] == proxToken[1]):                
                pilha[-1].pop()
                removeListaVazia(pilha)
                lastToken = proxToken
                proxToken = lex(i)
            else:
                if proxToken[0] in ['RELOP', 'Operador Aritmético']:
                    print('Erro: Produção (' + str(X[-1]) + ', ' + proxToken[1] + ' ) inesperada após um ' + lastToken[0])
                    break
                else:
                    print(proxToken[0])
                    print('Erro: Caractere ' + proxToken[0] + ' inesperado após um ' + lastToken[0])
                    break
        else:
            # Verifica na tabela preditiva se há uma produção para o token no não-terminal X[-1] (topo da pilha)
            if proxToken[0] in ['RELOP', 'Operador Aritmético'] and tabelaAnalise.loc[X[-1], proxToken[1]] == -1:
                print('Erro: Produção (' + str(X[-1]) + ', ' + proxToken[1] + ' ) inesperada após um ' + lastToken[1])
                break
            elif proxToken[0] not in ['RELOP', 'Operador Aritmético'] and tabelaAnalise.loc[X[-1], proxToken[0]] == -1:
                simbolos = getSimbolosFromErro(X[-1])
                print('Erro: Produção (' + str(X[-1]) + ', ' + proxToken[0] + ' ) inesperada!')
                print('Após um ' + lastToken[0] + ', é esperado os terminais a seguir:', simbolos)
                break
            else:
                # Nó raiz
                if X == ['Programa']:
                    no = arvore
                # Outros nós
                else:
                    # Percorre os filhos do nó anterior
                    for child in no.children:     
                        # Procura nos filhos o topo da pilha                   
                        if child.value == X[-1]:
                            # Atribui ao nó o topo da pilha
                            no = child
                
                if proxToken[0] in ['RELOP', 'Operador Aritmético']:
                    proxTokenAux = proxToken[1]
                else:
                    proxTokenAux = proxToken[0]
                    
                # Pega o valor da produção do Não-terminal x terminal
                valor = tabelaAnalise.loc[X[-1], proxTokenAux]
                
                # Procura o valor na tabela de produções
                resultado = tabelaProducoes.iloc[int(valor) - 1, :]
                
                # Transforma a lista de uma unica string em uma lista de strings
                producao = resultado.values[0].split()
                
                for k in range(0, len(producao)):
                    # Caso de ID e Numero
                    if producao[k] == proxToken[0] and (proxToken[0] == 'ID' or proxToken[0] == 'Numero'):
                        producaoAux = getTokenFromTabelaSimbolo(proxToken[1])
                        no.add_child(Node(producaoAux))
                    # Caso function
                    elif producao[k] == 'ID' and proxToken[0] == 'function':
                        # Primeiro ID do código é a primeira posição da tabela de símbolos
                        producaoAux = getTokenFromTabelaSimbolo(1)
                        no.add_child(Node(producaoAux))
                    else:
                        no.add_child(Node(producao[k]))
                        
                # Remove o topo da lista
                pilha[-1].pop()
                
                # Remover lista vazia do topo da pilha
                removeListaVazia(pilha)
                
                # Se a produção inversa for diferente de epsolon
                if producao[-1] != 'ε': 
                    # Coloque a produção de forma inversa na pilha
                    pilha.append(list(reversed(producao)))
                    
    if len(pilha) == 0 and proxToken[0] == '$':
        arvore.imprimir_arvore()
        print('Cadeia aceita!')
    else:
        print('Cadeia rejeitada!')


i = 1
arvore = Node('Programa')
pilha = []
pilha.append(['Programa'])
proxToken = lex(i)
analisePreditiva()