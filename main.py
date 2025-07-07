import os
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from vector_db.vector_db import create_retriever

# Initialize the LLM
llm = ChatOllama(
    model="qwen2.5:7b",
    temperature=0,
)

# Improved system prompt
system_prompt = SystemMessage(
    content=f"""You are an AI agent that analyzes entire codebases and generates professional README.md files for GitHub repositories.

Based on the project files provided below, create a comprehensive README.md that includes:

1. **Project Title** - Infer from the codebase
2. **Description** - What the project does and its purpose
3. **Features** - Key functionality and capabilities
4. **Installation** - How to set up the project
5. **Usage** - How to use the project with examples
6. **Project Structure** - Overview of the file/folder organization
7. **Dependencies** - Required packages and libraries
8. **Contributing** - Guidelines for contributors (if applicable)
9. **License** - If you can identify one

Make the README engaging, professional, and well-formatted with proper markdown syntax. Use badges, code blocks, and proper headings.

When using the retriever tool, search for relevant information about:
- Main functionality and purpose
- Dependencies and requirements
- Configuration files
- Entry points and main modules
- Documentation or existing README content
- Project structure and architecture
"""
)

user_inp_to_use_existing_db = input("Generate a new database (yes or no): ")

if user_inp_to_use_existing_db == "yes":
    retriever = create_retriever()
elif user_inp_to_use_existing_db == "no":
    retriever = create_retriever(use_existsing_db=True)
else:
    print("Invalid input... Generating a new vector database")
    retriever = create_retriever()


@tool
def retriever_tool(query: str) -> str:
    """
    This tool searches and retrieves the information from the vector database
    """
    docs = retriever.invoke(query)
    results = []
    for i, doc in enumerate(docs):
        results.append(f"Document {i+1}:\n{doc.page_content}")

    return "\n\n".join(results)

tools = [retriever_tool]
llm_with_tools = llm.bind_tools(tools)

def generate_readme():
    """
    Generate a README.md file by analyzing the project codebase
    """
    
    # Define queries to gather comprehensive information about the project
    queries = [
        "main.py entry point application startup",
        "package.json requirements.txt dependencies",
        "project structure folders directories",
        "configuration files config settings",
        "API endpoints routes handlers",
        "database models schemas",
        "README documentation comments",
        "installation setup instructions",
        "usage examples how to use"
    ]
    
    # Initial message to start the conversation
    human_message = HumanMessage(
        content="""Please analyze this codebase and generate a comprehensive README.md file. 
        
        Start by searching for information about the project's main functionality, dependencies, 
        structure, and usage patterns. Use the retriever tool to gather relevant information 
        from the codebase before generating the README.
        
        Make multiple searches to understand different aspects of the project:
        1. Main application files and entry points
        2. Dependencies and requirements
        3. Project structure and organization
        4. Configuration and setup files
        5. Key features and functionality
        """
    )
    
    # Create the conversation with system prompt and human message
    messages = [system_prompt, human_message]
    
    # Generate the README
    print("🔍 Analyzing codebase and generating README...")
    response = llm_with_tools.invoke(messages)
    
    # Handle tool calls if the LLM decides to use them
    while response.tool_calls:  # type: ignore
        print(f"🔧 Using retriever tool with query: {response.tool_calls[0]['args']['query']}")  # type: ignore
        
        # Add the AI message to conversation
        messages.append(response)
        
        # Execute tool calls
        for tool_call in response.tool_calls:  # type: ignore
            tool_result = retriever_tool.invoke(tool_call['args'])
            
            # Add tool result to conversation
            messages.append({
                "role": "tool",
                "content": tool_result,
                "tool_call_id": tool_call['id']
            })
        
        # Get next response
        response = llm_with_tools.invoke(messages)
    
    return response.content

def save_readme(content: str, filename: str = "README.md"):
    """
    Save the generated README content to a file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ README.md saved successfully to {filename}")
    except Exception as e:
        print(f"❌ Error saving README: {e}")

if __name__ == "__main__":
    # Choose your preferred approach
    
    # Approach 1: Let the LLM decide what to search for
    print("=== AI-Driven Analysis ===")
    readme_content = generate_readme()
    save_readme(readme_content, "generated_readme_2.md")  # type: ignore
    
    print("\n" + "="*50 + "\n")