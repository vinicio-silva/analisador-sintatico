from analisadorlexico import * 
from asyncio.windows_events import NULL
import pandas as pd
import ast


# lista dos terminais da gramatica
terminal = ['ID', 'Numero', 'char', 'int', 'float', 'function', 'se', 'entao', 'senao', 'enquanto', 'faca', 'repita', 'ate', '<', '<=', '==', '<>', '>', '>=', '+', '-', '*', '/', '^', '=', '(', ')', '{', '}', ';', ':', ',', '$']

# Realiza a leitura da tabela de analise sintatica, campo "names" são as colunas que contem os terminais no arquivo tabelaAnalise.xlsx
tabelaAnalise = pd.read_excel('tabelaAnalise.xlsx', names= terminal)

# Realiza a leitura da tabela de produções, campo "names[Producoes]" é a coluna que contem as produções no arquivo tabelaProducoes.xlsx.
tabelaProducoes = pd.read_excel('tabelaProducoes.xlsx', names =['Producoes'])

#Lê o arquivo de código
file = open("codigo.txt", "r")

#Tabela de Símbolo
TABELA_SIMBOLO = open("tabela-simbolo.txt", "r+")

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
        return '%s\n %s\n' % (self.chave, self.lista)
    
    
def estrutura_arvore(arvore, indent=0):
    for nodo in arvore:
        # Separando a entrada em pai e filhos
        nodo = nodo.split("\n")
        pai = ast.literal_eval(nodo[0].strip())
        filhos = ast.literal_eval(nodo[1].strip())

        # Imprimindo o pai
        print('  ' * indent + str(pai))

        # Imprimindo os filhos com setas e profundidade
        for filho in filhos:
            print('  ' * (indent + 1) + "-> Profundidade: " + str(indent + 1) + ", Nó: " + str(filho))
    print('Cadeia aceita!')

def removeListaVazia():
  ### remove lista vazia da pilha ###
    if pilha and not pilha[-1]:
        pilha.pop()

def getProducaoFromErro(topo):
    valor = tabelaAnalise.loc[topo, :]
    colunas = valor[valor > 0 ]
    simbolos = []
    for y in range(0, len(colunas)):
        simbolos.append(colunas.index[y])

    return simbolos

def getTokenFromTabelaSimbolo(linha):
    table = TABELA_SIMBOLO
    table.seek(0, 0)

    for num, row in enumerate(table, start=1):
        if num == linha:
            objeto = json.loads(row)
            return objeto['Lexema'] 
              

def analisePreditiva():
    global proxToken, pilha, arvore, producoes, lastToken
    while pilha:
        X = pilha[-1]

        # Se o topo da pilha está no terminal
        if X[-1] in terminal:
            #verifica se ele é o token correspondente: Se sim-> remove o topo e passa para o proximo token / Se não-> erro. 
            if (X[-1] == proxToken[0] or X[-1] == proxToken[1]):
                pilha[-1].pop()
                removeListaVazia()
                lastToken = proxToken
                proxToken = lex(i)
            else:
                if (proxToken[0] == 'RELOP' or proxToken[0] == 'Operador Aritimético'):
                    print('Erro: Produção (' +  str(X[-1]) + ', ' + proxToken[1] + ' ) inesperada após um ' + lastToken[0])
                    break
                else:
                    print(proxToken[0])
                    print('Erro: Caractere ' + proxToken[0] + ' inesperado após um ' + lastToken[0])
                    break
        else:
            # Verifica na tabela preditiva se há uma produção para o token no não-terminal X[-1] (topo da pilha)
            if (proxToken[0] == 'RELOP' or proxToken[0] == 'Operador Aritimético') and tabelaAnalise.loc[X[-1], proxToken[1]] == -1: #se não tiver retorna erro
                print('Erro: Produção (' +  str(X[-1]) + ', ' + proxToken[1] + ' ) inesperada após um ' + lastToken[1])
                break
            elif (proxToken[0] != 'RELOP' and proxToken[0] != 'Operador Aritimético') and tabelaAnalise.loc[X[-1], proxToken[0]] == -1: #se não tiver retorna erro
                producoes = getProducaoFromErro(X[-1])
                print('Erro: Produção (' +  str(X[-1]) + ', ' + proxToken[0] + ' ) inesperada!') 
                print('Após um ' + lastToken[0] + ', é esperado os terminais a seguir: ', producoes)               
                break
            
            else:
                sub_arvore = Arvore(pilha[-1])
                
                if proxToken[0] == 'RELOP' or proxToken [0] == 'Operador Aritimético':
                    proxTokenAux = proxToken[1]
                else:
                    proxTokenAux = proxToken[0]

                # Pega o valor da produção do Não-terminal, terminal
                valor = tabelaAnalise.loc[X[-1], proxTokenAux]

                # procura o valor na tabela de produções
                resultado = tabelaProducoes.iloc[int(valor)-1, :]

                # transforma a lista de uma unica string em uma lista de strings
                producao = resultado.values[0].split()

                for k in range(0, len(producao)):
                    if producao[k] == proxToken[0] and (proxToken[0] == 'ID' or proxToken[0] == 'Numero'):
                        producaoAux = getTokenFromTabelaSimbolo(proxToken[1])
                        sub_arvore.lista.append(producaoAux)
                    elif producao[k] == 'ID' and proxToken[0] == 'function':
                        producaoAux = getTokenFromTabelaSimbolo(1)
                        sub_arvore.lista.append(producaoAux)
                    else:
                        sub_arvore.lista.append(producao[k])

                arvore.append(sub_arvore.definir_subarvore())

                # remove o topo da lista
                pilha[-1].pop()

                #se após isso ficar uma lista vazia, remova-a da pilha
                removeListaVazia()

                # se a produção inversa for diferente de epsolon
                if (producao[-1] != 'ε'):
                    # coloque a produção de forma inversa na pilha
                    pilha.append(list(reversed(producao)))
                else: #caso seja, não coloque o epsolon na pilha
                    pass

    if len(pilha) == 0 and proxToken[0] == '$':        
        return arvore
    else:
        print('Cadeia rejeitada!')
                
############# "MAIN" ############
i=1
arvore = []
pilha = []
pilha.append(['Programa'])
proxToken = lex(i)
arvore = analisePreditiva()
estrutura_arvore(arvore)