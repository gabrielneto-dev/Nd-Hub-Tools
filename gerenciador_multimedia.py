import argparse
import re
import pulsectl


# ==========================================
# FUNÇÃO 1: LISTAR DISPOSITIVOS (GETTER)
# ==========================================
def obter_lista_dispositivos():
    """
    Retorna uma lista de dicionários (array) contendo todos os dispositivos
    ativos, seus modos, e as chaves (IDs) necessárias para ativá-los.
    """
    opcoes_disponiveis = []

    try:
        with pulsectl.Pulse("leitor-audio") as pulse:
            saidas = pulse.sink_list()
            sink_padrao_nome = pulse.server_info().default_sink_name

            for saida in saidas:
                nome_placa = saida.proplist.get("alsa.card_name", saida.description)
                volume = round(pulse.volume_get_all_chans(saida) * 100)

                # Caso a placa não tenha portas (Modo Único)
                if not saida.port_list:
                    ativo = saida.name == sink_padrao_nome
                    opcoes_disponiveis.append(
                        {
                            "dispositivo": nome_placa,
                            "modo": "Padrão",
                            "volume": volume,
                            "ativo": ativo,
                            # IDs de Ativação:
                            "id_sink": saida.name,
                            "id_porta": None,
                        }
                    )
                    continue

                # Caso a placa tenha múltiplas portas (Ex: HDMIs, Headphones)
                for porta in saida.port_list:
                    if porta.available == 1:  # Ignora portas desconectadas
                        continue

                    porta_ativa = (
                        saida.port_active is not None
                        and saida.port_active.name == porta.name
                    )
                    placa_ativa = saida.name == sink_padrao_nome
                    ativo = placa_ativa and porta_ativa

                    opcoes_disponiveis.append(
                        {
                            "dispositivo": nome_placa,
                            "modo": porta.description,
                            "volume": volume,
                            "ativo": ativo,
                            # IDs de Ativação:
                            "id_sink": saida.name,
                            "id_porta": porta.name,
                        }
                    )

    except Exception as e:
        print(f"Erro ao buscar dispositivos: {e}")

    return opcoes_disponiveis


# ==========================================
# FUNÇÃO 2: ALTERAR DISPOSITIVO (SETTER)
# ==========================================
def alterar_dispositivo(id_sink, id_porta=None):
    """
    Recebe os IDs de ativação e força o sistema a rotear o áudio para eles.
    Retorna True se houver sucesso, ou False em caso de erro.
    """
    try:
        with pulsectl.Pulse("modificador-audio") as pulse:
            # 1. Busca a lista atualizada do servidor
            saidas = pulse.sink_list()

            # 2. Encontra o objeto correspondente ao id_sink passado
            sink_alvo = next((s for s in saidas if s.name == id_sink), None)

            if not sink_alvo:
                print("Erro: Placa de som (sink) não encontrada no sistema.")
                return False

            # 3. Define a placa como saída padrão do sistema
            pulse.default_set(sink_alvo)

            # 4. Se um modo (porta) foi especificado, ativa ele dentro da placa
            if id_porta:
                porta_alvo = next(
                    (p for p in sink_alvo.port_list if p.name == id_porta), None
                )
                if porta_alvo:
                    pulse.port_set(sink_alvo, porta_alvo)
                else:
                    print("Erro: Porta de som não encontrada nesta placa.")
                    return False

            # 5. Puxa todos os aplicativos tocando som no momento para a nova saída
            sink_index = sink_alvo.index
            for fluxo in pulse.sink_input_list():
                try:
                    pulse.sink_input_move(fluxo.index, sink_index)
                except:
                    pass  # Ignora sons imutáveis do sistema

            return True

    except Exception as e:
        print(f"Erro crítico ao tentar alterar o áudio: {e}")
        return False


def iniciar_cli():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--action",
        type=str,
        default="list",
        choices=["list", "update"],
        help="Definir ação, se vai alterar dispositivo(update) ou listar(list)",
    )

    parser.add_argument(
        "--id_sink", type=str, help="Tem que ser o id_sink do dispositivo."
    )

    parser.add_argument("--id_porta", type=str, help="Porta.")

    args = parser.parse_args()

    if args.action == "update" and (args.id_sink is None or args.id_porta is None):
        parser.error("Eu preciso do dois argumentos preencidos.")

    if args.action == "list":
        return obter_lista_dispositivos()
    elif args.action == "update":
        return alterar_dispositivo(id_porta=args.id_porta, id_sink=args.id_sink)
    else:
        parser.error("A função de ação não corresponde as mapeadas!")


if __name__ == "__main__":
    result = iniciar_cli()
    print(result)
