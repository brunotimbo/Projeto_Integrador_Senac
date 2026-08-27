# blibliotecas e importações
import sqlite3
import tkinter as tk
import tkinter.messagebox as messagebox                         # mensgens de aviso
from tkinter import ttk                                         # importar subbliboteca do tkinter para tabela
from tkinter import filedialog as filedialog

# variáveis globais
entry_busca_ingrediente = None
caminho_imagem = ""

def conectar_banco_dados():
    # conexão com banco de dados
    conexao = sqlite3.connect('ficha_tecnica.db')
    cursor = conexao.cursor()

    # cria tabela ficha técnica
    cursor.execute('''CREATE TABLE IF NOT EXISTS fichas(
            id INTEGER PRIMARY KEY,
	        nome_preparo TEXT NOT NULL,
            imagem BLOB,
            nome_profissional TEXT,
            data_criacao TEXT DEFAULT (datetime('now', 'localtime')),
            data_atualizacao TEXT DEFAULT (datetime('now', 'localtime')),
            lista_ingredientes TEXT NOT NULL,
            quantidade_comprada INTEGER,
            valor_comprado_ingrediente REAL,
            quantidade_usada_ingrediente INTEGER,
            unidade_medida TEXT NOT NULL,
            valor_gasto_ingrediente REAL,
	        custo total REAL,          
	        porcoes REAL,
	        custo_porcao REAL,
	        modo_preparo TEXT) 
    ''')

    # cria tabela ingredientes
    cursor.execute('''CREATE TABLE IF NOT EXISTS ingredientes(
            id INTEGER PRIMARY KEY,
            ingrediente TEXT NOT NULL)
            ''')

    conexao.commit()
    conexao.close()

##########################  FUNÇÕES DE INGREDIENTES    ##########################

def pesquisar_ingrediente():

    ingrediente_procurado = entry_busca_ingrediente.get().strip()

    if not ingrediente_procurado:
        messagebox.showwarning("Aviso", "O campo não pode ficar vazio!")

    else:

        conexao = sqlite3.connect("ficha_tecnica.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT id, ingrediente FROM ingredientes WHERE ingrediente LIKE ?", ("%" + ingrediente_procurado + "%",),)
        resultado = cursor.fetchall()
        conexao.close()

        # Se a pesquisa não retornar nada, você também pode avisar o usuário se quiser
        if not resultado:
            messagebox.showinfo("Informação", "Nenhum ingrediente encontrado com esse termo.")

        limpar_tabela_ingredientes()


        # Insere os resultados na tabela do Tkinter
        for linha in resultado:
            tabela_ingredientes.insert("", tk.END, values=linha)

#atualizar ingrediente
def atualizar_ingrediente(ingrediente):
    conexao = sqlite3.connect("ficha_tecnica.db")
    cursor = conexao.cursor()
    cursor.execute("UPDATE ingredientes SET ingrediente = ?", (ingrediente))
    conexao.commit()
    conexao.close()

#deletar ingrediente
def deletar_ingrediente(ingrediente):
    conexao = sqlite3.connect("ficha_tecnica.db")
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM ingredientes WHERE ingrediente = ?", (ingrediente))
    conexao.commit()
    conexao.close()

# limpar janela
def limpar_janela():
      for widget in janela.winfo_children():
            widget.destroy()

# limpa a tabela ingredientes
def limpar_tabela_ingredientes():
    
    for item in tabela_ingredientes.get_children():
        tabela_ingredientes.delete(item)

# atualiza a tabela ingredientes
def atualizar_tabela_ingredientes():

    limpar_tabela_ingredientes()

    # Conecta ao banco de dados SQLite
    conexao = sqlite3.connect("ficha_tecnica.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT id, ingrediente FROM ingredientes")
    linhas = cursor.fetchall()

    # Insere os dados na Treeview
    for linha in linhas:
        tabela_ingredientes.insert("", "end", values=linha)

    conexao.close()

# deleta ingrediente da tabela ingrendientes
def deletar_ingrediente():
    selecionados = tabela_ingredientes.selection()
    
    if not selecionados:
        messagebox.showwarning("Aviso", "Selecione uma linha para deletar.")
        return
    
    # 1. Caixa de confirmação antes de alterar o banco de dados
    confirmacao = messagebox.askyesno(
        "Confirmar Exclusão", 
        f"Tem certeza que deseja deletar {len(selecionados)} item(ns)?"
    )
    
    # 2. Se o usuário clicar em "Não", interrompe a função
    if not confirmacao:
        return
        
    # 3. Se clicou em "Sim", o código abaixo continua e deleta
    conexao = sqlite3.connect("ficha_tecnica.db")
    cursor = conexao.cursor()
    
    for item in selecionados:
        valores = tabela_ingredientes.item(item, "values")
        id_registro = valores[0]
        
        cursor.execute("DELETE FROM ingredientes WHERE id = ?", (id_registro,))
        tabela_ingredientes.delete(item)
        
    conexao.commit()
    conexao.close()
    messagebox.showinfo("Sucesso", "Registro(s) deletado(s) com sucesso!")

