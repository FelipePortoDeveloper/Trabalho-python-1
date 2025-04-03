import difflib
import json
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# Classe que representa um livro na biblioteca
class Livro:
    def __init__(self, titulo, autor, publicacao, isbn, categoria, id_exemplar):
        # Inicializa os atributos do livro
        self.titulo = titulo  # Título do livro
        self.autor = autor  # Autor do livro
        self.publicacao = publicacao  # Data de publicação do livro
        self.isbn = isbn  # ISBN do livro
        self.categoria = categoria  # Categoria do livro
        self.id_exemplar = id_exemplar  # ID único do exemplar do livro
        self.emprestado = False  # Indica se o livro está emprestado
        self.emprestimos_count = 0  # Contador de quantas vezes o livro foi emprestado

# Classe que representa um usuário da biblioteca
class Usuario:
    def __init__(self, nome, email, tipo):
        # Inicializa os atributos do usuário
        self.nome = nome  # Nome do usuário
        self.email = email  # Email do usuário
        self.tipo = tipo  # Tipo de usuário (ex: aluno, professor)

# Classe que gerencia a biblioteca, incluindo livros, usuários e empréstimos
class Biblioteca:
    def __init__(self, livros_arquivo="livros.txt", usuarios_arquivo="usuarios.txt", emprestimos_arquivo="emprestimos.txt"):
        # Inicializa os arquivos que armazenam os dados da biblioteca
        self.livros_arquivo = livros_arquivo  # Caminho do arquivo de livros
        self.usuarios_arquivo = usuarios_arquivo  # Caminho do arquivo de usuários
        self.emprestimos_arquivo = emprestimos_arquivo  # Caminho do arquivo de empréstimos

    # Método para carregar dados de um arquivo JSON
    def carregar_dados(self, arquivo):
        try:
            with open(arquivo, "r") as f:
                return json.load(f)  # Retorna os dados carregados do arquivo
        except (FileNotFoundError, json.JSONDecodeError):
            return []  # Retorna uma lista vazia se o arquivo não for encontrado ou estiver vazio

    # Método para salvar dados em um arquivo JSON
    def salvar_dados(self, arquivo, dados):
        with open(arquivo, "w") as f:
            json.dump(dados, f, indent=4)  # Salva os dados no arquivo com formatação

    # Método para obter o próximo ID disponível para um livro
    def get_next_id(self):
        livros = self.carregar_dados(self.livros_arquivo)  # Carrega a lista de livros
        if livros:
            max_id = max(livro["id_exemplar"] for livro in livros)  # Encontra o maior ID existente
            return max_id + 1  # Retorna o próximo ID
        return 1  # Retorna 1 se não houver livros cadastrados

    # Método para listar todos os livros cadastrados
    def listar_todos_livros(self):
        return self.carregar_dados(self.livros_arquivo)  # Retorna a lista de livros

    # Método para cadastrar um novo livro
    def cadastra_livro(self, livro):
        livros = self.carregar_dados(self.livros_arquivo)  # Carrega a lista de livros
        livros.append(livro.__dict__)  # Adiciona o novo livro à lista
        self.salvar_dados(self.livros_arquivo, livros)  # Salva a lista atualizada
        messagebox.showinfo("Sucesso", "Livro cadastrado com sucesso!")  # Exibe mensagem de sucesso

    # Método para cadastrar um novo usuário
    def cadastra_usuario(self, usuario):
        usuarios = self.carregar_dados(self.usuarios_arquivo)  # Carrega a lista de usuários
        # Verifica se o email já está cadastrado
        if any(u["email"] == usuario.email for u in usuarios):
            messagebox.showwarning("Erro", "Usuário já cadastrado com este e-mail.")  # Exibe aviso se o email já existir
            return
        usuarios.append(usuario.__dict__)  # Adiciona o novo usuário à lista
        self.salvar_dados(self.usuarios_arquivo, usuarios)  # Salva a lista atualizada
        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")  # Exibe mensagem de sucesso

    # Método para registrar um empréstimo de livro
    def cadastra_emprestimo(self, id_exemplar, usuario_email):
        livros = self.carregar_dados(self.livros_arquivo)  # Carrega a lista de livros
        usuarios = self.carregar_dados(self.usuarios_arquivo)  # Carrega a lista de usuários
        emprestimos = self.carregar_dados(self.emprestimos_arquivo)  # Carrega a lista de empréstimos

        # Busca o livro que será emprestado
        livro = next((l for l in livros if l["id_exemplar"] == id_exemplar and not l["emprestado"]), None)
        # Busca o usuário que está solicitando o empréstimo
        usuario = next((u for u in usuarios if u["email"] == usuario_email), None)

        # Verifica se o livro não foi encontrado ou já está emprestado
        if not livro:
            messagebox.showerror("Erro", "Livro não encontrado ou já emprestado!")  # Exibe mensagem de erro
            return
        # Verifica se o usuário não foi encontrado
        if not usuario:
            messagebox.showerror("Erro", "Usuário não encontrado!")  # Exibe mensagem de erro
            return

        livro["emprestado"] = True  # Marca o livro como emprestado
        livro["emprestimos_count"] = livro.get("emprestimos_count", 0) + 1  # Incrementa o contador de empréstimos
        self.salvar_dados(self.livros_arquivo, livros)  # Salva a lista de livros atualizada

        # Cria um novo registro de empréstimo
        novo_emprestimo = {
            "id_exemplar": id_exemplar,
            "usuario_email": usuario_email,
            "data_emprestimo": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Data e hora do empréstimo
        }
        emprestimos.append(novo_emprestimo)  # Adiciona o novo empréstimo à lista
        self.salvar_dados(self.emprestimos_arquivo, emprestimos)  # Salva a lista de empréstimos atualizada
        messagebox.showinfo("Sucesso", "Empréstimo registrado com sucesso!")  # Exibe mensagem de sucesso

    # Método para listar todos os empréstimos ativos
    def lista_emprestimos(self):
        emprestimos = self.carregar_dados(self.emprestimos_arquivo)  # Carrega a lista de empréstimos
        if not emprestimos:
            messagebox.showinfo("Info", "Nenhum empréstimo ativo.")  # Exibe mensagem se não houver empréstimos
            return
        # Cria uma mensagem com os detalhes dos empréstimos
        msg = "\n".join([f"Livro ID: {emp['id_exemplar']}, Usuário: {emp['usuario_email']}, Data: {emp['data_emprestimo']}" for emp in emprestimos])
        messagebox.showinfo("Empréstimos Ativos", msg)  # Exibe a lista de empréstimos ativos

    # Método para devolver um livro
    def devolve_livro(self, id_exemplar):
        livros = self.carregar_dados(self.livros_arquivo)  # Carrega a lista de livros
        emprestimos = self.carregar_dados(self.emprestimos_arquivo)  # Carrega a lista de empréstimos

        # Busca o livro que será devolvido
        livro = next((l for l in livros if l["id_exemplar"] == id_exemplar), None)
        if livro:
            livro["emprestado"] = False  # Marca o livro como não emprestado
        
        self.salvar_dados(self.livros_arquivo, livros)  # Salva a lista de livros atualizada

        # Remove o registro do empréstimo da lista
        emprestimos = [emp for emp in emprestimos if emp["id_exemplar"] != id_exemplar]
        self.salvar_dados(self.emprestimos_arquivo, emprestimos)  # Salva a lista de empréstimos atualizada

        messagebox.showinfo("Sucesso", "Livro devolvido com sucesso!")  # Exibe mensagem de sucesso

    # Método para buscar livros com base em um critério
    def busca_livros(self, criterio, valor):
      
        livros = self.carregar_dados(self.livros_arquivo)  # Carrega a lista de livros
        # Filtra os livros que atendem ao critério de busca

        livros = self.carregar_dados(self.livros_arquivo)
        resultados = []

        if criterio.lower() == "título":
            criterio = "titulo"

            for livro in livros:
                similaridade = difflib.SequenceMatcher(None, valor.lower(), livro[criterio].lower()).ratio()

                if similaridade >= 0.3:
                    resultados.append(livro)
        else:
            resultados = [livro for livro in livros if valor.lower() in livro[criterio].lower()]

        if resultados:
            # Cria uma mensagem com os resultados da busca
            msg = "\n".join([f"{livro['titulo']} - {livro['autor']} - {livro['categoria']}" for livro in resultados])
            messagebox.showinfo("Resultado da Busca", msg)  # Exibe os resultados da busca
        else:
            messagebox.showinfo("Resultado da Busca", "Nenhum livro encontrado.")  # Exibe mensagem se não houver resultados

    # Método para contar livros por categoria
    def livros_por_categoria(self):
        livros = self.carregar_dados(self.livros_arquivo)  # Carrega a lista de livros
        categoria_count = {}  # Dicionário para contar livros por categoria
        for livro in livros:
            categoria = livro["categoria"]  # Obtém a categoria do livro
            categoria_count[categoria] = categoria_count.get(categoria, 0) + 1  # Incrementa o contador da categoria
        if categoria_count:
            # Cria uma mensagem com a contagem de livros por categoria
            msg = "\n".join([f"{cat}: {count}" for cat, count in categoria_count.items()])
            messagebox.showinfo("Livros por Categoria", msg)  # Exibe a contagem de livros por categoria
        else:
            messagebox.showinfo("Livros por Categoria", "Nenhum livro cadastrado.")  # Exibe mensagem se não houver livros

    # Método para contar empréstimos por tipo de usuário
    def emprestimos_por_usuario(self):
        emprestimos = self.carregar_dados(self.emprestimos_arquivo)  # Carrega a lista de empréstimos
        usuarios = self.carregar_dados(self.usuarios_arquivo)  # Carrega a lista de usuários
        type_count = {}  # Dicionário para contar empréstimos por tipo de usuário
        for emp in emprestimos:
            email = emp["usuario_email"]  # Obtém o email do usuário do empréstimo
            user = next((u for u in usuarios if u["email"] == email), None)  # Busca o usuário correspondente
            if user:
                tipo = user["tipo"]  # Obtém o tipo do usuário
                type_count[tipo] = type_count.get(tipo, 0) + 1  # Incrementa o contador do tipo de usuário
        if type_count:
            # Cria uma mensagem com a contagem de empréstimos por tipo de usuário
            msg = "\n".join([f"{tipo}: {count}" for tipo, count in type_count.items()])
            messagebox.showinfo("Empréstimos por Tipo de Usuário", msg)  # Exibe a contagem de empréstimos por tipo de usuário
        else:
            messagebox.showinfo("Empréstimos por Tipo de Usuário", "Nenhum empréstimo registrado.")  # Exibe mensagem se não houver empréstimos

    # Método para listar os livros mais emprestados
    def livros_mais_emprestados(self):
        livros = self.carregar_dados(self.livros_arquivo)  # Carrega a lista de livros
        if not livros:
            messagebox.showinfo("Livros mais Emprestados", "Nenhum livro cadastrado.")  # Exibe mensagem se não houver livros
            return

        # Garante que todos os livros tenham um contador de empréstimos
        for livro in livros:
            if "emprestimos_count" not in livro:
                livro["emprestimos_count"] = 0
        # Ordena os livros pelo número de empréstimos em ordem decrescente
        sorted_books = sorted(livros, key=lambda l: l["emprestimos_count"], reverse=True)
        top_books = sorted_books[:3]  # Seleciona os 3 livros mais emprestados
        # Cria uma mensagem com os livros mais emprestados
        msg = "\n".join([f"{livro['titulo']} - {livro['emprestimos_count']} empréstimos" for livro in top_books])
        messagebox.showinfo("Livros Mais Emprestados", msg)  # Exibe os livros mais emprestados

