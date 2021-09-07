# Arquitetura e Organização de Computadores II
# Atividade 1F
# Implementação de simulador de scoreboarding
# Python 3.8.5 64-bit
#
# Aluno: Vinícius Kenzo Fukace
# RA: 115672

# TODO:
# deu bosta na emissao multipla
# refazer os comentarios das funcoes toString
# fazer TUDO
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
        self.latencia: int = 0
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
            'Emissao', 'Leitura', 'Execucao', 'Escrita']

    #     self.instr: List[Union[Instrucao, None]]
    #     self.instr = [None] * len(self.estagios)

    # # Exibe na tela quais instruções se encontram em cada estágio do pipeline.
    # # Quando um estágio estiver sem instruções, a saída apresenta '-'
    # def toString(self):
    #     print(f"\nPipeline =================================================")
    #     for i in range(len(self.estagios)):
    #         if type(self.instr[i]) is Instrucao:
    #             print(f"{self.estagios[i]:>10}: {self.instr[i].string}")
    #         else:
    #             print(f"{self.estagios[i]:>10}: -")


class Processador:
    def __init__(self) -> None:
        # A arquitetura deve ter registradores nomeados r1 até r12, e um rb
        self.numReg: int = 12
        self.reg: Dict[str, str] = {}
        for i in range(1, self.numReg + 1):
            self.reg["r" + str(i)] = '0'
        self.reg['rb'] = '0'

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


class Scoreboard:
    # Inicia o scoreboard com todos os campos vazios.
    def __init__(self) -> None:
        self.listaUF: List[str] = ['Integer',
                                   'Mult1', 'Mult2', 'Add', "Divide"]
        self.campos: List[str] = ['Busy', 'OP',
                                  'Fi', 'Fj', 'Fk', 'Qj', 'Qk', 'Rj', 'Rk']
        self.tabela: Dict[str, Dict[str, str]] = {}

        for uf in self.listaUF:
            self.tabela[uf] = {}
            for campo in self.campos:
                self.tabela[uf][campo] = ''
            self.tabela[uf]['Busy'] = 'No'

    # Esvazia os campos de uma Unidade Funcional e preenche o campo 'Busy' com 'No'.
    # Assume que uf é uma Unidade Funcional válida.
    def limpaUF(self, uf: str) -> None:
        for campo in self.campos:
            self.tabela[uf][campo] = ''
        self.tabela[uf]['Busy'] = 'No'

    # Retorna True se existe alguma instrução no Scoreboard, False caso contrário.
    def temInstrucao(self) -> bool:
        for uf in self.listaUF:
            if self.tabela[uf]['Busy'] == 'Yes':
                return True
        return False

    # Exibe na tela o estado das unidades funcionais.
    def toString(self):
        txt: str = f''
        print(f"\nScoreboard ===============================================")
        for uf in self.listaUF:
            txt = f'{uf:7} | {self.tabela[uf]}'
            print(txt)


