import os
import asyncio
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel

async def test_groq_llm():
    os.environ['GROQ_API_KEY'] = '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'
    print("Environment variable set.")
    
    model = GroqModel('llama-3.3-70b-versatile')
    print("Model initialized.")
    
    agent = Agent(model)
    print("Agent created.")
    
    prompt = "What is AI agent?"
    print(f"Running prompt: {prompt}")
    
    response = await agent.run(prompt)
    print("Response received.")
    
    assert response is not None
    print(response)

if __name__ == "__main__":
    asyncio.run(test_groq_llm())