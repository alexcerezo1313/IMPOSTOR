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

if "impostor_index" not in st.session_state:
    st.session_state.impostor_index = None

if "secret_word" not in st.session_state:
    st.session_state.secret_word = None

if "step" not in st.session_state:
    st.session_state.step = "config"   # config → words → reveal

if "show_role" not in st.session_state:
    st.session_state.show_role = False


# ------------------------------------------------------------
#                        FUNCIONES ÚTILES
# ------------------------------------------------------------

def reset_game():
    st.session_state.players = []
    st.session_state.num_players = 3
    st.session_state.current_player_input = 0
    st.session_state.impostor_index = None
    st.session_state.secret_word = None
    st.session_state.show_role = False
    st.session_state.step = "config"

def new_round():
    num_players = len(st.session_state.players)

    st.session_state.impostor_index = random.randint(0, num_players - 1)

    candidate_words = []
    for idx, p in enumerate(st.session_state.players):
        if idx != st.session_state.impostor_index:
            candidate_words.extend(p["words"])

    st.session_state.secret_word = random.choice(candidate_words)
    st.session_state.show_role = False
    st.session_state.step = "reveal"

def parse_words(text):
    words = re.split(r"[,;\n]+", text)
    return [w.strip() for w in words if w.strip()]


# ------------------------------------------------------------
#                     PANTALLA 1 – CONFIGURACIÓN
# ------------------------------------------------------------

def ui_config():
    st.title("🎭 Juego del Impostor")

    st.markdown("""
    *Cómo se juega*  
    - Cada jugador escribe su nombre y 5–10 palabras (de uno en uno).  
    - En cada ronda:  
      ✔ Se elige un impostor  
      ✔ Se elige una palabra que NO haya puesto el impostor  
      ✔ Todos la ven excepto el impostor  
    """)

    st.session_state.num_players = st.number_input(
        "Número de jugadores:", 
        min_value=3, max_value=15, step=1,
        value=st.session_state.num_players
    )

    if st.button("Continuar ➜"):
        st.session_state.players = [
            {"name": "", "words": []}
            for _ in range(st.session_state.num_players)
        ]
        st.session_state.current_player_input = 0
        st.session_state.step = "words"


# ------------------------------------------------------------
#                  PANTALLA 2 – NOMBRES Y PALABRAS (UNO A UNO)
# ------------------------------------------------------------

def ui_words():
    idx = st.session_state.current_player_input
    total = st.session_state.num_players

    st.header(f"Jugador {idx+1} de {total}")

    name = st.text_input("Introduce tu nombre:", key="name_input")

    words_raw = st.text_area(
        "Escribe entre 5 y 10 palabras (separadas por comas o saltos de línea):",
        key="words_input",
        height=120
    )

    if st.button("Guardar y continuar ➜"):
        words = parse_words(words_raw)
        if len(words) < 5 or len(words) > 10:
            st.error("Debes introducir entre 5 y 10 palabras.")
            return

        st.session_state.players[idx]["name"] = name.strip() or f"Jugador {idx+1}"
        st.session_state.players[idx]["words"] = words

        # Siguiente jugador
        st.session_state.current_player_input += 1

        if st.session_state.current_player_input >= total:
            new_round()
        else:
            st.session_state.name_input = ""
            st.session_state.words_input = ""
            st.rerun()


# ------------------------------------------------------------
#               PANTALLA 3 – MOSTRAR ROLES POR JUGADOR
# ------------------------------------------------------------

def ui_reveal():
    st.header("🔍 Revelación de roles")

    players = st.session_state.players
    names = [p["name"] for p in players]

    selected = st.selectbox("Selecciona tu nombre:", names)

    # Mostrar rol solo si se pulsa el botón
    if st.button("👀 Ver mi rol"):
        st.session_state.show_role = True

    if st.session_state.show_role:
        idx = names.index(selected)
        st.markdown("---")

        if idx == st.session_state.impostor_index:
            st.subheader("😈 ERES EL IMPOSTOR")
            st.write("No conoces la palabra.")
        else:
            st.subheader("🗝️ Tu palabra secreta es:")
            st.markdown(f"# *{st.session_state.secret_word}*")

        st.markdown("---")
        if st.button("➡️ Continuar"):
            st.session_state.show_role = False
            st.rerun()

    st.markdown("---")

    if st.button("🔄 Nueva ronda"):
        new_round()

    if st.button("🔁 Reiniciar partida"):
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


if __name__ == "__main__":
    main()
    main()

