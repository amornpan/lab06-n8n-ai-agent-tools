# Lab 06: AI Agent with Tools — n8n Tool Calling

> **n8n AI Agent + OpenAI Chat Model (LLM Gateway) + Calculator + Wikipedia + Simple Memory**

## วัตถุประสงค์การเรียนรู้

เมื่อทำ Lab นี้สำเร็จ นักศึกษาจะสามารถ:

1. **เข้าใจ AI Agent** — ความแตกต่างระหว่าง AI Agent กับ Basic LLM Chain
2. **ใช้ Tool Calling** — ให้ AI ตัดสินใจเลือกเรียก tool ที่เหมาะสมเอง
3. **เชื่อมต่อ LLM Gateway** — ใช้ OpenAI Chat Model node ชี้ไป LLM Gateway (Ollama)
4. **เพิ่ม Tools** — ต่อ Calculator และ Wikipedia เข้ากับ AI Agent
5. **เขียน System Prompt** — กำหนดพฤติกรรม AI Agent ให้เรียก tools เมื่อเหมาะสม
6. **ใช้ Simple Memory** — ให้ AI Agent จำบทสนทนาได้
7. **ทดสอบ Tool Calling** — ตั้งคำถามที่บังคับให้ AI ใช้ tools
8. **Debug** — แก้ไขปัญหาเมื่อ AI Agent ไม่เรียก tool

---

## โจทย์

สร้าง AI Agent Workflow ใน n8n ที่สามารถ:

1. **รับข้อความจาก Chat UI** ของ n8n (ไม่ต้องใช้ Discord)
2. **ตัดสินใจเอง** ว่าจะใช้ tool ไหนตอบคำถาม
3. **คำนวณตัวเลข** ผ่าน Calculator tool
4. **ค้นหาข้อมูล** ผ่าน Wikipedia tool
5. **ใช้หลาย tools ร่วมกัน** เช่น ค้นหาข้อมูลแล้วนำไปคำนวณต่อ
6. **จำบทสนทนา** ผ่าน Simple Memory

---

## สถาปัตยกรรม

```
When chat message received (Chat Trigger)
    ↓
AI Agent (Tools Agent)
    ├── Chat Model*  → OpenAI Chat Model (LLM Gateway)
    ├── Memory       → Simple Memory (contextWindowLength: 10)
    ├── Tool         → Calculator
    └── Tool         → Wikipedia
```

### AI Agent ทำงานอย่างไร?

```
User ถามคำถาม
    ↓
AI Agent รับข้อความ
    ↓
AI ตัดสินใจ:
    ├── ต้องคำนวณ? → เรียก Calculator
    ├── ต้องค้นข้อมูล? → เรียก Wikipedia
    ├── ต้องทั้งคู่? → เรียก Wikipedia ก่อน แล้วส่งผลไป Calculator
    └── ตอบได้เลย? → ตอบจากความรู้ของ LLM
    ↓
AI รวบรวมผลลัพธ์ → ตอบ User
```

**ข้อแตกต่างจาก Lab 05:**
- Lab 05: Basic LLM Chain — data flow ตายตัว (Webhook → AI → API → AI → Discord)
- Lab 06: AI Agent — **AI ตัดสินใจเองว่าจะเรียก tool ไหน** ไม่มี flow ตายตัว

---

## Node ที่ต้องมี (4 Nodes + 3 Sub-nodes)

| # | Node Name | Type | หน้าที่ |
|---|-----------|------|---------|
| 1 | When chat message received | Chat Trigger | รับข้อความจาก n8n Chat UI |
| 2 | AI Agent | Agent (Tools Agent) | ตัดสินใจเรียก tools |
| ↳ | OpenAI Chat Model | Sub-node (LLM) | เชื่อมต่อ LLM Gateway |
| ↳ | Simple Memory | Sub-node (Memory) | จำบทสนทนา |
| ↳ | Calculator | Sub-node (Tool) | คำนวณตัวเลข |
| ↳ | Wikipedia | Sub-node (Tool) | ค้นหาข้อมูล |

