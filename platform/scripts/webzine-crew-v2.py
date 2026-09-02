#!/usr/bin/env python3
"""
Vital4Living Multi-Agent CrewAI Writing, Editorial, and Monetization Engine
Sprint 5/6 Expanded Implementation: Incorporating Advertising & Revenue Director Agent
Version-agnostic string model definitions to prevent Pydantic validation errors.
"""

import os
import sys
import json
from crewai import Agent, Task, Crew, Process

# ----------------------------------------------------------------------
# 1. ROUTING & LLM INITIALIZATION (LiteLLM Compatible Gateway)
# ----------------------------------------------------------------------
os.environ["OPENAI_API_BASE"] = os.getenv("OPENAI_API_BASE", "http://localhost:4000")
os.environ["OPENAI_API_KEY"] = os.getenv("LITELLM_MASTER_KEY", "sk-litellm-master-key")

# We pass these custom model name strings directly to CrewAI.
# Since CrewAI uses LiteLLM under the hood, and we have OPENAI_API_BASE 
# redirected to localhost:4000, CrewAI will call LiteLLM on port 4000, 
# which will then route them to Claude or DeepSeek perfectly!
premium_writer_llm = "premium-writer-llm"
cheap_llm = "cheap-llm"

# ----------------------------------------------------------------------
# 2. INPUT PAYLOAD EXTRACTION
# ----------------------------------------------------------------------
if len(sys.argv) < 2:
    print(json.dumps({
        "error": "Missing input payload. Usage: python webzine_crew_v2.py '<JSON_PAYLOAD_STRING>'"
    }))
    sys.exit(1)

try:
    payload = json.loads(sys.argv[1])
    target_topic = payload.get("topic_title", "Technical Field Analysis")
    target_persona = payload.get("persona", "Dex")
    evidence_package = payload.get("evidence_package", {})
    monetization_inventory = payload.get("monetization_inventory", [
        {
            "partner_name": "AvantLink - Salomon Outdoor",
            "monetization_type": "affiliate",
            "targeting_keywords": ["Mondo sizing", "DIN setting", "Salomon", "ski boots"],
            "destination_url": "https://partner.avantlink.com/click?merchantId=123&websiteId=456&url=https://www.salomon.com"
        },
        {
            "partner_name": "REI Co-op - Ultralight Gear",
            "monetization_type": "affiliate",
            "targeting_keywords": ["seam failure", "Dyneema", "ripstop", "backpack"],
            "destination_url": "https://rei.sjv.io/c/78910/f/backpacks?url=https://www.rei.com"
        },
        {
            "partner_name": "Premium Google AdSense - Mid Article PPC",
            "monetization_type": "ppc_ad_unit",
            "targeting_keywords": ["fabric denier", "torque specs", "hull geometry", "thermoregulation"],
            "ad_code_html": "<div class=\"v4l-ad-container\"><!-- AdsByGoogle --><ins class=\"adsbygoogle\" style=\"display:block; text-align:center;\" data-ad-layout=\"in-article\" data-ad-format=\"fluid\" data-ad-client=\"ca-pub-999999999\" data-ad-slot=\"1111111\"></ins><script>(adsbygoogle = window.adsbygoogle || []).push({});</script></div>"
        }
    ])
except Exception as e:
    print(json.dumps({"error": f"Invalid JSON payload: {str(e)}"}))
    sys.exit(1)

# ----------------------------------------------------------------------
# 3. DYNAMIC CONTRIBUTOR PERSONA ASSIGNMENT
# ----------------------------------------------------------------------
persona_bank = {
    "Sierra": {
        "role": "Sierra Marlowe - Fit & Sizing Standards Specialist",
        "goal": "Turn sizing, standards, geometry, and manufacturer specs into actionable fit choices.",
        "backstory": "An obsessive fit technician specializing in lasts, Mondo sizing, and volume profiles. Believes a size without a standard is pure marketing."
    },
    "Dex": {
        "role": "Dex Okafor - Outdoor Technology & Equipment Engineer",
        "goal": "Evaluate gear through specs, geometry, load ratings, and real-world durability.",
        "backstory": "A backcountry engineer who strips marketing fluff down to functional measurements, structural design, and field reliability."
    },
    "Wren": {
        "role": "Wren Calloway - Trail Physiology & Environmental Specialist",
        "goal": "Analyze physical performance, hydration, and altitude stress without giving false clinical certainty.",
        "backstory": "An outdoor physiology researcher focused on human adaptations, environmental strain, and clear safety-boundary analysis."
    },
    "Bo": {
        "role": "Bo Hartley - Materials & Gear Durability Analyst",
        "goal": "Break down fabric construction, seam failures, tear strength, and field repairability.",
        "backstory": "A used-gear inspector and materials expert who separates cosmetic wear from dangerous structural failure."
    },
    "Niko": {
        "role": "Niko Reyes - Setup & Field Tuning Technician",
        "goal": "Provide unambiguous mechanical setup instructions with distinct user vs technician boundaries.",
        "backstory": "A certified outdoor gear mechanic dedicated to proper torque, setup alignment, and field maintenance protocols."
    }
}

active_persona = persona_bank.get(target_persona, persona_bank["Dex"])

