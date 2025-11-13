import os

# Struktur folder dan file untuk MVP
structure = {
    "ai-report-swarm": {
        "README.md": "",
        ".gitignore": "",
        ".env.example": "",
        "requirements.txt": "",
        "demos": {
            "example_reports": {}
        },
        "src": {
            "app.py": "",
            "superagent": {
                "__init__.py": "",
                "planner.py": "",
                "plan_schema.py": "",
                "superagent.py": "",
                "swarm_manager.py": "",
                "memory.py": "",
                "aggregator.py": "",
                "adapters": {
                    "__init__.py": "",
                    "openai_adapter.py": ""
                },
                "agents": {
                    "__init__.py": "",
                    "base.py": "",
                    "research.py": "",
                    "trends.py": "",
                    "insights.py": "",
                    "writer.py": ""
                }
            }
        },
        "tests": {
            "test_planner.py": "",
            "test_research_agent.py": ""
        }
    }
}


def create_structure(base_path, structure_dict):
    for name, content in structure_dict.items():
        path = os.path.join(base_path, name)

        # Jika content adalah dict → ini folder
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)

        # Jika content string → ini file
        else:
            with open(path, "w") as f:
                f.write(content)


if __name__ == "__main__":
    base = "."  # Buat folder mulai dari current directory
    create_structure(base, structure)
    print("Project structure created successfully!")
