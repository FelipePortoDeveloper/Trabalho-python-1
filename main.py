import json
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class Livro:
    def __init__(self, titulo, autor, publicacao, isbn, categoria, id_exemplar):
        self.titulo = titulo
        self.autor = autor
        self.publicacao = publicacao
        self.isbn = isbn
        self.categoria = categoria
        self.id_exemplar = id_exemplar
        self.emprestado = False
        self.emprestimos_count = 0 

class Usuario:
    def __init__(self, nome, email, tipo):
        self.nome = nome
        self.email = email
        self.tipo = tipo

class Biblioteca:
    def __init__(self, livros_arquivo="livros.txt", usuarios_arquivo="usuarios.txt", emprestimos_arquivo="emprestimos.txt"):
        self.livros_arquivo = livros_arquivo
        self.usuarios_arquivo = usuarios_arquivo
        self.emprestimos_arquivo = emprestimos_arquivo

    def carregar_dados(self, arquivo):
        try:
            with open(arquivo, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def salvar_dados(self, arquivo, dados):
        with open(arquivo, "w") as f:
            json.dump(dados, f, indent=4)

    def get_next_id(self):
        livros = self.carregar_dados(self.livros_arquivo)
        if livros:
            max_id = max(livro["id_exemplar"] for livro in livros)
            return max_id + 1
        return 1

    def listar_todos_livros(self):
        return self.carregar_dados(self.livros_arquivo)

    def cadastra_livro(self, livro):
        livros = self.carregar_dados(self.livros_arquivo)
        livros.append(livro.__dict__)
        self.salvar_dados(self.livros_arquivo, livros)
        messagebox.showinfo("Sucesso", "Livro cadastrado com sucesso!")

    def cadastra_usuario(self, usuario):
        usuarios = self.carregar_dados(self.usuarios_arquivo)
        if any(u["email"] == usuario.email for u in usuarios):
            messagebox.showwarning("Erro", "Usuário já cadastrado com este e-mail.")
            return
        usuarios.append(usuario.__dict__)
        self.salvar_dados(self.usuarios_arquivo, usuarios)
        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")

    def cadastra_emprestimo(self, id_exemplar, usuario_email):
        livros = self.carregar_dados(self.livros_arquivo)
        usuarios = self.carregar_dados(self.usuarios_arquivo)
        emprestimos = self.carregar_dados(self.emprestimos_arquivo)

        livro = next((l for l in livros if l["id_exemplar"] == id_exemplar and not l["emprestado"]), None)
        usuario = next((u for u in usuarios if u["email"] == usuario_email), None)

        if not livro:
            messagebox.showerror("Erro", "Livro não encontrado ou já emprestado!")
            return
        if not usuario:
            messagebox.showerror("Erro", "Usuário não encontrado!")
            return

        livro["emprestado"] = True
        livro["emprestimos_count"] = livro.get("emprestimos_count", 0) + 1
        self.salvar_dados(self.livros_arquivo, livros)

        novo_emprestimo = {
            "id_exemplar": id_exemplar,
            "usuario_email": usuario_email,
            "data_emprestimo": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        emprestimos.append(novo_emprestimo)
        self.salvar_dados(self.emprestimos_arquivo, emprestimos)
        messagebox.showinfo("Sucesso", "Empréstimo registrado com sucesso!")

    def lista_emprestimos(self):
        emprestimos = self.carregar_dados(self.emprestimos_arquivo)
        if not emprestimos:
            messagebox.showinfo("Info", "Nenhum empréstimo ativo.")
            return
        msg = "\n".join([f"Livro ID: {emp['id_exemplar']}, Usuário: {emp['usuario_email']}, Data: {emp['data_emprestimo']}" for emp in emprestimos])
        messagebox.showinfo("Empréstimos Ativos", msg)

    def devolve_livro(self, id_exemplar):
        livros = self.carregar_dados(self.livros_arquivo)
        emprestimos = self.carregar_dados(self.emprestimos_arquivo)

        livro = next((l for l in livros if l["id_exemplar"] == id_exemplar), None)
        if livro:
            livro["emprestado"] = False
        
        self.salvar_dados(self.livros_arquivo, livros)

        emprestimos = [emp for emp in emprestimos if emp["id_exemplar"] != id_exemplar]
        self.salvar_dados(self.emprestimos_arquivo, emprestimos)

        messagebox.showinfo("Sucesso", "Livro devolvido com sucesso!")

    def busca_livros(self, criterio, valor):
        livros = self.carregar_dados(self.livros_arquivo)
        resultados = [livro for livro in livros if valor.lower() in livro[criterio].lower()]
        if resultados:
            msg = "\n".join([f"{livro['titulo']} - {livro['autor']} - {livro['categoria']}" for livro in resultados])
            messagebox.showinfo("Resultado da Busca", msg)
        else:
            messagebox.showinfo("Resultado da Busca", "Nenhum livro encontrado.")

    def livros_por_categoria(self):
        livros = self.carregar_dados(self.livros_arquivo)
        categoria_count = {}
        for livro in livros:
            categoria = livro["categoria"]
            categoria_count[categoria] = categoria_count.get(categoria, 0) + 1
        if categoria_count:
            msg = "\n".join([f"{cat}: {count}" for cat, count in categoria_count.items()])
            messagebox.showinfo("Livros por Categoria", msg)
        else:
            messagebox.showinfo("Livros por Categoria", "Nenhum livro cadastrado.")

    def emprestimos_por_usuario(self):
        emprestimos = self.carregar_dados(self.emprestimos_arquivo)
        usuarios = self.carregar_dados(self.usuarios_arquivo)
        type_count = {}
        for emp in emprestimos:
            email = emp["usuario_email"]
            user = next((u for u in usuarios if u["email"] == email), None)
            if user:
                tipo = user["tipo"]
                type_count[tipo] = type_count.get(tipo, 0) + 1
        if type_count:
            msg = "\n".join([f"{tipo}: {count}" for tipo, count in type_count.items()])
            messagebox.showinfo("Empréstimos por Tipo de Usuário", msg)
        else:
            messagebox.showinfo("Empréstimos por Tipo de Usuário", "Nenhum empréstimo registrado.")

    def livros_mais_emprestados(self):
        livros = self.carregar_dados(self.livros_arquivo)
        if not livros:
            messagebox.showinfo("Livros mais Emprestados", "Nenhum livro cadastrado.")
            return

        for livro in livros:
            if "emprestimos_count" not in livro:
                livro["emprestimos_count"] = 0
        sorted_books = sorted(livros, key=lambda l: l["emprestimos_count"], reverse=True)
        top_books = sorted_books[:3]
        msg = "\n".join([f"{livro['titulo']} - {livro['emprestimos_count']} empréstimos" for livro in top_books])
        messagebox.showinfo("Livros Mais Emprestados", msg)

class BibliotecaApp:
    def __init__(self, root):
        self.biblioteca = Biblioteca()
        self.root = root
        self.root.title("Sistema de Biblioteca")
        self.root.geometry("800x650")
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        notebook = ttk.Notebook(root)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.frame_livros = ttk.Frame(notebook)
        notebook.add(self.frame_livros, text="Livros")
        self.create_livros_tab()
        
        self.frame_usuarios = ttk.Frame(notebook)
        notebook.add(self.frame_usuarios, text="Usuários")
        self.create_usuarios_tab()
        
        self.frame_emprestimos = ttk.Frame(notebook)
        notebook.add(self.frame_emprestimos, text="Empréstimos")
        self.create_emprestimos_tab()
        
        self.frame_relatorios = ttk.Frame(notebook)
        notebook.add(self.frame_relatorios, text="Relatórios")
        self.create_relatorios_tab()

    def create_livros_tab(self):
        frame = self.frame_livros
        title_lbl = ttk.Label(frame, text="Cadastro e Listagem de Livros", font=("Helvetica", 18, "bold"))
        title_lbl.pack(pady=10)
        
        cadastro_frame = ttk.LabelFrame(frame, text="Cadastrar Livro")
        cadastro_frame.pack(fill="x", padx=20, pady=10)
        campos = ["Título", "Autor", "Publicação", "ISBN", "Categoria"]
        self.livro_vars = {}
        for campo in campos:
            frame_campo = ttk.Frame(cadastro_frame)
            frame_campo.pack(fill="x", padx=10, pady=5)
            lbl_campo = ttk.Label(frame_campo, text=campo + ":", width=15, anchor="w")
            lbl_campo.pack(side="left")
            var = tk.StringVar()
            entry = ttk.Entry(frame_campo, textvariable=var)
            entry.pack(side="left", expand=True, fill="x")
            self.livro_vars[campo.lower()] = var
        btn_cadastrar = ttk.Button(cadastro_frame, text="Cadastrar Livro", command=self.cadastrar_livro)
        btn_cadastrar.pack(pady=10)
        
        busca_frame = ttk.LabelFrame(frame, text="Buscar Livro")
        busca_frame.pack(fill="x", padx=20, pady=10)
        criterio_lbl = ttk.Label(busca_frame, text="Critério:", width=15, anchor="w")
        criterio_lbl.grid(row=0, column=0, padx=5, pady=5)
        self.criterio_var = tk.StringVar()
        self.criterio_combobox = ttk.Combobox(busca_frame, textvariable=self.criterio_var, state="readonly", values=["título", "autor", "categoria"])
        self.criterio_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.criterio_combobox.current(0)
        valor_lbl = ttk.Label(busca_frame, text="Valor:", width=15, anchor="w")
        valor_lbl.grid(row=1, column=0, padx=5, pady=5)
        self.valor_busca = tk.StringVar()
        entry_valor = ttk.Entry(busca_frame, textvariable=self.valor_busca)
        entry_valor.grid(row=1, column=1, padx=5, pady=5)
        btn_busca = ttk.Button(busca_frame, text="Buscar", command=self.buscar_livro)
        btn_busca.grid(row=2, column=0, columnspan=2, pady=10)
        
        btn_listar = ttk.Button(frame, text="Listar Todos os Livros", command=self.listar_todos_livros)
        btn_listar.pack(pady=10)

    def create_usuarios_tab(self):
        frame = self.frame_usuarios
        title_lbl = ttk.Label(frame, text="Cadastro de Usuários", font=("Helvetica", 18, "bold"))
        title_lbl.pack(pady=10)
        cadastro_frame = ttk.LabelFrame(frame, text="Cadastrar Usuário")
        cadastro_frame.pack(fill="x", padx=20, pady=10)
        campos = ["Nome", "Email", "Tipo"]
        self.usuario_vars = {}
        for campo in campos:
            frame_campo = ttk.Frame(cadastro_frame)
            frame_campo.pack(fill="x", padx=10, pady=5)
            lbl_campo = ttk.Label(frame_campo, text=campo + ":", width=15, anchor="w")
            lbl_campo.pack(side="left")
            var = tk.StringVar()
            entry = ttk.Entry(frame_campo, textvariable=var)
            entry.pack(side="left", expand=True, fill="x")
            self.usuario_vars[campo.lower()] = var
        btn_cadastrar = ttk.Button(cadastro_frame, text="Cadastrar Usuário", command=self.cadastrar_usuario)
        btn_cadastrar.pack(pady=10)

    def create_emprestimos_tab(self):
        frame = self.frame_emprestimos
        title_lbl = ttk.Label(frame, text="Gerenciar Empréstimos", font=("Helvetica", 18, "bold"))
        title_lbl.pack(pady=10)
        emprestimo_frame = ttk.LabelFrame(frame, text="Realizar Empréstimo")
        emprestimo_frame.pack(fill="x", padx=20, pady=10)
        lbl_id = ttk.Label(emprestimo_frame, text="ID Exemplar:", width=15, anchor="w")
        lbl_id.grid(row=0, column=0, padx=5, pady=5)
        self.emprestimo_id = tk.StringVar()
        entry_id = ttk.Entry(emprestimo_frame, textvariable=self.emprestimo_id)
        entry_id.grid(row=0, column=1, padx=5, pady=5)
        lbl_email = ttk.Label(emprestimo_frame, text="Email Usuário:", width=15, anchor="w")
        lbl_email.grid(row=1, column=0, padx=5, pady=5)
        self.emprestimo_email = tk.StringVar()
        entry_email = ttk.Entry(emprestimo_frame, textvariable=self.emprestimo_email)
        entry_email.grid(row=1, column=1, padx=5, pady=5)
        btn_emp = ttk.Button(emprestimo_frame, text="Realizar Empréstimo", command=self.realizar_emprestimo)
        btn_emp.grid(row=2, column=0, columnspan=2, pady=10)
        devolucao_frame = ttk.LabelFrame(frame, text="Devolver Livro")
        devolucao_frame.pack(fill="x", padx=20, pady=10)
        lbl_devolve = ttk.Label(devolucao_frame, text="ID Exemplar:", width=15, anchor="w")
        lbl_devolve.grid(row=0, column=0, padx=5, pady=5)
        self.devolve_id = tk.StringVar()
        entry_devolve = ttk.Entry(devolucao_frame, textvariable=self.devolve_id)
        entry_devolve.grid(row=0, column=1, padx=5, pady=5)
        btn_dev = ttk.Button(devolucao_frame, text="Devolver Livro", command=self.devolver_livro)
        btn_dev.grid(row=1, column=0, columnspan=2, pady=10)
        btn_lista = ttk.Button(frame, text="Listar Empréstimos", command=self.biblioteca.lista_emprestimos)
        btn_lista.pack(pady=10)

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

    def cadastrar_livro(self):

        campos_obrigatorios = ["título", "autor", "publicação", "isbn", "categoria"]
        for campo in campos_obrigatorios:
            valor = self.livro_vars[campo].get().strip()
            if not valor:
                messagebox.showerror("Erro", f"O campo {campo.capitalize()} é obrigatório.")
                return

        titulo = self.livro_vars["título"].get().strip()
        autor = self.livro_vars["autor"].get().strip()
        publicacao = self.livro_vars["publicação"].get().strip()
        isbn = self.livro_vars["isbn"].get().strip()
        categoria = self.livro_vars["categoria"].get().strip()

        id_exemplar = self.biblioteca.get_next_id()
        livro = Livro(titulo, autor, publicacao, isbn, categoria, id_exemplar)
        self.biblioteca.cadastra_livro(livro)
        for var in self.livro_vars.values():
            var.set("")

    def cadastrar_usuario(self):
        nome = self.usuario_vars["nome"].get().strip()
        email = self.usuario_vars["email"].get().strip()
        tipo = self.usuario_vars["tipo"].get().strip()
        if not (nome and email and tipo):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios.")
            return
        usuario = Usuario(nome, email, tipo)
        self.biblioteca.cadastra_usuario(usuario)
        for var in self.usuario_vars.values():
            var.set("")

    def buscar_livro(self):
        criterio = self.criterio_var.get()
        valor = self.valor_busca.get().strip()
        if not valor:
            messagebox.showerror("Erro", "Informe o valor para busca.")
            return
        self.biblioteca.busca_livros(criterio, valor)
        self.valor_busca.set("")

    def listar_todos_livros(self):
        livros = self.biblioteca.listar_todos_livros()
        if not livros:
            messagebox.showinfo("Listar Livros", "Nenhum livro cadastrado.")
            return

        lista_win = tk.Toplevel(self.root)
        lista_win.title("Todos os Livros")
        lista_win.geometry("750x400")
        tree = ttk.Treeview(lista_win, columns=("ID", "Título", "Autor", "Publicação", "ISBN", "Categoria", "Emprestado", "Empréstimos"), show="headings")
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
        tree.pack(expand=True, fill="both", padx=10, pady=10)
        for livro in livros:
            emprestado = "Sim" if livro.get("emprestado", False) else "Não"
            tree.insert("", "end", values=(livro["id_exemplar"], livro["titulo"], livro["autor"], livro["publicacao"], livro["isbn"], livro["categoria"], emprestado, livro.get("emprestimos_count", 0)))
            
    def realizar_emprestimo(self):
        try:
            id_exemplar = int(self.emprestimo_id.get())
        except Exception:
            messagebox.showerror("Erro", "ID Exemplar inválido.")
            return
        email = self.emprestimo_email.get().strip()
        self.biblioteca.cadastra_emprestimo(id_exemplar, email)
        self.emprestimo_id.set("")
        self.emprestimo_email.set("")

    def devolver_livro(self):
        try:
            id_exemplar = int(self.devolve_id.get())
        except Exception:
            messagebox.showerror("Erro", "ID Exemplar inválido.")
            return
        self.biblioteca.devolve_livro(id_exemplar)
        self.devolve_id.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = BibliotecaApp(root)
    root.mainloop()
