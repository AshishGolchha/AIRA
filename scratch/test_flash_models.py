import os
from dotenv import load_dotenv
from crewai import LLM, Agent, Task, Crew, Process

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

for model in ["gemini/gemini-3.7-flash", "gemini/gemini-3.6-flash"]:
    print(f"\n--- Testing CrewAI with {model} ---")
    try:
        llm = LLM(model=model, api_key=api_key)
        agent = Agent(
            role="Research Specialist",
            goal="Provide a concise one sentence status of Apple Inc.",
            backstory="You are a senior equity analyst.",
            llm=llm,
            verbose=False,
        )
        task = Task(
            description="Respond with exactly: AIRA_LIVE_GEMINI_OK",
            expected_output="The exact phrase AIRA_LIVE_GEMINI_OK",
            agent=agent,
        )
        crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
        output = crew.kickoff()
        raw = str(output.raw if hasattr(output, "raw") else output)
        print(f"[PASS] {model} Output: {raw.strip()}")
    except Exception as e:
        print(f"[FAIL] {model} Failed: {e}")
