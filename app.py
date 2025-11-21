import streamlit as st
import random
import re

# ------------------------------------------------------------
#                 ESTADO INICIAL DE LA APLICACIÓN
# ------------------------------------------------------------

if "players" not in st.session_state:
    st.session_state.players = []

if "num_players" not in st.session_state:
    st.session_state.num_players = 3

if "current_player_input" not in st.session_state:
    st.session_state.current_player_input = 0

if "current_reveal_index" not in st.session_state:
    st.session_state.current_reveal_index = 0

if "impostor_index" not in st.session_state:
    st.session_state.impostor_index = None

if "secret_word" not in st.session_state:
    st.session_state.secret_word = None

if "start_player_index" not in st.session_state:
    st.session_state.start_player_index = None

if "step" not in st.session_state:
    st.session_state.step = "config"

if "show_role" not in st.session_state:
    st.session_state.show_role = False

# NUEVO → palabras ya usadas en esta sesión
if "used_words" not in st.session_state:
    st.session_state.used_words = []


# ------------------------------------------------------------
#                        FUNCIONES ÚTILES
# ------------------------------------------------------------

def reset_game():
    """Reinicia toda la partida."""
    st.session_state.players = []
    st.session_state.num_players = 3
    st.session_state.current_player_input = 0
    st.session_state.current_reveal_index = 0
    st.session_state.impostor_index = None
    st.session_state.secret_word = None
    st.session_state.start_player_index = None
    st.session_state.show_role = False
    st.session_state.step = "config"
    st.session_state.used_words = []   # NUEVO → reiniciar historial de palabras


def parse_words(text):
    words = re.split(r"[,;\n]+", text)
    return [w.strip() for w in words if w.strip()]


def new_round():
    """Crea una ronda nueva con impostor y palabra NO repetida."""
    num_players = len(st.session_state.players)

    # Elegir impostor
    st.session_state.impostor_index = random.randint(0, num_players - 1)

    # Obtener todas las palabras posibles de NO impostores
    candidate_words = []
    for idx, p in enumerate(st.session_state.players):
        if idx != st.session_state.impostor_index:
            candidate_words.extend(p["words"])

    # Eliminar palabras ya usadas
    available_words = [w for w in candidate_words if w not in st.session_state.used_words]

    # Si no queda ninguna palabra útil → reiniciar lista de palabras usadas
    if not available_words:
        st.session_state.used_words = []
        available_words = candidate_words.copy()

    # Elegir palabra nueva
    st.session_state.secret_word = random.choice(available_words)

    # Guardar palabra como usada
    st.session_state.used_words.append(st.session_state.secret_word)

    st.session_state.current_reveal_index = 0
    st.session_state.show_role = False
    st.session_state.start_player_index = None
    st.session_state.step = "reveal"


def choose_start_player():
    """Elige quién empieza hablando, con 95% de probabilidad de NO ser impostor."""
    num_players = len(st.session_state.players)
    impostor = st.session_state.impostor_index
    non_impostors = [i for i in range(num_players) if i != impostor]

    if non_impostors and random.random() < 0.95:
        st.session_state.start_player_index = random.choice(non_impostors)
    else:
        st.session_state.start_player_index = random.randint(0, num_players - 1)


def advance_reveal():
    """Pasa al siguiente jugador o al inicio del juego si todos han revelado."""
    idx = st.session_state.current_reveal_index
    num_players = len(st.session_state.players)

    if idx < num_players - 1:
        st.session_state.current_reveal_index += 1
        st.session_state.show_role = False
        st.rerun()
    else:
        choose_start_player()
        st.session_state.step = "start_round"
        st.session_state.show_role = False
        st.rerun()


# ------------------------------------------------------------
#                     PANTALLA 1 – CONFIGURACIÓN
# ------------------------------------------------------------

