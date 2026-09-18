# blibliotecas e importações
import sqlite3
import tkinter as tk
import tkinter.messagebox as messagebox                         # mensgens de aviso
from tkinter import ttk                                         # importar subbliboteca do tkinter para tabela
from tkinter import filedialog as filedialog

# variáveis globais
entry_busca_ingrediente = None
caminho_imagem = ""

###     CONECTA BANCO DE DADOS      #####################################################################

def conectar_banco_dados():
    # conexão com banco de dados
    conexao = sqlite3.connect('ficha_tecnica.db')
    cursor = conexao.cursor()

    # cria tabela ficha técnica
    cursor.execute('''CREATE TABLE IF NOT EXISTS fichas(
            id INTEGER PRIMARY KEY,
	        nome_preparo,
            imagem BLOB,
            nome_profissional TEXT,
            data_criacao TEXT DEFAULT (datetime('now', 'localtime')),
            data_atualizacao TEXT DEFAULT (datetime('now', 'localtime')),
            lista_ingredientes TEXT,
            quantidade_comprada INTEGER,
            valor_comprado_ingrediente REAL,
            quantidade_usada_ingrediente INTEGER,
            unidade_medida TEXT,
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

# cria tabela medidas
    cursor.execute('''CREATE TABLE IF NOT EXISTS medidas(
            id INTEGER PRIMARY KEY,
            nome_medida TEXT NOT NULL) 
    ''')

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relacao_fichas_ingredientes (
            id INTEGER PRIMARY KEY,
            id_ficha INTEGER NOT NULL,
            id_ingrediente INTEGER NOT NULL,
            quantidade_comprada REAL,
            valor_comprado REAL,
            quantidade_usada REAL,
            medida TEXT,
            valor_gasto REAL,
            FOREIGN KEY (id_ficha) REFERENCES fichas(id) ON DELETE CASCADE,
            FOREIGN KEY (id_ingrediente) REFERENCES ingredientes(id)
        )
    """)

    conexao.commit()
    conexao.close()

###  FUNÇÕES DE JANELA    #########################################################################

# limpa janela
def limpar_janela():
      for widget in janela.winfo_children():
            widget.destroy()

###  FUNÇÕES DE INGREDIENTES    #########################################################################

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

# limpa a tabela ingredientess
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
def popup_editar_ingrediente():
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

###     FUNÇÕES DE MEDIDAS      #############################################################

# crud

# pesquisar
def pesquisar_medida():

    medida_procurada = entry_busca_medida.get().strip()

    if not medida_procurada:
        messagebox.showwarning("Aviso", "O campo não pode ficar vazio!")

    else:

        conexao = sqlite3.connect("ficha_tecnica.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome_medida FROM medidas WHERE nome_medida LIKE ?", ("%" + medida_procurada + "%",),)
        resultado = cursor.fetchall()
        conexao.close()

        # Se a pesquisa não retornar nada, você também pode avisar o usuário se quiser
        if not resultado:
            messagebox.showinfo("Informação", "Nenhuma medida encontrada com esse termo.")

        limpar_tabela_medidas()

        # Insere os resultados na tabela do Tkinter
        for linha in resultado:
            tabela_medidas.insert("", tk.END, values=linha)

# limpa a tabela ingredientes
def limpar_tabela_medidas():
    
    for item in tabela_medidas.get_children():
        tabela_medidas.delete(item)

# atualiza a tabela ingredientes
def atualizar_tabela_medidas():

    limpar_tabela_medidas()

    # Conecta ao banco de dados SQLite
    conexao = sqlite3.connect("ficha_tecnica.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome_medida FROM medidas")
    linhas = cursor.fetchall()

    # Insere os dados na Treeview
    for linha in linhas:
        tabela_medidas.insert("", "end", values=linha)

    conexao.close()

# deletar
def deletar_medida():
    selecionados = tabela_medidas.selection()
    
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
        valores = tabela_medidas.item(item, "values")
        id_registro = valores[0]
        
        cursor.execute("DELETE FROM medidas WHERE id = ?", (id_registro,))
        tabela_medidas.delete(item)
        
    conexao.commit()
    conexao.close()
    messagebox.showinfo("Sucesso", "Medida deletada com sucesso!")

# popups de medidas

# adicionar
def popup_adicionar_medida():
    popup_adicionar_medida = tk.Toplevel()
    popup_adicionar_medida.title("Adicionar medida")
    popup_adicionar_medida.geometry("300x150")
    # Bloqueia a janela principal até fechar o pop-up
    popup_adicionar_medida.grab_set()

    # Elementos visuais do Pop-up
    label = tk.Label(popup_adicionar_medida, text="Nome da medida nova:")
    label.pack(pady=10)

    entry_adicionar_medida = tk.Entry(popup_adicionar_medida, width=30)
    entry_adicionar_medida.pack(pady=5)

    def cadastrar_medida_banco():
        nova_medida = entry_adicionar_medida.get().strip()

        if not nova_medida:
            messagebox.showwarning("Aviso", "O campo não pode ficar vazio!")
            return
        
        else:
            # Atualiza no Banco de Dados SQLite3
            conexao = sqlite3.connect("ficha_tecnica.db")
            cursor = conexao.cursor()
            cursor.execute("INSERT INTO medidas (nome_medida) VALUES (?)", (nova_medida,))
            conexao.commit()
            conexao.close()    

            # Atualiza a linha visualmente na tabela Tkinter
            atualizar_tabela_medidas()

            # Fecha o pop-up e avisa o usuário
            popup_adicionar_medida.destroy()
            messagebox.showinfo("Sucesso", "Medida adicionada com sucesso.")

    # Botão Salvar dentro do Pop-up
    botao_salvar = tk.Button(popup_adicionar_medida, text="Salvar", command=cadastrar_medida_banco)
    botao_salvar.pack(pady=15)

# editar    
def popup_editar_medida():
    # 1. Verifica se há uma linha selecionada
    selecao = tabela_medidas.selection()
    if not selecao:
        messagebox.showwarning("Aviso", "Por favor, selecione uma medida para editar!")
        return

    # 2. Captura a linha selecionada e seus dados
    item_id = selecao[0]
    valores = tabela_medidas.item(item_id, "values")

    # Supondo que a tabela tem: Coluna 0 (ID) e Coluna 1 (Nome)
    id_medida = valores[0]
    nome_atual = valores[1]

    # 3. Criação do pop-up editar ingrediente
    popup_editar_medida = tk.Toplevel()
    popup_editar_medida.title("Editar Ingrediente")
    popup_editar_medida.geometry("300x150")
    # Bloqueia a janela principal até fechar o pop-up
    popup_editar_medida.grab_set()

    # Elementos visuais do Pop-up
    label = tk.Label(popup_editar_medida, text="Nome da medida:")
    label.pack(pady=10)

    entry_editar_medida = tk.Entry(popup_editar_medida, width=30)
    entry_editar_medida.pack(pady=5)
    # Preenche o campo com o nome atual do ingrediente
    entry_editar_medida.insert(0, nome_atual)

    def atualizar_medida_banco():
        # 4. Função interna para salvar os dados
        novo_nome = entry_editar_medida.get().strip()

        if not novo_nome:
            messagebox.showwarning("Aviso", "O campo não pode ficar vazio!")
            return

        else:
            # Atualiza no Banco de Dados SQLite3
            conexao = sqlite3.connect("ficha_tecnica.db")
            cursor = conexao.cursor()
            cursor.execute("UPDATE medidas SET nome_medida = ? WHERE id = ?", (novo_nome, id_medida))
            conexao.commit()
            conexao.close()

            # Atualiza a linha visualmente na tabela Tkinter
            tabela_medidas.item(item_id, values=(id_medida, novo_nome))

            # Fecha o pop-up e avisa o usuário
            popup_editar_medida.destroy()
            messagebox.showinfo("Sucesso", "Medida atualizada com sucesso!")

    # Botão Salvar dentro do Pop-up
    botao_salvar = tk.Button(popup_editar_medida, text="Salvar", command=atualizar_medida_banco)
    botao_salvar.pack(pady=15)

###     FUNÇÕES DE FICHA        ################################################################

def adicionar_ingrediente_ficha():

    ingrediente = entry_ingrediente.get().strip()
    quantidade_comprada_str = entry_quantidade_comprada.get().strip()
    valor_comprado_str = entry_valor_comprado.get().strip()
    quantidade_usada_str = entry_quantidade_usada.get().strip()

    # 2. Validação: Impedir campos vazios
    if not (ingrediente and quantidade_comprada_str and valor_comprado_str and quantidade_usada_str):
        messagebox.showwarning("Aviso", "Todos os campos devem ser preenchidos!")
        return

    # 3. Validação manual de números (substitui o try/except para evitar erros de digitação)
    # Remove o ponto decimal temporariamente para checar se o resto são apenas dígitos
    checar_qtd_c = quantidade_comprada_str.replace(".", "", 1)
    checar_val_c = valor_comprado_str.replace(".", "", 1)
    checar_qtd_u = quantidade_usada_str.replace(".", "", 1)

    if not (checar_qtd_c.isdigit() and checar_val_c.isdigit() and checar_qtd_u.isdigit()):
        messagebox.showerror(
            "Erro de Digitação",
            "Use apenas números e ponto (.) como separador decimal nos campos numéricos.",
        )
        return

    # 4. Conversão segura para Float
    quantidade_comprada = float(quantidade_comprada_str)
    valor_comprado = float(valor_comprado_str)
    quantidade_usada = float(quantidade_usada_str)

    # Evitar divisão por zero
    if quantidade_comprada == 0:
        messagebox.showerror("Erro", "A quantidade comprada não pode ser zero.")
        return

    # 5. Cálculo do valor usado
    valor_usado = (valor_comprado / quantidade_comprada) * quantidade_usada

    # 6. Salvar no Banco de Dados
    conexao = sqlite3.connect("ficha_tecnica.db")
    cursor = conexao.cursor()
    cursor.execute(
        """
        INSERT INTO relacao_fichas_ingredientes (ingrediente, quantidade_comprada, valor_comprado, quantidade_usada, medida, valor_gasto)
        VALUES (?, ?, ?, ?, ?)
    """,
        (ingrediente, quantidade_comprada, valor_comprado, quantidade_usada, valor_usado),
    )
    conexao.commit()
    conexao.close()

    # 7. Mostrar popup de sucesso com o resultado
    messagebox.showinfo(
        "Sucesso",
        f"Dados salvos com sucesso!\n\n"
        f"Ingrediente: {ingrediente}\n"
        f"Valor Usado Calculado: R$ {valor_usado:.2f}",
    )

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
    
        # resultados = buscar_ingredientes_por_nome(texto)
    
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
    entry_ingrediente.delete(0, tk.END)
    entry_ingrediente.insert(0, escolha)

def navegar_lista(event):
  # Permite descer para a lista usando a seta do teclado
  if event.keysym == "Down" and lista_sugestoes.size() > 0:
    lista_sugestoes.focus_set()
    lista_sugestoes.selection_set(0)

def popup_incluir_ingrediente_ficha():

    global entrada_ingrediente, lista_sugestoes, entry_ingrediente, entry_quantidade_comprada, entry_valor_comprado, entry_quantidade_usada, entry

    popup_incluir_ingrediente_ficha = tk.Toplevel()
    popup_incluir_ingrediente_ficha.title("Ingrediente na Ficha")
    popup_incluir_ingrediente_ficha.geometry("300x700")
    # Bloqueia a janela principal até fechar o pop-up
    popup_incluir_ingrediente_ficha.grab_set()

    # Rótulo
    rotulo = tk.Label(janela, text="Selecione o ingrediente:")
    rotulo.pack(pady=10)

    # Campo de entrada de texto
    entry_ingrediente = tk.Entry(popup_incluir_ingrediente_ficha, width=30)
    entry_ingrediente.pack(pady=5)

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
    entry_ingrediente.bind("<KeyRelease>", ao_digitar)
    entry_ingrediente.bind("<Down>", navegar_lista)

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

# Botão Salvar dentro do Pop-up
    botao_salvar = tk.Button(popup_incluir_ingrediente_ficha, text="Salvar", command=adicionar_ingrediente_ficha)
    botao_salvar.pack(pady=15)

# limpa a tabela ingredientess
def limpar_tabela_fichas():
    
    for item in tabela_fichas.get_children():
        tabela_fichas.delete(item)

# atualiza a tabela ingredientes
def atualizar_tabela_fichas():

    limpar_tabela_fichas()

    # Conecta ao banco de dados SQLite
    conexao = sqlite3.connect("ficha_tecnica.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome_preparo, nome_profissional FROM fichas")
    linhas = cursor.fetchall()

    # Insere os dados na Treeview
    for linha in linhas:
        tabela_fichas.insert("", "end", values=linha)

    conexao.close()

def cadastrar_ficha():
# Remove espaços em branco do início e fim para evitar burlar com a barra de espaço
    preparo = entry_nome_preparo.get().strip()
    profissional = entry_nome_profissional.get().strip()
    porcoes= entry_porcoes.get().strip()
    modo_preparo = area_texto_modo_preparo.get("1.0", tk.END).strip()

    # Validação: verifica se algum dos campos está vazio
    if not preparo or not profissional:
        # Exibe o alerta de erro caso falte preenchimento
        messagebox.showwarning(
            "Aviso", "Todos os campos precisam ser preenchidos!"
        )
        return

    # Inserção no banco caso os campos estejam preenchidos
    conexao = sqlite3.connect("ficha_tecnica.db")
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO fichas (nome_preparo, nome_profissional, porcoes, modo_preparo) VALUES (?, ?, ?, ?)", (preparo, profissional, porcoes, modo_preparo),)
    conexao.commit()
    conexao.close()
    # Alerta de sucesso
    messagebox.showinfo("Sucesso", "Dados cadastrados com sucesso!")

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
    frame_popup_cabecalho.pack(fill="both")    

    # # ---------- COLUNA DA ESQUERDA (imagem) ----------
    frame_esquerda = tk.Frame(frame_popup_cabecalho, width=200, height=100, borderwidth=1, relief="solid")
    frame_esquerda.pack(side="left", padx=10, pady=10, anchor="n", fill="both")
    frame_esquerda.pack_propagate(False)  # mantém tamanho fixo mesmo sem imagem

    # Botão que funciona como widget para inserir a imagem
    botao_imagem = tk.Button(frame_esquerda, text="Escolher Imagem", command=selecionar_imagem)
    botao_imagem.pack(pady=10, expand=True)

    lbl_status = tk.Label(frame_esquerda, text="Nenhuma imagem selecionada", fg="gray")
    lbl_status.pack(pady=5)

    label_nome_preparo = tk.Label(frame_popup_cabecalho, text="Nome do preparo")
    label_nome_preparo.pack()

    entry_nome_preparo = tk.Entry(frame_popup_cabecalho)
    entry_nome_preparo.pack(pady=20)

    label_nome_responsavel = tk.Label(frame_popup_cabecalho, text="Profissional responsável")
    label_nome_responsavel.pack()

    entry_nome_responsavel = tk.Entry(frame_popup_cabecalho)
    entry_nome_responsavel.pack(pady=20)

    # ---------- COLUNA DA DIREITA (campos de digitação) ----------
    # frame_direita = tk.Frame(frame_popup_cabecalho, borderwidth=1, relief="solid")
    # frame_direita.pack(fill="both", expand=True, padx=10, pady=10)    


    # def criar_campo(frame_pai, texto_label, largura_entry=20):
    #     frame_campo = tk.Frame(frame_pai, borderwidth="1", relief="solid")
    #     frame_campo.pack(padx=10)
    #     label = tk.Label(frame_campo, text=texto_label)
    #     label.pack(anchor="w")
    #     entry = tk.Entry(frame_campo, width=largura_entry)
    #     entry.pack(anchor="w", pady=5)

    #     return entry

    # criar_campo(frame_popup_cabecalho, "Nome do preparo", )
    # criar_campo(frame_popup_cabecalho, "Profissional responsável", )

    frame_popup_menu_tabela = tk.Frame(frame_popup, borderwidth=1, relief="raised")
    frame_popup_menu_tabela.pack(fill="both", anchor="center", padx=10, pady=10)

    # botões da tela ingredientes
    botao_retirar_ingrediente_ficha = tk.Button(frame_popup_menu_tabela, text="Adicionar")
    botao_retirar_ingrediente_ficha.pack(side= "right", padx=10, anchor="center", expand=True)

    botao_editar_ingrediente_ficha = tk.Button(frame_popup_menu_tabela, text="Editar")
    botao_editar_ingrediente_ficha.pack(side= "right", padx=10, anchor="center", expand=True)

    botao_incluir_ingrediente_ficha = tk.Button(frame_popup_menu_tabela, text="Deletar", command=popup_incluir_ingrediente_ficha)
    botao_incluir_ingrediente_ficha.pack(side= "right", padx=10, anchor="center", expand=True)

    frame_popup_tabela = tk.Frame(frame_popup, borderwidth=1, relief="raised")
    frame_popup_tabela.pack(fill="both", expand=True) 

###     TELAS      #################################################################################

# inicial
def tela_inicio():

    global lbl_status, tabela_fichas

    limpar_janela()

    # frame da tela ficha
    frame_ficha = tk.Frame(janela, borderwidth=1, relief="raised", bg="#FDC180")
    frame_ficha.pack(fill="both", expand=True)

    # título da tela de início
    label_titulo = tk.Label(frame_ficha, text=" 🍴 Ficha Técnica de Preparo 👨‍🍳", font=("Arial", 24), bg="#FDC180")
    label_titulo.pack(pady=10)

    #frame do menu
    frame_menu_ficha = tk.Frame(frame_ficha, borderwidth=1, relief="raised")
    frame_menu_ficha.pack(pady=10)

    # campo de busca de ingrdiente   
    entry_busca_ficha = tk.Entry(frame_menu_ficha)
    entry_busca_ficha.pack(side="left", padx=10, pady=5)    

    # botões da tela ficha
    botao_medidas = tk.Button(frame_menu_ficha, text="Medidas", command=tela_medidas)
    botao_medidas.pack(side="right", padx=10, pady=5)
    
    botao_ingredientes = tk.Button(frame_menu_ficha, text="Ingredientes", command=tela_ingredientes)
    botao_ingredientes.pack(side="right", padx=10, pady=5)

    botao_deletar_ficha = tk.Button(frame_menu_ficha, text="Deletar", command=deletar_ingrediente, bg="#da2222")
    botao_deletar_ficha.pack(side="right", padx=10, pady=5)
    
    botao_editar_ficha = tk.Button(frame_menu_ficha, text="Editar", command=popup_editar_ingrediente, bg="#dac722")
    botao_editar_ficha.pack(side="right", padx=10, pady=5)

    botao_cadastrar_ficha = tk.Button(frame_menu_ficha, text="Adicionar", command=tela_nova_ficha , bg="#22da50")
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


# tabela de fichas
    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure("Treeview.Heading", font=("Arial", 14, "bold"), background="#004c94", foreground="#f7941d")
    estilo.configure("Treeview", rowheight=28, font=("Arial", 10))

    # cria tabela
    tabela_fichas = ttk.Treeview(frame_ficha,columns=("id", "nome_preparo", "nome_profissional") , show="headings", )

    # largura das colunas
    tabela_fichas.column("id", width=5, anchor="w")   # Coluna 1 com 100 pixels
    tabela_fichas.column("nome_preparo", width=250, anchor="w")    # Coluna 2 com 250 pixels
    tabela_fichas.column("nome_profissional", width=250, anchor="w")    # Coluna 2 com 250 pixels

    # títulos das colunas
    tabela_fichas.heading("id", text="ID")
    tabela_fichas.heading("nome_preparo", text="Preparo")
    tabela_fichas.heading("nome_profissional", text="Responsável")

    # exibe a tabela
    tabela_fichas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    atualizar_tabela_fichas()

# nova ficha
def tela_nova_ficha():

    global entry_nome_preparo, entry_nome_profissional, entry_porcoes, area_texto_modo_preparo

    limpar_janela()

    # frame do popup adicionar ficha
    frame_nova_ficha = tk.Frame(janela, borderwidth=1, relief="raised", bg="#FDC180")
    frame_nova_ficha.pack(fill="both", expand=True)

    label_titulo = tk.Label(frame_nova_ficha, text="Nova Ficha de Preparo", font=("Arial", 24), bg="#FDC180")
    label_titulo.pack(pady=10)

    frame_popup_cabecalho = tk.Frame(frame_nova_ficha, borderwidth=1, relief="raised")
    frame_popup_cabecalho.pack(fill="both")    

    # ---------- COLUNA DA ESQUERDA (imagem) ----------
    frame_esquerda = tk.Frame(frame_popup_cabecalho, width=200, height=100, borderwidth=1, relief="solid")
    frame_esquerda.pack(side="left", padx=10, pady=10, anchor="n", fill="both")
    frame_esquerda.pack_propagate(False)  # mantém tamanho fixo mesmo sem imagem

    # Botão que funciona como widget para inserir a imagem
    botao_imagem = tk.Button(frame_esquerda, text="Escolher Imagem", command=selecionar_imagem)
    botao_imagem.pack(pady=10, expand=True)

    lbl_status = tk.Label(frame_esquerda, text="Nenhuma imagem selecionada", fg="gray")
    lbl_status.pack(pady=5)

    label_nome_preparo = tk.Label(frame_popup_cabecalho, text="Nome do preparo")
    label_nome_preparo.pack()

    entry_nome_preparo = tk.Entry(frame_popup_cabecalho)
    entry_nome_preparo.pack(pady=20)

    label_nome_responsavel = tk.Label(frame_popup_cabecalho, text="Profissional responsável")
    label_nome_responsavel.pack()

    entry_nome_profissional = tk.Entry(frame_popup_cabecalho)
    entry_nome_profissional.pack(pady=20)

    label_porcoes = tk.Label(frame_popup_cabecalho, text="Número de porções")
    label_porcoes.pack()

    entry_porcoes = tk.Entry(frame_popup_cabecalho)
    entry_porcoes.pack(pady=20)

    # Cria um Frame para agrupar o Text e a Scrollbar juntos
    frame_modo_preparo = tk.Frame(frame_popup_cabecalho)
    frame_modo_preparo.pack(pady=10, padx=10)

    # 1. Cria a barra de rolagem (Scrollbar) dentro do frame
    scrollbar = tk.Scrollbar(frame_modo_preparo)
    # Posiciona a barra à direita e faz ela preencher toda a altura (Y)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    label_modo_preparo = tk.Label(frame_modo_preparo, text="Modo de preparo")
    label_modo_preparo.pack()

    # 2. Cria o campo de texto (Text) vinculado à scrollbar
    # O yscrollcommand avisa a barra de rolagem quando o texto se move
    area_texto_modo_preparo = tk.Text(frame_modo_preparo, width=40, height=8, wrap="word", yscrollcommand=scrollbar.set)
    area_texto_modo_preparo.pack(side=tk.LEFT)

    # 3. Configura a barra de rolagem para controlar a visão vertical (yview) do texto
    scrollbar.config(command=area_texto_modo_preparo.yview)

# botões do menu nova ficha

    #frame do menu
    frame_menu = tk.Frame(frame_nova_ficha, borderwidth=1, relief="raised")
    frame_menu.pack(pady=10)

    botao_retirar_ingrediente_ficha = tk.Button(frame_menu, text="Excluir")
    botao_retirar_ingrediente_ficha.pack(side= "right", padx=10, pady=5)

    botao_editar_ingrediente_ficha = tk.Button(frame_menu, text="Editar")
    botao_editar_ingrediente_ficha.pack(side= "right", padx=10, pady=5)

    botao_adicionar_ingrediente_ficha = tk.Button(frame_menu, text="Adicionar", command=popup_incluir_ingrediente_ficha)
    botao_adicionar_ingrediente_ficha.pack(side= "right", padx=10, pady=5)

# botão salvar
    botao_salvar = tk.Button(frame_nova_ficha, text="Salvar", command=cadastrar_ficha)
    botao_salvar.pack(side= "right", padx=10, pady=5)

# ingredientes
def tela_ingredientes():

    global entry_busca_ingrediente, tabela_ingredientes

    limpar_janela()

    # frame da tela ingredientes
    frame_ingredientes = tk.Frame(janela, borderwidth=1, relief="raised", bg="#FDC180")
    frame_ingredientes.pack(fill="both", expand=True)

    # título da tela ingredientes
    label_titulo = tk.Label(frame_ingredientes, text="Ingredientes", font=("Arial", 24), bg="#FDC180")
    label_titulo.pack(pady=10)

    frame_menu_ingredientes = tk.Frame(frame_ingredientes, borderwidth=1, relief="sunken" , bg="#80ACFD")
    frame_menu_ingredientes.pack(pady=10)

    # campo de busca de ingrdiente   
    entry_busca_ingrediente = tk.Entry(frame_menu_ingredientes)
    entry_busca_ingrediente.pack(side="left", padx=10, pady=5)

    # botões da tela ingredientes
    botao_ficha = tk.Button(frame_menu_ingredientes, text="Ficha Técnica", command=tela_inicio)
    botao_ficha.pack(side="right", padx=10, pady=5)
    
    botao_deletar_ingrediente = tk.Button(frame_menu_ingredientes, text="Deletar", command=deletar_ingrediente, bg="#da2222")
    botao_deletar_ingrediente.pack(side="right", padx=10, pady=5)

    botao_editar_ingrediente = tk.Button(frame_menu_ingredientes, text="Editar", command=popup_editar_ingrediente, bg="#dac722")
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

# medidas    
def tela_medidas():

    global entry_busca_medida, tabela_medidas

    limpar_janela()

    # frame da tela ficha
    frame_medidas = tk.Frame(janela, borderwidth=1, relief="raised", bg="#FDC180")
    frame_medidas.pack(fill="both", expand=True)

    # título da tela ingredientes
    label_titulo = tk.Label(frame_medidas, text="Medidas", font=("Arial", 24), bg="#FDC180")
    label_titulo.pack(pady=10)

    frame_menu_medidas = tk.Frame(frame_medidas, borderwidth=1, relief="raised")
    frame_menu_medidas.pack(pady=10)

    # campo de busca de ingrdiente   
    entry_busca_medida = tk.Entry(frame_menu_medidas)
    entry_busca_medida.pack(side="left", padx=10, pady=5)

    # botões da tela ingredientes
    botao_ficha = tk.Button(frame_menu_medidas, text="Ficha Técnica", command=tela_inicio)
    botao_ficha.pack(side="right", padx=10, pady=5)
    
    botao_deletar_medida = tk.Button(frame_menu_medidas, text="Deletar", command=deletar_medida, bg="#da2222")
    botao_deletar_medida.pack(side="right", padx=10, pady=5)

    botao_editar_medida = tk.Button(frame_menu_medidas, text="Editar", command=popup_editar_medida, bg="#dac722")
    botao_editar_medida.pack(side="right", padx=10, pady=5)

    botao_atualizar_tabela_medidas = tk.Button(frame_menu_medidas, text="Mostrar Lista Completa", command=atualizar_tabela_medidas)
    botao_atualizar_tabela_medidas.pack(side="right", padx=10, pady=5) 

    botao_cadastrar_medida = tk.Button(frame_menu_medidas, text="Adicionar", command=popup_adicionar_medida , bg="#22da50")
    botao_cadastrar_medida.pack(side="right", padx=10, pady=5)

    botao_pesquisar_medida = tk.Button(frame_menu_medidas, text="Pesquisar", command=pesquisar_medida)
    botao_pesquisar_medida.pack(side="right", padx=10, pady=5)

    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure("Treeview.Heading", font=("Arial", 14, "bold"), background="#004c94", foreground="#f7941d")
    estilo.configure("Treeview", rowheight=28, font=("Arial", 10))

    # cria tabela
    tabela_medidas = ttk.Treeview(frame_medidas,columns=("id", "nome_medida") , show="headings", )

    # largura das colunas
    tabela_medidas.column("id", width=5, anchor="w")   # Coluna 1 com 100 pixels
    tabela_medidas.column("nome_medida", width=250, anchor="w")    # Coluna 2 com 250 pixels

    # títulos das colunas
    tabela_medidas.heading("id", text="ID")
    tabela_medidas.heading("nome_medida", text="Medidas")

    # exibe a tabela
    tabela_medidas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    conexao = sqlite3.connect("ficha_tecnica.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM medidas")
    resultado = cursor.fetchall()

    for linha in resultado:
        tabela_medidas.insert('', tk.END, values=linha)

    # Seleciona as colunas id e ingrediente da tabela
    cursor.execute("SELECT id, nome_medida FROM medidas")
    conexao.close()

###   INÍCIO   ######################################################################################

# conecta db
conectar_banco_dados()

# cria a janela principal
janela = tk.Tk()
janela.title("Maedu")
janela.geometry("700x700")
janela.resizable(False, False)

# exibe tela ficha
tela_inicio()

janela.mainloop()