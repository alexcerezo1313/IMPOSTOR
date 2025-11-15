import streamlit as st
import random
import re

# ---------- INIT STATE ----------
if "step" not in st.session_state:
    st.session_state.step = "config"   # "config" -> "words" -> "reveal"
if "num_players" not in st.session_state:
    st.session_state.num_players = 3
if "players" not in st.session_state:
    st.session_state.players = []
if "impostor_index" not in st.session_state:
    st.session_state.impostor_index = None
if "secret_word" not in st.session_state:
    st.session_state.secret_word = None


# ---------- HELPERS ----------

def reset_game():
    st.session_state.step = "config"
    st.session_state.num_players = 3
    st.session_state.players = []
    st.session_state.impostor_index = None
    st.session_state.secret_word = None


def parse_words(raw_text):
    """Convierte el texto en lista de palabras separadas por coma o salto de línea."""
    if not raw_text:
        return []
    parts = re.split(r"[,;\n]+", raw_text)
    return [p.strip() for p in parts if p.strip()]


# ---------- UI PANTALLA 1: CONFIGURACIÓN ----------

def ui_config():
    st.title("🎭 Juego del Impostor (Streamlit)")

    st.markdown(
        """
        *Cómo funciona:*
        1. Elige cuántos jugadores sois (3 a 15).
        2. Cada jugador escribe su nombre y *5–10 palabras*.
        3. El juego elige un impostor en secreto.
        4. Se elige una palabra que:
           - La ven todos menos el impostor.
           - *NO puede ser* una palabra escrita por el impostor.
        """
    )

    st.session_state.num_players = st.number_input(
        "Número de jugadores:",
        min_value=3,
        max_value=15,
        value=st.session_state.num_players,
        step=1,
    )

    if st.button("Continuar ➜"):
        st.session_state.players = [
            {"name": f"Jugador {i+1}", "words": []}
            for i in range(st.session_state.num_players)
        ]
        st.session_state.step = "words"


# ---------- UI PANTALLA 2: NOMBRES Y PALABRAS ----------

def ui_words():
    st.header("👥 Nombres y palabras de los jugadores")

    st.markdown("Cada jugador debe escribir *5–10 palabras* separadas por comas o saltos de línea.")

    num_players = st.session_state.num_players

    for i in range(num_players):
        st.subheader(f"Jugador {i+1}")

        name_key = f"name_{i}"
        words_key = f"words_{i}"

        # Nombre
        name_value = st.session_state.players[i]["name"]
        name = st.text_input(f"Nombre del jugador {i+1}:", value=name_value, key=name_key)

        # Palabras
        default_words = ", ".join(st.session_state.players[i]["words"])
        words_input = st.text_area(
            f"Palabras de {name}:",
            value=default_words,
            key=words_key,
            height=80,
        )

    error_placeholder = st.empty()

    if st.button("Crear partida ➜"):
        players = []
        valid = True

        for i in range(num_players):
            name = st.session_state.get(f"name_{i}", "").strip()
            if not name:
                name = f"Jugador {i+1}"

            words_raw = st.session_state.get(f"words_{i}", "")
            words = parse_words(words_raw)

            if len(words) < 5 or len(words) > 10:
                error_placeholder.error(
                    f"❌ El jugador {name} debe escribir entre 5 y 10 palabras. "
                    f"(Ahora tiene {len(words)})"
                )
                valid = False
                break

            players.append({"name": name, "words": words})

        if not valid:
            return

        st.session_state.players = players

        # Elegir impostor aleatorio
        impostor_index = random.randint(0, num_players - 1)
        st.session_state.impostor_index = impostor_index

        # Crear lista de palabras posibles (solo de jugadores NO impostores)
        candidate_words = []
        for idx, p in enumerate(players):
            if idx != impostor_index:
                candidate_words.extend(p["words"])

        if not candidate_words:
            error_placeholder.error("❌ No hay palabras válidas. Revisa la lista.")
            return

        st.session_state.secret_word = random.choice(candidate_words)
        st.session_state.step = "reveal"


# ---------- UI PANTALLA 3: REVELAR ROLES ----------

def ui_reveal():
    st.header("🔍 Revelación de roles")

    players = st.session_state.players
    impostor_index = st.session_state.impostor_index
    secret_word = st.session_state.secret_word

    st.markdown(
        """
        👉 *Instrucciones:*
        - Todos miran hacia otro lado.
        - Cada jugador selecciona su nombre y pulsa *“Ver mi rol”*.
        - Solo ese jugador mira la pantalla.
        """
    )

    names = [p["name"] for p in players]
    selected_name = st.selectbox("Selecciona tu nombre:", names)
    index = names.index(selected_name)

    if st.button("Ver mi rol"):
        st.markdown("---")
        if index == impostor_index:
            st.subheader("😈 Eres el IMPOSTOR")
            st.write("No conoces la palabra. Intenta pasar desapercibido.")
        else:
            st.subheader("🗝️ Tu palabra secreta es:")
            st.markdown(f"# *{secret_word}*")
            st.write("Todos los demás (menos el impostor) tienen esta palabra.")

    st.markdown("---")

    if st.button("🔁 Reiniciar partida"):
        reset_game()


# ---------- MAIN ----------

def main():
    st.sidebar.button("🔁 Reiniciar juego", on_click=reset_game)

    step = st.session_state.step

    if step == "config":
        ui_config()
    elif step == "words":
        ui_words()
    elif step == "reveal":
        ui_reveal()


if _name_ == "_main_":
    main()
