# Registry for Labeeb AI models, tools, and agents

class ModelRegistry:
    def __init__(self):
        self.models = {}
    def register(self, name, model):
        self.models[name] = model
    def get(self, name):
        return self.models.get(name)

class ToolRegistry:
    def __init__(self):
        self.tools = {}
    def register(self, name, tool):
        self.tools[name] = tool
    def get(self, name):
        return self.tools.get(name)

class AgentRegistry:
    def __init__(self):
        self.agents = {}
    def register(self, name, agent):
        self.agents[name] = agent
    def get(self, name):
        return self.agents.get(name) 