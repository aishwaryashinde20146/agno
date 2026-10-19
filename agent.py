from agno import tool
import google.generativeai as genai
from agno import Agent

hospital_agent = Agent(config_path="agno.yaml")


genai.configure(api_key="AIzaSyBeSQvtHBO8q7fs7TZIaE0APWureF9pqY8 ")

@tool(name="gemini_text", description="Call Gemini 2.5 to generate a response")
def gemini_text(prompt: str):
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

