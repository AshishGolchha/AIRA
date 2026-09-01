import os
from dotenv import load_dotenv
from crewai import LLM, Agent, Task, Crew, Process

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

test_models = [
    "gemini/gemini-3.6-flash",
    "gemini/gemini-3.5-flash",
    "gemini/gemini-flash-latest",
    "gemini/gemini-2.5-flash",
]

for model in test_models:
    print(f"\n--- Testing CrewAI model: {model} ---")
    try:
        llm = LLM(model=model, api_key=api_key)
        agent = Agent(
            role="Analyst",
            goal="Respond with one word: Verified",
            backstory="Analyst",
            llm=llm,
            verbose=False,
        )
        task = Task(
            description="Respond with single word: Verified",
            expected_output="Single word.",
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
        out = crew.kickoff()
        print(f"[SUCCESS] {model} works! Output: {out.raw.strip() if hasattr(out, 'raw') else str(out).strip()}")
        break
    except Exception as e:
        print(f"[FAIL] {model} failed: {e}")
