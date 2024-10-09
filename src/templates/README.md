**Agent template**

```
{
    "metadata": 
    {"name": "agent-template", "description": "Agent template"}, "spec": {"type": "
agent", "version": "1.0.0", "image": "python:3.7", "command": "python3 agent.py", "resources": {"
requests": {"cpu": "0.1", "memory": "64Mi"}, "limits": {"cpu": "0.5", "memory": "256Mi"}}}}

```