# abre pop-up adicionar ingrediente
def abrir_popup_adicionar_ingrediente():
    popup_adicionar_ingrediente = tk.Toplevel()
    popup_adicionar_ingrediente.title("Editar Ingrediente")
    popup_adicionar_ingrediente.geometry("300x150")
    # Bloqueia a janela principal até fechar o pop-up
    popup_adicionar_ingrediente.grab_set()

    # Elementos visuais do Pop-up
    label = tk.Label(popup_adicionar_ingrediente, text="Nome do Ingrediente:")
    label.pack(pady=10)

    entry_adicionar_ingrediente = tk.Entry(popup_adicionar_ingrediente, width=30)
    entry_adicionar_ingrediente.pack(pady=5)

    def cadastrar_ingrediente_banco():
        novo_ingrediente = entry_adicionar_ingrediente.get().strip()

        if not novo_ingrediente:
            messagebox.showwarning("Aviso", "O campo não pode ficar vazio!")
            return
        
        else:
            # Atualiza no Banco de Dados SQLite3
            conexao = sqlite3.connect("ficha_tecnica.db")
            cursor = conexao.cursor()
            cursor.execute("INSERT INTO ingredientes (ingrediente) VALUES (?)", (novo_ingrediente,))
            conexao.commit()
            conexao.close()    

            # Atualiza a linha visualmente na tabela Tkinter
            atualizar_tabela_ingredientes()

            # Fecha o pop-up e avisa o usuário
            popup_adicionar_ingrediente.destroy()
            messagebox.showinfo("Sucesso", "Ingrediente adicionado com sucesso.")

    # Botão Salvar dentro do Pop-up
    botao_salvar = tk.Button(popup_adicionar_ingrediente, text="Salvar", command=cadastrar_ingrediente_banco)
    botao_salvar.pack(pady=15)

# abre popup para edição do nome do ingrediente    
def abrir_popup_editar_ingrediente():
    # 1. Verifica se há uma linha selecionada
    selecao = tabela_ingredientes.selection()
    if not selecao:
        messagebox.showwarning("Aviso", "Por favor, selecione um ingrediente para editar!")
        return

    # 2. Captura a linha selecionada e seus dados
    item_id = selecao[0]
    valores = tabela_ingredientes.item(item_id, "values")

    # Supondo que a tabela tem: Coluna 0 (ID) e Coluna 1 (Nome)
    id_ingrediente = valores[0]
    nome_atual = valores[1]

    # 3. Criação do pop-up editar ingrediente
    popup_editar_ingrediente = tk.Toplevel()
    popup_editar_ingrediente.title("Editar Ingrediente")
    popup_editar_ingrediente.geometry("300x150")
    # Bloqueia a janela principal até fechar o pop-up
    popup_editar_ingrediente.grab_set()

    # Elementos visuais do Pop-up
    label = tk.Label(popup_editar_ingrediente, text="Nome do ingrediente:")
    label.pack(pady=10)

    entry_editar_ingrediente = tk.Entry(popup_editar_ingrediente, width=30)
    entry_editar_ingrediente.pack(pady=5)
    # Preenche o campo com o nome atual do ingrediente
    entry_editar_ingrediente.insert(0, nome_atual)

    def atualizar_ingrediente_banco():
        # 4. Função interna para salvar os dados
        novo_nome = entry_editar_ingrediente.get().strip()

        if not novo_nome:
            messagebox.showwarning("Aviso", "O nome não pode ficar vazio!")
            return

        else:
            # Atualiza no Banco de Dados SQLite3
            conexao = sqlite3.connect("ficha_tecnica.db")
            cursor = conexao.cursor()
            cursor.execute("UPDATE ingredientes SET ingrediente = ? WHERE id = ?", (novo_nome, id_ingrediente))
            conexao.commit()
            conexao.close()

            # Atualiza a linha visualmente na tabela Tkinter
            tabela_ingredientes.item(item_id, values=(id_ingrediente, novo_nome))

            # Fecha o pop-up e avisa o usuário
            popup_editar_ingrediente.destroy()
            messagebox.showinfo("Sucesso", "Ingrediente atualizado com sucesso!")

    # Botão Salvar dentro do Pop-up
    botao_salvar = tk.Button(popup_editar_ingrediente, text="Salvar", command=atualizar_ingrediente_banco)
    botao_salvar.pack(pady=15)

##########################  FUNÇÕES DE FICHA    ##########################

