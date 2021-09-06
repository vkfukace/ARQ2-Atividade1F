# Arquitetura e Organização de Computadores II
# Atividade 1F
# Implementação de simulador de scoreboarding
# Python 3.8.5 64-bit
#
# Aluno: Vinícius Kenzo Fukace
# RA: 115672

# TODO:
# mudar a classe instrucao p ter os campos da tabela
# redefinir/renomear as classes
# fazer TUDO
# escrever arquivo

import sys
from typing import List, TextIO, Union, Dict


# Definição de Dados


class Instrucao:
    # Separa a string da instrução em seus componentes.
    def __init__(self, strInstrucao: str) -> None:
        # Separa o opcode do resto
        strAux = strInstrucao.partition(' ')

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


class Pipeline:
    # Inicia o pipeline com todos os estados vazios
    def __init__(self) -> None:
        # Caso um estágio estiver sem instruções, será usado None
        self.estagios: List[str] = [
            'Busca', 'Emissao', 'Leitura', 'Execucao', 'Escrita']

        self.instr: List[Union[Instrucao, None]]
        self.instr = [None] * len(self.estagios)

    # Exibe na tela quais instruções se encontram em cada estágio do pipeline.
    # Quando um estágio estiver sem instruções, a saída apresenta '-'
    def printEstado(self):
        print(f"\nPipeline =================================================")
        for i in range(len(self.estagios)):
            if type(self.instr[i]) is Instrucao:
                print(f"{self.estagios[i]:>10}: {self.instr[i].string}")
            else:
                print(f"{self.estagios[i]:>10}: -")

    # Retorna True se existe alguma instrução na pipeline, False caso contrário.
    def status(self) -> bool:
        for i in range(len(self.estagios)):
            if type(self.instr[i]) == Instrucao:
                return True
        return False


class Processador:
    def __init__(self) -> None:
        self.pipeline = Pipeline()

        # A arquitetura deve ter registradores nomeados r1 até r12, e um rb
        self.numReg: int = 12
        self.reg: Dict[str, str] = {}
        for i in range(1, self.numReg + 1):
            self.reg["r" + str(i)] = ''
        self.reg['rb'] = ''

        # PC – Contador de programa;
        self.pc: int = 0

    # Exibe os valores armazenados em cada um dos registradores na tela.
    def printEstado(self):
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


class Scoreboard:
    # Inicia o scoreboard com todos os campos vazios.
    def __init__(self) -> None:
        self.listaUF: List[str] = ['Integer',
                                   'Mult1', 'Mult2', 'Add', "Divide"]
        self.campos: List[str] = ['Busy', 'OP',
                                  'Fi', 'Fj', 'Fk', 'Qj', 'Qk', 'Rj', 'Rk']
        self.tamCampos: List[int] = [4, 5, 2, 2, 2, 7, 7, 3, 3]

        self.tabela: Dict[str, Dict[str, str]] = {}
        for uf in self.listaUF:
            self.tabela[uf] = {}
            for campo in self.campos:
                self.tabela[uf][campo] = ''

    # Exibe na tela o estado das unidades funcionais.
    def printEstado(self):
        txt: str = f''
        print(f"\nScoreboard ===============================================")
        # for i in range(self.numReg):
        #     chave: str = f'r{i}'
        #     temp: str = f'{chave:>3}: {self.reg[chave]:7} | '
        #     txt = f'{txt}{temp}'
        print(txt)
        for uf in self.listaUF:
            txt = f'{uf:7} | {self.tabela[uf]}'
            print(txt)