class TabelaInstrucoes:
    # Inicia a tabela que contém todas as instruções e o ciclo em que
    # cada estágio do pipeline foi completo
    def __init__(self, memoria: Memoria, pipeline: Pipeline) -> None:
        self.ciclos: Dict[str, Dict[str, Union[int, str]]] = {}

        for instrucao in memoria.instrucoes:
            self.ciclos[instrucao.string] = {}
            for estagio in pipeline.estagios:
                self.ciclos[instrucao.string][estagio] = '-'

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
        self.proc = Processador()
        self.pipeline = Pipeline()
        self.memoria = Memoria(arqEntrada)
        self.scoreboard = Scoreboard()
        self.tabelaInstr = TabelaInstrucoes(self.memoria, self.pipeline)
        self.ciclo: int = 0

        self.listaInstrucoes: List[str] = [
            'ld', 'addd', 'subd', 'muld', 'divd']
        self.listaLatencias: Dict[str, int] = {}
        self.listaLatencias['ld'] = 1
        self.listaLatencias['addd'] = 2
        self.listaLatencias['subd'] = 2
        self.listaLatencias['muld'] = 10
        self.listaLatencias['divd'] = 40

    #####################
    # Estágios do pipeline

    # Retorna True se é possível realizar a escrita, False caso contrário.
    # Assume que há uma instrução no estágio de escrita

    def __verificaEscrita(self, imgScoreboard: Scoreboard) -> None:
        uf: str = self.pipeline.instr[2].uf
        flag1: bool = True
        flag2: bool = True
        flag3: bool = True

        for f in imgScoreboard.listaUF:
            flag1 = imgScoreboard.tabela[f]['Fj'] != imgScoreboard.tabela[uf]['Fi']
            flag2 = imgScoreboard.tabela[f]['Rj'] == 'No'
            flag3 = flag1 or flag2
            flag1 = imgScoreboard.tabela[f]['Fk'] != imgScoreboard.tabela[uf]['Fi']
            flag2 = imgScoreboard.tabela[f]['Rk'] == 'No'
            flag3 = flag3 and (flag1 or flag2)
            if not flag3:
                return False

        return True

    # Faz a escrita do resultados.
    def __escrita(self, imgScoreboard: Scoreboard) -> None:
        # TODO: esse primeiro if sai pra isso:
        # for uf in self.scoreboard.listaUF:
        #     if self.scoreboard.tabela[uf]['Busy'] == 'Yes':
        #         pass
        if type(self.pipeline.instr[3]) is Instrucao:
            self.pipeline.instr[3] = None
        if type(self.pipeline.instr[2]) is Instrucao:
            if self.__verificaEscrita(imgScoreboard):
                # Atribuir a outras variáveis para diminuir o tamanho da linha
                instrucao = self.pipeline.instr[2]
                uf: str = instrucao.uf

                for f in imgScoreboard.listaUF:
                    if imgScoreboard.tabela[f]['Qj'] == uf:
                        self.scoreboard.tabela[f]['Rj'] = 'Yes'
                    if imgScoreboard.tabela[f]['Qk'] == uf:
                        self.scoreboard.tabela[f]['Rk'] = 'Yes'

                self.proc.reg[self.scoreboard.tabela[uf]['Fi']] = '0'
                self.scoreboard.limpaUF(uf)
                self.tabelaInstr.ciclos[instrucao.string]['Escrita'] = self.ciclo
                self.pipeline.instr[3] = self.pipeline.instr[2]
                self.pipeline.instr[2] = None

    # Faz a execução da instrução.
    def __execucao(self, imgScoreboard: Scoreboard) -> None:
        if type(self.pipeline.instr[1]) is Instrucao:
            instrucao = self.pipeline.instr[1]
            if self.pipeline.instr[1].latencia > 1:
                self.pipeline.instr[1].latencia -= 1
            else:
                self.tabelaInstr.ciclos[instrucao.string]['Execucao'] = self.ciclo
                self.pipeline.instr[2] = self.pipeline.instr[1]
                self.pipeline.instr[1] = None

    # Faz a leitura dos operandos
    def __leitura(self, imgScoreboard: Scoreboard) -> None:
        if type(self.pipeline.instr[0]) is Instrucao:
            instrucao = self.pipeline.instr[0]
            uf: str = instrucao.uf

            if imgScoreboard.tabela[uf]['Rj'] == 'Yes' and imgScoreboard.tabela[uf]['Rk'] == 'Yes':
                self.scoreboard.tabela[uf]['Rj'] = 'No'
                self.scoreboard.tabela[uf]['Rk'] = 'No'
                self.scoreboard.tabela[uf]['Qj'] = '0'
                self.scoreboard.tabela[uf]['Qk'] = '0'
                self.tabelaInstr.ciclos[instrucao.string]['Leitura'] = self.ciclo
                self.pipeline.instr[1] = self.pipeline.instr[0]
                self.pipeline.instr[0] = None

    # Se for possível realizar a emissão, retorna a UF onde a instrução vai,
    # retorna '' caso contrário.
    def __ufEmissao(self, instrucao: Instrucao, imgScoreboard: Scoreboard) -> str:
        if self.proc.reg[instrucao.operandos[0]] == '0':
            if instrucao.opcode == 'ld':
                if imgScoreboard.tabela['Integer']['Busy'] == 'No':
                    return 'Integer'
            elif instrucao.opcode == 'addd' or instrucao.opcode == 'subd':
                if imgScoreboard.tabela['Add']['Busy'] == 'No':
                    return 'Add'
            elif instrucao.opcode == 'divd':
                if imgScoreboard.tabela['Divide']['Busy'] == 'No':
                    return 'Divide'
            elif instrucao.opcode == 'muld':
                if imgScoreboard.tabela['Mult1']['Busy'] == 'No':
                    return 'Mult1'
                elif imgScoreboard.tabela['Mult2']['Busy'] == 'No':
                    return 'Mult2'
        return ''

    # Faz a emissão da instrução.
    # A busca está inclusa no estágio de emissão
    # Assume a instrução está no formato correto
    def __emissao(self, imgScoreboard: Scoreboard) -> None:
        if self.proc.pc < len(self.memoria.instrucoes):
            instrucao = self.memoria.instrucoes[self.proc.pc]
            uf = self.__ufEmissao(instrucao, imgScoreboard)
            if uf != '':
                self.scoreboard.tabela[uf]['Busy'] = 'Yes'
                self.scoreboard.tabela[uf]['OP'] = instrucao.opcode
                self.scoreboard.tabela[uf]['Fi'] = instrucao.operandos[0]
                self.scoreboard.tabela[uf]['Fj'] = instrucao.operandos[1]
                self.scoreboard.tabela[uf]['Fk'] = instrucao.operandos[2]
                if instrucao.opcode == 'ld':
                    self.scoreboard.tabela[uf]['Qj'] = '0'
                else:
                    self.scoreboard.tabela[uf]['Qj'] = self.proc.reg[instrucao.operandos[1]]
                self.scoreboard.tabela[uf]['Qk'] = self.proc.reg[instrucao.operandos[2]]

                if self.scoreboard.tabela[uf]['Qk'] == '0':
                    self.scoreboard.tabela[uf]['Rk'] = 'Yes'
                else:
                    self.scoreboard.tabela[uf]['Rk'] = 'No'

                if self.scoreboard.tabela[uf]['Qj'] == '0':
                    self.scoreboard.tabela[uf]['Rj'] = 'Yes'
                else:
                    self.scoreboard.tabela[uf]['Rj'] = 'No'

                self.pipeline.instr[0] = instrucao
                self.pipeline.instr[0].uf = uf
                opcode = self.pipeline.instr[0].opcode
                self.pipeline.instr[0].latencia = self.listaLatencias[opcode]
                self.proc.reg[instrucao.operandos[0]] = uf
                self.tabelaInstr.ciclos[instrucao.string]['Emissao'] = self.ciclo
                self.proc.pc += 1

    # Retorna True caso haja instruções na memória que não terminaram a execução,
    # retorna False caso contrário.
    def status(self) -> bool:
        if self.proc.pc < len(self.memoria.instrucoes) or self.scoreboard.temInstrucao():
            return True
        else:
            return False

    # Avança o estado da simulação da execução.
    def avanca(self) -> None:
        if self.status():
            self.ciclo += 1
            # imagemScoreboard é utilizada para simular a execução simultânea
            # As operações irão ler imagemScoreboard e operar no verdadeiro scoreboard
            imagemScoreboard: Scoreboard = copy.deepcopy(self.scoreboard)
            self.__escrita(imagemScoreboard)
            self.__execucao(imagemScoreboard)
            self.__leitura(imagemScoreboard)
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
                while opcao != 'x' and sim.status() == True:
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