def buscar_ingredientes_por_nome(texto_digitado):
    conexao = sqlite3.connect('ficha_tecnica.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT ingrediente FROM ingredientes WHERE ingrediente LIKE ? ORDER BY ingrediente LIMIT 10", (f"%{texto_digitado}%",))
    resultados = [linha[0] for linha in cursor.fetchall()]
    conexao.close()
    return resultados

def abrir_popup_adicionar_ingrediente_ficha():
    popup_adicionar_ingrediente_ficha = tk.Toplevel()
    popup_adicionar_ingrediente_ficha.title("Ingrediente na Ficha")
    popup_adicionar_ingrediente_ficha.geometry("700x200")
    # Bloqueia a janela principal até fechar o pop-up
    popup_adicionar_ingrediente_ficha.grab_set()

    frame_busca = tk.Frame(popup_adicionar_ingrediente_ficha)
    frame_busca.pack(padx=10, fill="x")


    entry_ingrediente = tk.Entry(frame_busca, width=40)
    entry_ingrediente.pack(fill="x")

    # Listbox de sugestões - começa escondida
    lista_sugestoes = tk.Listbox(popup_adicionar_ingrediente_ficha, height=5)
 
 
    def mostrar_sugestoes(event=None):
        texto = entry_ingrediente.get().strip()
    
        if texto == "":
            lista_sugestoes.pack_forget()
            return
    
        resultados = buscar_ingredientes_por_nome(texto)
    
        lista_sugestoes.delete(0, "end")
    
        if not resultados:
            lista_sugestoes.pack_forget()
            return
    
        for item in resultados:
            lista_sugestoes.insert("end", item)
    
        # exibe a listbox logo abaixo do campo de busca, só se ainda não estiver visível
        if not lista_sugestoes.winfo_ismapped():
            lista_sugestoes.pack(padx=10, fill="x", after=frame_busca)
    
    
    def selecionar_sugestao(event):
        if not lista_sugestoes.curselection():
            return
        valor_selecionado = lista_sugestoes.get(lista_sugestoes.curselection())
    
        entry_ingrediente.delete(0, "end")
        entry_ingrediente.insert(0, valor_selecionado)
    
        lista_sugestoes.pack_forget()
    
    
    def esconder_sugestoes_ao_perder_foco(event):
        # pequeno delay pra dar tempo do clique na listbox ser processado antes de esconder
        janela.after(150, lista_sugestoes.pack_forget)
    
    
    entry_ingrediente.bind("<KeyRelease>", mostrar_sugestoes)
    lista_sugestoes.bind("<<ListboxSelect>>", selecionar_sugestao)
    entry_ingrediente.bind("<FocusOut>", esconder_sugestoes_ao_perder_foco)

# Elementos visuais do Pop-up
    label6 = tk.Label(popup_adicionar_ingrediente_ficha, text="Quantidade comprada:")
    label6.pack(pady=10)
    entry_adicionar_quantidade_comprada_ficha = tk.Entry(popup_adicionar_ingrediente_ficha, width=30)
    entry_adicionar_quantidade_comprada_ficha.pack(pady=5)

# Elementos visuais do Pop-up
    label7 = tk.Label(popup_adicionar_ingrediente_ficha, text="Valor comprado:")
    label7.pack(pady=10)
    entry_adicionar_valor_comprado_ficha = tk.Entry(popup_adicionar_ingrediente_ficha, width=30)
    entry_adicionar_valor_comprado_ficha.pack(pady=5)

# Elementos visuais do Pop-up
    label8 = tk.Label(popup_adicionar_ingrediente_ficha, text="Quantidade usada:")
    label8.pack(pady=10)
    entry_adicionar_quantidade_usada_ficha = tk.Entry(popup_adicionar_ingrediente_ficha, width=30)
    entry_adicionar_quantidade_usada_ficha.pack(pady=5)

# Elementos visuais do Pop-up
    label9 = tk.Label(popup_adicionar_ingrediente_ficha, text="Unidade de medida:")
    label9.pack(pady=10)
    entry_adicionar_unidade_medida_ficha = tk.Entry(popup_adicionar_ingrediente_ficha, width=30)
    entry_adicionar_unidade_medida_ficha.pack(pady=5)

def abrir_popup_editar_ingrediente_ficha():
    pass

def abrir_popup_excluir_ingrediente_ficha():
    pass

def selecionar_imagem():
    global caminho_imagem
    # Abre o explorador de arquivos para escolher a imagem
    caminho_imagem = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=[("Arquivos de Imagem", "*.jpg *.jpeg *.png")]
    )
    if caminho_imagem:
        lbl_status.config(text=f"Selecionado: {caminho_imagem.split('/')[-1]}")


