import subprocess
import time
import json
import os

# --- DEFINA O CAMINHO ABSOLUTO AQUI ---
# Ex: "/home/neto/scripts/config.json"
CAMINHO_CONFIG = "/home/neto/gns/tools/ducking.json"


def carregar_configuracoes():
    """Lê o arquivo JSON e retorna os valores. Se der erro, usa um padrão."""
    try:
        with open(CAMINHO_CONFIG, "r") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        print(
            f"⚠️ Arquivo de config não encontrado em {CAMINHO_CONFIG}. Usando valores padrão."
        )
        return {"volume_baixo": "0.2", "volume_alto": "1.0", "tempo_verificacao": 1}
    except json.JSONDecodeError:
        print("⚠️ Erro ao ler o JSON (formato inválido). Usando valores padrão.")
        return {"volume_baixo": "0.2", "volume_alto": "1.0", "tempo_verificacao": 1}


def get_playing_players():
    """Retorna o nome do player que está tocando agora (exceto Spotify e GSConnect)."""
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

            status_result = subprocess.run(
                ["playerctl", "-p", player, "status"], capture_output=True, text=True
            )
            status = status_result.stdout.strip()

            if status == "Playing":
                return player

        return None
    except Exception:
        return None


def set_spotify_volume(volume):
    subprocess.run(
        ["playerctl", "-p", "spotify", "volume", str(volume)], stderr=subprocess.DEVNULL
    )


def main():
    print("🎧 Monitor de áudio iniciado com suporte a JSON...")
    ducked = False

    while True:
        # 1. Carrega as configurações mais recentes do JSON a cada ciclo
        config = carregar_configuracoes()
        vol_baixo = str(config.get("volume_baixo", "0.2"))
        vol_alto = str(config.get("volume_alto", "1.0"))
        tempo_espera = int(config.get("tempo_verificacao", 1))

        # 2. Verifica quem está tocando
        trigger_player = get_playing_players()

        # 3. Aplica a lógica de ducking com os valores do JSON
        if trigger_player and not ducked:
            print(f"▶️ Abaixando o Spotify para {vol_baixo} (Trigger: {trigger_player})...")
            set_spotify_volume(vol_baixo)
            ducked = True

        elif not trigger_player and ducked:
            print(f"⏸️ Restaurando o Spotify para {vol_alto}...")
            set_spotify_volume(vol_alto)
            ducked = False

        time.sleep(tempo_espera)


if __name__ == "__main__":
    main()
