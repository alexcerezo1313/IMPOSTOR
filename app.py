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

if "impostor_index" not in st.session_state:
    st.session_state.impostor_index = None

if "secret_word" not in st.session_state:
    st.session_state.secret_word = None

if "step" not in st.session_state:
    st.session_state.step = "config"   # config → words → reveal

# ------------------------------------------------------------
#                        FUNCIONES ÚTILES
# ------------------------------------------------------------

def reset_game():
    st.session_state.players = []
    st.session_state.num_players = 3
    st.session_state.impostor_index = None
    st.session_state.secret_word = None
    st.session_state.step = "config"

def new_round():
    """Crea un impostor y una palabra nueva sin borrar jugadores."""
    num_players = len(st.session_state.players)

    # Elegir impostor nuevo aleatorio
    st.session_state.impostor_index = random.randint(0, num_players - 1)

    # Crear lista de palabras válidas (solo de NO impostores)
    candidate_words = []
    for idx, p in enumerate(st.session_state.players):
        if idx != st.session_state.impostor_index:
            candidate_words.extend(p["words"])

    st.session_state.secret_word = random.choice(candidate_words)

    # Ir directamente a la pantalla de revelación
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
    - Cada jugador escribe su nombre  
    - Cada jugador aporta 5–10 palabras  
    - En cada ronda:  
      ✔ Se elige un impostor  
      ✔ Se elige una palabra que NO haya puesto el impostor  
      ✔ Todos ven la palabra menos el impostor  
    """)

    st.session_state.num_players = st.number_input(
        "Número de jugadores:", 
        min_value=3, max_value=15, value=st.session_state.num_players, step=1
    )

    if st.button("Continuar ➜ Introducir nombres y palabras"):
        st.session_state.players = [
            {"name": f"Jugador {i+1}", "words": []}
            for i in range(st.session_state.num_players)
        ]
        st.session_state.step = "words"

# ------------------------------------------------------------
#                  PANTALLA 2 – NOMBRES Y PALABRAS
# ------------------------------------------------------------

def ui_words():
    st.header("👥 Jugadores y palabras")

    for i in range(st.session_state.num_players):
        st.subheader(f"Jugador {i+1}")

        # Nombre
        st.session_state.players[i]["name"] = st.text_input(
            f"Nombre del jugador {i+1}",
            value=st.session_state.players[i]["name"],
            key=f"name_{i}"
        )

        # Palabras
        raw_words = st.text_area(
            f"Palabras de {st.session_state.players[i]['name']} (5–10)",
            value=", ".join(st.session_state.players[i]["words"]),
            key=f"words_{i}",
            height=80
        )

    if st.button("Crear partida ➜"):
        # Validar todo
        for i in range(st.session_state.num_players):
            words = parse_words(st.session_state.get(f"words_{i}", ""))
            if len(words) < 5 or len(words) > 10:
                st.error(f"❌ El jugador {i+1} debe poner entre 5 y 10 palabras.")
                return
            st.session_state.players[i]["words"] = words

        # Crear primera ronda
        new_round()

# ------------------------------------------------------------
#               PANTALLA 3 – MOSTRAR ROLES POR JUGADOR
# ------------------------------------------------------------

def ui_reveal():
    st.header("🔍 Revelación de roles")

    players = st.session_state.players
    names = [p["name"] for p in players]

    selected = st.selectbox("Selecciona tu nombre:", names)

    if st.button("Ver mi rol"):
        idx = names.index(selected)

        st.markdown("---")

        if idx == st.session_state.impostor_index:
            st.subheader("😈 ERES EL IMPOSTOR")
            st.write("No conoces la palabra. Intenta no levantar sospechas.")
        else:
            st.subheader("🗝️ Tu palabra secreta es:")
            st.markdown(f"# *{st.session_state.secret_word}*")

    st.markdown("---")

    # Nueva ronda sin borrar jugadores
    if st.button("🔄 Nueva ronda"):
        new_round()

    # Reinicio total
    if st.button("🔁 Reiniciar partida"):
        reset_game()

# ------------------------------------------------------------
#                            MAIN
# ------------------------------------------------------------

def main():
    st.sidebar.button("🔁 Reiniciar Juego", on_click=reset_game)

    if st.session_state.step == "config":
        ui_config()
    elif st.session_state.step == "words":
        ui_words()
    elif st.session_state.step == "reveal":
        ui_reveal()

# 🔥 ESTA ES LA LÍNEA QUE TE FALLABA — AHORA ESTÁ PERFECTA
if __name__ == "__main__":

    main()
