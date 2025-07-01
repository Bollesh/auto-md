import os
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage

source_path = "project/"

skip_extensions = {'.exe', '.dll', '.bin', '.jpg', '.jpeg', '.png', '.gif', 
                   '.bmp', '.ico', '.zip', '.rar', '.7z', '.tar', '.gz',
                   '.mp3', '.mp4', '.avi', '.mkv', '.pdf', '.pyc'}

with open("all_files.txt", "w", encoding="utf-8") as f:
    for dirpath, dirnames, filenames in os.walk(source_path):
        # Skip __pycache__ directories
        if "__pycache__" in dirpath:
            continue 
            
        print(f"dir: {dirpath}")
        f.write(f"Current Directory: {dirpath}\n")
        f.write("=" * 50 + "\n")
        
        for filename in filenames:
            file_ext = os.path.splitext(filename)[1].lower()
            
            # Skip binary files - fix the logic here
            if file_ext in skip_extensions:
                print(f"\tSkipping: {filename}")
                continue
                
            print(f"\tfile: {filename}")
            f.write(f"\nCurrent File: {filename}\n")
            f.write("-" * 30 + "\n")
            
            # Use os.path.join for proper path handling
            file_path = os.path.join(dirpath, filename)
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as sub_f:
                    content = sub_f.read()
                    f.write(content)
                    f.write(f"\n--- End of {filename} ---\n\n")
            except Exception as e:
                error_msg = f"Error reading {filename}: {str(e)}\n\n"
                print(f"\t{error_msg.strip()}")
                f.write(error_msg)

# Read the consolidated project file
with open("all_files.txt", "r", encoding="utf-8") as f:
    project = f.read()

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

PROJECT FILES:
{project}
"""
)

# Generate README
print("Generating README...")
res = llm.invoke(input=[system_prompt])

# Save the generated README
with open("your_readme.md", "w", encoding="utf-8") as f:
    f.write(res.content)  # type: ignore

print("README.md generated successfully!")
print("\n" + "="*50)
print("Generated README Preview:")
print("="*50)
print(res.content[:500] + "..." if len(res.content) > 500 else res.content)  # type: ignore