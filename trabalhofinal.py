from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import sys

COMPANY = {
    "nome_empresa": "SoftLib Solutions",
    "nome_produto": "EmpréstimoEasy",
    "historia": (
        "Fundada em 2025 por entusiastas de bibliotecas e desenvolvedores, a SoftLib "
        "Solutions cria soluções simples e escaláveis para gestão de acervos e empréstimos. "
        "Nossa missão é aproximar leitores e conhecimento com tecnologia acessível, "
        "dando autonomia total ao usuário final."
    ),
    "funcionarios": [
        ("Mateus de Mattos", "Desenvolvedor Líder"),
        ("Kauã Neves", "Analista de Sistemas"),
        ("Arthur Santanna", "Testador QA"),
    ],
    "logo_ascii":
        """
         ,_,
        [0,0]
        |)--)- SoftLib Solutions
        -”-”-
        """
}


@dataclass
class User:
    codigo: str
    nome: str
    tipo: str
    login: str
    senha: str


@dataclass
class Book:
    codigo: str
    titulo: str
    autor: str


@dataclass
class BookStatus:
    codigo_livro: str
    posicao: str
    estado_conservacao: str
    acessivel_emprestimo: bool


@dataclass
class LoanRecord:
    codigo_emprestimo: str
    codigo_cliente: str
    codigo_livro: str
    data_emprestimo: datetime
    data_devolucao_prevista: datetime
    data_devolucao_real: Optional[datetime] = None
    multa_cobrada: float = 0.0
    renovacoes_realizadas: int = 0


