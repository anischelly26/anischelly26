from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from src.coach_agent import PadelCoachAgent
from src.movement_database import MovementDatabase, PHASES
from src.pose_analyzer import PoseAnalyzer
from src.rules_database import RulesDatabase


st.set_page_config(
    page_title="PadelVision AI",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .stApp { background: #0d0f12; color: #f4f6f8; }
      [data-testid="stSidebar"] { background: #15181d; border-right: 1px solid #292d33; }
      .hero { padding: 1.2rem 0 1.6rem 0; }
      .hero h1 { font-size: 2.55rem; margin-bottom: .35rem; letter-spacing: -0.04em; }
      .hero p { color: #aeb6c2; font-size: 1.05rem; max-width: 830px; }
      .brand-dot { color: #39d98a; }
      .panel {
        background: #15181d; border: 1px solid #292d33; border-radius: 18px;
        padding: 1.15rem 1.25rem; margin-bottom: 1rem;
      }
      .status-pill {
        display: inline-block; padding: .27rem .6rem; border-radius: 999px;
        background: #173326; color: #73e3ac; font-size: .78rem; margin: 0 .35rem .35rem 0;
      }
      .muted { color: #9ca5b1; }
      div[data-testid="stMetric"] {
        background: #15181d; border: 1px solid #292d33; padding: 12px 15px; border-radius: 14px;
      }
      .stButton button, .stDownloadButton button { border-radius: 12px; font-weight: 700; }
      [data-testid="stChatMessage"] { border-radius: 16px; padding: .55rem .75rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_movement_database() -> MovementDatabase:
    return MovementDatabase()


@st.cache_resource
def get_rules_database() -> RulesDatabase:
    return RulesDatabase()


@st.cache_resource
def get_agent() -> PadelCoachAgent:
    return PadelCoachAgent(get_movement_database(), get_rules_database())


movement_db = get_movement_database()
rules_db = get_rules_database()
agent = get_agent()

for key, default in {
    "report": None,
    "annotated_video": None,
    "chat_messages": [],
    "pending_prompt": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


with st.sidebar:
    st.markdown("## 🎾 PadelVision")
    st.caption("Video strategy analysis + AI coaching + official rules")
    st.divider()

    stroke = st.selectbox(
        "Stroke to analyse",
        movement_db.strokes,
        index=movement_db.strokes.index("Forehand Groundstroke") if "Forehand Groundstroke" in movement_db.strokes else 0,
    )
    handedness = "Right"
    st.info("Current movement reference: right-handed player")
    camera_view = st.selectbox(
        "Camera position",
        ["Behind player", "Front of player"],
        help="A stable rear view is recommended for the current prototype.",
    )
    motion_threshold = st.slider("Movement sensitivity", 0.01, 0.12, 0.04, 0.01)

    st.divider()
    st.markdown("### AI Coach")
    advanced_mode = st.toggle("Advanced LLM mode", value=False)
    api_key = ""
    model = "gpt-4.1-mini"
    if advanced_mode:
        api_key = st.text_input("OpenAI API key", type="password", help="Used only in this running app session.")
        model = st.text_input("Model", value="gpt-4.1-mini")
    st.caption("The local coach works without an API key. Advanced mode improves free-form conversation.")

    st.divider()
    st.markdown('<span class="status-pill">Movement DB connected</span>', unsafe_allow_html=True)
    st.markdown('<span class="status-pill">FIP rules connected</span>', unsafe_allow_html=True)
    st.caption(f"{len(movement_db.references):,} movement reference rows")
    st.caption(rules_db.version_label)


st.markdown(
    """
    <div class="hero">
      <h1>Your AI padel coach<span class="brand-dot">.</span></h1>
      <p>PadelVision analyses the movement privately, then gives you a strategic coaching report: what the overall pattern is causing, what to do differently in a match, how to rebuild the movement, and how to train it.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

analyze_tab, coach_tab, knowledge_tab = st.tabs(["Analyze", "AI Coach", "Knowledge"])


with analyze_tab:
    uploaded_file = st.file_uploader(
        "Upload a short video containing one complete stroke",
        type=["mp4", "mov", "avi", "m4v"],
    )

    if uploaded_file:
        left, right = st.columns([1.25, 1])
        with left:
            st.video(uploaded_file.getvalue())
        with right:
            st.markdown(
                """
                <div class="panel">
                  <b>Best recording setup</b><br><br>
                  <span class="muted">One player · full body visible · stable camera · one complete stroke · 3–10 seconds</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            analyze_clicked = st.button("Analyze my movement", type="primary", use_container_width=True)

        if analyze_clicked:
            suffix = Path(uploaded_file.name).suffix or ".mp4"
            progress = st.progress(0, text="Preparing analysis...")
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    input_path = Path(tmpdir) / f"input{suffix}"
                    output_path = Path(tmpdir) / "padelvision_annotated.mp4"
                    input_path.write_bytes(uploaded_file.getvalue())

                    progress.progress(10, text="Loading pose model and movement knowledge...")
                    analyzer = PoseAnalyzer(database=movement_db)
                    progress.progress(25, text="Reading the movement frame by frame...")
                    report = analyzer.process_video(
                        input_path=input_path,
                        output_path=output_path,
                        handedness=handedness.lower(),
                        stroke=stroke,
                        camera_view=camera_view,
                        motion_threshold=motion_threshold,
                    )
                    progress.progress(90, text="Turning the movement analysis into a match strategy...")
                    st.session_state.report = report
                    st.session_state.annotated_video = output_path.read_bytes() if output_path.exists() else None
                    st.session_state.chat_messages = [{"role": "assistant", "content": agent.welcome(report)}]
                    progress.progress(100, text="Analysis complete.")
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")

    report = st.session_state.report
    if report:
        st.divider()
        if report["detection_rate"] < 0.65:
            st.warning(
                "This recording was not tracked reliably enough for a strong strategy analysis. "
                "Re-record with the full body visible and a stable camera."
            )
        else:
            st.success("Video analysed. The movement data has been converted into a player-facing strategy.")

        st.markdown(agent.strategy_analysis(report))

        if st.session_state.annotated_video:
            st.download_button(
                "Download analysed video",
                data=st.session_state.annotated_video,
                file_name="PadelVision_analysed.mp4",
                mime="video/mp4",
                use_container_width=True,
            )

        st.caption(
            "The body-point and binary comparison remain internal. "
            "They are used only to identify the movement pattern and generate the strategy above."
        )


with coach_tab:
    report = st.session_state.report
    st.markdown("### PadelVision Coach")
    st.caption("Ask about your video strategy, match decisions, technique, training drills, or the official rules of padel.")

    q1, q2, q3, q4 = st.columns(4)
    if q1.button("Give me my strategy", use_container_width=True):
        st.session_state.pending_prompt = "Give me the complete strategy analysis from my latest video."
    if q2.button("Match plan", use_container_width=True):
        st.session_state.pending_prompt = "Based on my latest video, what match strategy should I use until I fix the movement?"
    if q3.button("Is my serve legal?", use_container_width=True):
        st.session_state.pending_prompt = "What are the rules for a legal padel serve?"
    if q4.button("Explain padel scoring", use_container_width=True):
        st.session_state.pending_prompt = "Explain the official padel scoring options."

    if not st.session_state.chat_messages:
        st.session_state.chat_messages = [{"role": "assistant", "content": agent.welcome(report)}]

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    typed_question = st.chat_input("Ask your padel coach...")
    question = typed_question or st.session_state.pending_prompt
    st.session_state.pending_prompt = None

    if question:
        st.session_state.chat_messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking like a padel coach..."):
                answer = agent.answer(
                    question,
                    report=report,
                    history=st.session_state.chat_messages,
                    api_key=api_key if advanced_mode else None,
                    model=model if advanced_mode else None,
                )
                st.markdown(answer)
        st.session_state.chat_messages.append({"role": "assistant", "content": answer})


with knowledge_tab:
    technique_subtab, rules_subtab = st.tabs(["Technique strategy", "Official rules"])

    with technique_subtab:
        st.markdown("### How PadelVision uses the movement database")
        st.markdown(
            """
            The movement database works **behind the scenes**. It helps the AI identify where a stroke pattern
            becomes less efficient, but the player is not shown raw landmarks, binary directions, or body-point tables.

            After a video is analysed, the coach converts the internal comparison into:

            **Movement pattern → Tactical consequence → Match strategy → Rebuild sequence → Drill**

            This keeps the feedback useful on court instead of overwhelming the player with technical data.
            """
        )
        st.info(
            "The current movement reference remains prototype coaching data and should be validated with qualified padel coaches before being treated as universal ground truth."
        )

    with rules_subtab:
        st.markdown("### Official FIP rules knowledge")
        st.success(rules_db.version_label)
