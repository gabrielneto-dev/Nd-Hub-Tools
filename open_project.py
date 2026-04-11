'''
- Atualização de pastas de projetos
- Salvar novo projeto(Caminho do projeto, com string ou caminho direto)
- Deletar projeto
- Menu de projetos
'''

from app._banco import GerenciadorConexao
import os
import sys
from pathlib import Path

CREATE_BANCO = """
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        path TEXT NOT NULL UNIQUE
    );
"""

path_banco = "/home/neto/.pyscripts/projects.db"

def validar_caminho(caminho: str) -> bool:
    """Valida se o caminho existe e é um diretório"""
    try:
        return os.path.exists(caminho) and os.path.isdir(caminho)
    except (OSError, TypeError):
        return False

def validar_nome_projeto(nome: str) -> tuple[bool, str]:
    """Valida o nome do projeto"""
    if not nome or not nome.strip():
        return False, "Nome do projeto não pode estar vazio."
    
    nome = nome.strip()
    
    if len(nome) > 100:
        return False, "Nome do projeto muito longo (máximo 100 caracteres)."
    
    # Validar caracteres inválidos para nomes de projeto
    caracteres_invalidos = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in caracteres_invalidos:
        if char in nome:
            return False, f"Nome do projeto contém caractere inválido: '{char}'"
    
    return True, nome

def list_projects() -> list:
    """Lista todos os projetos com validações"""
    try:
        with GerenciadorConexao(path_banco) as db:
            db.executar(CREATE_BANCO)
            projects = db.executar("SELECT * FROM projects ORDER BY name").fetchall()
            
            if not projects:
                print("\nNenhum projeto cadastrado.")
                return []
            
            print("\n=== Projetos Cadastrados ===")
            for index, project in enumerate(projects):
                status = "✓" if validar_caminho(project[2]) else "✗"
                print(f"{index + 1} - {project[1]} [{status}]")
            
            return projects
            
    except Exception as e:
        print(f"\nErro ao listar projetos: {e}")
        return []

def save_project() -> bool:
    """Salva um novo projeto com validações"""
    try:
        caminho = os.getcwd()
        
        # Validar caminho atual
        if not validar_caminho(caminho):
            print("\nErro: Caminho atual não é válido ou não existe.")
            return False
        
        with GerenciadorConexao(path_banco) as db:
            db.executar(CREATE_BANCO)
            
            # Verificar se caminho já existe
            contagem = db.executar("SELECT * FROM projects WHERE path = ?", (caminho,)).fetchall()
            if contagem:
                print("\nErro: Este caminho já está cadastrado em outro projeto.")
                return False
            
            # Obter e validar nome do projeto
            while True:
                nome_project = input("\nQual o nome do projeto: ").strip()
                
                is_valid, mensagem = validar_nome_projeto(nome_project)
                if not is_valid:
                    print(f"Erro: {mensagem}")
                    continue
                
                nome_project = mensagem  # Nome já validado e tratado
                
                # Verificar se nome já existe
                projeto_existente = db.executar(
                    "SELECT * FROM projects WHERE name = ?", 
                    (nome_project,)
                ).fetchall()
                
                if projeto_existente:
                    print("Erro: Nome do projeto já existe. Tente um nome diferente!")
                else:
                    break
            
            # Inserir projeto
            resultado = db.executar(
                "INSERT INTO projects (name, path) VALUES (?, ?)", 
                (nome_project, caminho)
            )
            
            if resultado:
                print("\n✓ Projeto salvo com sucesso!")
                return True
            else:
                print("\n✗ Erro ao salvar projeto.")
                return False
                
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        return False
    except Exception as e:
        print(f"\nErro inesperado ao salvar projeto: {e}")
        return False

def delete_project() -> bool:
    """Deleta um projeto com validações"""
    try:
        projects = list_projects()
        
        if not projects:
            return False
        
        while True:
            try:
                selected = input("\nDigite o número do projeto para deletar (ou 'c' para cancelar): ").strip()
                
                if selected.lower() == 'c':
                    print("Operação cancelada.")
                    return False
                
                selected = int(selected) - 1
                
                if 0 <= selected < len(projects):
                    break
                else:
                    print(f"Erro: Número inválido. Digite um número entre 0 e {len(projects)-1}")
                    
            except ValueError:
                print("Erro: Digite um número válido.")
        
        # Confirmação de segurança
        projeto_nome = projects[selected][1]
        confirmacao = input(f"\nTem certeza que deseja deletar o projeto '{projeto_nome}'? (s/N): ").strip().lower()
        
        if confirmacao not in ['s', 'sim', 'y', 'yes']:
            print("Operação cancelada.")
            return False
        
        with GerenciadorConexao(path_banco) as db:
            resultado = db.executar("DELETE FROM projects WHERE id = ?", (projects[selected][0],))
            
            if resultado:
                print("\n✓ Projeto deletado com sucesso!")
                return True
            else:
                print("\n✗ Erro ao deletar projeto!")
                return False
                
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        return False
    except Exception as e:
        print(f"\nErro inesperado ao deletar projeto: {e}")
        return False

