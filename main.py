import sys
import re

# Classe que representa um escopo
class Escopo:
    def __init__(self):
        self.variaveis = {}  # Dicionário para armazenar variáveis e seus valores

    def adicionar_variavel(self, lexema, tipo, valor):
        # Adiciona uma variável ao escopo atual
        if lexema in self.variaveis:
            return f"Erro: Variável '{lexema}' já declarada no escopo atual."
        self.variaveis[lexema] = {'tipo': tipo, 'valor': valor}
        return None

    def obter_variavel(self, lexema):
        # Obtém uma variável do escopo atual
        return self.variaveis.get(lexema, None)

# Classe que gerencia os escopos
class GerenciadorEscopos:
    def __init__(self):
        self.pilha_escopos = [Escopo()]  # Pilha de escopos

    def entrar_escopo(self):
        # Adiciona um novo escopo à pilha
        self.pilha_escopos.append(Escopo())

    def sair_escopo(self):
        # Remove o escopo mais recente da pilha
        if len(self.pilha_escopos) > 1:
            self.pilha_escopos.pop()
        else:
            print("Erro: Tentativa de finalizar escopo inexistente.")

    def adicionar_variavel(self, lexema, tipo, valor, linha):
        # Adiciona uma variável ao escopo atual e trata erros de declaração duplicada
        erro = self.pilha_escopos[-1].adicionar_variavel(lexema, tipo, valor)
        if erro:
            print(f"Erro linha {linha + 1}: {erro}")

    def encontrar_variavel(self, lexema):
        # Procura uma variável nos escopos, do mais interno para o mais externo
        for escopo in reversed(self.pilha_escopos):
            variavel = escopo.obter_variavel(lexema)
            if variavel:
                return variavel
        return None

# Função que faz o pré-processamento de uma linha de código
def preprocessar_linha(linha):
    pattern = r'(?<!\s)([=,])(?!\s)' 
    return re.sub(pattern, r' \1 ', linha)

def analisar_programa(conteudo_programa):
    gerenciador = GerenciadorEscopos()
    linhas = conteudo_programa.strip().split('\n')

    # Itera sobre cada linha do programa
    for num_linha, linha in enumerate(linhas):
        linha = linha.split('#')[0].strip()  # Remove comentários
        if not linha:
            continue

        linha = preprocessar_linha(linha)  # Pré-processa a linha para adicionar espaços
        tokens = linha.split()

        if not tokens:
            continue

        comando = tokens[0]  # Obtém o comando (primeiro token da linha)
        if comando == 'BLOCO':
            gerenciador.entrar_escopo()  # Adiciona um novo escopo à pilha
        elif comando == 'FIM':
            gerenciador.sair_escopo()  # Remove o escopo mais recente da pilha
        elif comando in ['NUMERO', 'CADEIA']:
            tipo = comando 
            declaracoes = ' '.join(tokens[1:]).split(',')  # Divide a linha em declarações de variáveis
            for declaracao in declaracoes:
                partes = declaracao.split('=')  # Divide a declaração em nome e valor
                lexema_var = partes[0].strip()
                valor = "" if tipo == 'CADEIA' else 0  # Define o valor padrão baseado no tipo
                if len(partes) > 1:
                    valor = partes[1].strip().strip('"')  # Remove aspas do valor, se houver
                    if tipo == 'NUMERO':
                        try:
                            valor = float(valor) if '.' in valor or 'e' in valor.lower() else int(valor)
                        except ValueError:
                            print(f"Erro linha {num_linha + 1}: Valor inválido '{valor}' para o tipo {tipo}.")
                            continue
                gerenciador.adicionar_variavel(lexema_var, tipo, valor, num_linha)  # Adiciona a variável ao escopo atual
        elif comando == 'PRINT':
            variavel = gerenciador.encontrar_variavel(tokens[1].strip())  # Procura a variável no escopo
            if variavel:
                valor = variavel['valor']
                print(f'"{valor}"' if variavel['tipo'] == 'CADEIA' else valor)  # Imprime o valor da variável
            else:
                print(f"Erro linha {num_linha + 1} - Variável não declarada.")
        elif len(tokens) > 2 and tokens[1] == '=':
            lexema_var = tokens[0].strip()
            valor = ' '.join(tokens[2:]).strip()
            variavel_destino = gerenciador.encontrar_variavel(lexema_var)  # Procura a variável de destino no escopo
            if valor.startswith('"') and valor.endswith('"'):
                valor = valor.strip('"')  
            elif valor.replace('.', '', 1).isdigit() or (valor[0] in '+-' and valor[1:].replace('.', '', 1).isdigit()):
                valor = float(valor) if '.' in valor or 'e' in valor.lower() else int(valor)  # Converte o valor para número
            else:
                variavel_origem = gerenciador.encontrar_variavel(valor)  # Procura a variável de origem no escopo
                if variavel_origem:
                    valor = variavel_origem['valor']
                else:
                    print(f"Erro linha {num_linha + 1} - Variável não declarada.")
                    continue
            if variavel_destino:
                if (variavel_destino['tipo'] == 'NUMERO' and isinstance(valor, (int, float))) or \
                   (variavel_destino['tipo'] == 'CADEIA' and isinstance(valor, str)):
                    variavel_destino['valor'] = valor  # Atribui o valor à variável de destino
                else:
                    print(f"Erro linha {num_linha + 1}, tipos não compatíveis.")
            else:
                print(f"Erro linha {num_linha + 1} - Variável não declarada.")


def main():
    if len(sys.argv) != 2:
        print("Digite o comando python main.py (nome do arquivo.txt)")
        return

    nome_arquivo = sys.argv[1]
    try:
        with open(nome_arquivo, 'r') as arquivo:
            conteudo_programa = arquivo.read()
        analisar_programa(conteudo_programa)
    except FileNotFoundError:
        print(f"Erro: nome invalido ou arquivo '{nome_arquivo}' não localizado.")

if __name__ == "__main__":
    main()
