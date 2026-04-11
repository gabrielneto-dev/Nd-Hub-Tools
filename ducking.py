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
    try:
        result = subprocess.run(["playerctl", "-l"], capture_output=True, text=True)
        players = result.stdout.strip().split("\n")

        playing_other = False

        for player in players:
            if not player:
                continue

            status_result = subprocess.run(
                ["playerctl", "-p", player, "status"], capture_output=True, text=True
            )
            status = status_result.stdout.strip()

            if player.startswith("spotify"):
                continue

            if status == "Playing":
                playing_other = True
                break

        return playing_other
    except FileNotFoundError:
        return False


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
        is_other_playing = get_playing_players()

        # 3. Aplica a lógica de ducking com os valores do JSON
        if is_other_playing and not ducked:
            print(f"▶️ Abaixando o Spotify para {vol_baixo}...")
            set_spotify_volume(vol_baixo)
            ducked = True

        elif not is_other_playing and ducked:
            print(f"⏸️ Restaurando o Spotify para {vol_alto}...")
            set_spotify_volume(vol_alto)
            ducked = False

        time.sleep(tempo_espera)


if __name__ == "__main__":
    main()