def open_project() -> bool:
    """Abre um projeto no VSCode com validações"""
    try:
        projects = list_projects()
        
        if not projects:
            return False
        
        # Filtrar apenas projetos com caminhos válidos
        projetos_validos = []
        for project in projects:
            if validar_caminho(project[2]):
                projetos_validos.append(project)
        
        if not projetos_validos:
            print("\nNenhum projeto com caminho válido encontrado.", file=sys.stderr)
            return False
        
        try: 
            selected = int(sys.argv[3]) - 1
        except:
            while True:
                try:
                    selected = input("\nDigite o número do projeto para abrir (ou 'c' para cancelar): ").strip()
                    
                    if selected.lower() == 'c':
                        print("Operação cancelada.")
                        return False
                    
                    selected = int(selected) - 1
                    
                    if 0 <= selected < len(projetos_validos):
                        break
                    else:
                        print(f"Erro: Número inválido. Digite um número entre 0 e {len(projetos_validos)-1}")
                        
                except ValueError:
                    print("Erro: Digite um número válido.")
        
        projeto_caminho = projetos_validos[selected][2]
        
        # Verificar se o VSCode está disponível
        if os.system("which nvim > /dev/null 2>&1") != 0:
            print("\nErro: NeoVim não encontrado. Certifique-se de que está instalado e no PATH.")
            return False
        
        print(f"\nAbrindo projeto '{projetos_validos[selected][1]}' no Vim...", file=sys.stderr)
        resultado = os.system(f"nvim '{projeto_caminho}'")
        try:
            path_script_saida = "/home/neto/.pyscripts/ir_projeto.sh"

            # Usar aspas simples em 'cd' é mais seguro para caminhos com espaços
            comando_cd = f"cd '{projeto_caminho}'\n" 

            with open(path_script_saida, 'w', encoding='utf-8') as f:
                f.write(comando_cd)
            os.system(f"chmod +x {path_script_saida}")
        except Exception as e:
            print(f"Erro ao criar script de cd: {e}", file=sys.stderr)
        
        if resultado == 0:
            print("✓ Projeto aberto com sucesso!",file=sys.stderr)
            return True
        else:
            print("✗ Erro ao abrir projeto no NeoVim.", file=sys.stderr)
            return False
            
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"\nErro inesperado ao abrir projeto: {e}", file=sys.stderr)
        return False

def menu_project(select: int | None = None):
    """Menu principal com validações"""
    try:
        if select is None:
            while True:
                print("\n" + "="*40)
                print("          MENU DE PROJETOS")
                print("="*40)
                print(" 0 - Sair")
                print(" 1 - Abrir projeto")
                print(" 2 - Adicionar projeto")
                print(" 3 - Deletar projeto")
                print(" 4 - Listar projetos")
                print("="*40)
                
                try:
                    selected = input(">> ").strip()
                    
                    if not selected:
                        print("Erro: Digite uma opção.")
                        continue
                    
                    selected = int(selected)
                    break
                    
                except ValueError:
                    print("Erro: Opção inválida! Digite um número.")
            
            menu_project(selected)
        else:
            if select == 0:
                print("\nSaindo... Até logo!")
                sys.exit(0)
                
            elif select == 1:
                open_project()
                
            elif select == 2:
                save_project()
                
            elif select == 3:
                delete_project()
                
            elif select == 4:
                list_projects()
                
            else:
                print("\nErro: Opção inválida!")
           
            
    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\nErro inesperado no menu: {e}")

def atualizar_projects() -> bool:
    """Atualiza a lista de projetos removendo caminhos inválidos"""
    try:
        with GerenciadorConexao(path_banco) as db:
            db.executar(CREATE_BANCO)
            projects = db.executar("SELECT * FROM projects").fetchall()
            
            if not projects:
                print("Nenhum projeto para verificar.")
                return True
            
            projetos_removidos = 0
            for project in projects:
                if not validar_caminho(project[2]):
                    print(f"Removendo projeto inválido: {project[1]}")
                    db.executar("DELETE FROM projects WHERE id = ?", (project[0],))
                    projetos_removidos += 1
            
            if projetos_removidos > 0:
                print(f"\n✓ {projetos_removidos} projeto(s) inválido(s) removido(s).")
            else:
                print("✓ Todos os projetos estão válidos.")
            
            return True
            
    except Exception as e:
        print(f"\n✗ Erro ao atualizar projetos: {e}")
        return False

def verificar_banco_dados() -> bool:
    """Verifica se o banco de dados está acessível"""
    try:
        # Verificar se o diretório do banco existe
        banco_path = Path(path_banco)
        banco_path.parent.mkdir(parents=True, exist_ok=True)
        
        with GerenciadorConexao(path_banco) as db:
            db.executar(CREATE_BANCO)
            return True
            
    except Exception as e:
        print(f"Erro crítico: Não foi possível acessar o banco de dados: {e}")
        return False

def main_projects():
    
    if len(sys.argv) > 1:
        if sys.argv[2] == "open" or sys.argv[2] == "1":
            atualizar_projects()
            open_project()
            return
        if sys.argv[2] == "list" or sys.argv[2] == "4":
            atualizar_projects()
            list_projects()
            return
        if sys.argv[2] == "del" or sys.argv[2] == "3":
            atualizar_projects()
            delete_project()
            return
        if sys.argv[2] == "add" or sys.argv[2] == "2":
            atualizar_projects()
            save_project()
            return
    
    
    """Função principal com todas as validações"""
    try:
        print("Iniciando gerenciador de projetos...")
        
        # Verificar banco de dados
        if not verificar_banco_dados():
            print("Erro: Não foi possível inicializar o banco de dados.")
            sys.exit(1)
        
        # Atualizar projetos
        atualizar_projects()
        
        # Iniciar menu
        menu_project()
        
    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\nErro crítico: {e}")
        sys.exit(1)
