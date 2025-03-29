import json

class Livro:

    def __init__(self, arquivo="livros.txt"):
        self.arquivo = arquivo

    def cadastra(self, titulo, autor, publicacao, isbn, categoria):
        novo_livro = {
            "titulo": titulo,
            "autor": autor,
            "publicacao": publicacao,
            "isbn": isbn,
            "categoria": categoria
        }

        try:
            with open(self.arquivo, "r") as arquivo:
                lista_de_livros = json.load(arquivo)
        except (FileNotFoundError, json.JSONDecodeError):
            lista_de_livros = []

        # Verifica se o livro já existe na lista antes de adicionar
        if novo_livro in lista_de_livros:
            return

        lista_de_livros.append(novo_livro)

        with open(self.arquivo, "w") as arquivo:
            json.dump(lista_de_livros, arquivo, indent=4)

    def lista_livros(self):
        try:
            with open(self.arquivo, "r") as arquivo:
                lista_de_livros = json.load(arquivo)

                if not lista_de_livros:
                    print("Nenhum livro cadastrado.")
                    return

                for livro in lista_de_livros:
                    print(f"Título: {livro['titulo']}, Autor: {livro['autor']}, "
                          f"Publicação: {livro['publicacao']}, ISBN: {livro['isbn']}, "
                          f"Categoria: {livro['categoria']}")
        except (FileNotFoundError, json.JSONDecodeError):
            print("Nenhum livro cadastrado.")

    def busca_livro(self, metodo:str, valor: str):
            with open(self.arquivo, "r") as arquivo:
                lista_de_livros = json.load(arquivo)
                resultado = []

                metodo = metodo.lower()

                if not lista_de_livros:
                    print("Nenhum livro cadastrado.")
                    return

                if metodo not in ["titulo", "autor", "categoria"]:
                    print("Método não está na lista de metodos disponíveis")
                    return             
                
                for livro in lista_de_livros:
                    if valor.lower() in livro[metodo].lower():
                        resultado.append(livro)

                if resultado:
                    for livro in resultado:
                        print(f"Título: {livro['titulo']}, Autor: {livro['autor']}, "
                            f"Publicação: {livro['publicacao']}, ISBN: {livro['isbn']}, "
                            f"Categoria: {livro['categoria']}")
                    return
                else:
                    print("Nenhum livro encontrado com esse critério.")
            

livros = Livro()

livros.cadastra("Jogos Mortais", "J. K. Rowling", "31/08/2003", "6.54", "Terror")
livros.cadastra("IT: A Coisa", "Stephen King", "20/01/1999", "10", "Terror")

livros.busca_livro("categoria", "terror")