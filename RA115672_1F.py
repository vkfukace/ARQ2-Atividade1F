# Arquitetura e Organização de Computadores II
# Atividade 1F
# Implementação de simulador de scoreboarding
# Python 3.8.5 64-bit
#
# Aluno: Vinícius Kenzo Fukace
# RA: 115672

# TODO:
# fazer exemplos
# mudar as funcoes toString
# ver como formatar boolean em uma fstring
# refazer os comentarios - especialmente das funcoes toString
# escrever arquivo

import sys
import copy
from typing import List, TextIO, Union, Dict


# Definição de Dados

class Instrucao:
    # Separa a string da instrução em seus componentes.
    def __init__(self, strInstrucao: str) -> None:
        # Separa o opcode do resto
        strAux = strInstrucao.partition(' ')

        self.uf: str = ''
        self.string: str = strInstrucao
        self.opcode: str = strAux[0]
        self.operandos: List[str] = []

        # Remove o opcode e recebe os operandos
        strAux = strAux[2].split(',')

        if self.opcode == 'ld':
            self.operandos.append(strAux[0].strip())
            strAux = strAux[1].split(')')
            self.operandos.append(strAux[0].replace('(', '').strip())
            self.operandos.append(strAux[1].strip())
        else:
            for operando in strAux:
                operando = operando.strip()
                self.operandos.append(operando)


class Processador:
    def __init__(self) -> None:
        # A arquitetura deve ter registradores nomeados r1 até r12, e um rb
        self.numReg: int = 12
        self.reg: Dict[str, str] = {}
        for i in range(1, self.numReg + 1):
            self.reg["r" + str(i)] = '-'
        self.reg['rb'] = '-'

        # PC – Contador de programa;
        self.pc: int = 0

    # Exibe os valores armazenados em cada um dos registradores na tela.
    def toString(self):
        txt: str = f''
        print(f"\nRegistradores ============================================")
        for i in range(1, self.numReg + 1):
            chave: str = f'r{i}'
            temp: str = f'{chave:>3}: {self.reg[chave]:7}|'
            txt = f'{txt}{temp}'
        print(txt)
        print(f' pc:{self.pc}')


class Memoria:
    # Inicia a memória com todas as instruções em arq.
    def __init__(self, arq: TextIO) -> None:
        self.instrucoes: List[Instrucao] = []
        for linha in arq:
            self.instrucoes.append(Instrucao(linha.rstrip()))


class UnidadeFuncional:
    def __init__(self, nome: str, listaOP: List[str], latencia: int) -> None:
        self.nome: str = nome
        self.busy: bool = False
        self.op: str = ''
        self.fi: str = ''
        self.fj: str = ''
        self.fk: str = ''
        self.qj: str = ''
        self.qk: str = ''
        self.rj: bool = False
        self.rk: bool = False
        self.listaOP: List[str] = listaOP
        self.latencia: int = latencia
        self.latenciaAtual: int = latencia
        self.instrucao: int = -1
        self.estagioCompleto: int = -1

    # Esvazia os campos de uma Unidade Funcional e os preenche com os valores padrão.
    def reset(self) -> None:
        self.busy: bool = False
        self.op: str = ''
        self.fi: str = ''
        self.fj: str = ''
        self.fk: str = ''
        self.qj: str = ''
        self.qk: str = ''
        self.rj: bool = False
        self.rk: bool = False
        self.latenciaAtual: int = self.latencia
        self.instrucao: int = -1
        self.estagioCompleto: int = -1

    # Retorna True se opcode está entre as operações que a UF executa
    def operaInstrucao(self, opcode: str) -> bool:
        return opcode in self.listaOP

    # Exibe na tela o estado da unidade funcional.
    def toString(self) -> str:
        string = f'{self.nome:7}|{self.busy:5}|{self.op:5}|{self.fi:3}|{self.fj:3}|{self.fk:3}'
        string = f'{string}|{self.qj:7}|{self.qk:7}|{self.rj:5}|{self.rk:5}'
        print(string)


class Scoreboard:
    # Inicia o scoreboard com todos os campos vazios.
    def __init__(self) -> None:
        self.listaUF: List[UnidadeFuncional] = []
        self.listaUF.append(UnidadeFuncional('Integer', ['ld'], 1))
        self.listaUF.append(UnidadeFuncional('Mult1', ['muld'], 10))
        self.listaUF.append(UnidadeFuncional('Mult2', ['muld'], 10))
        self.listaUF.append(UnidadeFuncional('Add', ['addd', 'subd'], 2))
        self.listaUF.append(UnidadeFuncional('Divide', ['divd'], 40))

    # Retorna True se existe alguma instrução no Scoreboard, False caso contrário.
    def temInstrucao(self) -> bool:
        for uf in self.listaUF:
            if uf.busy == True:
                return True
        return False

    # Retorna a posição da UF na lista baseado na UF
    def indiceUF(self, uf: UnidadeFuncional) -> int:
        return self.listaUF.index(uf)

    # Retorna a posição da UF na lista baseado no nome
    # Retorna -1 caso não seja encontrada
    def indiceNome(self, nomeUF: str) -> int:
        for i in range(len(self.listaUF)):
            if self.listaUF[i].nome == nomeUF:
                return i
        return -1

    # Exibe na tela o estado das unidades funcionais.
    def toString(self):
        txt: str = f''
        print(f"\nScoreboard ===============================================")
        for uf in self.listaUF:
            uf.toString()


