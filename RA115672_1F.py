# Arquitetura e Organização de Computadores II
# Atividade 1F
# Implementação de simulador de scoreboarding
# Python 3.9.2 64-bit
#
# Aluno: Vinícius Kenzo Fukace
# RA: 115672
#
# Descrição dos Exemplos
# ex1 e ex2 - Conjuntos de instruções iguais ordenadas de forma diferente.
# ex3 - Instruções usando somente uma unidade funcional.
# ex4 - Exemplo com múltiplas dependências RAW.
# ex5 - Exemplo com dependências RAW, WAR e WAW.


import sys
import copy
from typing import List, TextIO, Dict


# Definição de Dados

class Instrucao:
    # Separa a string da instrução em seus componentes.
    # Assume que o opcode e os operandos estão de acordo com
    # a especificação da atividade.
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


class ListaRegistradores:
    # Inicializa os registradores r1 até r12, rb e o contador de programa (pc).
    def __init__(self) -> None:
        self.__numReg: int = 12
        self.regVazio: str = '-'
        self.reg: Dict[str, str] = {}
        for i in range(1, self.__numReg + 1):
            self.reg["r" + str(i)] = self.regVazio
        self.reg['rb'] = self.regVazio

        # PC – Contador de programa;
        self.pc: int = 0

    # Retorna uma string com os valores armazenados em cada um dos registradores
    # e no pc.
    def toString(self) -> str:
        string: str = f"\nRegistradores ============================================\n"
        for i in range(1, self.__numReg + 1):
            chave: str = f'r{i}'
            string = string + f'{chave}: {self.reg[chave]:3}|'
        string = string + f'\npc:{self.pc}'
        return string


class Memoria:
    # Inicializa a memória com todas as instruções em arq convertidas para
    # o tipo Instrucao.
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

    # Retorna uma string com o estado da unidade funcional.
    def toString(self) -> str:
        string = f'{self.nome:7}|{self.busy!s:5}|{self.op:4}|{self.fi:3}|{self.fj:3}|{self.fk:3}'
        string = string + \
            f'|{self.qj:7}|{self.qk:7}|{self.rj!s:5}|{self.rk!s:5}\n'
        return string


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

    # Retorna a posição da UF na lista baseado no objeto uf
    def indiceUF(self, uf: UnidadeFuncional) -> int:
        return self.listaUF.index(uf)

    # Retorna a posição da UF na lista baseado no nome
    # Retorna -1 caso não seja encontrada
    def indiceNome(self, nomeUF: str) -> int:
        for i in range(len(self.listaUF)):
            if self.listaUF[i].nome == nomeUF:
                return i
        return -1

    # Retorna uma string com o estado das unidades funcionais.
    def toString(self):
        string: str = f"\nScoreboard ===============================================\n"
        string = string + f'UF     |Busy |OP  |Fi |Fj |Fk |Qj     |Qk     |Rj   |Rk\n'
        for uf in self.listaUF:
            string = string + f'{uf.toString()}'
        return string


class TabelaInstrucoes:
    # Inicializa a tabela que contém todas as instruções e o ciclo em que
    # cada estágio do pipeline foi completo
    def __init__(self, memoria: Memoria, estagiosPipeline: List[str]) -> None:
        self.ciclos: List[Dict[str, str]] = []
        self.__estagiosPipeline = estagiosPipeline

        for i in range(len(memoria.instrucoes)):
            self.ciclos.append({})
            self.ciclos[i]['instrucao'] = memoria.instrucoes[i].string
            for estagio in self.__estagiosPipeline:
                self.ciclos[i][estagio] = '-'

    # Retorna uma string com as informações da instrução de posição i na tabela
    def __instrucaoToString(self, i: int) -> str:
        # tinha que atribuir a uma str separada antes, senão não funcionava.
        strInstrucao: str = self.ciclos[i]['instrucao']
        string = f'{strInstrucao:20}'
        for estagio in self.__estagiosPipeline:
            string = string + f'|{self.ciclos[i][estagio]!s:8}'
        string = string + '\n'
        return string

    # Retorna uma string com as informações de todas as instruções na tabela
    def toString(self) -> None:
        string: str = f"\nTabela de Instrucoes =====================================\n"
        string = string + f'Instrucao           '
        for estagio in self.__estagiosPipeline:
            string = string + f'|{estagio:8}'
        string = string + '\n'

        for instrucao in range(len(self.ciclos)):
            string = string + self.__instrucaoToString(instrucao)
        return string


