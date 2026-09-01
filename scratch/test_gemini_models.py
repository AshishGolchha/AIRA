import os
from dotenv import load_dotenv
from crewai import LLM, Agent, Task, Crew, Process

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

models_to_test = [
    "gemini/gemini-2.0-flash",
    "gemini/gemini-2.0-flash-exp",
    "gemini/gemini-1.5-flash",
    "gemini/gemini-1.5-pro",
]

print(f"Testing CrewAI with API Key (len={len(api_key)})...")

for model in models_to_test:
    print(f"\n--- Testing model: {model} ---")
    try:
        llm = LLM(model=model, api_key=api_key)
        agent = Agent(
            role="Analyst",
            goal="Answer with 1 word: Ready",
            backstory="Analyst",
            llm=llm,
            verbose=False,
        )
        task = Task(
            description="Respond with the single word: Ready",
            expected_output="Single word.",
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
        output = crew.kickoff()
        raw = str(output.raw if hasattr(output, "raw") else output)
        print(f"[PASS] {model} succeeded! Output: {raw.strip()}")
        break
    except Exception as e:
        print(f"[FAIL] {model} failed: {e}")