class TabelaInstrucoes:
    # Inicia a tabela que contém todas as instruções e o ciclo em que
    # cada estágio do pipeline foi completo
    def __init__(self, memoria: Memoria, estagiosPipeline: List[str]) -> None:
        self.ciclos: Dict[int, Dict[str, Union[int, str]]] = {}

        for i in range(len(memoria.instrucoes)):
            self.ciclos[i] = {}
            self.ciclos[i]['instrucao'] = memoria.instrucoes[i].string
            for estagio in estagiosPipeline:
                self.ciclos[i][estagio] = '-'

    def toString(self) -> None:
        txt: str = f''
        print(f"\nTabela de Instrucoes =====================================")
        for instrucao in self.ciclos.keys():
            txt = f'{instrucao:20} | {self.ciclos[instrucao]}'
            print(txt)


class Simulador:
    # Inicia o simulador usando o arquivo que contém o conjunto de instruções e
    # o arquivo de saída
    def __init__(self, arqEntrada: TextIO, arqSaida: TextIO) -> None:
        self.ciclo: int = 0
        self.estagiosPipeline: List[str] = [
            'Emissao', 'Leitura', 'Execucao', 'Escrita']
        self.proc = Processador()
        self.memoria = Memoria(arqEntrada)
        self.scoreboard = Scoreboard()
        self.tabelaInstr = TabelaInstrucoes(
            self.memoria, self.estagiosPipeline)

    #####################
    # Estágios do pipeline

    # Retorna True se é possível realizar a escrita, False caso contrário.
    # Assume que há uma instrução no estágio de escrita

    def __podeEscrita(self, imgScoreboard: Scoreboard, uf: UnidadeFuncional) -> None:
        iUF: int = self.scoreboard.indiceUF(uf)
        flag1: bool = True
        flag2: bool = True
        flag3: bool = True

        for f in range(len(imgScoreboard.listaUF)):
            flag1 = imgScoreboard.listaUF[f].fj != imgScoreboard.listaUF[iUF].fi
            flag2 = imgScoreboard.listaUF[f].rj == False
            flag3 = flag1 or flag2
            flag1 = imgScoreboard.listaUF[f].fk != imgScoreboard.listaUF[iUF].fi
            flag2 = imgScoreboard.listaUF[f].rk == False
            flag3 = flag3 and (flag1 or flag2)
            if not flag3:
                return False

        return True

    # Faz a escrita do resultados.
    def __escrita(self, imgScoreboard: Scoreboard, uf: UnidadeFuncional) -> None:
        iUF: int = self.scoreboard.indiceUF(uf)
        if self.__podeEscrita(imgScoreboard, uf):
            # Atribuir a outras variáveis para diminuir o tamanho da linha
            nomeUF = self.scoreboard.listaUF[iUF].nome

            for f in range(len(imgScoreboard.listaUF)):
                if imgScoreboard.listaUF[f].qj == nomeUF:
                    self.scoreboard.listaUF[f].rj = True
                if imgScoreboard.listaUF[f].qk == nomeUF:
                    self.scoreboard.listaUF[f].rk = True

            self.proc.reg[self.scoreboard.listaUF[iUF].fi] = '-'
            self.tabelaInstr.ciclos[uf.instrucao]['Escrita'] = self.ciclo
            self.scoreboard.listaUF[iUF].reset()

    # Faz a execução da instrução.

    def __execucao(self, imgScoreboard: Scoreboard, uf: UnidadeFuncional) -> None:
        iUF: int = self.scoreboard.indiceUF(uf)
        if self.scoreboard.listaUF[iUF].latenciaAtual > 1:
            self.scoreboard.listaUF[iUF].latenciaAtual -= 1
        else:
            self.tabelaInstr.ciclos[uf.instrucao]['Execucao'] = self.ciclo
            self.scoreboard.listaUF[iUF].estagioCompleto = 2

    # Faz a leitura dos operandos
    def __leitura(self, imgScoreboard: Scoreboard, uf: UnidadeFuncional) -> None:
        iUF: int = self.scoreboard.indiceUF(uf)
        if imgScoreboard.listaUF[iUF].rj == True and imgScoreboard.listaUF[iUF].rk == True:
            self.scoreboard.listaUF[iUF].rj = False
            self.scoreboard.listaUF[iUF].rk = False
            self.scoreboard.listaUF[iUF].qj = '-'
            self.scoreboard.listaUF[iUF].qk = '-'

            self.tabelaInstr.ciclos[uf.instrucao]['Leitura'] = self.ciclo
            self.scoreboard.listaUF[iUF].estagioCompleto = 1

    # Se for possível realizar a emissão, retorna a UF onde a instrução vai,
    # retorna '' caso contrário.
    def __ufEmissao(self, instrucao: Instrucao, imgScoreboard: Scoreboard) -> str:
        if self.proc.reg[instrucao.operandos[0]] == '-':
            for uf in imgScoreboard.listaUF:
                if uf.busy == False and uf.operaInstrucao(instrucao.opcode):
                    return uf.nome
        return ''

    # Faz a emissão da instrução.
    # A busca está inclusa no estágio de emissão
    def __emissao(self, imgScoreboard: Scoreboard) -> None:
        if self.proc.pc < len(self.memoria.instrucoes):
            instrucao = self.memoria.instrucoes[self.proc.pc]
            nomeUF = self.__ufEmissao(instrucao, imgScoreboard)
            if nomeUF != '':
                uf: int = imgScoreboard.indiceNome(nomeUF)
                self.scoreboard.listaUF[uf].busy = True
                self.scoreboard.listaUF[uf].op = instrucao.opcode
                self.scoreboard.listaUF[uf].fi = instrucao.operandos[0]
                self.scoreboard.listaUF[uf].fj = instrucao.operandos[1]
                self.scoreboard.listaUF[uf].fk = instrucao.operandos[2]

                if instrucao.opcode == 'ld':
                    self.scoreboard.listaUF[uf].qj = '-'
                    self.scoreboard.listaUF[uf].qk = '-'
                else:
                    self.scoreboard.listaUF[uf].qj = self.proc.reg[instrucao.operandos[1]]
                    self.scoreboard.listaUF[uf].qk = self.proc.reg[instrucao.operandos[2]]

                if self.scoreboard.listaUF[uf].qk == '-':
                    self.scoreboard.listaUF[uf].rk = True
                else:
                    self.scoreboard.listaUF[uf].rk = False

                if self.scoreboard.listaUF[uf].qj == '-':
                    self.scoreboard.listaUF[uf].rj = True
                else:
                    self.scoreboard.listaUF[uf].rj = False

                self.scoreboard.listaUF[uf].instrucao = self.proc.pc
                self.scoreboard.listaUF[uf].estagioCompleto = 0
                self.proc.reg[instrucao.operandos[0]] = nomeUF
                self.tabelaInstr.ciclos[self.proc.pc]['Emissao'] = self.ciclo
                self.proc.pc += 1

    # Retorna True caso haja instruções na memória que não terminaram a execução,
    # retorna False caso contrário.
    def podeContinuarExecucao(self) -> bool:
        if self.proc.pc < len(self.memoria.instrucoes) or self.scoreboard.temInstrucao():
            return True
        else:
            return False

    # Avança o estado da simulação da execução.
    def avanca(self) -> None:
        if self.podeContinuarExecucao():
            self.ciclo += 1
            # imagemScoreboard é utilizada para simular a execução simultânea
            # As operações irão ler imagemScoreboard e operar no verdadeiro scoreboard
            imagemScoreboard: Scoreboard = copy.deepcopy(self.scoreboard)
            for uf in self.scoreboard.listaUF:
                if uf.busy:
                    if uf.estagioCompleto == 2:
                        self.__escrita(imagemScoreboard, uf)
                    elif uf.estagioCompleto == 1:
                        self.__execucao(imagemScoreboard, uf)
                    elif uf.estagioCompleto == 0:
                        self.__leitura(imagemScoreboard, uf)
            self.__emissao(imagemScoreboard)
            pass

    # Mostra o estado do pipeline, scoreboard e registradores.
    def toString(self) -> None:
        print(f'Ciclo: {self.ciclo}')
        # self.pipeline.toString()
        self.tabelaInstr.toString()
        self.scoreboard.toString()
        self.proc.toString()


