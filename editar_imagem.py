"""
╔══════════════════════════════════════════════════════════════╗
║           EDITOR DE IMAGENS — Variações de Criativos         ║
╚══════════════════════════════════════════════════════════════╝

Aplica ajustes leves nas imagens: zoom, saturação, brilho e contraste.
Usa a biblioteca 'seletor.py' para navegação interativa de arquivos.

Uso interativo (recomendado):
    python editar_imagem.py

Uso via linha de comando:
    python editar_imagem.py --pasta /fotos
    python editar_imagem.py --arquivos foto1.jpg foto2.png
    python editar_imagem.py --pasta /fotos --saida /saida --zoom 0.06
"""

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageEnhance

# ─── Importa a biblioteca de seleção ───────────────────────────
try:
    from lib.seletor import selecionar_arquivos, selecionar_destino

    SELETOR_DISPONIVEL = True
except ImportError:
    SELETOR_DISPONIVEL = False

# ─── Cores ANSI ────────────────────────────────────────────────
R = "\033[0m"
B = "\033[1m"
DIM = "\033[2m"
CY = "\033[96m"
GR = "\033[92m"
YE = "\033[93m"
RE = "\033[91m"
WH = "\033[97m"
MA = "\033[95m"
BL = "\033[94m"

EXTENSOES = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"]


# ─── Utilitários ───────────────────────────────────────────────


