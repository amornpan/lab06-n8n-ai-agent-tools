"""
Lab 06: AI Agent with Tools - 10 Auto-grading Tests
ตรวจสอบโครงสร้างไฟล์ workflow.json โดยไม่ต้องรัน n8n
"""

import pytest
import json
import os

WORKFLOW_FILE = 'workflow.json'


class TestWorkflowFile:
    """ตรวจสอบไฟล์ workflow.json (16 คะแนน)"""

    @pytest.fixture(autouse=True)
    def load_workflow(self):
        if os.path.exists(WORKFLOW_FILE):
            with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
                self.workflow = json.load(f)
                self.nodes = self.workflow.get('nodes', [])
                self.connections = self.workflow.get('connections', {})
        else:
            self.workflow = None
            self.nodes = []
            self.connections = {}

    def test_01_workflow_file_exists(self):
        """Test 1: มีไฟล์ workflow.json (8 คะแนน)"""
        assert os.path.exists(WORKFLOW_FILE), \
            "workflow.json not found - กรุณา export workflow จาก n8n"

    def test_02_workflow_valid_json(self):
        """Test 2: เป็น valid JSON (8 คะแนน)"""
        assert self.workflow is not None, "workflow.json is not valid JSON"
        assert 'nodes' in self.workflow, "workflow.json missing 'nodes' key"
        assert 'connections' in self.workflow, "workflow.json missing 'connections' key"
        assert len(self.nodes) > 0, "workflow.json has no nodes"


class TestChatTrigger:
    """ตรวจสอบ Chat Trigger Node (10 คะแนน)"""

    @pytest.fixture(autouse=True)
    def load_workflow(self):
        if os.path.exists(WORKFLOW_FILE):
            with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
                self.workflow = json.load(f)
                self.nodes = self.workflow.get('nodes', [])
        else:
            self.workflow = None
            self.nodes = []

    def test_03_has_chat_trigger(self):
        """Test 3: มี Chat Trigger node (10 คะแนน)"""
        chat_trigger_nodes = [n for n in self.nodes
                              if 'chattrigger' in n.get('type', '').lower().replace('.', '').replace('-', '').replace('_', '')]
        assert len(chat_trigger_nodes) > 0, \
            "ไม่พบ Chat Trigger Node - ต้องมี 'When chat message received' node"


class TestAIAgent:
    """ตรวจสอบ AI Agent Node (22 คะแนน)"""

    @pytest.fixture(autouse=True)
    def load_workflow(self):
        if os.path.exists(WORKFLOW_FILE):
            with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
                self.workflow = json.load(f)
                self.nodes = self.workflow.get('nodes', [])
        else:
            self.workflow = None
            self.nodes = []

    def test_04_has_ai_agent(self):
        """Test 4: มี AI Agent node (12 คะแนน)"""
        agent_nodes = [n for n in self.nodes
                       if 'agent' in n.get('type', '').lower()]
        assert len(agent_nodes) > 0, \
            "ไม่พบ AI Agent Node - ต้องมี AI Agent (Tools Agent)"

    def test_09_agent_has_system_message(self):
        """Test 9: AI Agent มี System Message (10 คะแนน)"""
        agent_nodes = [n for n in self.nodes
                       if 'agent' in n.get('type', '').lower()]
        assert len(agent_nodes) > 0, "ไม่พบ AI Agent Node"

        agent = agent_nodes[0]
        options = agent.get('parameters', {}).get('options', {})
        system_message = options.get('systemMessage', '')
        assert len(system_message) > 10, \
            "AI Agent ไม่มี System Message หรือสั้นเกินไป — ต้องมี System Prompt ที่บอก AI ให้ใช้ tools"


class TestSubNodes:
    """ตรวจสอบ Sub-nodes: LLM, Calculator, Wikipedia, Memory (42 คะแนน)"""

    @pytest.fixture(autouse=True)
    def load_workflow(self):
        if os.path.exists(WORKFLOW_FILE):
            with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
                self.workflow = json.load(f)
                self.nodes = self.workflow.get('nodes', [])
                self.connections = self.workflow.get('connections', {})
        else:
            self.workflow = None
            self.nodes = []
            self.connections = {}

    def test_05_has_llm_model(self):
        """Test 5: มี OpenAI Chat Model node (12 คะแนน)"""
        llm_nodes = [n for n in self.nodes
                     if any(keyword in n.get('type', '').lower()
                            for keyword in ['lmchatopenai', 'lmchatollama', 'lmchat'])]
        assert len(llm_nodes) > 0, \
            "ไม่พบ Chat Model Node - ต้องมี OpenAI Chat Model หรือ Ollama Chat Model"

    def test_06_has_calculator(self):
        """Test 6: มี Calculator tool (10 คะแนน)"""
        calc_nodes = [n for n in self.nodes
                      if 'calculator' in n.get('type', '').lower()]
        assert len(calc_nodes) > 0, \
            "ไม่พบ Calculator Tool - ต้องเพิ่ม Calculator เป็น tool ของ AI Agent"

    def test_07_has_wikipedia(self):
        """Test 7: มี Wikipedia tool (10 คะแนน)"""
        wiki_nodes = [n for n in self.nodes
                      if 'wikipedia' in n.get('type', '').lower()]
        assert len(wiki_nodes) > 0, \
            "ไม่พบ Wikipedia Tool - ต้องเพิ่ม Wikipedia เป็น tool ของ AI Agent"

    def test_08_has_memory(self):
        """Test 8: มี Memory node (10 คะแนน)"""
        memory_nodes = [n for n in self.nodes
                        if 'memory' in n.get('type', '').lower()]
        assert len(memory_nodes) > 0, \
            "ไม่พบ Memory Node - ต้องเพิ่ม Simple Memory เข้ากับ AI Agent"


class TestConnections:
    """ตรวจสอบ Connections (10 คะแนน)"""

    @pytest.fixture(autouse=True)
    def load_workflow(self):
        if os.path.exists(WORKFLOW_FILE):
            with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
                self.workflow = json.load(f)
                self.nodes = self.workflow.get('nodes', [])
                self.connections = self.workflow.get('connections', {})
        else:
            self.workflow = None
            self.nodes = []
            self.connections = {}

    def test_10_tools_connected_to_agent(self):
        """Test 10: tools เชื่อมเข้า AI Agent ผ่าน ai_tool (10 คะแนน)"""
        has_tool_connection = False
        for node_name, conn_types in self.connections.items():
            if 'ai_tool' in conn_types:
                has_tool_connection = True
                break

        assert has_tool_connection, \
            "ไม่พบ connection แบบ ai_tool — Calculator และ Wikipedia ต้องเชื่อมเข้า AI Agent ผ่าน Tool connection"