class Simulador:
    # Inicia o simulador usando o arquivo que contém o conjunto de instruções.
    def __init__(self, arqEntrada: TextIO) -> None:
        self.ciclo: int = 0
        self.estagiosPipeline: List[str] = [
            'Emissao', 'Leitura', 'Execucao', 'Escrita']
        self.listaReg = ListaRegistradores()
        self.memoria = Memoria(arqEntrada)
        self.scoreboard = Scoreboard()
        self.tabelaInstr = TabelaInstrucoes(
            self.memoria, self.estagiosPipeline)

    #####################
    # Estágios do pipeline

    # Retorna True se é possível realizar a escrita em uf, False caso contrário.
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

    # Realiza a etapa de escrita dos resultados em uf.
    def __escrita(self, imgScoreboard: Scoreboard, uf: UnidadeFuncional) -> None:
        if self.__podeEscrita(imgScoreboard, uf):
            iUF: int = self.scoreboard.indiceUF(uf)
            nomeUF = self.scoreboard.listaUF[iUF].nome

            for f in range(len(imgScoreboard.listaUF)):
                if imgScoreboard.listaUF[f].qj == nomeUF:
                    self.scoreboard.listaUF[f].rj = True
                if imgScoreboard.listaUF[f].qk == nomeUF:
                    self.scoreboard.listaUF[f].rk = True

            self.listaReg.reg[self.scoreboard.listaUF[iUF].fi] = self.listaReg.regVazio
            self.tabelaInstr.ciclos[uf.instrucao]['Escrita'] = self.ciclo
            self.scoreboard.listaUF[iUF].reset()

    # Realiza a etapa de execução da instrução em uf.
    def __execucao(self, uf: UnidadeFuncional) -> None:
        iUF: int = self.scoreboard.indiceUF(uf)
        if self.scoreboard.listaUF[iUF].latenciaAtual > 1:
            self.scoreboard.listaUF[iUF].latenciaAtual -= 1
        else:
            self.tabelaInstr.ciclos[uf.instrucao]['Execucao'] = self.ciclo
            self.scoreboard.listaUF[iUF].estagioCompleto = 2

    # Realiza a etapa de leitura dos operandos em uf.
    def __leitura(self, imgScoreboard: Scoreboard, uf: UnidadeFuncional) -> None:
        iUF: int = self.scoreboard.indiceUF(uf)
        if imgScoreboard.listaUF[iUF].rj == True and imgScoreboard.listaUF[iUF].rk == True:
            self.scoreboard.listaUF[iUF].rj = False
            self.scoreboard.listaUF[iUF].rk = False
            self.scoreboard.listaUF[iUF].qj = self.listaReg.regVazio
            self.scoreboard.listaUF[iUF].qk = self.listaReg.regVazio

            self.tabelaInstr.ciclos[uf.instrucao]['Leitura'] = self.ciclo
            self.scoreboard.listaUF[iUF].estagioCompleto = 1

    # Se for possível realizar a emissão, retorna o nome da UF onde a instrução vai,
    # retorna '' caso contrário.
    def __ufEmissao(self, instrucao: Instrucao, imgScoreboard: Scoreboard) -> str:
        if self.listaReg.reg[instrucao.operandos[0]] == self.listaReg.regVazio:
            for uf in imgScoreboard.listaUF:
                if uf.busy == False and uf.operaInstrucao(instrucao.opcode):
                    return uf.nome
        return ''

    # Realiza a etapa de emissão da instrução.
    # A busca está inclusa no estágio de emissão
    def __emissao(self, imgScoreboard: Scoreboard) -> None:
        if self.listaReg.pc < len(self.memoria.instrucoes):
            instrucao = self.memoria.instrucoes[self.listaReg.pc]
            nomeUF = self.__ufEmissao(instrucao, imgScoreboard)
            if nomeUF != '':
                uf: int = imgScoreboard.indiceNome(nomeUF)
                self.scoreboard.listaUF[uf].busy = True
                self.scoreboard.listaUF[uf].op = instrucao.opcode
                self.scoreboard.listaUF[uf].fi = instrucao.operandos[0]
                self.scoreboard.listaUF[uf].fj = instrucao.operandos[1]
                self.scoreboard.listaUF[uf].fk = instrucao.operandos[2]

                if instrucao.opcode == 'ld':
                    self.scoreboard.listaUF[uf].qj = self.listaReg.regVazio
                    self.scoreboard.listaUF[uf].qk = self.listaReg.regVazio
                else:
                    self.scoreboard.listaUF[uf].qj = self.listaReg.reg[instrucao.operandos[1]]
                    self.scoreboard.listaUF[uf].qk = self.listaReg.reg[instrucao.operandos[2]]

                if self.scoreboard.listaUF[uf].qk == self.listaReg.regVazio:
                    self.scoreboard.listaUF[uf].rk = True
                else:
                    self.scoreboard.listaUF[uf].rk = False

                if self.scoreboard.listaUF[uf].qj == self.listaReg.regVazio:
                    self.scoreboard.listaUF[uf].rj = True
                else:
                    self.scoreboard.listaUF[uf].rj = False

                self.scoreboard.listaUF[uf].instrucao = self.listaReg.pc
                self.scoreboard.listaUF[uf].estagioCompleto = 0
                self.listaReg.reg[instrucao.operandos[0]] = nomeUF
                self.tabelaInstr.ciclos[self.listaReg.pc]['Emissao'] = self.ciclo
                self.listaReg.pc += 1

    # Retorna True caso haja instruções na memória que não terminaram a execução,
    # retorna False caso contrário.
    def podeContinuar(self) -> bool:
        if self.listaReg.pc < len(self.memoria.instrucoes) or self.scoreboard.temInstrucao():
            return True
        else:
            return False

    # Avança o estado da simulação da execução.
    def avanca(self) -> None:
        if self.podeContinuar():
            self.ciclo += 1
            # imagemScoreboard é utilizada para simular a execução simultânea
            # As operações irão ler imagemScoreboard e operar no verdadeiro scoreboard
            imagemScoreboard: Scoreboard = copy.deepcopy(self.scoreboard)
            self.__emissao(imagemScoreboard)
            for uf in self.scoreboard.listaUF:
                if uf.busy:
                    if uf.estagioCompleto == 0:
                        self.__leitura(imagemScoreboard, uf)
                    elif uf.estagioCompleto == 1:
                        self.__execucao(uf)
                    elif uf.estagioCompleto == 2:
                        self.__escrita(imagemScoreboard, uf)
            pass

    # Escreve o estado atual do simulador na tela.
    def printEstado(self) -> None:
        string: str = (
            f'\n################################################################\n')
        string = string+f'Ciclo: {self.ciclo}'
        print(string)
        print(self.tabelaInstr.toString())
        print(self.scoreboard.toString())
        print(self.listaReg.toString())

    # Escreve o estado atual do simulador em arq.
    def escreveEmArquivo(self, arq: TextIO) -> None:
        string: str = (
            f'################################################################\n')
        string = string+f'Ciclo: {self.ciclo}\n'
        arq.write(string)
        arq.write(self.tabelaInstr.toString())
        arq.write(self.scoreboard.toString())
        arq.write(self.listaReg.toString())
        arq.write('\n\n')


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
            sim: Simulador = Simulador(arqEntrada)
            print("Inicialização do simulador completa.")

            print(f'Gerando arquivo de log {nomeArqSaida}')
            with open(nomeArqSaida, mode='wt', encoding='utf-8') as log:
                sim.escreveEmArquivo(log)
                while sim.podeContinuar() and sim.ciclo < 1000:
                    # O limite de 1000 ciclos é arbitrário para evitar execução infinita em testes
                    # onde as instruções não estão escritas corretamente.
                    sim.avanca()
                    sim.escreveEmArquivo(log)

            print("Execucao Finalizada.")

    else:
        print("Execução Invalida!")
        print("Exemplo de entrada: .\RA115672_1F.py <nome do arquivo>.asm")


if __name__ == '__main__':
    main()
