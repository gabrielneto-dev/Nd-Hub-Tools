import json
import subprocess
import os

# --- CAMINHO DO SEU ARQUIVO ---
# Defina o caminho absoluto para o JSON aqui
CAMINHO_CONFIG = "/home/neto/gns/tools/ducking.json"


def ler_config():
    """Lê o arquivo JSON atual. Retorna valores padrão em caso de erro."""
    try:
        with open(CAMINHO_CONFIG, "r") as arquivo:
            return json.load(arquivo)
    except Exception:
        return {"volume_baixo": "0.2", "volume_alto": "1.0", "tempo_verificacao": 1}


def salvar_config(config):
    """Sobrescreve o arquivo JSON com o novo dicionário de configurações."""
    with open(CAMINHO_CONFIG, "w") as arquivo:
        json.dump(config, arquivo, indent=4)


def outro_app_esta_tocando():
    """Verifica no sistema via playerctl se há outro player (além do Spotify) tocando."""
    try:
        result = subprocess.run(["playerctl", "-l"], capture_output=True, text=True)
        players = result.stdout.strip().split("\n")

        for player in players:
            if not player:
                continue

            # Filtro inteligente: ignora Spotify (local ou remoto) e GSConnect (controles remotos)
            player_lower = player.lower()
            if "spotify" in player_lower or player.startswith("GSConnect"):
                continue

            # Checa o status do player atual
            status = subprocess.run(
                ["playerctl", "-p", player, "status"], capture_output=True, text=True
            ).stdout.strip()

            if status == "Playing":
                return True
        return False
    except Exception:
        return False


def atualizar_volume_ducking(novo_volume_porcentagem):
    """
    Função principal (Entrypoint) para a sua interface chamar.

    Argumento:
    - novo_volume_porcentagem: Inteiro ou Float de 0 a 100.
    """
    # 1. Converte a escala de 0-100 para 0.0-1.0
    volume_float = float(novo_volume_porcentagem) / 100.0
    volume_str = f"{volume_float:.2f}"

    # 2. Atualiza e salva o config.json
    config = ler_config()
    config["volume_baixo"] = volume_str
    salvar_config(config)

    # 3. Se houver áudio concorrente tocando, aplica a mudança no sistema imediatamente
    if outro_app_esta_tocando():
        subprocess.run(
            ["playerctl", "-p", "spotify", "volume", volume_str],
            stderr=subprocess.DEVNULL,
        )
