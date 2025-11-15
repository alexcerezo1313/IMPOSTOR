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
    """
    Convierte un texto en una lista de palabras:
    - separadas por comas, punto y coma o saltos de línea
    - quita espacios y vacíos
    """
    if not raw_text:
        return []
    parts = re.split(r"[,;\n]+", raw_text)
    words = [p.strip() for p in parts if p.strip()]
    return words


# ---------- UI PANTALLA 1: CONFIGURACIÓN ----------

def ui_config():
    st.title("🎭 Juego del Impostor (Streamlit)")

    st.markdown(
        """
        *Cómo funciona:*
        1. Elige cuántos jugadores sois (3 a 15).
        2. Cada jugador escribirá su nombre y *5–10 palabras*.
        3. El juego elegirá *un impostor al azar*.
        4. Se elegirá una palabra que:
           - La verán *todos menos el impostor*.
           - *NO puede ser* una palabra escrita por el impostor.
        5. Cada jugador mira la pantalla por turnos para ver su rol.
        """
    )

    st.session_state.num_players = st.number_input(
        "Número de jugadores",
        min_value=3,
        max_value=15,
        step=1,
        value=st.session_state.num_players,
    )

    if st.button("Continuar ➜ Introducir nombres y palabras"):
        # Creamos estructura vacía de jugadores
        st.session_state.players = [
            {"name": f"Jugador {i+1}", "words": []}
            for i in range(st.session_state.num_players)
        ]
        st.session_state.step = "words"


# ---------- UI PANTALLA 2: NOMBRES Y PALABRAS ----------

def ui_words():
    st.header("👥 Nombres y palabras de los jugadores")

    st.markdown(
        """
        Para cada jugador:
        - Escribe su *nombre*.
        - Escribe *5 a 10 palabras*, separadas por comas o saltos de línea.
        """
    )

    num_players = st.session_state.num_players

    # Inputs dinámicos
    for i in range(num_players):
        st.subheader(f"Jugador {i+1}")
        name_key = f"name_{i}"
        words_key = f"words_{i}"

        # Nombre
        default_name = (
            st.session_state.players[i]["name"]
            if i < len(st.session_state.players)
            else f"Jugador {i+1}"
        )

        name = st.text_input(
            f"Nombre del jugador {i+1}",
            value=default_name,
            key=name_key,
        )

        # Palabras
        default_words_text = ""
        if st.session_state.players[i]["words"]:
            default_words_text = ", ".join(st.session_state.players[i]["words"])

        words_text = st.text_area(
            f"Palabras de {name or f'jugador {i+1}'} (5–10)",
            value=default_words_text,
            key=words_key,
            height=80,
        )

    error_placeholder = st.empty()

    if st.button("Guardar y crear partida ➜"):
        players = []
        valid = True
        msg_error = ""

        for i in range(num_players):
            name = st.session_state.get(f"name_{i}", "").strip()
            if not name:
                name = f"Jugador {i+1}"

            words_raw = st.session_state.get(f"words_{i}", "")
            words = parse_words(words_raw)

            if len(words) < 5 or len(words) > 10:
                valid = False
                msg_error = (
                    f"❌ El jugador {i+1} ({name}) debe escribir entre 5 y 10 palabras "
                    f"(ahora tiene {len(words)})."
                )
                break

            players.append({"name": name, "words": words})

        if not valid:
            error_placeholder.error(msg_error)
            return

        # Guardamos jugadores definitivos
        st.session_state.players = players

        # Elegimos impostor y palabra secreta
        num_players = len(players)
        impostor_index = random.randint(0, num_players - 1)

        # Palabras posibles para la pista: de todos menos del impostor
        candidate_words = []
        for idx, p in enumerate(players):
            if idx == impostor_index:
                continue
            candidate_words.extend(p["words"])

        if not candidate_words:
            error_placeholder.error(
                "❌ No hay palabras disponibles fuera de las escritas por el impostor. "
                "Revisa las listas."
            )
            return

        secret_word = random.choice(candidate_words)

        st.session_state.impostor_index = impostor_index
        st.session_state.secret_word = secret_word
        st.session_state.step = "reveal"


# ---------- UI PANTALLA 3: REVELAR ROLES ----------

def ui_reveal():
    st.header("🔍 Fase de revelación")

    players = st.session_state.players
    impostor_index = st.session_state.impostor_index
    secret_word = st.session_state.secret_word

    if impostor_index is None or secret_word is None:
        st.error("Ha ocurrido un error creando la partida. Reinicia el juego.")
        return

    st.markdown(
        """
        👉 *Instrucciones:*
        1. Todos miran hacia otro lado.
        2. Un jugador selecciona su nombre y pulsa *“Ver mi rol”*.
        3. Sólo ese jugador mira la pantalla.
        4. Después se oculta la pantalla o se pulsa otro nombre, y así sucesivamente.
        """
    )

    # Selector de jugador
    names = [p["name"] for p in players]
    selected_name = st.selectbox("Selecciona tu nombre:", names)
    selected_index = names.index(selected_name)

    if st.button("Ver mi rol"):
        st.markdown("---")
        if selected_index == impostor_index:
            st.subheader("😈 Eres el IMPOSTOR")
            st.write(
                "No conoces la palabra. Intenta pasar desapercibido mientras los "
                "demás hablan."
            )
        else:
            st.subheader("🗝️ Tu palabra secreta es:")
            st.markdown(f"# *{secret_word}*")
            st.write(
                "Todos los jugadores (excepto el impostor) tienen esta misma palabra."
            )

    st.markdown("---")
    if st.button("🔁 Reiniciar partida"):
        reset_game()


# ---------- MAIN ----------

def main():
    # Botón pequeño arriba a la derecha para reiniciar rápido
    st.sidebar.button("🔁 Reiniciar juego", on_click=reset_game)

    step = st.session_state.step

    if step == "config":
        ui_config()
    elif step == "words":
        ui_words()
    elif step == "reveal":
        ui_reveal()
    else:
        st.write("Estado desconocido, reiniciando...")
        reset_game()
        ui_config()


if _name_ == "__main__":
    main()