class Simulador:
    # Inicia o simulador usando o arquivo que contém o conjunto de instruções
    def __init__(self, arq: TextIO) -> None:
        self.pro = Processador()
        self.mem = Memoria(arq)
        self.scoreboard = Scoreboard()
        self.ciclo: int = 0

        self.latenciaLD: int = 1
        self.latenciaMULD: int = 10
        self.latenciaDIVD: int = 40
        self.latenciaADDD: int = 2
        self.latenciaSUBD: int = 2

    #####################
    # Estágios do pipeline

    # Faz a escrita do resultados.
    def __escrita(self) -> None:
        if type(self.pro.pipeline.instr[4]) is Instrucao:
            pass

            self.pro.pipeline.instr[4] = None

    # Faz a execução da instrução.
    def __execucao(self) -> None:
        if type(self.pro.pipeline.instr[2]) is Instrucao:
            if self.pro.pipeline.instr[2].opcode == 'blt':
                self.blt(self.pro.pipeline.instr[2])
            elif self.pro.pipeline.instr[2].opcode == 'bgt':
                self.bgt(self.pro.pipeline.instr[2])
            elif self.pro.pipeline.instr[2].opcode == 'beq':
                self.beq(self.pro.pipeline.instr[2])
            elif self.pro.pipeline.instr[2].opcode == 'j':
                self.j(self.pro.pipeline.instr[2])
            elif self.pro.pipeline.instr[2].opcode == 'jr':
                self.jr(self.pro.pipeline.instr[2])
            elif self.pro.pipeline.instr[2].opcode == 'jal':
                self.jal(self.pro.pipeline.instr[2])

            self.pro.pipeline.instr[3] = self.pro.pipeline.instr[2]
            self.pro.pipeline.instr[2] = None

    # Faz a leitura dos operandos
    def __leitura(self) -> None:
        if self.hazard == -1:
            if type(self.pro.pipeline.instr[1]) is str:
                self.pro.pipeline.instr[2] = Instrucao(
                    self.pro.pipeline.instr[1])
                self.pro.pipeline.instr[1] = None

    # Faz a emissão da instrução.
    def __emissao(self) -> None:
        if type(self.pro.pipeline.instr[3]) is Instrucao:
            if self.pro.pipeline.instr[3].opcode == 'sw':
                self.sw(self.pro.pipeline.instr[3])

            self.pro.pipeline.instr[4] = self.pro.pipeline.instr[3]
            self.pro.pipeline.instr[3] = None

    # Faz a busca de instrução.
    def __busca(self) -> None:
        if self.hazard == -1:
            self.pro.pipeline.instr[1] = self.pro.pipeline.instr[0]
            if self.pro.pc < len(self.mem.instrucoes):
                self.pro.pipeline.instr[0] = self.mem.instrucoes[self.pro.pc]
                self.pro.pc += 1
            else:
                self.pro.pipeline.instr[0] = None

    # # Verifica a existência de hazards de dados na pipeline.
    # # Se houver hazard, guarda o índice do estágio em que se encontra o hazard
    # # em self.hazard e retorna True.
    # # Caso contrário, guarda -1 em self.hazard e retorna False.
    # def __existeHazard(self) -> bool:
    #     # Verifica somente a instrução no estágio de decodificação, pois a
    #     # leitura de operandos é feita somente no estágio de execução
    #     if type(self.pro.pipeline.instr[1]) is str:
    #         inst: Instrucao = Instrucao(self.pro.pipeline.instr[1])

    #         # Para cada estágio após o de decodificação
    #         for i in range(2, len(self.pro.pipeline.estagios)):
    #             if type(self.pro.pipeline.instr[i]) is Instrucao:
    #                 # Se o primeiro operando da inst está nesse estágio (RAW, WAW)
    #                 if inst.operandos[0] in self.pro.pipeline.instr[i].operandos:
    #                     self.hazard = i
    #                     return True
    #                 # Se o primeiro operando desse estágio está em inst (WAR)
    #                 if self.pro.pipeline.instr[i].operandos[0] in inst.operandos:
    #                     self.hazard = i
    #                     return True
    #     self.hazard = -1
    #     return False

    # Avança o estado da simulação da execução.
    def avanca(self) -> None:
        # todo: verificar se o pc > len(memoria)
        self.__escrita()
        self.__execucao()
        self.__leitura()
        self.__emissao()
        self.__busca()

    # Mostra o estado dos registradores, pipeline e scoreboard.
    def printEstado(self) -> None:
        print(f'Ciclo: {self.ciclo}')
        self.pro.pipeline.printEstado()
        self.scoreboard.printEstado()
        self.pro.printEstado()


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
            sim: Simulador = Simulador(arqEntrada)
            print("Inicialização do simulador completa.")

            nomeArqSaida: str = sys.argv[1].strip(".asm")
            nomeArqSaida = nomeArqSaida + ".out"
            print(f'Gerando arquivo de log {nomeArqSaida}')
            with open(nomeArqSaida, mode='wt', encoding='utf-8') as log:
                sim.printEstado()

                # opcao: str
                # print(f'\nInsira \'x\' para sair, qualquer outra letra para avancar: ', end='')
                # opcao = input()
                # while opcao != 'x' and sim.status() == True:
                #     sim.avanca()
                #     sim.printEstado()
                #     print(
                #         f'\nInsira \'x\' para sair, qualquer outra letra para avancar: ', end='')
                #     opcao = input()

            print("Execucao Finalizada.")

    else:
        print("Execução Invalida!")
        print("Exemplo de entrada: python3 RA115672_1F.py <nome do arquivo>.asm")


if __name__ == '__main__':
    main()
