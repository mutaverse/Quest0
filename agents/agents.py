import json
import sys
import os
from datetime import datetime
from aisuite import Client
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.arxiv_search import arxiv_search_tool
from tools.web_search import tavily_search_tool
load_dotenv('.env')


today = datetime.now().strftime("%Y-%m-%d")

client = Client()


# Corpus Collector Agent
def corpus_collector(domain: str, provider: str, model: str, temperature: float = 1.0):
    """
    Collects corpus (research papers and relevant articles) from sources.
    """

    user_prompt = f"""
    You are a research assistant specializing in academic data collection.

    Your task:
    Given a research domain or topic of interest, use the available tools 
    (arxiv_search_tool: academic papers, and tavily_search_tool: general web search)
    to retrieve the most relevant and recent papers or articles.

    Research domain: {domain}
    Today is {today}

    OUTPUT FORMAT (STRICT):
    A valid JSON array named "corpus" where each element contains:
        {{
        "title": "...",
        "authors": "...",
        "year": "...",
        "abstract": "...",
        "source": "arxiv" | "web",
        "url": "..."
    }}

    HARD CONSTRAINTS
     - Do NOT include any explanation, commentary, or markdown.
     - Avoid duplicate entries (match by title).
     - Always include publication year and source.
     - Only return JSON output (no prose before or after).
     - Prioritize literature published within the last 5 years (from 2020 to {today[:4]}),
     as recent studies best reflect current trends and research gaps.
     - However, if a topic is theoretical or foundational, include older **seminal** works 
    that are frequently cited or historically important.
     - Always balance **recency** and **relevance** over quantity.
    """.strip()

    # Build the agent
    messages = [{"role": "user", "content": user_prompt}]

    tools = [arxiv_search_tool, tavily_search_tool]

    try:
        response = client.chat.completions.create(
            model=f"{provider}:{model}",
            messages=messages,
            tools=tools,
            tool_choice = "auto",
            temperature=temperature,
            max_turns=5
        )
        content = response.choices[0].message.content
        return content
    except Exception as e:
        return f"[Model Error: {e}]"

# Corpus Analyzer Agent
def corpus_analyzer(corpus_json: json, provider: str, model: str, temperature: float = 1.0):
    """
    Analyzes research corpus into thematic concepts
    """
    user_prompt = f"""
    You are an AI research analyst skilled in literature review.

    Your task:
    Analyze the following list of papers (titles, abstracts, metadata) and extract key
    themes, trends, and areas of focus.

    INPUT:
    {corpus_json}

    OUTPUT FORMAT (STRICT):
    A valid JSON object with these fields:
        {{
        "themes": [
            {{
                "name": "Explainable AI in healthcare imaging",
                "summary": "Recent works focus on interpretability of CNNs for radiology...",
                "representative_papers": ["Paper Title 1", "Paper Title 2", ...] 
            }},
            ...
        ],
        "emerging_trends": [
            "Shift from model interpretability to human trust calibration",
            "Integration of LLMs into medical reasoning pipelines"
        ],
        "common_limitations": [
            "Lack of patient-centric validation",
            "Overreliance on synthetic datasets"
        ]
    }}

    HARD CONSTRAINTS:
    - Use concise summaries (under 200 words per theme).
    - Each theme must include at least one representative paper title.
    - Do NOT generate new facts beyond what the corpus implies.
    - Only output the JSON object (no prose or markdown).
    """.strip()

    messages = [{"role": "user", "content": user_prompt}]

    try:
        response = client.chat.completions.create(
            model=f"{provider}:{model}",
            messages=messages,
            temperature=temperature,
            max_turns=5
        )
        content = response.choices[0].message.content
        return content
    except Exception as e:
        return f"[Model Error: {e}]"
    

# Research Gap Identifier Agent
def gap_identifier(analysis_summary: json, provider: str, model: str, temperature: float = 1.0):
    """
    Analyzes research report into thematic concepts.
    """

    user_prompt = f"""
    You are an AI research strategist.

    Your task:
    Using the following analysis summary,
    identify concrete research gaps in the domain.

    INPUT:
    {analysis_summary}

    OUTPUT FORMAT (STRICT):
    1. A valid JSON array named "research_gaps" where each element is:
       {{
       "gap_title": "Lack of interpretability in multimodal healthcare AI",
       "description": "Although recent work focuses on CNN explainability, there is limited research on interpretability for multimodal patient data.",
       "evidence_from_analysis": "Common limitation: lack of multimodal validation.",
       "potential_impact": "High — directly improves real-world trust and adoption."
        }} 
    
    2. Include at least 3 and at most 8 gaps.

    HARD CONSTRAINTS:
    - Derive every gap from provided analysis; do not invent unsupported claims.
    - Avoid vague language (“not enough research” → specify subtopic or method).
    - Return only JSON (no prose or markdown).
    - Keep each description under 150 words.
    """.strip()

    messages = [{"role": "user", "content": user_prompt}]

    try:
        response = client.chat.completions.create(
            model=f"{provider}:{model}",
            messages=messages,
            temperature=temperature,
            max_turns=5
        )
        content = response.choices[0].message.content
        return content
    except Exception as e:
        return f"[Model Error: {e}]"

# Research Top Generator Agent
def topic_generator(
        research_gaps: json,
        research_level: str,
        provider: str,
        model: str,
        focus_area: str = None,
        temperature: float = 1.0
):
    """
    Generates research topics
    """

    user_prompt = f"""
    You are an academic writing assistant specializing in research topic formulation.

    Your task:
    Given a list of identified research gaps and the user's research level or preference,
    propose well-structured and original research topics.

    INPUT:
    - Research gaps: {research_gaps}
    - Research level: {research_level}
    - Focus area preference: {focus_area}

    OUTPUT FORMAT (STRICT):
    1. A valid JSON array named "research_topics" where each element is:
    {{
       "topic_title": "Designing Trust-Aware Explainable AI Interfaces for Clinicians",
       "research_question": "How can explainable AI interfaces be optimized to enhance clinician trust in model recommendations?",
       "motivation": "Bridges human-AI trust gap in critical decision systems.",
       "suggested_methodology": "Mixed-methods study combining model interpretability metrics with clinician user testing.",
       "expected_contribution": "Framework for measuring and improving clinician trust in XAI systems."
   }}

   2. Include between 3 and 10 topics.

   HARD CONSTRAINTS:
   - Ensure each topic directly addresses a listed research gap.
   - Maintain logical flow (gap → question → method → contribution).
   - Use academic tone, concise phrasing
   - Output JSON only (no prose, no markdown).
    """.strip()

    messages = [{"role": "user", "content": user_prompt}]

    try:
        response = client.chat.completions.create(
            model=f"{provider}:{model}",
            messages=messages,
            temperature = temperature,
            max_turns=5
        )
        content = response.choices[0].message.content
        return content
    except Exception as e:
        return f"[Model Error: {e}]"
