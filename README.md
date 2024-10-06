# Guided Agentic Systems (GAS)

**Guided Agentic Systems (GAS)** is a framework that integrates Large Language Models (LLMs) as active participants in human-driven processes. The goal is to create collaborative environments where LLMs take on roles such as Scrum Master, Product Owner, Lead Developer, and Developers within events like sprint planning and scrum meetings. Human participants guide these AI agents to complete tasks, fostering a seamless interaction between humans and AI in organizational workflows.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Configuring Agents](#configuring-agents)
  - [Running a Meeting](#running-a-meeting)
- [Architecture](#architecture)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Overview

GAS leverages the capabilities of LLMs to simulate human roles in collaborative settings. By incorporating AI agents into meetings and events, organizations can:

- Enhance productivity by automating routine tasks.
- Foster creativity through AI-generated insights.
- Provide training and support by simulating roles for learning purposes.

**Key Concepts:**

- **Human-Guided Interaction:** A human participant directs the flow, ensuring that AI agents contribute effectively towards task completion.
- **Role-Based Agents:** Each AI agent is assigned a specific role with customized prompts and behaviors.
- **Tool Integration:** Agents can utilize tools and functions to perform actions like recording backlog items, writing and executing code, and more.

## Features

- **Customizable Agent Roles:** Easily define and customize AI agents for different roles within your process.
- **Prompt Configuration:** Manage system prompts, tools, and settings for each agent.
- **Conversation Management:** Maintain conversation history and context for coherent interactions.
- **Code Execution:** Developers can write and execute code within the conversation flow.
- **Tool Calling:** Agents can call functions or tools to perform specific tasks.
- **Meeting Orchestration:** Agents can initiate and manage meetings or events.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Access to a compatible LLM API (e.g., OpenAI GPT-4, Llama models)
- Necessary API keys and credentials for the LLM service
- Git (for cloning the repository)

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/guided-agentic-systems.git
   cd guided-agentic-systems