# Classe que representa a interface gráfica da biblioteca
class BibliotecaApp:
    def __init__(self, root):
        self.biblioteca = Biblioteca()  # Cria uma instância da classe Biblioteca
        self.root = root  # Armazena a referência da janela principal
        self.root.title("Sistema de Biblioteca")  # Define o título da janela
        self.root.geometry("800x650")  # Define o tamanho da janela
        self.style = ttk.Style()  # Cria um estilo para a interface
        self.style.theme_use("clam")  # Define o tema da interface
        
        # Cria um notebook para organizar as abas da interface
        notebook = ttk.Notebook(root)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Cria a aba para livros
        self.frame_livros = ttk.Frame(notebook)
        notebook.add(self.frame_livros, text="Livros")
        self.create_livros_tab()  # Chama o método para criar a aba de livros
        
        # Cria a aba para usuários
        self.frame_usuarios = ttk.Frame(notebook)
        notebook.add(self.frame_usuarios, text="Usuários")
        self.create_usuarios_tab()  # Chama o método para criar a aba de usuários
        
        # Cria a aba para empréstimos
        self.frame_emprestimos = ttk.Frame(notebook)
        notebook.add(self.frame_emprestimos, text="Empréstimos")
        self.create_emprestimos_tab()  # Chama o método para criar a aba de empréstimos
        
        # Cria a aba para relatórios
        self.frame_relatorios = ttk.Frame(notebook)
        notebook.add(self.frame_relatorios, text="Relatórios")
        self.create_relatorios_tab()  # Chama o método para criar a aba de relatórios

    # Método para criar a aba de livros
    def create_livros_tab(self):
        frame = self.frame_livros
        title_lbl = ttk.Label(frame, text="Cadastro e Listagem de Livros", font=("Helvetica", 18, "bold"))
        title_lbl.pack(pady=10)  # Adiciona o título da aba

        # Cria um frame para cadastro de livros
        cadastro_frame = ttk.LabelFrame(frame, text="Cadastrar Livro")
        cadastro_frame.pack(fill="x", padx=20, pady=10)
        campos = ["Título", "Autor", "Publicação", "ISBN", "Categoria"]  # Campos para cadastro
        self.livro_vars = {}  # Dicionário para armazenar as variáveis dos campos
        for campo in campos:
            frame_campo = ttk.Frame(cadastro_frame)
            frame_campo.pack(fill="x", padx=10, pady=5)
            lbl_campo = ttk.Label(frame_campo, text=campo + ":", width=15, anchor="w")
            lbl_campo.pack(side="left")  # Adiciona o rótulo do campo
            var = tk.StringVar()  # Cria uma variável para armazenar o valor do campo
            entry = ttk.Entry(frame_campo, textvariable=var)  # Cria um campo de entrada
            entry.pack(side="left", expand=True, fill="x")  # Adiciona o campo de entrada
            self.livro_vars[campo.lower()] = var  # Armazena a variável no dicionário
        btn_cadastrar = ttk.Button(cadastro_frame, text="Cadastrar Livro", command=self.cadastrar_livro)
        btn_cadastrar.pack(pady=10)  # Adiciona o botão de cadastro

        # Cria um frame para busca de livros
        busca_frame = ttk.LabelFrame(frame, text="Buscar Livro")
        busca_frame.pack(fill="x", padx=20, pady=10)
        criterio_lbl = ttk.Label(busca_frame, text="Critério:", width=15, anchor="w")
        criterio_lbl.grid(row=0, column=0, padx=5, pady=5)  # Adiciona o rótulo do critério
        self.criterio_var = tk.StringVar()  # Variável para armazenar o critério de busca
        self.criterio_combobox = ttk.Combobox(busca_frame, textvariable=self.criterio_var, state="readonly", values=["título", "autor", "categoria"])
        self.criterio_combobox.grid(row=0, column=1, padx=5, pady=5)  # Adiciona a combobox para selecionar o critério
        self.criterio_combobox.current(0)  # Define o critério padrão
        valor_lbl = ttk.Label(busca_frame, text="Valor:", width=15, anchor="w")
        valor_lbl.grid(row=1, column=0, padx=5, pady=5)  # Adiciona o rótulo do valor
        self.valor_busca = tk.StringVar()  # Variável para armazenar o valor de busca
        entry_valor = ttk.Entry(busca_frame, textvariable=self.valor_busca)  # Cria um campo de entrada para o valor
        entry_valor.grid(row=1, column=1, padx=5, pady=5)  # Adiciona o campo de entrada
        btn_busca = ttk.Button(busca_frame, text="Buscar", command=self.buscar_livro)
        btn_busca.grid(row=2, column=0, columnspan=2, pady=10)  # Adiciona o botão de busca
        
        btn_listar = ttk.Button(frame, text="Listar Todos os Livros", command=self.listar_todos_livros)
        btn_listar.pack(pady=10)  # Adiciona o botão para listar todos os livros

    # Método para criar a aba de usuários
    def create_usuarios_tab(self):
        frame = self.frame_usuarios
        title_lbl = ttk.Label(frame, text="Cadastro de Usuários", font=("Helvetica", 18, "bold"))
        title_lbl.pack(pady=10)  # Adiciona o título da aba
        cadastro_frame = ttk.LabelFrame(frame, text="Cadastrar Usuário")
        cadastro_frame.pack(fill="x", padx=20, pady=10)  # Cria um frame para cadastro de usuários
        campos = ["Nome", "Email", "Tipo"]  # Campos para cadastro
        self.usuario_vars = {}  # Dicionário para armazenar as variáveis dos campos
        for campo in campos:
            frame_campo = ttk.Frame(cadastro_frame)
            frame_campo.pack(fill="x", padx=10, pady=5)
            lbl_campo = ttk.Label(frame_campo, text=campo + ":", width=15, anchor="w")
            lbl_campo.pack(side="left")  # Adiciona o rótulo do campo
            var = tk.StringVar()  # Cria uma variável para armazenar o valor do campo
            entry = ttk.Entry(frame_campo, textvariable=var)  # Cria um campo de entrada
            entry.pack(side="left", expand=True, fill="x")  # Adiciona o campo de entrada
            self.usuario_vars[campo.lower()] = var  # Armazena a variável no dicionário
        btn_cadastrar = ttk.Button(cadastro_frame, text="Cadastrar Usuário", command=self.cadastrar_usuario)
        btn_cadastrar.pack(pady=10)  # Adiciona o botão de cadastro

    # Método para criar a aba de empréstimos
    def create_emprestimos_tab(self):
        frame = self.frame_emprestimos
        title_lbl = ttk.Label(frame, text="Gerenciar Empréstimos", font=("Helvetica", 18, "bold"))
        title_lbl.pack(pady=10)  
        emprestimo_frame = ttk.LabelFrame(frame, text="Realizar Empréstimo")
        emprestimo_frame.pack(fill="x", padx=20, pady=10)  # Cria um frame para realizar empréstimos
        lbl_id = ttk.Label(emprestimo_frame, text="ID Exemplar:", width=15, anchor="w")
        lbl_id.grid(row=0, column=0, padx=5, pady=5)  # Adiciona o rótulo do ID do exemplar
        self.emprestimo_id = tk.StringVar()  # Variável para armazenar o ID do exemplar
        entry_id = ttk.Entry(emprestimo_frame, textvariable=self.emprestimo_id)  # Cria um campo de entrada para o ID
        entry_id.grid(row=0, column=1, padx=5, pady=5)  # Adiciona o campo de entrada
        lbl_email = ttk.Label(emprestimo_frame, text="Email Usuário:", width=15, anchor="w")
        lbl_email.grid(row=1, column=0, padx=5, pady=5)  # Adiciona o rótulo do email do usuário
        self.emprestimo_email = tk.StringVar()  # Variável para armazenar o email do usuário
        entry_email = ttk.Entry(emprestimo_frame, textvariable=self.emprestimo_email)  # Cria um campo de entrada para o email
        entry_email.grid(row=1, column=1, padx=5, pady=5)  # Adiciona o campo de entrada
        btn_emp = ttk.Button(emprestimo_frame, text="Realizar Empréstimo", command=self.realizar_emprestimo)
        btn_emp.grid(row=2, column=0, columnspan=2, pady=10)  # Adiciona o botão para realizar o empréstimo
        devolucao_frame = ttk.LabelFrame(frame, text="Devolver Livro")
        devolucao_frame.pack(fill="x", padx=20, pady=10)  # Cria um frame para devolver livros
        lbl_devolve = ttk.Label(devolucao_frame, text="ID Exemplar:", width=15, anchor="w")
        lbl_devolve.grid(row=0, column=0, padx=5, pady=5)  # Adiciona o rótulo do ID do exemplar
        self.devolve_id = tk.StringVar()  # Variável para armazenar o ID do exemplar a ser devolvido
        entry_devolve = ttk.Entry(devolucao_frame, textvariable=self.devolve_id)  # Cria um campo de entrada para o ID
        entry_devolve.grid(row=0, column=1, padx=5, pady=5)  # Adiciona o campo de entrada
        btn_dev = ttk.Button(devolucao_frame, text="Devolver Livro", command=self.devolver_livro)
        btn_dev.grid(row=1, column=0, columnspan=2, pady=10)  # Adiciona o botão para devolver o livro
        btn_lista = ttk.Button(frame, text="Listar Empréstimos", command=self.biblioteca.lista_emprestimos)
        btn_lista.pack(pady=10)  # Adiciona o botão para listar empréstimos

    # Método para criar a aba de relatórios
    def create_relatorios_tab(self):
        frame = self.frame_relatorios
        title_lbl = ttk.Label(frame, text="Relatórios", font=("Helvetica", 18, "bold"))
        title_lbl.pack(pady=10)  
        btn_categoria = ttk.Button(frame, text="Quantidade de Livros por Categoria", command=self.biblioteca.livros_por_categoria)
        btn_categoria.pack(pady=10, padx=20, fill="x")  
        btn_emprestimos = ttk.Button(frame, text="Empréstimos por Tipo de Usuário", command=self.biblioteca.emprestimos_por_usuario)
        btn_emprestimos.pack(pady=10, padx=20, fill="x")  
        btn_mais_emprestados = ttk.Button(frame, text="Livros Mais Emprestados", command=self.biblioteca.livros_mais_emprestados)
        btn_mais_emprestados.pack(pady=10, padx=20, fill="x")  

    # Método para cadastrar um livro
    def cadastrar_livro(self):
        campos_obrigatorios = ["título", "autor", "publicação", "isbn", "categoria"]  # Campos obrigatórios para cadastro
        for campo in campos_obrigatorios:
            valor = self.livro_vars[campo].get().strip()  # Obtém o valor do campo
            if not valor:
                messagebox.showerror("Erro", f"O campo {campo.capitalize()} é obrigatório.")  # Exibe mensagem de erro se o campo estiver vazio
                return

        # Obtém os valores dos campos
        titulo = self.livro_vars["título"].get().strip()
        autor = self.livro_vars["autor"].get().strip()
        publicacao = self.livro_vars["publicação"].get().strip()
        isbn = self.livro_vars["isbn"].get().strip()
        categoria = self.livro_vars["categoria"].get().strip()

        id_exemplar = self.biblioteca.get_next_id()  # Obtém o próximo ID disponível
        livro = Livro(titulo, autor, publicacao, isbn, categoria, id_exemplar)  # Cria uma instância do livro
        self.biblioteca.cadastra_livro(livro)  # Cadastra o livro na biblioteca
        for var in self.livro_vars.values():
            var.set("")  # Limpa os campos após o cadastro

    # Método para cadastrar um usuário
    def cadastrar_usuario(self):
        nome = self.usuario_vars["nome"].get().strip()  # Obtém o nome do usuário
        email = self.usuario_vars["email"].get().strip()  # Obtém o email do usuário
        tipo = self.usuario_vars["tipo"].get().strip()  # Obtém o tipo do usuário
        if not (nome and email and tipo):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios.")  # Exibe mensagem de erro se algum campo estiver vazio
            return
        usuario = Usuario(nome, email, tipo)  # Cria uma instância do usuário
        self.biblioteca.cadastra_usuario(usuario)  # Cadastra o usuário na biblioteca
        for var in self.usuario_vars.values():
            var.set("")  # Limpa os campos após o cadastro

    # Método para buscar um livro
    def buscar_livro(self):
        criterio = self.criterio_var.get()  # Obtém o critério de busca
        valor = self.valor_busca.get().strip()  # Obtém o valor de busca
        if not valor:
            messagebox.showerror("Erro", "Informe o valor para busca.")  # Exibe mensagem de erro se o valor estiver vazio
            return
        self.biblioteca.busca_livros(criterio, valor)  # Chama o método de busca de livros
        self.valor_busca.set("")  # Limpa o campo de busca após a operação

    # Método para listar todos os livros cadastrados
    def listar_todos_livros(self):
        livros = self.biblioteca.listar_todos_livros()  # Obtém a lista de todos os livros
        if not livros:
            messagebox.showinfo("Listar Livros", "Nenhum livro cadastrado.")  # Exibe mensagem se não houver livros
            return

        # Cria uma nova janela para exibir a lista de livros
        lista_win = tk.Toplevel(self.root)
        lista_win.title("Todos os Livros")  # Define o título da nova janela
        lista_win.geometry("750x400")  # Define o tamanho da nova janela
        # Cria uma árvore para exibir os detalhes dos livros
        tree = ttk.Treeview(lista_win, columns=("ID", "Título", "Autor", "Publicação", "ISBN", "Categoria", "Emprestado", "Empréstimos"), show="headings")
        # Define os cabeçalhos da árvore
        tree.heading("ID", text="ID Exemplar")
        tree.heading("Título", text="Título")
        tree.heading("Autor", text="Autor")
        tree.heading("Publicação", text="Publicação")
        tree.heading("ISBN", text="ISBN")
        tree.heading("Categoria", text="Categoria")
        tree.heading("Emprestado", text="Emprestado")
        tree.heading("Empréstimos", text="Empréstimos")
        tree.column("ID", width=80, anchor="center")
        tree.column("Título", width=150)
        tree.column("Autor", width=120)
        tree.column("Publicação", width=80, anchor="center")
        tree.column("ISBN", width=100, anchor="center")
        tree.column("Categoria", width=100, anchor="center")
        tree.column("Emprestado", width=80, anchor="center")
        tree.column("Empréstimos", width=100, anchor="center")
        tree.pack(expand=True, fill="both", padx=10, pady=10)  # Adiciona a árvore à janela

        # Insere os livros na árvore
        for livro in livros:
            emprestado = "Sim" if livro.get("emprestado", False) else "Não"  # Verifica se o livro está emprestado
            tree.insert("", "end", values=(livro["id_exemplar"], livro["titulo"], livro["autor"], livro["publicacao"], livro["isbn"], livro["categoria"], emprestado, livro.get("emprestimos_count", 0)))  # Adiciona os detalhes do livro

    # Método para realizar um empréstimo
    def realizar_emprestimo(self):
        try:
            id_exemplar = int(self.emprestimo_id.get())  # Obtém o ID do exemplar
        except Exception:
            messagebox.showerror("Erro", "ID Exemplar inválido.")  # Exibe mensagem de erro se o ID não for válido
            return
        email = self.emprestimo_email.get().strip()  # Obtém o email do usuário
        self.biblioteca.cadastra_emprestimo(id_exemplar, email)  # Registra o empréstimo
        self.emprestimo_id.set("")  # Limpa o campo do ID do exemplar
        self.emprestimo_email.set("")  # Limpa o campo do email do usuário

    # Método para devolver um livro
    def devolver_livro(self):
        try:
            id_exemplar = int(self.devolve_id.get())  # Obtém o ID do exemplar a ser devolvido
        except Exception:
            messagebox.showerror("Erro", "ID Exemplar inválido.")  # Exibe mensagem de erro se o ID não for válido
            return
        self.biblioteca.devolve_livro(id_exemplar)  # Registra a devolução do livro
        self.devolve_id.set("")  # Limpa o campo do ID do exemplar

# Inicializa a aplicação
if __name__ == "__main__":
    root = tk.Tk()  # Cria a janela principal
    app = BibliotecaApp(root)  # Cria uma instância da aplicação
    root.mainloop()  # Inicia o loop principal da interface gráfica