# Contributor Agent representing the dynamically loaded persona
contributor_agent = Agent(
    role=active_persona["role"],
    goal=active_persona["goal"],
    backstory=active_persona["backstory"],
    verbose=False,
    allow_delegation=False,
    llm=premium_writer_llm
)

# NEW: Advertising & Revenue Director Agent
revenue_director = Agent(
    role="Advertising & Monetization Director",
    goal="Maximize RPM and affiliate conversions by programmatically inserting contextual affiliate links and responsive pay-per-click (PPC) ad blocks.",
    backstory="""A data-driven ad tech veteran who treats monetization as a core product feature. Believes that high-converting 
    contextual affiliate links and non-intrusive PPC ad blocks should enhance the user journey without causing banner 
    fatigue or degrading page speed. Strict defender of reader trust—link contextual relevance must be 100% accurate.""",
    verbose=False,
    allow_delegation=False,
    llm=premium_writer_llm
)

# Managing Editor and Fact Auditor Agent
managing_editor = Agent(
    role="Managing Editor & Fact Auditor",
    goal="Enforce publication integrity, audit source claims, block AI clichés, and structure Ghost CMS JSON.",
    backstory="A strict digital publisher who rejects unsupported claims, buzzwords, and generic formatting.",
    verbose=False,
    allow_delegation=False,
    llm=premium_writer_llm
)

# ----------------------------------------------------------------------
# 4. TASK DEFINITIONS & CONSTRAINTS
# ----------------------------------------------------------------------
task_draft = Task(
    description=f"""
    Write a technical decision guide on: '{target_topic}'.
    
    EVIDENCE PACKAGE:
    {json.dumps(evidence_package, indent=2)}
    
    REQUIREMENTS:
    - Base every claim directly on the approved evidence package.
    - Do not invent specifications or convert estimates into confirmed facts.
    - Use Markdown tables where comparisons clarify technical differences.
    - Reference primary sources for critical specs.
    - Label manufacturer claims and estimates clearly.
    - Include a 'Last Reviewed' timestamp.
    
    PROHIBITED PHRASES & AI CLICHÉS:
    - 'in today's landscape'
    - 'delve'
    - 'testament'
    - 'furthermore'
    - 'game-changer'
    - 'revolutionize'
    - 'a tapestry of'
    - 'nestled'
    - 'beacon of'
    - Generic '10 Best' listicle formatting
    """,
    expected_output="Authoritative article drafted in clean Markdown with no AI-generated fluff.",
    agent=contributor_agent
)

# NEW: Contextual Monetization Task
task_monetize = Task(
    description=f"""
    Audit the drafted article and insert high-intent contextual affiliate links and responsive pay-per-click (PPC) ad units.
    
    MONETIZATION INVENTORY RULES:
    {json.dumps(monetization_inventory, indent=2)}
    
    INSTRUCTIONS & RIGID DENSITY BOUNDARIES:
    1. Scan the text for exact-match or semantically close keywords specified in the inventory.
    2. Convert those key phrases into Markdown affiliate links using the provided 'destination_url' template.
       - Limit to a MAXIMUM of three (3) affiliate links per 500 words. Never link consecutive sentences.
       - Ensure the anchor text is highly relevant (e.g. link 'Mondo sizing standards' instead of just 'sizing').
    3. Place responsive PPC ad blocks inside the markdown where natural content breaks occur:
       - Insert exactly one (1) PPC block (using 'ad_code_html' or placeholder comment if null) after the 2nd paragraph.
       - If the article exceeds 800 words, insert a second (2nd) PPC block immediately preceding the 'Conclusion' or final section.
       - PPC ad block placeholder syntax to use if 'ad_code_html' is missing:
         <!-- V4L PPC SLOT: partner_name -->
    4. Do NOT alter the factual claims, spec numbers, or authoritative persona tone.
    """,
    expected_output="The original draft enriched with highly targeted, context-appropriate affiliate links and responsive PPC code blocks.",
    agent=revenue_director,
    dependencies=[task_draft]
)

task_editorial_audit = Task(
    description="""
    Audit the monetized article against strict publishing standards:
    1. Verify every metric and spec is supported by the evidence package.
    2. Confirm no banned phrases or generic transition fluff exist.
    3. Ensure persona voice aligns with their designated specialty.
    4. Verify that monetization features (affiliate links, PPC containers) conform to density limits and do not corrupt formatting.
    5. Compile the audited content into valid JSON for the Ghost API:
       {
         "meta_title": "Concise SEO Title (<60 chars)",
         "meta_description": "Precise summary (<155 chars)",
         "html_body": "Full article converted to clean HTML tags with tables, inline affiliate links, and embedded PPC containers."
       }
    """,
    expected_output="A single valid JSON object with keys: meta_title, meta_description, html_body.",
    agent=managing_editor,
    dependencies=[task_monetize]
)

# ----------------------------------------------------------------------
# 5. EXECUTION PIPELINE
# ----------------------------------------------------------------------
webzine_crew = Crew(
    agents=[contributor_agent, revenue_director, managing_editor],
    tasks=[task_draft, task_monetize, task_editorial_audit],
    process=Process.sequential
)

if __name__ == "__main__":
    try:
        result = webzine_crew.kickoff()
        print(result)
    except Exception as e:
        print(json.dumps({"error": f"CrewAI Execution Failed: {str(e)}"}))
        sys.exit(1)