# Verifica os parâmetros de execução
# Retorna True se estão dentro do padrão, False caso contrário
# Não verifica se o arquivo .asm existe
def verificaParametros(parametros: List[str]) -> bool:
    if len(parametros) >= 2:
        strVerificacao: List[str] = parametros[1].split('.')
        if strVerificacao[-1] == "asm":
            return True
    return False


# Função Principal

def main():
    if verificaParametros(sys.argv) == True:
        # Automaticamente fecha o arquivo caso haja erros
        with open(sys.argv[1], mode='rt', encoding='utf-8') as arqEntrada:
            nomeArqSaida: str = sys.argv[1].strip(".asm")
            nomeArqSaida = nomeArqSaida + ".out"

            print(f'Gerando arquivo de log {nomeArqSaida}')
            with open(nomeArqSaida, mode='wt', encoding='utf-8') as log:
                sim: Simulador = Simulador(arqEntrada, log)
                print("Inicialização do simulador completa.")

                sim.toString()

                opcao: str
                print(
                    f'\nInsira \'x\' para sair, qualquer outra letra para avancar: ', end='')
                opcao = input()
                while opcao != 'x' and sim.podeContinuarExecucao() == True:
                    sim.avanca()
                    sim.toString()
                    print(
                        f'\nInsira \'x\' para sair, qualquer outra letra para avancar: ', end='')
                    opcao = input()

            print("Execucao Finalizada.")

    else:
        print("Execução Invalida!")
        print("Exemplo de entrada: python3 RA115672_1F.py <nome do arquivo>.asm")


if __name__ == '__main__':
    main()
