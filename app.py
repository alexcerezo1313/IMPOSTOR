import streamlit as st
import random
import palabras  # Aquí se cargan las palabras desde palabras.py

# ------------------------------------------------------------
#                 ESTADO INICIAL DE LA APLICACIÓN
# ------------------------------------------------------------

if "players" not in st.session_state:
    st.session_state.players = []

if "num_players" not in st.session_state:
    st.session_state.num_players = 3

if "impostor_index" not in st.session_state:
    st.session_state.impostor_index = None

if "secret_word" not in st.session_state:
    st.session_state.secret_word = None

if "start_player_index" not in st.session_state:
    st.session_state.start_player_index = None

if "used_words" not in st.session_state:
    st.session_state.used_words = []   # ← palabras ya jugadas

if "step" not in st.session_state:
    st.session_state.step = "config"

if "current_reveal_index" not in st.session_state:
    st.session_state.current_reveal_index = 0

if "show_role" not in st.session_state:
    st.session_state.show_role = False


# ------------------------------------------------------------
#                        FUNCIONES ÚTILES
# ------------------------------------------------------------

def reset_game():
    """Reinicia toda la partida y resetea palabras usadas."""
    st.session_state.players = []
    st.session_state.num_players = 3
    st.session_state.impostor_index = None
    st.session_state.secret_word = None
    st.session_state.start_player_index = None
    st.session_state.used_words = []     # reiniciar palabras usadas
    st.session_state.current_reveal_index = 0
    st.session_state.show_role = False
    st.session_state.step = "config"



def get_new_word():
    """Escoge una palabra de palabras.PALABRAS sin repetir."""
    disponibles = [w for w in palabras.PALABRAS if w not in st.session_state.used_words]

    # Si no queda ninguna palabra, reiniciar lista
    if not disponibles:
        st.session_state.used_words = []
        disponibles = palabras.PALABRAS.copy()

    secret = random.choice(disponibles)
    st.session_state.used_words.append(secret)

    return secret



def new_round():
    """Crea una nueva ronda con impostor y palabra secreta."""
    num_players = len(st.session_state.players)

    st.session_state.impostor_index = random.randint(0, num_players - 1)

    # Nueva palabra secreta (no repetida)
    st.session_state.secret_word = get_new_word()

    st.session_state.current_reveal_index = 0
    st.session_state.show_role = False
    st.session_state.start_player_index = None
    st.session_state.step = "reveal"



def choose_start_player():
    """Elige quién empieza hablando, 95% probabilidad de NO ser impostor."""
    num_players = len(st.session_state.players)
    impostor = st.session_state.impostor_index
    non_impostors = [i for i in range(num_players) if i != impostor]

    if random.random() < 0.95 and non_impostors:
        st.session_state.start_player_index = random.choice(non_impostors)
    else:
        st.session_state.start_player_index = random.randint(0, num_players - 1)



def advance_reveal():
    """Pasa al siguiente jugador o a la pantalla de inicio del juego."""
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
    st.title("🎭 Juego del Impostor (versión con palabras.py)")

    st.markdown("""
    ### Cómo se juega
    1. Cada jugador introduce **solo su nombre**.  
    2. La palabra secreta viene del archivo **palabras.py**.  
    3. No se repiten palabras hasta gastar toda la lista.  
    4. El impostor no conocerá la palabra.
    """)

    st.session_state.num_players = st.number_input(
        "Número de jugadores:",
        min_value=3,
        max_value=15,
        step=1,
        value=st.session_state.num_players
    )

    if st.button("Continuar ➜"):
        st.session_state.players = [{"name": ""} for _ in range(st.session_state.num_players)]
        st.session_state.step = "words"


# ------------------------------------------------------------
#         PANTALLA 2 – INTRODUCIR NOMBRES
# ------------------------------------------------------------

def ui_words():
    st.header("Introduce los nombres de los jugadores")

    all_ok = True
    for i in range(st.session_state.num_players):
        name = st.text_input(f"Nombre del jugador {i+1}:", key=f"name_{i}")
        if not name.strip():
            all_ok = False
        st.session_state.players[i]["name"] = name.strip() or f"Jugador {i+1}"

    if st.button("Guardar y continuar ➜"):
        if not all_ok:
            st.error("Todos los jugadores deben tener nombre.")
        else:
            new_round()


# ------------------------------------------------------------
#         PANTALLA 3 – REVELAR ROLES
# ------------------------------------------------------------

def ui_reveal():
    idx = st.session_state.current_reveal_index
    player = st.session_state.players[idx]

    st.header("Revelación de roles")
    st.subheader(f"Turno de: **{player['name']}**")

    st.markdown("👉 Solo **esta persona** debe mirar ahora.")

    if st.button("👀 Revelar rol"):
        st.session_state.show_role = True

    if st.session_state.show_role:
        st.markdown("---")

        if idx == st.session_state.impostor_index:
            st.subheader("😈 ERES EL IMPOSTOR")
        else:
            st.subheader("🗝️ Tu palabra secreta es:")
            st.markdown(f"# **{st.session_state.secret_word}**")

        st.markdown("---")

        if st.button("➡️ Continuar"):
            advance_reveal()


# ------------------------------------------------------------
#       PANTALLA 4 – INICIO DEL JUEGO
# ------------------------------------------------------------

def ui_start_round():
    idx = st.session_state.start_player_index
    player = st.session_state.players[idx]

    st.header("🚀 Inicio del juego")
    st.subheader(f"Empieza hablando: **{player['name']}**")

    st.markdown("---")

    if st.button("😈 Revelar impostor"):
        impostor = st.session_state.players[st.session_state.impostor_index]["name"]
        st.success(f"El impostor era: **{impostor}**")

    st.markdown("---")

    if st.button("🔄 Nueva ronda"):
        new_round()
        st.rerun()

    if st.button("🔁 Reiniciar partida completa"):
        reset_game()
        st.rerun()


# ------------------------------------------------------------
#                            MAIN
# ------------------------------------------------------------

def main():
    st.sidebar.button("🔁 Reiniciar juego", on_click=reset_game)

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