class LibrarySystem:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.users: Dict[str, User] = {}
        self.books: Dict[str, Book] = {}
        self.loans: List[LoanRecord] = []
        self.book_statuses: Dict[str, BookStatus] = {}
        self.current_user: Optional[User] = None

        self.PRAZO_DIAS_INICIAL = 7
        self.PRAZO_DIAS_RENOVACAO = 7
        self.MAX_RENOVACOES = 2
        self.MULTA_DIA = 0.50

        self.load_all_files()

    def load_all_files(self):
        try:
            self.load_users(self.base_path / "usuarios.txt")
            self.load_books(self.base_path / "livros.txt")
            self.load_book_statuses(self.base_path / "status_livros.txt")
            self.load_loans(self.base_path / "emprestimos.txt")
        except FileNotFoundError as e:
            print(f"[AVISO] Arquivo não encontrado: {e.args[0]}")
        except Exception as e:
            print(f"[ERRO] Falha ao carregar arquivos: {e}")

    def load_users(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"usuarios.txt não encontrado em {path}")
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                parts = line.split(";")
                if len(parts) < 5: continue
                codigo, nome, tipo, login, senha = [p.strip() for p in parts[:5]]
                user = User(codigo, nome, tipo, login, senha)
                self.users[user.login] = user

    def load_books(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"livros.txt não encontrado em {path}")
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                parts = line.split(";")
                if len(parts) < 3: continue
                codigo, titulo, autor = [p.strip() for p in parts[:3]]
                book = Book(codigo, titulo, autor)
                self.books[book.codigo] = book

    def load_book_statuses(self, path: Path):
        if not path.exists():
            return
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                parts = line.split(";")
                if len(parts) < 4: continue

                codigo, pos, estado, acessivel_txt = [p.strip() for p in parts[:4]]
                acessivel = acessivel_txt.lower() == 'true'

                status = BookStatus(codigo, pos, estado, acessivel)
                self.book_statuses[codigo] = status

    def load_loans(self, path: Path):
        if not path.exists():
            return
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                parts = line.split(";")
                if len(parts) < 8: continue

                codigo_emp, cod_cli, cod_livro, dt_emp_txt, dt_prev_txt, dt_real_txt, multa_txt, reno_txt = [p.strip()
                                                                                                             for p in
                                                                                                             parts[:8]]

                try:
                    dt_emp = datetime.strptime(dt_emp_txt, "%Y-%m-%d")
                    dt_prev = datetime.strptime(dt_prev_txt, "%Y-%m-%d")
                    dt_real = datetime.strptime(dt_real_txt, "%Y-%m-%d") if dt_real_txt.lower() != 'none' else None
                    multa = float(multa_txt)
                    renovacoes = int(reno_txt)

                    rec = LoanRecord(codigo_emp, cod_cli, cod_livro, dt_emp, dt_prev, dt_real, multa, renovacoes)
                    self.loans.append(rec)
                except ValueError:
                    continue

    def validate_user(self, login: str, senha: str) -> bool:
        user = self.users.get(login)
        if user and user.senha == senha:
            self.current_user = user
            return True
        return False

    def show_about(self):
        print("\n" + "=" * 50)
        print(COMPANY["logo_ascii"])
        print(f"Empresa: {COMPANY['nome_empresa']}")
        print(f"Produto: {COMPANY['nome_produto']}\n")
        print("História:")
        print(COMPANY["historia"] + "\n")
        print("Funcionários:")
        for nome, func in COMPANY["funcionarios"]:
            print(f" - {nome}: {func}")
        print("=" * 50 + "\n")

    def calculate_current_fine(self, record: LoanRecord) -> float:
        if record.data_devolucao_real:
            return 0.0

        hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if hoje > record.data_devolucao_prevista:
            dias_atraso = (hoje - record.data_devolucao_prevista).days
            return dias_atraso * self.MULTA_DIA
        return 0.0

    def get_current_user_loans_status(self):
        if not self.current_user:
            return []

        user_loans: List[LoanRecord] = [
            ln for ln in self.loans
            if ln.codigo_cliente == self.current_user.codigo and ln.data_devolucao_real is None
        ]

        loan_statuses = []
        for ln in user_loans:
            book = self.books.get(ln.codigo_livro)
            title = book.titulo if book else f"[Livro {ln.codigo_livro} Desconhecido]"

            multa = self.calculate_current_fine(ln)
            atrasado = multa > 0.0

            loan_statuses.append({
                'record': ln,
                'titulo': title,
                'atrasado': atrasado,
                'multa_atual': multa
            })
        return loan_statuses

    def list_loans_for_current_user(self):
        print(f"\n--- Empréstimos Ativos de {self.current_user.nome} ---")
        loan_statuses = self.get_current_user_loans_status()

        if not loan_statuses:
            print("Nenhum empréstimo ativo no momento.\n")
            return

        total_multa = 0.0
        for i, status in enumerate(loan_statuses, 1):
            ln = status['record']
            status_txt = "ATRASADO 🔴" if status['atrasado'] else "No Prazo 🟢"
            multa_txt = f" (Multa: R$ {status['multa_atual']:.2f})" if status['atrasado'] else ""

            print(f"{i}. [{ln.codigo_livro}] {status['titulo']}")
            print(f"   Empréstimo: {ln.data_emprestimo.strftime('%Y-%m-%d')}")
            print(f"   Dev. Prevista: {ln.data_devolucao_prevista.strftime('%Y-%m-%d')}")
            print(f"   Status: {status_txt}{multa_txt} | Renovações: {ln.renovacoes_realizadas}/{self.MAX_RENOVACOES}")

            total_multa += status['multa_atual']

        print("----------------------------------")
        print(f"Total de Multas a Pagar: R$ {total_multa:.2f}")
        print("----------------------------------\n")

    def renew_loan(self):
        if not self.current_user or self.current_user.tipo.lower() != "cliente":
            print("Funcionalidade apenas para clientes autenticados.")
            return

        loan_statuses = self.get_current_user_loans_status()
        if not loan_statuses:
            print("Não há empréstimos ativos para renovação.\n")
            return

        print("\n--- RENOVAR EMPRÉSTIMO ---")
        for i, status in enumerate(loan_statuses, 1):
            print(
                f"{i}. {status['titulo']} (Prevista: {status['record'].data_devolucao_prevista.strftime('%Y-%m-%d')})")
            print(f"   Renovações: {status['record'].renovacoes_realizadas}/{self.MAX_RENOVACOES}")

        try:
            choice = input("Digite o número do item para renovar (ou 0 para cancelar): ").strip()
            item_index = int(choice) - 1
            if item_index < 0 or item_index >= len(loan_statuses):
                print("Operação cancelada ou inválida.")
                return

            status_selecionado = loan_statuses[item_index]
            record = status_selecionado['record']

            if status_selecionado['atrasado']:
                print("\n🚫 Renovação negada: O livro está ATRASADO. Regularize sua situação (multa) antes.")
                return

            if record.renovacoes_realizadas >= self.MAX_RENOVACOES:
                print(f"\n🚫 Renovação negada: Limite máximo de {self.MAX_RENOVACOES} renovações atingido.")
                return

            record.renovacoes_realizadas += 1
            record.data_devolucao_prevista += timedelta(days=self.PRAZO_DIAS_RENOVACAO)

            print(f"\n✅ Renovação bem-sucedida!")
            print(
                f"   {status_selecionado['titulo']} (Nova Dev. Prevista: {record.data_devolucao_prevista.strftime('%Y-%m-%d')})")
            print(f"   Total de renovações: {record.renovacoes_realizadas}/{self.MAX_RENOVACOES}")

        except ValueError:
            print("Opção inválida.")

    def list_books(self):
        print("\n--- Lista de Livros (Disponibilidade e Status) ---")
        if not self.books:
            print("Nenhum livro cadastrado.")
            return

        for b in sorted(self.books.values(), key=lambda x: x.titulo):
            status = self.book_statuses.get(b.codigo)

            acessivel = "Sim" if status and status.acessivel_emprestimo else "Não 🚫"
            estado = status.estado_conservacao if status else "N/A"
            posicao = status.posicao if status else "N/A"

            emprestado = any(ln for ln in self.loans if ln.codigo_livro == b.codigo and ln.data_devolucao_real is None)

            disp_txt = "Emprestado" if emprestado else "Disponível"

            print(f"[{b.codigo}] {b.titulo} — {b.autor} ({disp_txt})")
            print(f"   > Estado: {estado} | Posição: {posicao} | Acessível: {acessivel}")

        print("----------------------------------\n")

    def list_all_loans(self):
        print("\n--- Todos os Empréstimos Cadastrados (Histórico) ---")
        if not self.loans:
            print("Nenhum empréstimo registrado.")
            return

        for r in sorted(self.loans, key=lambda x: x.data_emprestimo, reverse=True):
            book = self.books.get(r.codigo_livro)
            title = book.titulo if book else f"[código {r.codigo_livro} não encontrado]"
            user = next((u for u in self.users.values() if u.codigo == r.codigo_cliente), None)
            user_name = user.nome if user else f"[cliente {r.codigo_cliente} não encontrado]"

            dev_real_txt = r.data_devolucao_real.strftime('%Y-%m-%d') if r.data_devolucao_real else "ATIVO"
            status_loan = "DEVOLVIDO" if r.data_devolucao_real else "ATIVO"

            print(f"[{r.codigo_emprestimo}] {status_loan} | Cliente: {user_name}")
            print(
                f"  > Livro: {title} | Empréstimo: {r.data_emprestimo.strftime('%Y-%m-%d')} | Previsto: {r.data_devolucao_prevista.strftime('%Y-%m-%d')}")
            print(
                f"  > Devolução Real: {dev_real_txt} | Multa: R$ {r.multa_cobrada:.2f} | Renovações: {r.renovacoes_realizadas}")

        print("----------------------------------\n")

    def run_console(self):
        print("=" * 60)
        print("Bem-vindo ao sistema de Empréstimos - EmpréstimoEasy (SoftLib Solutions)")
        print("Digite seu login e senha para acessar o sistema.")
        print("=" * 60)
        try:
            login = input("Informe o login do usuário: ").strip()
            senha = input("Informe a senha do usuário: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExecução interrompida. Saindo...")
            sys.exit(0)

        if not self.validate_user(login, senha):
            print("\nAcesso negado: login ou senha inválidos.")
            return

        print(f"\nAcesso liberado. Bem-vindo, {self.current_user.nome} ({self.current_user.tipo}).\n")
        print("Informações do Desenvolvedor (Menu Sobre):")
        print(f"Empresa: {COMPANY['nome_empresa']} - Produto: {COMPANY['nome_produto']}")
        print("\n")

        if self.current_user.tipo.lower() == "cliente":
            while True:
                print("--- Menu (Cliente) ---")
                print("1 - Visualizar Empréstimos e Multas")
                print("2 - Renovar Empréstimo (Diferencial de Autoatendimento!)")
                print("3 - Visualizar Livros e Status")
                print("4 - Sobre a SoftLib Solutions")
                print("5 - Sair")
                choice = input("Escolha uma opção: ").strip()
                if choice == "1":
                    self.list_loans_for_current_user()
                elif choice == "2":
                    self.renew_loan()
                elif choice == "3":
                    self.list_books()
                elif choice == "4":
                    self.show_about()
                elif choice == "5":
                    print("Saindo... Obrigado Pela Preferência!")
                    break
                else:
                    print("Opção inválida. Tente novamente.\n")

        elif self.current_user.tipo.lower() == "bibliotecario":
            while True:
                print("--- Menu (Bibliotecário) ---")
                print("1 - Listar todos os empréstimos (Histórico Completo)")
                print("2 - Visualizar Livros e Status")
                print("3 - Sobre a SoftLib Solutions")
                print("4 - Sair")
                choice = input("Escolha uma opção: ").strip()
                if choice == "1":
                    self.list_all_loans()
                elif choice == "2":
                    self.list_books()
                elif choice == "3":
                    self.show_about()
                elif choice == "4":
                    print("Saindo... Obrigado Pela Preferência!")
                    break
                else:
                    print("Opção inválida. Tente novamente.\n")
        else:
            print("Tipo de usuário desconhecido. Saindo...")


def main():
    base_path = Path(__file__).parent
    system = LibrarySystem(base_path)
    system.run_console()


if __name__ == "__main__":
    main()