import pandas as pd
import subprocess  # Módulo para executar comandos do sistema

class LojaConveniencia:
    def __init__(self, arquivo_planilha, caixa_inicial=1000):
        self.arquivo_planilha = arquivo_planilha
        self.caixa = caixa_inicial
        self.carregar_dados()

    def carregar_dados(self):
        try:
            dados = pd.read_excel(self.arquivo_planilha, sheet_name='dados_loja')
            self.estoque = dados.set_index('Produto')[['Quantidade', 'Preco_Compra', 'Preco_Venda']]
            self.caixa = dados['Caixa'].iloc[0]
        except FileNotFoundError:
            self.criar_planilha()
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            self.estoque = pd.DataFrame(columns=['Quantidade', 'Preco_Compra', 'Preco_Venda'])

    def salvar_dados(self):
        dados = pd.DataFrame({'Produto': self.estoque.index, 'Quantidade': self.estoque['Quantidade'].values,
                              'Preco_Compra': self.estoque['Preco_Compra'].values,
                              'Preco_Venda': self.estoque['Preco_Venda'].values})
        dados['Caixa'] = self.caixa
        dados.to_excel(self.arquivo_planilha, index=False, sheet_name='dados_loja')

    def criar_planilha(self):
        dados = pd.DataFrame({'Produto': [], 'Quantidade': [], 'Preco_Compra': [], 'Preco_Venda': [], 'Caixa': []})
        dados.to_excel(self.arquivo_planilha, index=False, sheet_name='dados_loja')

    def mostrar_estoque(self):
        print("Estoque:")
        if self.estoque.last_valid_index() is None:
            print('O estoque está vazio')
        else:
            temp_csv_path = 'temp_estoque.csv'
            self.estoque.to_csv(temp_csv_path, index_label='Produto')

            subprocess.run(['csvlook', temp_csv_path], check=True)

            subprocess.run(['rm', temp_csv_path], check=True)

    def mostrar_caixa(self):
        print(f"Caixa disponível: ${self.caixa:.2f}")

    def entrada_caixa(self, valor):
        self.caixa += valor
        print(f"Entrada de caixa: +${valor:.2f}")
        self.mostrar_caixa()

    def saida_caixa(self, valor):
        if valor > self.caixa:
            print("Erro: Fundos insuficientes.")
        else:
            self.caixa -= valor
            print(f"Saida de caixa: -${valor:.2f}")
            self.mostrar_caixa()

    def adicionar_produto(self, produto, quantidade, preco_compra, preco_venda):
        if produto in self.estoque.index:
            self.estoque.at[produto, 'Quantidade'] += quantidade
        else:
            novo_produto = pd.Series({'Quantidade': quantidade, 'Preco_Compra': preco_compra,
                                      'Preco_Venda': preco_venda}, name=produto)
            self.estoque = pd.concat([self.estoque, novo_produto.to_frame().T])
        custo_total = quantidade * preco_compra
        self.saida_caixa(custo_total)
        print(f"Produto '{produto}' adicionado ao estoque. Custo: ${custo_total:.2f}")

    def vender_produto(self, produto, quantidade):
        if produto in self.estoque.index and self.estoque.at[produto, 'Quantidade'] >= quantidade:
            preco_venda = self.estoque.at[produto, 'Preco_Venda']
            valor_total = quantidade * preco_venda
            self.estoque.at[produto, 'Quantidade'] -= quantidade
            self.entrada_caixa(valor_total)
            print(f"{quantidade} unidades de '{produto}' vendidas. Valor: ${valor_total:.2f}")
        else:
            print("Erro: Produto indisponível ou quantidade insuficiente em estoque.")

    def exibir_menu(self):
        print("\nMenu:")
        print("1. Mostrar Estoque")
        print("2. Mostrar Caixa")
        print("3. Adicionar Produto")
        print("4. Vender Produto")
        print("5. Sair")
        return input("Escolha uma opção: ")

arquivo_planilha = 'loja_conveniencia.xlsx'

loja = LojaConveniencia(arquivo_planilha)

while True:
    escolha = loja.exibir_menu()

    if escolha == '1':
        loja.mostrar_estoque()
    elif escolha == '2':
        loja.mostrar_caixa()
    elif escolha == '3':
        produto = input("Nome do produto: ")
        quantidade = int(input("Quantidade: "))
        preco_compra = float(input("Preço de compra: $"))
        preco_venda = float(input("Preço de venda: $"))
        loja.adicionar_produto(produto, quantidade, preco_compra, preco_venda)
    elif escolha == '4':
        produto = input("Nome do produto: ")
        quantidade = int(input("Quantidade: "))
        loja.vender_produto(produto, quantidade)
    elif escolha == '5':
        loja.salvar_dados()
        print("Saindo do programa. Até mais!")
        break
    else:
        print("Opção inválida. Tente novamente.")
