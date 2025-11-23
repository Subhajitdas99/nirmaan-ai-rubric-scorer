import streamlit as st
from app.rubric_scoring import score_transcript_full

st.set_page_config(
    page_title="Spoken Communication Scorer",
    page_icon="🎤",
    layout="centered",
)

st.title("🎤 Spoken Communication Scorer")
st.write("Paste the transcript and enter the audio duration (seconds), then click **Score**.")

# --- Inputs ---
transcript = st.text_area(
    "Transcript",
    height=260,
    placeholder="Paste the self-introduction transcript here...",
)

duration_sec = st.number_input(
    "Duration (seconds)",
    min_value=1,
    value=52,
    step=1,
)

if st.button("Score", type="primary"):
    if not transcript.strip():
        st.warning("Please paste a transcript first.")
    else:
        with st.spinner("Scoring transcript..."):
            result = score_transcript_full(transcript, duration_sec)

        st.divider()
        st.subheader("Results")

        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(
                f"Words: **{result['words']}** · "
                f"Duration: **{int(result['duration_sec'])}s** · "
                f"WPM: **{result['wpm']}**"
            )
            st.caption(
                f"Base rubric score: **{result['base_rubric_score']}** · "
                f"Semantic (0–10): **{result['semantic_score_0_10']}**"
            )
        with col2:
            st.metric("Overall Score", f"{result['overall_score']} / 100")

        # Table of criteria
        st.write("### Criterion Breakdown")
        crit_rows = []
        for c in result["criteria"]:
            crit_rows.append(
                {
                    "Criterion": c["criterion"],
                    "Score": f"{c['score']} / {c['max_score']}",
                    "Detail": c["detail"],
                }
            )

        st.dataframe(
            crit_rows,
            use_container_width=True,
        )