def buscar_ingredientes(termo=""):
  conexao = sqlite3.connect("ficha_tecnica.db")
  cursor = conexao.cursor()

  if termo == "":
    # Busca todos os ingredientes em ordem alfabética no início
    cursor.execute("SELECT ingrediente FROM ingredientes ORDER BY ingrediente")
  else:
    # Busca filtrada por termos digitados
    cursor.execute(
        "SELECT ingrediente FROM ingredientes WHERE ingrediente LIKE ? ORDER BY ingrediente",
        (f"%{termo}%",),
    )

  resultados = cursor.fetchall()
  conexao.close()

  # Retorna uma lista limpa apenas com os textos
  return [linha[0] for linha in resultados]


def atualizar_lista(sugestoes):
  # Limpa a lista antes de colocar novos dados
  lista_sugestoes.delete(0, tk.END)

  if sugestoes:
    # Se encontrou ingredientes, adiciona normalmente
    for item in sugestoes:
      lista_sugestoes.insert(tk.END, item)
  else:
    # Se a busca veio vazia (Nenhum resultado), mostra o aviso
    lista_sugestoes.insert(tk.END, 'Nenhum ingrediente encontrado')




def ao_digitar(event):
  if event.keysym in ("Up", "Down", "Return", "Escape"):
    return

  digitado = entrada_ingrediente.get()

  # Se tiver 2 ou mais letras, filtra. Se tiver menos, mostra tudo de novo.
  if len(digitado) >= 2:
    sugestoes = buscar_ingredientes(digitado)
    atualizar_lista(sugestoes)
  else:
    sugestoes_iniciais = buscar_ingredientes()
    atualizar_lista(sugestoes_iniciais)

def ao_selecionar(event):
  if lista_sugestoes.curselection():
    indice = lista_sugestoes.curselection()
    escolha = lista_sugestoes.get(indice)

    # Bloqueia a seleção caso o texto seja a mensagem de erro
    if escolha == 'Nenhum ingrediente encontrado':
      return

    # Preenche o campo de texto se for um ingrediente válido
    entrada_ingrediente.delete(0, tk.END)
    entrada_ingrediente.insert(0, escolha)

def navegar_lista(event):
  # Permite descer para a lista usando a seta do teclado
  if event.keysym == "Down" and lista_sugestoes.size() > 0:
    lista_sugestoes.focus_set()
    lista_sugestoes.selection_set(0)


def popup_incluir_ingrediente_ficha():

    global entrada_ingrediente, lista_sugestoes

    popup_incluir_ingrediente_ficha = tk.Toplevel()
    popup_incluir_ingrediente_ficha.title("Nova Ficha Técnica")
    popup_incluir_ingrediente_ficha.geometry("300x700")
    # Bloqueia a janela principal até fechar o pop-up
    popup_incluir_ingrediente_ficha.grab_set()

    # Rótulo
    rotulo = tk.Label(janela, text="Digite ou selecione o ingrediente:")
    rotulo.pack(pady=10)

    # Campo de entrada de texto
    entrada_ingrediente = tk.Entry(popup_incluir_ingrediente_ficha, width=30)
    entrada_ingrediente.pack(pady=5)

    # Frame para agrupar a lista e a barra de rolagem lado a lado
    frame_lista = tk.Frame(popup_incluir_ingrediente_ficha)
    frame_lista.pack(pady=5)

    # Barra de Rolagem (Scrollbar)
    barra_rolagem = tk.Scrollbar(frame_lista, orient=tk.VERTICAL)

    # Lista de sugestões fixa na tela
    lista_sugestoes = tk.Listbox(
        frame_lista, width=28, height=8, yscrollcommand=barra_rolagem.set
    )

    # Configura a barra para rolar a lista de ingredientes
    barra_rolagem.config(command=lista_sugestoes.yview)

    # Posiciona a lista e a barra lado a lado dentro do Frame
    lista_sugestoes.pack(side=tk.LEFT, fill=tk.BOTH)
    barra_rolagem.pack(side=tk.RIGHT, fill=tk.Y)

    # Carrega todos os ingredientes logo na abertura do programa
    ingredientes_iniciais = buscar_ingredientes()
    atualizar_lista(ingredientes_iniciais)

    # Vinculação de Eventos (Binds)
    entrada_ingrediente.bind("<KeyRelease>", ao_digitar)
    entrada_ingrediente.bind("<Down>", navegar_lista)

    # Eventos para clique simples, duplo clique ou Enter na lista
    lista_sugestoes.bind("<<ListboxSelect>>", ao_selecionar)
    lista_sugestoes.bind("<Double-Button-1>", ao_selecionar)
    lista_sugestoes.bind("<Return>", ao_selecionar)

    label_quantidade_comprada = tk.Label(popup_incluir_ingrediente_ficha, text="Quantidade comprada:")
    label_quantidade_comprada.pack(pady=10)
    entry_quantidade_comprada = tk.Entry(popup_incluir_ingrediente_ficha, width=30)
    entry_quantidade_comprada.pack(pady=5)

    label_valor_comprada = tk.Label(popup_incluir_ingrediente_ficha, text="Valor comprado:")
    label_valor_comprada.pack(pady=10)
    entry_valor_comprado = tk.Entry(popup_incluir_ingrediente_ficha, width=30)
    entry_valor_comprado.pack(pady=5)

    label_quantidade_usada = tk.Label(popup_incluir_ingrediente_ficha, text="Quantidade usada:")
    label_quantidade_usada.pack(pady=10)
    entry_quantidade_usada = tk.Entry(popup_incluir_ingrediente_ficha, width=30)
    entry_quantidade_usada.pack(pady=5)

    label_unidade_medida = tk.Label(popup_incluir_ingrediente_ficha, text="Unidade de medida:")
    label_unidade_medida.pack(pady=10)
    entry_unidade_medida = tk.Entry(popup_incluir_ingrediente_ficha, width=30)
    entry_unidade_medida.pack(pady=5)