> **หมายเหตุ**: OpenAI Chat Model, Simple Memory, Calculator, Wikipedia เป็น sub-node ที่เชื่อมเข้ากับ AI Agent ผ่าน connection types: `ai_languageModel`, `ai_memory`, `ai_tool`

---

## การตั้งค่า OpenAI Chat Model (LLM Gateway)

Lab นี้ใช้ **LLM Gateway** ที่ `https://minddatatech.com/llm-api/v1` ซึ่งเป็น OpenAI-compatible API

### ตั้งค่า Credentials ใน n8n:

1. ไปที่ **Credentials** → **Add Credential** → **OpenAI API**
2. กรอกข้อมูล:
   - **API Key**: ใช้ key ที่ได้จาก LLM Gateway
   - **Base URL**: `https://minddatatech.com/llm-api/v1`
3. บันทึก

### ตั้งค่า OpenAI Chat Model node:

- **Model**: เลือก model ที่ LLM Gateway รองรับ (เช่น `gpt-oss:20b`)
- **Credentials**: เลือก OpenAI API ที่สร้างไว้

---

## System Prompt

System Prompt สำคัญมาก — เป็นตัวกำหนดว่า AI Agent จะเรียก tool เมื่อไหร่

### ตัวอย่าง System Prompt ที่ดี:

```
คุณคือ AI Assistant ที่มี tools ช่วยทำงาน

กฎการใช้ tools:
- เมื่อผู้ใช้ถามเรื่องที่ต้องคำนวณตัวเลข → ใช้ Calculator เสมอ
- เมื่อผู้ใช้ถามข้อมูลเกี่ยวกับบุคคล สถานที่ หรือเหตุการณ์ → ใช้ Wikipedia ค้นหาเสมอ
- เมื่อต้องค้นข้อมูลแล้วนำไปคำนวณ → ใช้ Wikipedia ก่อน แล้วใช้ Calculator
- ห้ามตอบจากความจำของตัวเอง ให้ใช้ tools ที่มีอยู่ทุกครั้ง

ตอบเป็นภาษาไทยเสมอ
```

### ทำไม System Prompt สำคัญ?

- **ไม่มี System Prompt**: AI อาจตอบจากความรู้ในตัวเลย ไม่เรียก tool
- **มี System Prompt ที่ดี**: AI จะเรียก tool เสมอเมื่อเจอคำถามที่ตรงกับ tool

---

## ตัวอย่างคำถามทดสอบ

### ทดสอบ Calculator:
- `1234567 * 7654321 เท่ากับเท่าไหร่`
- `ถ้าเงินเดือน 35000 จ่ายภาษี 5% เหลือเท่าไหร่`
- `2 ยกกำลัง 32 เท่ากับเท่าไหร่`

### ทดสอบ Wikipedia:
- `Moo Deng คืออะไร`
- `ประเทศญี่ปุ่นมีประชากรเท่าไหร่`
- `ดาวอังคารอยู่ห่างจากโลกเท่าไหร่`

### ทดสอบ Multi-tool (Wikipedia + Calculator):
- `ประชากรญี่ปุ่นมีกี่คน ถ้าลดลง 2% ต่อปี อีก 5 ปีจะเหลือเท่าไหร่`
- `GDP ของไทยเท่าไหร่ ถ้าโต 3% ต่อปี อีก 10 ปีจะเป็นเท่าไหร่`

### ทดสอบ Memory:
1. ถาม: `ฉันชื่ออาร์ม`
2. ถาม: `ฉันชื่ออะไร` → AI ต้องตอบ "อาร์ม" ได้

---

## เกณฑ์คะแนน (100 คะแนน)

