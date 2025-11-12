import streamlit as st
import json
from agents.agents import corpus_collector, corpus_analyzer, gap_identifier, topic_generator


# ---------------------- Sidebar -----------------------------
st.sidebar.title("Settings")

### Available models
model_options = {
    "OpenAI": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    "Anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
    "Mistral": ["mistral-large", "mistral-medium", "mistral-small"],
    "Groq": ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "meta-llama/llama-guard-4-12b", "openai/gpt-oss-20b", "moonshotai/kimi-k2-instruct-0905"],
    "Ollama": ["kimi-k2-thinking:cloud"]
}

provider = st.sidebar.selectbox("Model Provider", list(model_options.keys()))
model = st.sidebar.selectbox("Model Name", model_options[provider])
research_level = st.sidebar.selectbox(
    "Research Level", ["Undergraduate", "Masters", "PhD"], 
    help= (
        "This helps the agents tailor the complexity and depth of the research topics generated."
    )
)
temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.05,
    help="Lower = more deterministic, Higher = more creative"
)

st.sidebar.caption("Adjust these settings to control how your agents respond.")
st.sidebar.markdown("---")

# ------------------------------ Main -------------------------------------
st.markdown(
    "<h1 style='text-align: center;'>Quest0</h1>",
    unsafe_allow_html=True
)
st.write("Enter a research domain or topic, and let the agents uncover gaps and suggest novel research ideas.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Describe your research area of interest"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ------------ Pipeline Execution ----------------
    with st.chat_message("assistant"):
        st.markdown("**Running agents...**")

        # corpus collector
        with st.spinner("Collecting recent papers and articles..."):
            corpus_json = corpus_collector(
                domain=prompt,
                provider=provider.lower(),
                model=model,
                temperature=temperature
            )
        
        # Parse JSON safely (extract outside expander for history)
        try:
            corpus_data = json.loads(corpus_json).get("corpus", [])
        except (json.JSONDecodeError, AttributeError):
            corpus_data = []
            st.error("Failed to parse corpus data. The output may not be valid JSON.")
        
        with st.expander("Corpus Collector Output", expanded=False):
            st.markdown("### Corpus Collected")
            st.markdown("---")
            
            if corpus_data:
                for i, paper in enumerate(corpus_data, 1):
                    st.markdown(f"**{i}. {paper.get('title', 'Untitled')}**")
                    st.markdown(
                        f"""
                        - **Authors:** {paper.get('authors', 'N/A')}
                        - **Year:** {paper.get('year', 'N/A')}
                        - **Source:** {paper.get('source', 'N/A')}
                        - **Abstract:** {paper.get('abstract', 'No abstract available.')}
                        - **URL:** [View Paper]({paper.get('url', '#')})
                        """
                    )
                st.divider()
            else:
                st.info("No papers or articles found in the corpus.")

        # corpus analyzer
        with st.spinner("Analyzing collected corpus..."):
            analyzed_json = corpus_analyzer(
                corpus_json=corpus_json,
                provider=provider.lower(),
                model=model,
                temperature=temperature
            )

        # Parse analyzed data (extract outside expander for history)
        try:
            analyzed_data = json.loads(analyzed_json)
            themes = analyzed_data.get("themes", [])
            emerging_trends = analyzed_data.get("emerging_trends", [])
            common_limitations = analyzed_data.get("common_limitations", [])
        except (json.JSONDecodeError, AttributeError):
            themes, emerging_trends, common_limitations = [], [], []
            st.error("Failed to parse data. The output may not be valid JSON.")

        with st.expander("Corpus Analyzer Output", expanded=False):

            if themes:
                st.subheader("Identified Themes")
                for i, theme in enumerate(themes, 1):
                    with st.container():
                        st.markdown(f"**{i}. {theme.get('name', 'Unnamed Theme')}**")
                        st.markdown(
                            f"""
                            - **Summary:** {theme.get('summary', 'No summary available.')}
                            - **Representative Papers:** {', '.join(theme.get('representative_papers', []) or ['N/A'])}
                            """
                        )
                st.divider()

            if emerging_trends:
                st.subheader("Emerging Trends")
                for i, trend in enumerate(emerging_trends, 1):
                    st.markdown(f"- {trend}")

            if common_limitations:
                st.subheader("Common Limitations")
                for i, limitation in enumerate(common_limitations, 1):
                    st.markdown(f"- {limitation}")
            

            if not (themes or emerging_trends or common_limitations):
                st.warning("No structured analysis found in the output.")
             

        # research gap identifier
        with st.spinner("Identifying research gaps..."):
            gaps_json = gap_identifier(
                analysis_summary=analyzed_json,
                provider=provider.lower(),
                model=model,
                temperature=temperature
            )

        # Parse gaps data (extract outside expander for history)
        try:
            gaps_data = json.loads(gaps_json)
            research_gaps = gaps_data.get("research_gaps", [])
        except (json.JSONDecodeError, AttributeError):
            research_gaps = []
            st.error("Failed to parse data. The output may not be valid JSON.")

        with st.expander("Research Gap Identifier Output", expanded=False):
            if research_gaps:
                st.subheader("Identified Research Gaps")
                for i, gap in enumerate(research_gaps, 1):
                    with st.container():
                        st.markdown(f"**{i}. {gap.get('gap_title', 'Untitled Gap')}**")
                        st.markdown(
                            f"""
                            - **Description:** {gap.get('description', 'No description available.')}
                            - **Evidence from Analysis:** {gap.get('evidence_from_analysis', 'N/A')}
                            - **Potential Impact:** {gap.get('potential_impact', 'N/A')}
                            """
                        )
                st.divider()
            else:
                st.warning("No research gaps identified in the output.")


        # Research Topic Generator
        with st.spinner("Generating potential research topics..."):
            topics_json = topic_generator(
                research_gaps=gaps_json,
                research_level=research_level,
                provider=provider.lower(),
                model=model,
                temperature=temperature
            )
        
        # Parse topics data (extract outside display for history)
        try:
            topics_data = json.loads(topics_json).get("research_topics", [])
        except (json.JSONDecodeError, AttributeError):
            topics_data = []
            st.error("Failed to parse research topics. The output may not be valid JSON.")

        st.markdown("### Suggested Research Topics")

        if topics_data:
            for i, topic in enumerate(topics_data, 1):
                with st.container():
                    st.markdown(f"#### {i}. {topic.get('topic_title', 'Untitled Topic')}")
                    st.markdown(
                    f"""
                    - **Research Question:** {topic.get('research_question', 'N/A')}
                    - **Motivation:** {topic.get('motivation', 'N/A')}
                    - **Suggested Methodology:** {topic.get('suggested_methodology', 'N/A')}
                    - **Expected Contribution:** {topic.get('expected_contribution', 'N/A')}
                    """,
                    unsafe_allow_html=True,
                )
                    
        else:
            st.info("No research topics found in the output.")
        st.markdown("---")

        # Build comprehensive response for chat history
        response_parts = ["**Research Analysis Pipeline Completed**\n\n"]
        
        # Add corpus summary
        if corpus_data:
            response_parts.append(f"### Corpus Collected\n{len(corpus_data)} papers/articles found.\n\n")
        
        # Add themes summary
        if themes:
            response_parts.append("### Identified Themes\n")
            for i, theme in enumerate(themes, 1):
                response_parts.append(f"**{i}. {theme.get('name', 'Unnamed Theme')}**\n")
                response_parts.append(f"- Summary: {theme.get('summary', 'No summary available.')}\n")
            response_parts.append("\n")
        
        # Add emerging trends
        if emerging_trends:
            response_parts.append("### Emerging Trends\n")
            for trend in emerging_trends:
                response_parts.append(f"- {trend}\n")
            response_parts.append("\n")
        
        # Add common limitations
        if common_limitations:
            response_parts.append("### Common Limitations\n")
            for limitation in common_limitations:
                response_parts.append(f"- {limitation}\n")
            response_parts.append("\n")
        
        # Add research gaps
        if research_gaps:
            response_parts.append("### Identified Research Gaps\n")
            for i, gap in enumerate(research_gaps, 1):
                response_parts.append(f"**{i}. {gap.get('gap_title', 'Untitled Gap')}**\n")
                response_parts.append(f"- Description: {gap.get('description', 'No description available.')}\n")
                response_parts.append(f"- Potential Impact: {gap.get('potential_impact', 'N/A')}\n\n")
        
        # Add research topics
        if topics_data:
            response_parts.append("### Suggested Research Topics\n")
            for i, topic in enumerate(topics_data, 1):
                response_parts.append(f"**{i}. {topic.get('topic_title', 'Untitled Topic')}**\n")
                response_parts.append(f"- Research Question: {topic.get('research_question', 'N/A')}\n")
                response_parts.append(f"- Motivation: {topic.get('motivation', 'N/A')}\n")
                response_parts.append(f"- Suggested Methodology: {topic.get('suggested_methodology', 'N/A')}\n")
                response_parts.append(f"- Expected Contribution: {topic.get('expected_contribution', 'N/A')}\n\n")
        else:
            response_parts.append("No research topics were generated.\n")

        # Build final response message
        full_response = "".join(response_parts)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})