# abre pop-up adicionar ingrediente
def abrir_popup_adicionar_ficha():
    popup_adicionar_ficha = tk.Toplevel()
    popup_adicionar_ficha.title("Nova Ficha Técnica")
    popup_adicionar_ficha.geometry("700x700")
    # Bloqueia a janela principal até fechar o pop-up
    popup_adicionar_ficha.grab_set()

    # frame do popup adicionar ficha
    frame_popup = tk.Frame(popup_adicionar_ficha, borderwidth=1, relief="raised")
    frame_popup.pack(fill="both", expand=True)

    frame_popup_cabecalho = tk.Frame(frame_popup, borderwidth=1, relief="raised")
    frame_popup_cabecalho.pack(fill="both", expand=True)    

    # ---------- COLUNA DA ESQUERDA (imagem) ----------
    frame_esquerda = tk.Frame(frame_popup_cabecalho, width=200, height=200, borderwidth=1, relief="solid")
    frame_esquerda.pack(side="left", padx=10, pady=10, anchor="n", fill="both")
    frame_esquerda.pack_propagate(False)  # mantém tamanho fixo mesmo sem imagem

    # Botão que funciona como widget para inserir a imagem
    botao_imagem = tk.Button(frame_esquerda, text="Escolher Imagem", command=selecionar_imagem)
    botao_imagem.pack(pady=10, expand=True)

    lbl_status = tk.Label(frame_esquerda, text="Nenhuma imagem selecionada", fg="gray")
    lbl_status.pack(pady=5)

    # ---------- COLUNA DA DIREITA (campos de digitação) ----------
    frame_direita = tk.Frame(frame_popup_cabecalho, borderwidth=1, relief="solid")
    frame_direita.pack(fill="both", expand=True, padx=10, pady=10)    


    def criar_campo(frame_pai, texto_label, largura_entry=20):
        frame_campo = tk.Frame(frame_pai, borderwidth="1", relief="solid")
        frame_campo.pack(padx=10)
        label = tk.Label(frame_campo, text=texto_label)
        label.pack(anchor="w")
        entry = tk.Entry(frame_campo, width=largura_entry)
        entry.pack(anchor="w", pady=5)

        return entry

    frame_popup_menu_tabela = tk.Frame(frame_popup, borderwidth=1, relief="raised")
    frame_popup_menu_tabela.pack(fill="both", expand=True, anchor="center")

    # botões da tela ingredientes
    botao_retirar_ingrediente_ficha = tk.Button(frame_popup_menu_tabela, text="Retirar Ingrediente")
    botao_retirar_ingrediente_ficha.pack(side= "right", padx=10, anchor="center", expand=True)

    botao_editar_ingrediente_ficha = tk.Button(frame_popup_menu_tabela, text="Editar Ingrediente")
    botao_editar_ingrediente_ficha.pack(side= "right", padx=10, anchor="center", expand=True)

    botao_incluir_ingrediente_ficha = tk.Button(frame_popup_menu_tabela, text="Incluir Ingrediente", command=popup_incluir_ingrediente_ficha)
    botao_incluir_ingrediente_ficha.pack(side= "right", padx=10, anchor="center", expand=True)

    frame_popup_tabela = tk.Frame(frame_popup, borderwidth=1, relief="raised")
    frame_popup_tabela.pack(fill="both", expand=True) 
    


# # Elementos visuais do Pop-up
#     label1 = tk.Label(frame_popup_1, text="Nome do preparo:")
#     label1.pack(side="left")
#     entry_adicionar_nome_preparo_ficha = tk.Entry(frame_popup_1, width=30)
#     entry_adicionar_nome_preparo_ficha.pack(side="left", pady=5)
# # Elementos visuais do Pop-up
#     label2 = tk.Label(frame_popup_1, text="Profissional responsável:")
#     label2.pack(side="left")
#     entry_adicionar_profissional_ficha = tk.Entry(frame_popup_1, width=30)
#     entry_adicionar_profissional_ficha.pack(side="left", pady=5)