| Test | คะแนน | ตรวจสอบ |
|------|--------|---------|
| test_01: workflow.json exists | 8 | มีไฟล์ workflow.json |
| test_02: valid JSON | 8 | เป็น JSON + มี nodes, connections |
| test_03: Chat Trigger | 10 | มี Chat Trigger node |
| test_04: AI Agent | 12 | มี AI Agent node (Tools Agent) |
| test_05: LLM Model | 12 | มี OpenAI Chat Model node |
| test_06: Calculator | 10 | มี Calculator tool |
| test_07: Wikipedia | 10 | มี Wikipedia tool |
| test_08: Memory | 10 | มี Simple Memory node |
| test_09: System Message | 10 | AI Agent มี System Message |
| test_10: Connections | 10 | tools เชื่อมเข้า AI Agent ผ่าน ai_tool |
| **รวม** | **100** | |

> **ทดสอบ**: `pytest tests/ -v --tb=short`

---

## Common Errors

| ปัญหา | สาเหตุ | วิธีแก้ |
|--------|--------|---------|
| "None of your tools were used" | System Prompt ไม่บอกให้ใช้ tools | เพิ่ม System Message ที่สั่งให้ใช้ tools |
| AI ตอบเองไม่เรียก tool | LLM รู้คำตอบอยู่แล้ว | ถามสิ่งที่ LLM ไม่รู้ เช่น คำนวณเลขใหญ่ |
| OpenAI Chat Model error | Base URL หรือ API Key ผิด | ตรวจสอบ Credentials: Base URL ต้องเป็น `https://minddatatech.com/llm-api/v1` |
| "No language model connected" | ไม่ได้เพิ่ม sub-node LLM | เพิ่ม OpenAI Chat Model เข้า AI Agent |
| Wikipedia ค้นไม่เจอ | คำค้นเป็นภาษาไทย | Wikipedia tool ค้นเป็นภาษาอังกฤษ ให้ AI แปลก่อน |
| Memory ไม่จำ | Session เปลี่ยน | ใช้ session เดิม ไม่ต้อง refresh หน้า |

---

## โครงสร้างโปรเจกต์

```
lab06-n8n-ai-agent-tools/
├── .github/workflows/
│   └── autograding.yml        ← CI/CD Pipeline
├── workflow.json               ← [นักศึกษาทำ] Export จาก n8n
├── README.md                   ← เอกสารนี้
├── SETUP_GUIDE.md              ← คู่มือติดตั้งทีละขั้นตอน
├── examples/
│   ├── sample-chat-calculator.md    ← ตัวอย่างถาม Calculator
│   ├── sample-chat-wikipedia.md     ← ตัวอย่างถาม Wikipedia
│   └── sample-chat-multi-tool.md    ← ตัวอย่างใช้หลาย tools
├── tests/
│   ├── conftest.py
│   └── test_workflow.py       ← 10 Auto-grading Tests
└── quiz/
    └── quiz.md                ← 10 คำถาม Quiz
```

---

## ขั้นตอนการทำงาน

1. ศึกษา `README.md` นี้ให้เข้าใจ concept AI Agent + Tools
2. ตั้งค่า LLM Gateway credentials ใน n8n
3. สร้าง Workflow: Chat Trigger → AI Agent → เพิ่ม tools
4. เขียน System Prompt ให้ AI Agent เรียก tools
5. ทดสอบคำถามแต่ละแบบ (Calculator / Wikipedia / Multi-tool / Memory)
6. ดู Logs ใน n8n ว่า tools ถูกเรียกจริง
7. Export workflow เป็น JSON → วางทับ `workflow.json`
8. รัน `pytest tests/ -v --tb=short` ให้ผ่าน 100 คะแนน
9. Push ขึ้น GitHub

---

## Resources

- [n8n AI Agent Documentation](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/)
- [n8n OpenAI Chat Model](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.lmchatopenai/)
- [n8n Calculator Tool](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolcalculator/)
- [n8n Wikipedia Tool](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolwikipedia/)
- [n8n Simple Memory](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.memorybufferwindow/)
