📚 EmpréstimoEasy - Sistema de Gestão de Bibliotecas em Python
O EmpréstimoEasy é um sistema de gerenciamento de acervo e empréstimos de bibliotecas totalmente desenvolvido em Python Puro, com interface de console. O projeto utiliza dataclasses para estruturar dados (Usuários, Livros, Empréstimos) e simula a persistência lendo e gerenciando arquivos de texto.

O sistema é um excelente exemplo de Programação Orientada a Objetos (POO) e demonstra a implementação de lógicas de negócio cruciais, como o cálculo de multas em tempo real e o controle rigoroso de prazos usando a biblioteca datetime.

✨ Destaques Funcionais
O acesso é dividido em dois perfis principais:

Cliente (Autoatendimento): O usuário pode visualizar o status de seus empréstimos, checar multas pendentes e, crucialmente, renovar o prazo de devolução (limitado a 2 vezes), desde que o livro não esteja atrasado.

Bibliotecário (Supervisão): Tem acesso ao histórico completo de todos os empréstimos (ativos e devolvidos) e ao status detalhado do acervo.