# # Elementos visuais do Pop-up
#     label3 = tk.Label(frame_popup_1, text="Data de criação:")
#     label3.pack()
#     entry_adicionar_data_criacao_ficha = tk.Entry(frame_popup_1, width=30)
#     entry_adicionar_data_criacao_ficha.pack(pady=5)

# # Elementos visuais do Pop-up
#     label4 = tk.Label(frame_popup_1, text="Data de atualização:")
#     label4.pack()
#     entry_adicionar_data_atualizacao_ficha = tk.Entry(frame_popup_1, width=30)
#     entry_adicionar_data_atualizacao_ficha.pack(pady=5)

# Elementos visuais do Pop-up
    label5 = tk.Label(popup_adicionar_ficha, text="Lista de ingredientes:")
    label5.pack(pady=10)
    entry_adicionar_lista_ingredientes_ficha = tk.Entry(popup_adicionar_ficha, width=30)
    entry_adicionar_lista_ingredientes_ficha.pack(pady=5)

# Elementos visuais do Pop-up
    label6 = tk.Label(popup_adicionar_ficha, text="Quantidade comprada:")
    label6.pack(pady=10)
    entry_adicionar_quantidade_comprada_ficha = tk.Entry(popup_adicionar_ficha, width=30)
    entry_adicionar_quantidade_comprada_ficha.pack(pady=5)

# Elementos visuais do Pop-up
    label7 = tk.Label(popup_adicionar_ficha, text="Valor comprado:")
    label7.pack(pady=10)
    entry_adicionar_valor_comprado_ficha = tk.Entry(popup_adicionar_ficha, width=30)
    entry_adicionar_valor_comprado_ficha.pack(pady=5)

# Elementos visuais do Pop-up
    label8 = tk.Label(popup_adicionar_ficha, text="Quantidade usada:")
    label8.pack(pady=10)
    entry_adicionar_quantidade_usada_ficha = tk.Entry(popup_adicionar_ficha, width=30)
    entry_adicionar_quantidade_usada_ficha.pack(pady=5)

# Elementos visuais do Pop-up
    label9 = tk.Label(popup_adicionar_ficha, text="Unidade de medida:")
    label9.pack(pady=10)
    entry_adicionar_unidade_medida_ficha = tk.Entry(popup_adicionar_ficha, width=30)
    entry_adicionar_unidade_medida_ficha.pack(pady=5)

# Elementos visuais do Pop-up
#     label10 = tk.Label(popup_adicionar_ficha, text="Porções:")
#     label10.pack(pady=10)
#     entry_adicionar_porcoes_ficha = tk.Entry(popup_adicionar_ficha, width=30)
#     entry_adicionar_porcoes_ficha.pack(pady=5)

# # Elementos visuais do Pop-up
#     label11 = tk.Label(popup_adicionar_ficha, text="Modo de preparo")
#     label11.pack(pady=10)
#     entry_adicionar_modo_preparo_ficha = tk.Entry(popup_adicionar_ficha, width=30)
#     entry_adicionar_modo_preparo_ficha.pack(pady=5)

    # def cadastrar_ficha_banco():
    #     novo_ingrediente = entry_adicionar_ingrediente.get().strip()

    #     if not novo_ingrediente:
    #         messagebox.showwarning("Aviso", "O campo não pode ficar vazio!")
    #         return
        
    #     else:
    #         # Atualiza no Banco de Dados SQLite3
    #         conexao = sqlite3.connect("ficha_tecnica.db")
    #         cursor = conexao.cursor()
    #         cursor.execute("INSERT INTO ingredientes (ingrediente) VALUES (?)", (novo_ingrediente,))
    #         conexao.commit()
    #         conexao.close()    

    #         # Atualiza a linha visualmente na tabela Tkinter
    #         atualizar_tabela_ingredientes()

    #         # Fecha o pop-up e avisa o usuário
    #         abrir_popup_adicionar_ficha.destroy()
    #         messagebox.showinfo("Sucesso", "Ficha Técnica adicionada com sucesso.")

    # Botão Salvar dentro do Pop-up
    # botao_salvar_ficha = tk.Button(abrir_popup_adicionar_ficha, text="Salvar")
    # botao_salvar_ficha.pack(pady=15)

##########################   TELAS   ##########################