def _human(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _ok(msg):
    print(f"  {GR}✔{R}  {msg}")


def _err(msg):
    print(f"  {RE}✘{R}  {RE}{msg}{R}")


def _warn(msg):
    print(f"  {YE}⚠{R}  {WH}{msg}{R}")


def _info(msg):
    print(f"  {BL}ℹ{R}  {msg}")


def _sep():
    print(f"  {DIM}{'─' * 60}{R}")


def banner():
    print(f"""
{MA}{B}
  ███████╗██████╗ ██╗████████╗ ██████╗ ██████╗
  ██╔════╝██╔══██╗██║╚══██╔══╝██╔═══██╗██╔══██╗
  █████╗  ██║  ██║██║   ██║   ██║   ██║██████╔╝
  ██╔══╝  ██║  ██║██║   ██║   ██║   ██║██╔══██╗
  ███████╗██████╔╝██║   ██║   ╚██████╔╝██║  ██║
  ╚══════╝╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
{R}{DIM}  Variações de Criativos  ·  v2.0{R}
{MA}{"─" * 50}{R}""")


# ─── Edição de imagem ──────────────────────────────────────────


def editar_imagem(
    img_path: Path, zoom: float, saturacao: float, brilho: float, contraste: float,
    inverter: bool
) -> Image.Image:
    img = Image.open(img_path).convert("RGB")
    w, h = img.size

    if zoom > 0:
        cx, cy = int(w * zoom / 2), int(h * zoom / 2)
        img = img.crop((cx, cy, w - cx, h - cy))
        img = img.resize((w, h), Image.LANCZOS)

    if inverter:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    img = ImageEnhance.Color(img).enhance(saturacao)
    img = ImageEnhance.Brightness(img).enhance(brilho)
    img = ImageEnhance.Contrast(img).enhance(contraste)
    return img


def resolver_destino_auto(arquivos: list) -> Path:
    """Destino inteligente quando nenhum é especificado."""
    pastas = {f.parent.resolve() for f in arquivos}
    if len(pastas) == 1:
        destino = pastas.pop() / "editadas"
    else:
        destino = Path.cwd() / "editadas"
    destino.mkdir(parents=True, exist_ok=True)
    return destino


def processar(arquivos: list, destino: Path, zoom, saturacao, brilho, contraste, inverter: bool, sufixo_editada: bool):
    print(f"\n  {MA}▶{R}  {B}EDITANDO IMAGENS{R}")
    _sep()
    print(f"  {BL}ℹ{R}  Destino: {WH}{destino.resolve()}{R}")
    nome_modo = "nome_editada" if sufixo_editada else "nome original"
    print(f"  {BL}ℹ{R}  Nomenclatura: {WH}{nome_modo}{R}")
    print(f"  {BL}ℹ{R}  {len(arquivos)} imagem(ns) para processar\n")

    sucesso, erros = 0, 0
    nomes_usados = {}

    for i, arquivo in enumerate(arquivos, 1):
        nome_base, ext = arquivo.stem, arquivo.suffix.lower()
        chave = nome_base + ext
        if sufixo_editada:
            if chave in nomes_usados:
                nomes_usados[chave] += 1
                nome_saida = f"{nome_base}_{nomes_usados[chave]}_editada{ext}"
            else:
                nomes_usados[chave] = 0
                nome_saida = f"{nome_base}_editada{ext}"
        else:
            if chave in nomes_usados:
                nomes_usados[chave] += 1
                nome_saida = f"{nome_base}_{nomes_usados[chave]}{ext}"
            else:
                nomes_usados[chave] = 0
                nome_saida = f"{nome_base}{ext}"

        print(
            f"  {DIM}[{i}/{len(arquivos)}]{R}  {WH}{arquivo.name}{R}  →  {CY}{nome_saida}{R}"
        )

        try:
            img = editar_imagem(arquivo, zoom, saturacao, brilho, contraste, inverter)
            caminho_saida = destino / nome_saida
            img.save(caminho_saida, quality=95)
            sz = caminho_saida.stat().st_size
            _ok(f"Salvo: {nome_saida}  ({_human(sz)})")
            sucesso += 1
        except Exception as e:
            _err(f"Erro: {e}")
            erros += 1

    _sep()
    print(f"\n  {GR}{B}✔ {sucesso} editada(s){R}", end="")
    if erros:
        print(f"   {RE}{B}✘ {erros} com falha{R}", end="")
    print(f"\n  {DIM}Saída: {destino.resolve()}{R}\n")


# ─── Menu interativo ───────────────────────────────────────────


def _perguntar_nome() -> bool:
    """Pergunta obrigatória sobre o nome do arquivo de saída. Retorna True = com sufixo _editada."""
    print(f"\n  {MA}▶{R}  {B}NOME DO ARQUIVO DE SAÍDA{R}")
    _sep()
    print(f"  {YE}⚠{R}  {WH}Esta opção é obrigatória — escolha uma das alternativas:{R}\n")
    while True:
        print(f"  {CY}1{R}.  {B}Com sufixo{R}   {DIM}— ex: foto_editada.jpg{R}")
        print(f"  {CY}2{R}.  {B}Nome original{R} {DIM}— ex: foto.jpg  (sem sufixo){R}\n")
        esc = input(f"  {CY}►{R} ").strip()
        if esc == "1":
            _ok("Arquivos serão salvos com sufixo '_editada'.")
            return True
        elif esc == "2":
            _ok("Arquivos serão salvos com o nome original.")
            return False
        else:
            _warn("Digite 1 ou 2.")


def menu_parametros() -> dict:
    """Permite ajustar os parâmetros de edição de forma interativa."""
    print(f"\n  {MA}▶{R}  {B}PARÂMETROS DE EDIÇÃO{R}")
    _sep()

    defaults = {"zoom": 0.05, "saturacao": 1.05, "brilho": 1.03, "contraste": 1.02}
    labels = {
        "zoom": ("Zoom (recorte de borda)", "0.05"),
        "saturacao": ("Saturação de cores", "1.05"),
        "brilho": ("Brilho", "1.03"),
        "contraste": ("Contraste", "1.02"),
    }

    print(f"  {DIM}Pressione Enter para usar o valor padrão de cada item.{R}\n")

    params = {}
    for key, (label, default_str) in labels.items():
        while True:
            raw = input(f"  {CY}{label}{R} [{DIM}{default_str}{R}]: ").strip()
            if not raw:
                params[key] = defaults[key]
                break
            try:
                params[key] = float(raw)
                break
            except ValueError:
                _warn("Digite um número válido (ex: 1.05) ou pressione Enter.")

    print()

    # ── Inversão horizontal (obrigatório) ──
    print(f"\n  {MA}▶{R}  {B}INVERSÃO DE LADOS{R}  {DIM}(espelhamento horizontal){R}")
    _sep()
    print(f"  {YE}⚠{R}  {WH}Esta opção é obrigatória — escolha uma das alternativas:{R}\n")
    while True:
        print(f"  {CY}1{R}.  {B}Sim{R}  {DIM}— inverter a imagem horizontalmente{R}")
        print(f"  {CY}2{R}.  {B}Não{R}  {DIM}— manter a imagem original{R}\n")
        esc = input(f"  {CY}►{R} ").strip()
        if esc == "1":
            params["inverter"] = True
            _ok("Inversão horizontal ativada.")
            break
        elif esc == "2":
            params["inverter"] = False
            _ok("Sem inversão.")
            break
        else:
            _warn("Digite 1 para Sim ou 2 para Não.")

    params["sufixo_editada"] = _perguntar_nome()

    print()
    return params


def modo_interativo():
    """Fluxo completo interativo usando seletor.py."""
    banner()

    if not SELETOR_DISPONIVEL:
        _err("'seletor.py' não encontrado. Coloque-o na mesma pasta que este script.")
        sys.exit(1)

    # ── 1. Escolher arquivos ou pasta ──
    print(f"""
  {B}O que deseja editar?{R}

  {CY}1{R}.  {B}Selecionar arquivos específicos{R}   {DIM}(de qualquer pasta){R}
  {CY}2{R}.  {B}Selecionar uma pasta inteira{R}       {DIM}(todos os formatos suportados){R}
  {CY}0{R}.  {DIM}Sair{R}
""")
    escolha = input(f"  {CY}►{R} ").strip()

    if escolha == "0":
        sys.exit(0)

    arquivos = []

    if escolha == "1":
        # Arquivos específicos via navegador
        arquivos = selecionar_arquivos(extensoes=EXTENSOES)

    elif escolha == "2":
        # Pasta inteira via navegador de diretórios
        pasta = (
            selecionar_destino.__wrapped__
            if hasattr(selecionar_destino, "__wrapped__")
            else None
        )

        # Usa selecionar_arquivos a partir de uma pasta — usuário navega até ela e usa [a]
        _info(
            "Navegue até a pasta desejada e pressione [a] para selecionar todas as imagens, depois [ok]."
        )
        input(f"  {DIM}Enter para abrir o navegador...{R}")
        arquivos = selecionar_arquivos(extensoes=EXTENSOES)

    else:
        _warn("Opção inválida.")
        sys.exit(1)

    if not arquivos:
        _warn("Nenhum arquivo selecionado.")
        sys.exit(0)

    # ── 2. Escolher destino ──
    print(f"\n  {B}Onde salvar os arquivos editados?{R}\n")
    print(
        f"  {CY}1{R}.  {B}Destino automático{R}   {DIM}(pasta 'editadas' junto aos arquivos){R}"
    )
    print(f"  {CY}2{R}.  {B}Escolher destino{R}      {DIM}(navegar até a pasta){R}\n")
    esc_dest = input(f"  {CY}►{R} ").strip()

    if esc_dest == "2":
        destino = selecionar_destino()
    else:
        destino = resolver_destino_auto(arquivos)

    # ── 3. Parâmetros de edição ──
    print(f"\n  {B}Ajustar parâmetros de edição?{R}  {DIM}[s/N]{R} ", end="")
    if input().strip().lower() == "s":
        params = menu_parametros()
    else:
        params = {"zoom": 0.05, "saturacao": 1.05, "brilho": 1.03, "contraste": 1.02}
        # ── Inversão obrigatória mesmo sem ajustar demais parâmetros ──
        print(f"\n  {MA}▶{R}  {B}INVERSÃO DE LADOS{R}  {DIM}(espelhamento horizontal){R}")
        _sep()
        print(f"  {YE}⚠{R}  {WH}Esta opção é obrigatória — escolha uma das alternativas:{R}\n")
        while True:
            print(f"  {CY}1{R}.  {B}Sim{R}  {DIM}— inverter a imagem horizontalmente{R}")
            print(f"  {CY}2{R}.  {B}Não{R}  {DIM}— manter a imagem original{R}\n")
            esc = input(f"  {CY}►{R} ").strip()
            if esc == "1":
                params["inverter"] = True
                _ok("Inversão horizontal ativada.")
                break
            elif esc == "2":
                params["inverter"] = False
                _ok("Sem inversão.")
                break
            else:
                _warn("Digite 1 para Sim ou 2 para Não.")
        # ── Nome do arquivo obrigatório mesmo sem ajustar demais parâmetros ──
        params["sufixo_editada"] = _perguntar_nome()

    # ── 4. Processar ──
    processar(arquivos, destino, **params)
    input(f"  {DIM}Pressione Enter para sair...{R}")


# ─── Modo CLI (linha de comando) ───────────────────────────────


def modo_cli():
    parser = argparse.ArgumentParser(
        description="Editor de imagens para variações de criativos.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    origem = parser.add_mutually_exclusive_group(required=True)
    origem.add_argument(
        "--pasta",
        "-p",
        metavar="PASTA",
        help="Pasta de imagens (processa todas, incluindo subpastas)",
    )
    origem.add_argument(
        "--arquivos",
        "-a",
        metavar="ARQ",
        nargs="+",
        help="Arquivos específicos (podem estar em pastas diferentes)",
    )

    parser.add_argument(
        "--saida",
        "-s",
        metavar="PASTA_SAIDA",
        help="Pasta de destino (opcional; criada automaticamente)",
    )
    parser.add_argument("--zoom", type=float, default=0.05)
    parser.add_argument("--saturacao", type=float, default=1.05)
    parser.add_argument("--brilho", type=float, default=1.03)
    parser.add_argument("--contraste", type=float, default=1.02)
    parser.add_argument(
        "--inverter",
        required=True,
        choices=["sim", "nao"],
        metavar="sim|nao",
        help="Inversão horizontal da imagem (obrigatório: 'sim' ou 'nao')",
    )
    parser.add_argument(
        "--nome",
        required=True,
        choices=["editada", "original"],
        metavar="editada|original",
        help="Nome do arquivo de saída (obrigatório: 'editada' = foto_editada.jpg, 'original' = foto.jpg)",
    )
    args = parser.parse_args()

    banner()

    arquivos = []

    if args.pasta:
        p = Path(args.pasta)
        if not p.is_dir():
            _err(f"Pasta não encontrada: {args.pasta}")
            sys.exit(1)
        arquivos = [f for f in p.rglob("*") if f.suffix.lower() in EXTENSOES]
        if not arquivos:
            _warn(f"Nenhuma imagem encontrada em: {args.pasta}")
            sys.exit(1)

    if args.arquivos:
        for a in args.arquivos:
            p = Path(a)
            if not p.is_file():
                _warn(f"Arquivo não encontrado, ignorando: {a}")
                continue
            if p.suffix.lower() not in EXTENSOES:
                _warn(f"Formato não suportado, ignorando: {a}")
                continue
            arquivos.append(p)

    if not arquivos:
        _err("Nenhum arquivo válido para processar.")
        sys.exit(1)

    destino = Path(args.saida) if args.saida else resolver_destino_auto(arquivos)
    destino.mkdir(parents=True, exist_ok=True)

    processar(
        arquivos,
        destino,
        zoom=args.zoom,
        saturacao=args.saturacao,
        brilho=args.brilho,
        contraste=args.contraste,
        inverter=(args.inverter == "sim"),
        sufixo_editada=(args.nome == "editada"),
    )


# ─── Entrada ───────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) > 1:
        modo_cli()
    else:
        modo_interativo()