def ui_config():
    st.title("🎭 Juego del Impostor")

    st.markdown("""
    **Cómo se juega**  
    1. Cada jugador, por separado, escribe su nombre y 3–10 palabras.  
    2. El juego elige un impostor y una palabra que ese impostor NO haya escrito.  
    3. La palabra **no puede repetirse** hasta reiniciar el juego.  
    4. Después se indica quién empieza la ronda.
    """)

    st.session_state.num_players = st.number_input(
        "Número de jugadores:",
        min_value=3,
        max_value=15,
        step=1,
        value=st.session_state.num_players,
        key="num_players_input"
    )

    if st.button("Continuar ➜", key="btn_config_continue"):
        st.session_state.players = [
            {"name": "", "words": []}
            for _ in range(st.session_state.num_players)
        ]
        st.session_state.current_player_input = 0
        st.session_state.step = "words"


# ------------------------------------------------------------
#          PANTALLA 2 – NOMBRES Y PALABRAS (UNO A UNO)
# ------------------------------------------------------------

def ui_words():
    idx = st.session_state.current_player_input
    total = st.session_state.num_players

    st.header(f"Jugador {idx+1} de {total}")

    name = st.text_input("Introduce tu nombre:", key=f"name_input_{idx}")

    words_raw = st.text_area(
        "Escribe entre 3 y 10 palabras (separadas por comas o saltos de línea):",
        key=f"words_input_{idx}",
        height=120
    )

    if st.button("Guardar y continuar ➜", key=f"btn_save_player_{idx}"):
        words = parse_words(words_raw)
        if len(words) < 3 or len(words) > 10:
            st.error("Debes introducir entre 3 y 10 palabras.")
            return

        st.session_state.players[idx]["name"] = name.strip() or f"Jugador {idx+1}"
        st.session_state.players[idx]["words"] = words

        st.session_state.current_player_input += 1

        if st.session_state.current_player_input >= total:
            new_round()
        else:
            st.rerun()


# ------------------------------------------------------------
#         PANTALLA 3 – REVELAR ROLES (UNO TRAS OTRO)
# ------------------------------------------------------------

def ui_reveal():
    idx = st.session_state.current_reveal_index
    player = st.session_state.players[idx]

    st.header("Revelación de roles")
    st.subheader(f"Turno de: **{player['name']}**")

    st.markdown("👉 Solo **esta persona** debe mirar la pantalla ahora mismo.")

    if st.button("👀 Revelar rol", key=f"btn_show_role_{idx}"):
        st.session_state.show_role = True

    if st.session_state.show_role:
        st.markdown("---")

        if idx == st.session_state.impostor_index:
            st.subheader("😈 ERES EL IMPOSTOR")
            st.write("No conoces la palabra. Intenta pasar desapercibido.")
        else:
            st.subheader("🗝️ Tu palabra secreta es:")
            st.markdown(f"# **{st.session_state.secret_word}**")

        st.markdown("---")

        if st.button("➡️ Continuar", key=f"btn_continue_role_{idx}"):
            advance_reveal()


# ------------------------------------------------------------
#       PANTALLA 4 – INICIO DEL JUEGO / QUIÉN EMPIEZA
# ------------------------------------------------------------

def ui_start_round():
    idx = st.session_state.start_player_index
    player = st.session_state.players[idx]

    st.header("🚀 Inicio del juego")

    st.subheader(f"Empieza hablando: **{player['name']}**")

    st.markdown("---")

    if st.button("😈 Revelar impostor", key="btn_reveal_impostor"):
        impostor = st.session_state.players[st.session_state.impostor_index]["name"]
        st.success(f"El impostor era: **{impostor}**")

    st.markdown("---")

    if st.button("🔄 Nueva ronda", key="btn_new_round_start"):
        new_round()
        st.rerun()

    if st.button("🔁 Reiniciar partida completa", key="btn_reset_full_start"):
        reset_game()
        st.rerun()


# ------------------------------------------------------------
#                            MAIN
# ------------------------------------------------------------

def main():
    st.sidebar.button("🔁 Reiniciar Juego", on_click=reset_game)

    step = st.session_state.step

    if step == "config":
        ui_config()
    elif step == "words":
        ui_words()
    elif step == "reveal":
        ui_reveal()
    elif step == "start_round":
        ui_start_round()


if __name__ == "__main__":
    main()