# tela ingredientes
def tela_ingredientes():

    global entry_busca_ingrediente, tabela_ingredientes

    limpar_janela()

    # frame da tela ingredientes
    frame_ingredientes = tk.Frame(janela, borderwidth=1, relief="raised", bg="#FDC180")
    frame_ingredientes.pack(fill="both", expand=True)

    # título da tela ingredientes
    label_titulo = tk.Label(frame_ingredientes, text=" 🍴 Ingredientes 👨‍🍳", font=("Arial", 24), bg="#FDC180")
    label_titulo.pack(pady=10)

    frame_menu_ingredientes = tk.Frame(frame_ingredientes, borderwidth=1, relief="sunken" , bg="#80ACFD")
    frame_menu_ingredientes.pack(pady=10)

    # campo de busca de ingrdiente   
    entry_busca_ingrediente = tk.Entry(frame_menu_ingredientes)
    entry_busca_ingrediente.pack(side="left", padx=10, pady=5)

    # botões da tela ingredientes
    botao_ficha = tk.Button(frame_menu_ingredientes, text="Ficha Técnica", command=tela_ficha)
    botao_ficha.pack(side="right", padx=10, pady=5)
    
    botao_deletar_ingrediente = tk.Button(frame_menu_ingredientes, text="Deletar", command=deletar_ingrediente, bg="#da2222")
    botao_deletar_ingrediente.pack(side="right", padx=10, pady=5)

    botao_editar_ingrediente = tk.Button(frame_menu_ingredientes, text="Editar", command=abrir_popup_editar_ingrediente, bg="#dac722")
    botao_editar_ingrediente.pack(side="right", padx=10, pady=5)

    botao_atualizar_tabela_ingredientes = tk.Button(frame_menu_ingredientes, text="Mostrar Lista Completa", command=atualizar_tabela_ingredientes)
    botao_atualizar_tabela_ingredientes.pack(side="right", padx=10, pady=5) 

    botao_cadastrar_ingrediente = tk.Button(frame_menu_ingredientes, text="Adicionar", command=abrir_popup_adicionar_ingrediente , bg="#22da50")
    botao_cadastrar_ingrediente.pack(side="right", padx=10, pady=5)

    botao_pesquisar_ingrediente = tk.Button(frame_menu_ingredientes, text="Pesquisar", command=pesquisar_ingrediente)
    botao_pesquisar_ingrediente.pack(side="right", padx=10, pady=5)

    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure("Treeview.Heading", font=("Arial", 14, "bold"), background="#004c94", foreground="#f7941d")
    estilo.configure("Treeview", rowheight=28, font=("Arial", 10))

    # cria tabela
    tabela_ingredientes = ttk.Treeview(frame_ingredientes,columns=("id", "ingrediente") , show="headings", )

    # largura das colunas
    tabela_ingredientes.column("id", width=5, anchor="w")   # Coluna 1 com 100 pixels
    tabela_ingredientes.column("ingrediente", width=250, anchor="w")    # Coluna 2 com 250 pixels

    # títulos das colunas
    tabela_ingredientes.heading("id", text="ID")
    tabela_ingredientes.heading("ingrediente", text="Ingredientes")

    # exibe a tabela
    tabela_ingredientes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    conexao = sqlite3.connect("ficha_tecnica.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM ingredientes")
    resultado = cursor.fetchall()

    for linha in resultado:
        tabela_ingredientes.insert('', tk.END, values=linha)

    # Seleciona as colunas id e ingrediente da tabela
    cursor.execute("SELECT id, ingrediente FROM ingredientes")
    conexao.close()

