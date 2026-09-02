#!/usr/bin/env python3
"""
Vital4Living Multi-Agent CrewAI Writing, Editorial, and Monetization Engine
Sprint 5/6 Upgraded Implementation: Incorporating Ultra-Premium Copywriting Prompts
Uses version-agnostic string model definitions to completely bypass Pydantic validation errors on the VPS.
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
            "targeting_keywords": ["Mondo sizing", ["Salomon", "ski boots"]],
            "destination_url": "https://partner.avantlink.com/click?merchantId=123"
        },
        {
            "partner_name": "REI Co-op - Ultralight Gear",
            "monetization_type": "affiliate",
            "targeting_keywords": ["seam failure", "Dyneema", "ripstop", "backpack"],
            "destination_url": "https://rei.sjv.io/c/78910"
        },
        {
            "partner_name": "Premium Google AdSense - Mid Article PPC",
            "monetization_type": "ppc_ad_unit",
            "targeting_keywords": ["fabric denier", "torque specs", "hull geometry", "thermoregulation"],
            "ad_code_html": '<div class="v4l-ad-container"><!-- AdsByGoogle --><ins class="adsbygoogle" style="display:block; text-align:center;" data-ad-layout="in-article" data-ad-format="fluid" data-ad-client="ca-pub-999999999" data-ad-slot="1111111"></ins><script>(adsbygoogle = window.adsbygoogle || []).push({});</script></div>'
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
        "goal": "Write highly engaging, elite-level technical copy about boots, lasts, volume, and shell tolerances.",
        "backstory": """An obsessive, no-nonsense ski boot fitter and technical standards specialist. You despise marketing fluff,
        dry summaries, and AI clichés. You speak in direct, visceral, active terms, using boot-bench jargon naturally 
        (e.g., lasts, instep heights, sole length blocks, shell wraps). You write with the sharp, uncompromising tone of a 
        veteran boot technician speaking directly to a seasoned, technical skier."""
    },
    "Dex": {
        "role": "Dex Okafor - Outdoor Technology & Equipment Engineer",
        "goal": "Write elite-level, structurally sound technical copy evaluating gear tolerances, geometry, and design integrity.",
        "backstory": """A backcountry design engineer who strips marketing jargon down to physical stress specs, shear strengths,
        and real-world structural reliability. You write with the clean, precise authority of an industrial designer who 
        knows exactly where joints shear, coatings flake, or materials warp under sub-zero friction."""
    },
    "Wren": {
        "role": "Wren Calloway - Trail Physiology & Environmental Specialist",
        "goal": "Draft high-authority physiological analyses of environmental strain without generic medical padding.",
        "backstory": """An outdoor physiology expert who focuses on VO2 curves, core thermoregulation, and high-altitude adaptations.
        You hate dry handwaving; you write with razor-sharp clinical logic, establishing distinct safety margins based 
        strictly on physical data and environmental stress calculations."""
    },
    "Bo": {
        "role": "Bo Hartley - Materials & Gear Durability Analyst",
        "goal": "Analyze fabric tear strength, seam engineering, and hardware durability with hyper-realistic engineering focus.",
        "backstory": """A used-gear forensic analyst who knows exactly how fabric deniers hold up to scree slopes and sub-zero cycles.
        You explain fabric construction (e.g., Dyneema grids, ripstop weaves, TPU laminates) with tactile detail, stripping away 
        all catalog buzzwords in favor of real, physical breakdown metrics."""
    },
    "Niko": {
        "role": "Niko Reyes - Setup & Field Tuning Technician",
        "goal": "Provide elite, unambiguous mechanical tuning and torque calibrations with strict technician boundaries.",
        "backstory": """A master gear mechanic who lives and breathes grease threads, DIN springs, and exact torque specs.
        You write with hyper-clear mechanical commands, telling readers exactly where to use a manual hex key versus 
        when to walk into a certified shop to avoid critical hardware failures."""
    }
}

active_persona = persona_bank.get(target_persona, persona_bank["Dex"])

contributor_agent = Agent(
    role=active_persona["role"],
    goal=active_persona["goal"],
    backstory=active_persona["backstory"],
    verbose=False,
    allow_delegation=False,
    llm=premium_writer_llm
)

revenue_director = Agent(
    role="Advertising & Monetization Director",
    goal="Identify placement opportunities for high-intent contextual links and PPC ad blocks without corrupting copy flow.",
    backstory="\"\"A data-driven digital monetization director who specializes in seamless ad integration. You treat layout \
    space with high respect, identifying natural content transitions where responsive ad blocks can fit cleanly without \
    disrupting the visual flow or degrading mobile screen real estate.\"\"\"",
    verbose=False,
    allow_delegation=False,
    llm=premium_writer_llm
)

managing_editor = Agent(
    role="Managing Editor & Fact Auditor",
    goal="Audit facts, strip away ALL AI-isms, eliminate repetitive intro/outro patterns, and enforce high-end magazine prose.",
    backstory="\"\"A ruthless digital editor who despises AI phrasing, passive voice, and redundant structures. You edit the \
    article to read like an elite tech feature from a premium print publication. You strip out all preambles, conversational \
    introductions, and repetitive conclusion wraps, leaving only raw, highly-engaging tech authority.\"\"\"",
    verbose=False,
    allow_delegation=False,
    llm=cheap_llm
)

# ----------------------------------------------------------------------
# 4. TASK DEFINITIONS & CONSTRAINTS (Sprint 5/6 Upgraded Copywriting Tasks)
# ----------------------------------------------------------------------
task_draft = Task(
    description=f"""
    Write an elite, highly detailed technical decision guide on: '{target_topic}'.
    
    EVIDENCE PACKAGE:
    {json.dumps(evidence_package, indent=2)}
    
    RIGID EDITORIAL RULES (CRITICAL FOR QUALITY):
    1. VOICE & TONE: Write from the perspective of {target_persona}. Use visceral, technical language.
       - Sierra: Last widths, Mondo standards, shell volumes, WTR binding interfaces.
       - Use active voice, varied sentence lengths (alternate brief 4-word sentences with longer compound analytical sentences).
    2. NO AI FLUFF / META INTROS:
       - DO NOT start with "In this guide...", "We will cover...", "This article is designed to..." or any variant.
       - Jump immediately into the core physical problem or technical reality of the topic.
    3. MAGAZINE HEADINGS ONLY:
       - Absolutely PROHIBITED headings: "Introduction", "Body", "Technical Overview", "Sizing Rules", "Conclusion", "Summary".
       - Instead, write custom, punchy, narrative headings (e.g., "The WTR Interface Paradox", "Manual Height Adjustments in the Field", "Sinking Heels and Instep Friction").
    4. FACT DIRECTNESS:
       - Embed the raw specs from the evidence package naturally as active metrics. 
       - Label manufacturer claims as "unverified estimates" or "Salomon asserts..." if they are unproven.
    5. NO CLICHÉS:
       - Strictly enforce the prohibited list: 'in today's landscape', 'delve', 'testament', 'furthermore', 'game-changer', 'revolutionize', 'a tapestry of', 'nestled', 'beacon of'.
    """,
    expected_output="A premium, print-ready editorial tech guide in clean Markdown, starting immediately with a sharp hook and featuring custom headings.",
    agent=contributor_agent
)

task_monetize = Task(
    description=f"""
    Identify placement zones in the drafted article to inject contextual affiliate links and responsive PPC ad slots.
    
    MONETIZATION INVENTORY RULES:
    {json.dumps(monetization_inventory, indent=2)}
    
    DENSITY & STRUCTURE COEXISTENCE:
    1. Scan the text for keyword targets and turn them into natural-fitting markdown affiliate links.
       - MAXIMUM of 3 affiliate links per 500 words. Never link consecutive sentences.
    2. Add designated inline markers for PPC ad slots to ensure natural flow:
       - Place the primary PPC marker [PRIMARY_PPC_SLOT] after the second paragraph.
       - If word count is over 800 words, place a secondary PPC marker [SECONDARY_PPC_SLOT] immediately preceding the last subheader.
    """,
    expected_output="The original draft annotated with contextual affiliate links and clear [PRIMARY_PPC_SLOT] / [SECONDARY_PPC_SLOT] position tags.",
    agent=revenue_director,
    dependencies=[task_draft]
)

task_editorial_audit = Task(
    description="""
    Perform a ruthless editorial audit of the monetized draft:
    1. FACT AUDIT: Cross-reference every metric and claim against the evidence package. Strip any claim not strictly supported.
    2. COPY EDIT: Rewrite any passive, repetitive, or sterile sentences. Erase any conversational introductions ("In the world of ski gear...", "As a boot fitter..."). Make the prose jump straight onto the bench.
    3. CLICHÉ SWEEP: Run an absolute block on banned AI words. Ensure headings are narrative, editorial, and engaging.
    4. GHOST STRUCTURE: Convert the audited copy into clean HTML, preserving the [PRIMARY_PPC_SLOT] and [SECONDARY_PPC_SLOT] markers exactly as they are.
    5. Output the result in this exact, rigid JSON block for the Ghost API:
       {
         "meta_title": "Concise, punchy SEO Title (<60 chars, no pipes/wraps)",
         "meta_description": "Precise, narrative summary (<155 chars)",
         "html_body": "Full article in clean HTML tags, with lists, inline affiliate links, and the [PRIMARY_PPC_SLOT] / [SECONDARY_PPC_SLOT] markers preserved."
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