# tela ficha
def tela_ficha():

    global lbl_status

    limpar_janela()

    # frame da tela ficha
    frame_ficha = tk.Frame(janela, borderwidth=1, relief="raised", bg="#FDC180")
    frame_ficha.pack(fill="both", expand=True)

    # título da tela ingredientes
    label_titulo = tk.Label(frame_ficha, text=" 🍴 Ficha Técnica de Preparo 👨‍🍳", font=("Arial", 24), bg="#FDC180")
    label_titulo.pack(pady=10)

    frame_menu_ficha = tk.Frame(frame_ficha, borderwidth=1, relief="raised")
    frame_menu_ficha.pack(pady=10)

    # campo de busca de ingrdiente   
    entry_busca_ficha = tk.Entry(frame_menu_ficha)
    entry_busca_ficha.pack(side="left", padx=10, pady=5)    

    # botões da tela ficha
    botao_ingredientes = tk.Button(frame_menu_ficha, text="Ingredientes", command=tela_ingredientes)
    botao_ingredientes.pack(side="right", padx=10, pady=5)

    botao_deletar_ficha = tk.Button(frame_menu_ficha, text="Deletar", command=deletar_ingrediente, bg="#da2222")
    botao_deletar_ficha.pack(side="right", padx=10, pady=5)
    
    botao_editar_ficha = tk.Button(frame_menu_ficha, text="Editar", command=abrir_popup_editar_ingrediente, bg="#dac722")
    botao_editar_ficha.pack(side="right", padx=10, pady=5)

    botao_cadastrar_ficha = tk.Button(frame_menu_ficha, text="Adicionar", command=abrir_popup_adicionar_ficha , bg="#22da50")
    botao_cadastrar_ficha.pack(side="right", padx=10, pady=5) 

    botao_pesquisar_ficha = tk.Button(frame_menu_ficha, text="Pesquisar")
    botao_pesquisar_ficha.pack(side="right", padx=10, pady=5)

   # ------------- FRAME PRINCIPAL -------------------------------
    frame_principal = tk.Frame(frame_ficha, borderwidth=1, relief="solid")
    frame_principal.pack(padx=10, pady=10)

    # ---------- COLUNA DA ESQUERDA (imagem) ----------
    frame_esquerda = tk.Frame(frame_principal, width=200, height=200, borderwidth=1, relief="solid")
    frame_esquerda.pack(side="left", padx=10, pady=10, anchor="n", fill="both")
    frame_esquerda.pack_propagate(False)  # mantém tamanho fixo mesmo sem imagem

    # Botão que funciona como widget para inserir a imagem
    botao_imagem = tk.Button(frame_esquerda, text="Escolher Imagem", command=selecionar_imagem)
    botao_imagem.pack(pady=10, expand=True)

    lbl_status = tk.Label(frame_esquerda, text="Nenhuma imagem selecionada", fg="gray")
    lbl_status.pack(pady=5)

    # ---------- COLUNA DA DIREITA (campos de digitação) ----------
    frame_direita = tk.Frame(frame_principal, borderwidth=1, relief="solid")
    frame_direita.pack(fill="both", expand=True, padx=10, pady=10)
 
    tk.Label(frame_direita, text="Nome do preparo:").pack(anchor="w", pady=(0, 2))
    entry_nome_preparo = tk.Entry(frame_direita, width=30)
    entry_nome_preparo.pack(anchor="w", pady=(0, 10))

    tk.Label(frame_direita, text="Profissional:").pack(anchor="w", pady=(0, 2))
    entry_nome_profissional = tk.Entry(frame_direita, width=30)
    entry_nome_profissional.pack(anchor="w", pady=(0, 10))

    tk.Label(frame_direita, text="Criação:").pack(anchor="w", pady=(0, 2))
    entry_data_criacao = tk.Entry(frame_direita, width=30)
    entry_data_criacao.pack(anchor="w", pady=(0, 10))

    tk.Label(frame_direita, text="Atualização:").pack(anchor="w", pady=(0, 2))
    entry_data_atualizacao = tk.Entry(frame_direita, width=30)
    entry_data_atualizacao.pack(anchor="w", pady=(0, 10))

    # ---------- FRAME TABELA FICHA ----------

    # cria tabela
    tabela_ficha = ttk.Treeview(frame_ficha,columns=(
                                                    "lista_ingredientes",
                                                    "quantidade_comprada",
                                                    "valor_comprado_ingrediente",
                                                    "quantidade_usada_ingrediente",
                                                    "unidade_medida",
                                                    "valor_gasto_ingrediente") ,
                                                    show="headings", )

    # largura das colunas
    tabela_ficha.column("lista_ingredientes", width=50, anchor="w")   
    tabela_ficha.column("quantidade_comprada", width=50, anchor="w")    
    tabela_ficha.column("valor_comprado_ingrediente", width=50, anchor="w")    
    tabela_ficha.column("quantidade_usada_ingrediente", width=50, anchor="w")    
    tabela_ficha.column("unidade_medida", width=50, anchor="w")    
    tabela_ficha.column("valor_gasto_ingrediente", width=50, anchor="w")   

    # títulos das colunas
    tabela_ficha.heading("lista_ingredientes", text="Ingredientes")   
    tabela_ficha.heading("quantidade_comprada", text="Qtd Comprada")    
    tabela_ficha.heading("valor_comprado_ingrediente", text="Valor Comprado")    
    tabela_ficha.heading("quantidade_usada_ingrediente", text="Qtd Usada")    
    tabela_ficha.heading("unidade_medida", text="Medida")    
    tabela_ficha.heading("valor_gasto_ingrediente", text="Valor Gasto")

    conexao = sqlite3.connect("ficha_tecnica.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM fichas")
    resultado = cursor.fetchall()

    for linha in resultado:
        tabela_ficha.insert('', tk.END, values=linha)

    # Seleciona as colunas id e ingrediente da tabela
    cursor.execute("SELECT lista_ingredientes, quantidade_comprada,  valor_comprado_ingrediente,  quantidade_usada_ingrediente, unidade_medida, valor_gasto_ingrediente FROM fichas")
    conexao.close()  
    

    # exibe a tabela
    tabela_ficha.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
 
    # frame_tabela_ficha = tk.Frame(frame_ficha, borderwidth=1, relief="solid")
    # frame_tabela_ficha.pack(padx=10, pady=10)
    
    

##########################   INÍCIO   ##########################

conectar_banco_dados()

# cria a janela principal
janela = tk.Tk()
janela.title("Maedu")
janela.geometry("700x700")
janela.resizable(False, False)

tela_ficha()

janela.mainloop()