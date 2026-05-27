# 设计文档：Harness Skill

## Overview

Harness Skill 是一个用于 Kiro 的访谈式 Skill，通过引导用户完成多阶段访谈来生成完整的 Harness Engineering 文档系统。该系统生成的 Markdown 文档可被多种 AI Agent 平台（Claude、Codex、Cursor、Windsurf、Hermes、OpenClaw 等）自动发现和引用。

---

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Harness Skill                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │  Interview      │  │  Response       │  │  State          │          │
│  │  Orchestrator   │──│  Collector      │──│  Manager        │          │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘          │
│           │                    │                    │                    │
│           ▼                    ▼                    ▼                    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Document Generator                            │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │    │
│  │  │ Template │ │ Renderer │ │  Path    │ │  Layer   │           │    │
│  │  │  Engine  │ │          │ │ Resolver │ │ Builder  │           │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│                              ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Output: Harness Engineering System            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### 分层架构

```
┌──────────────────────────────────────────────────────────────┐
│                    Agent Entry Points                         │
│  AGENTS.md │ CLAUDE.md │ .cursor/rules/ │ .windsurf/rules/   │
├──────────────────────────────────────────────────────────────┤
│                    Harness Map (harness-map.md)               │
│                    中央导航索引                                │
├──────────────────────────────────────────────────────────────┤
│  Platform   │  Domain     │ Application │ Interface │ Memory  │
│  Layer      │  Layer      │ Layer       │ Layer     │ Layer   │
│             │             │             │           │         │
│  design.md  │ domain-     │ project-    │ user-     │ memory. │
│  arch.md    │ model.md    │ structure.md│ guide.md  │ md      │
│  brain.md   │ business-   │ code-       │ api-      │ decision│
│  schema.md  │ rules.md    │ templates.md│ docs.md   │ s.md    │
│  prd.md     │ use-cases.md│ test-       │ deployment│ patterns│
│  ...        │ bugs.md     │ strategy.md │ .md       │ .md     │
│             │ todos.md    │ ci-cd.md    │           │         │
└──────────────────────────────────────────────────────────────┘
```

---

## 核心组件

### 1. Interview Orchestrator（访谈编排器）

负责管理访谈流程的执行顺序和状态转换。

**职责：**
- 初始化访谈会话
- 协调四个访谈阶段的执行顺序
- 处理阶段间的状态转换
- 支持访谈中断和恢复

**状态机：**

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   IDLE      │────▶│  PROJECT_   │────▶│   AGENT_    │────▶│ARCHITECTURE │────▶│ PROTOTYPE_  │
│             │     │ EXPLORATION │     │ PERSONALITY │     │             │     │    SPECS    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │                   │
      │                   │                   │                   │                   │
      ▼                   ▼                   ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  INTERRUPTED│◀────│  INTERRUPTED│◀────│  INTERRUPTED│◀────│  INTERRUPTED│◀────│   SUMMARY   │
│  (保存状态)  │     │  (保存状态)  │     │  (保存状态)  │     │  (保存状态)  │     │  (确认)     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                                          │
                                                                                          ▼
                                                                                  ┌─────────────┐
                                                                                  │ GENERATING  │
                                                                                  │ (文档生成)   │
                                                                                  └─────────────┘
                                                                                          │
                                                                                          ▼
                                                                                  ┌─────────────┐
                                                                                  │  COMPLETED  │
                                                                                  └─────────────┘
```

### 2. Response Collector（响应收集器）

负责收集、验证和存储用户在访谈中的响应。

**数据结构：**

```typescript
interface InterviewResponse {
  // 项目探索阶段
  projectExploration: {
    projectName: string;
    projectDescription: string;
    projectGoals: string[];
    successCriteria: string[];
    targetUsers: TargetUser[];
    coreFeatures: Feature[];
  };
  
  // Agent 性格阶段（可选）
  agentPersonality?: {
    voiceEnabled: boolean;
    tone?: 'professional' | 'friendly' | 'casual' | 'formal';
    style?: 'concise' | 'detailed' | 'technical' | 'accessible';
    formality?: number; // 1-10 scale
    voicePatterns?: VoicePattern[];
  };
  
  // 架构阶段
  architecture: {
    techStack: TechStack;
    architecturePattern: 'monolith' | 'microservices' | 'serverless' | 'hybrid';
    deployment: DeploymentConfig;
    integrations: Integration[];
  };
  
  // 原型规范阶段
  prototypeSpecs: {
    outputFormat: 'html' | 'markdown' | 'wirescript';
    fidelityLevel: 'low' | 'medium' | 'high';
    componentStructure: ComponentConfig;
    cssFramework?: string;
    docStyle?: string;
  };
}

interface TargetUser {
  name: string;
  description: string;
  primaryUseCases: string[];
}

interface Feature {
  name: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
}

interface TechStack {
  languages: string[];
  frameworks: string[];
  databases: string[];
}

interface DeploymentConfig {
  cloudProvider?: string;
  containerization?: 'docker' | 'kubernetes' | 'none';
  cicdPlatform?: string;
}

interface Integration {
  name: string;
  type: 'api' | 'sdk' | 'service';
  purpose: string;
}

interface VoicePattern {
  type: 'filler' | 'pause' | 'emphasis';
  examples: string[];
}
```

### 3. State Manager（状态管理器）

负责访谈状态的持久化和恢复。

**状态文件格式：**

```json
{
  "version": "1.0",
  "timestamp": "2026-05-27T10:30:00Z",
  "currentPhase": "architecture",
  "completedPhases": ["projectExploration", "agentPersonality"],
  "responses": {
    "projectExploration": { ... },
    "agentPersonality": { ... }
  },
  "metadata": {
    "totalDuration": 300,
    "phasesCompleted": 2,
    "phasesRemaining": 2
  }
}
```

### 4. Document Generator（文档生成器）

负责根据收集的响应生成各类文档。

**组件结构：**

```
DocumentGenerator
├── TemplateEngine      // 模板处理
├── Renderer            // 内容渲染
├── PathResolver        // 路径解析
├── LayerBuilder        // 分层构建
│   ├── PlatformLayerBuilder
│   ├── DomainLayerBuilder
│   ├── ApplicationLayerBuilder
│   ├── InterfaceLayerBuilder
│   └── MemoryLayerBuilder
└── AgentEntryBuilder   // Agent 入口文件构建
```

---

## 数据模型

### Skill 元数据模型

```yaml
# SKILL.md frontmatter
name: harness-skill
description: |
  访谈式技能，用于创建跨平台兼容的 Harness Engineering 文档系统。
  当用户需要创建项目文档、架构设计、Agent 指令文件时触发。
  触发词：创建文档系统、生成 harness、项目文档、AI Agent 配置。
license: MIT
compatibility: Designed for Kiro IDE
metadata:
  version: "1.0.0"
  author: "Harness Team"
  keywords: ["documentation", "architecture", "agent", "interview"]
```

### 文档模板模型

每个文档类型对应一个模板：

```typescript
interface DocumentTemplate {
  name: string;
  type: DocumentType;
  required: boolean;
  conditional?: (response: InterviewResponse) => boolean;
  sections: TemplateSection[];
  placeholders: Placeholder[];
}

type DocumentType = 
  | 'design' | 'architecture' | 'brain' | 'schema' | 'prd' 
  | 'glossary' | 'constraints' | 'voice' | 'language' 
  | 'wireframe' | 'prototype' | 'search'
  | 'domain-model' | 'business-rules' | 'use-cases' | 'bugs' | 'todos'
  | 'project-structure' | 'code-templates' | 'test-strategy' | 'ci-cd'
  | 'user-guide' | 'api-docs' | 'deployment'
  | 'memory' | 'decisions' | 'patterns';

interface TemplateSection {
  title: string;
  level: number;
  content: string | ((response: InterviewResponse) => string);
  required: boolean;
}

interface Placeholder {
  key: string;
  description: string;
  defaultValue?: string;
  transform?: (value: any) => string;
}
```

### Harness Map 模型

```typescript
interface HarnessMap {
  sections: MapSection[];
  generatedAt: string;
  version: string;
}

interface MapSection {
  layer: 'platform' | 'domain' | 'application' | 'interface' | 'memory' | 'agent-entry';
  title: string;
  documents: MapDocument[];
}

interface MapDocument {
  name: string;
  path: string;
  description: string;
  generated: boolean;
}
```

---

## 目录结构

### Skill 目录结构

```
harness-skill/
├── SKILL.md                    # Skill 主文件
├── scripts/                    # 可执行脚本
│   ├── validate-project.sh     # 验证项目目录
│   └── generate-structure.py   # 生成目录结构
├── references/                 # 参考文档
│   ├── document-types.md       # 文档类型说明
│   ├── interview-guide.md      # 访谈指南
│   ├── template-spec.md        # 模板规范
│   └── agent-compatibility.md  # Agent 兼容性说明
└── assets/                     # 模板资产
    ├── templates/              # 文档模板
    │   ├── design.md.tmpl
    │   ├── architecture.md.tmpl
    │   ├── brain.md.tmpl
    │   └── ...
    └── examples/               # 示例输出
        ├── simple-project/
        └── voice-enabled-app/
```

### 生成的 Harness Engineering 系统目录结构

```
project-root/
├── harness-map.md              # 中央导航索引
├── AGENTS.md                   # 通用 Agent 入口
├── CLAUDE.md                   # Claude 专用入口
├── .cursor/
│   └── rules/
│       └── harness.mdc         # Cursor 规则
├── .windsurf/
│   └── rules/
│       └── harness.md          # Windsurf 规则
├── harness/
│   ├── platform/               # Platform 层
│   │   ├── design.md
│   │   ├── architecture.md
│   │   ├── brain.md
│   │   ├── schema.md
│   │   ├── prd.md
│   │   ├── glossary.md
│   │   ├── constraints.md
│   │   ├── language.md
│   │   ├── wireframe.md
│   │   ├── prototype.md
│   │   ├── search.md
│   │   └── voice.md            # 仅语音产品生成
│   ├── domain/                 # Domain 层
│   │   ├── domain-model.md
│   │   ├── business-rules.md
│   │   ├── use-cases.md
│   │   ├── bugs.md
│   │   └── todos.md
│   ├── application/            # Application 层
│   │   ├── project-structure.md
│   │   ├── code-templates.md
│   │   ├── test-strategy.md
│   │   └── ci-cd.md
│   └── interface/              # Interface 层
│       ├── user-guide.md
│       ├── api-docs.md
│       └── deployment.md
├── memory/                     # Memory 层
│   ├── memory.md
│   ├── decisions.md
│   └── patterns.md
└── .harness-skill-state.json   # 访谈状态（临时）
```

---

## 访谈流程设计

### Phase 1: 项目探索（Project Exploration）

```
┌────────────────────────────────────────────────────────────┐
│                    项目探索阶段                              │
├────────────────────────────────────────────────────────────┤
│  问题 1: 项目名称和描述                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 请告诉我您的项目名称和简短描述：                         │  │
│  │ 项目名称: [_______________]                           │  │
│  │ 项目描述: [_______________]                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  问题 2: 项目目标和成功标准                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 您的项目主要目标是什么？(可输入多个，回车结束)           │  │
│  │ 目标 1: [_______________]                             │  │
│  │ 目标 2: [_______________]                             │  │
│  │ [+ 添加更多]                                          │  │
│  │                                                       │  │
│  │ 如何衡量项目成功？                                      │  │
│  │ 标准: [_______________]                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  问题 3: 目标用户                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 谁会使用这个产品？                                       │  │
│  │ 用户类型: [_______________]                            │  │
│  │ 主要用例: [_______________]                            │  │
│  │ [+ 添加更多用户]                                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  问题 4: 核心功能                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 产品需要哪些核心功能？请按优先级排序：                    │  │
│  │ 1. [高优先级] [_______________]                        │  │
│  │ 2. [中优先级] [_______________]                        │  │
│  │ 3. [低优先级] [_______________]                        │  │
│  │ [+ 添加更多功能]                                        │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### Phase 2: Agent 性格（Agent Personality）

```
┌────────────────────────────────────────────────────────────┐
│                    Agent 性格阶段                            │
├────────────────────────────────────────────────────────────┤
│  问题 1: 语音产品检测                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 您的产品是否包含语音交互功能？                           │  │
│  │ ○ 是 → 生成 voice.md                                   │  │
│  │ ○ 否 → 跳过 voice.md                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  [如果选择"是"，显示以下问题]                                 │
│                                                             │
│  问题 2: Agent 语调                                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ AI Agent 应该使用什么语调？                             │  │
│  │ ○ 专业正式                                              │  │
│  │ ○ 友好亲切                                              │  │
│  │ ○ 简洁高效                                              │  │
│  │ ○ 技术导向                                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  问题 3: 响应风格                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Agent 如何回应用户？                                     │  │
│  │ 响应长度: [简短]────[适中]────[详细]                    │  │
│  │ 是否使用填充词? ○ 是 ○ 否                               │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### Phase 3: 架构（Architecture）

```
┌────────────────────────────────────────────────────────────┐
│                      架构阶段                                │
├────────────────────────────────────────────────────────────┤
│  问题 1: 技术栈                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 编程语言:                                               │  │
│  │ ○ TypeScript  ○ Python  ○ Go  ○ Java  ○ 其他: [___]   │  │
│  │                                                       │  │
│  │ 前端框架:                                               │  │
│  │ ○ React  ○ Vue  ○ Angular  ○ Svelte  ○ 无  ○ 其他     │  │
│  │                                                       │  │
│  │ 后端框架:                                               │  │
│  │ ○ Express  ○ FastAPI  ○ Spring Boot  ○ 无  ○ 其他     │  │
│  │                                                       │  │
│  │ 数据库:                                                 │  │
│  │ ○ PostgreSQL  ○ MySQL  ○ MongoDB  ○ SQLite  ○ 其他    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  问题 2: 架构模式                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 选择架构模式:                                           │  │
│  │ ○ 单体应用 (Monolith)                                   │  │
│  │ ○ 微服务 (Microservices)                                │  │
│  │ ○ 无服务器 (Serverless)                                 │  │
│  │ ○ 混合架构 (Hybrid)                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  问题 3: 部署配置                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 云服务商: ○ AWS  ○ GCP  ○ Azure  ○ 其他  ○ 无         │  │
│  │ 容器化:   ○ Docker  ○ Kubernetes  ○ 无                │  │
│  │ CI/CD:    ○ GitHub Actions  ○ GitLab CI  ○ 其他       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  问题 4: 第三方集成                                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 是否需要集成第三方服务？                                 │  │
│  │ 服务名称: [_______________]                            │  │
│  │ 集成类型: ○ API  ○ SDK  ○ 托管服务                     │  │
│  │ [+ 添加更多集成]                                        │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### Phase 4: 原型规范（Prototype Specs）

```
┌────────────────────────────────────────────────────────────┐
│                    原型规范阶段                              │
├────────────────────────────────────────────────────────────┤
│  问题 1: 输出格式                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 选择原型输出格式:                                       │  │
│  │ ○ HTML       - 可交互的 HTML 原型                      │  │
│  │ ○ Markdown   - 文档形式的线框图                        │  │
│  │ ○ WireScript - Lisp 风格的线框图语法                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  问题 2: 保真度级别                                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 原型保真度:                                             │  │
│  │ ○ 低保真 - 简单线框图，快速迭代                         │  │
│  │ ○ 中保真 - 带注释的线框图                               │  │
│  │ ○ 高保真 - 接近最终设计的原型                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  问题 3: 组件结构（根据输出格式动态显示）                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ [如果选择 HTML]                                         │  │
│  │ CSS 框架: ○ Tailwind  ○ Bootstrap  ○ 自定义           │  │
│  │                                                       │  │
│  │ [如果选择 Markdown]                                     │  │
│  │ 文档风格: ○ 简洁  ○ 详细  ○ 技术文档风格                │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### 访谈总结与确认

```
┌────────────────────────────────────────────────────────────┐
│                      访谈总结                                │
├────────────────────────────────────────────────────────────┤
│  ═══ 项目探索 ═══                                            │
│  项目名称: [用户输入]                                         │
│  项目目标: [用户输入]                                         │
│  目标用户: [用户输入]                                         │
│  核心功能: [用户输入]                                         │
│                                                             │
│  ═══ Agent 性格 ═══                                          │
│  语音产品: [是/否]                                           │
│  语调风格: [用户选择]                                         │
│                                                             │
│  ═══ 架构 ═══                                                │
│  技术栈: [用户选择]                                           │
│  架构模式: [用户选择]                                         │
│  部署配置: [用户选择]                                         │
│                                                             │
│  ═══ 原型规范 ═══                                            │
│  输出格式: [用户选择]                                         │
│  保真度: [用户选择]                                           │
│                                                             │
│  ═══ 将生成的文档 ═══                                        │
│  ✓ harness-map.md (中央索引)                                │
│  ✓ Platform 层 (12 个文档)                                   │
│  ✓ Domain 层 (5 个文档)                                      │
│  ✓ Application 层 (4 个文档)                                 │
│  ✓ Interface 层 (3 个文档)                                   │
│  ✓ Memory 层 (3 个文档)                                      │
│  ✓ Agent 入口文件 (4 个文件)                                  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ [确认并生成]    [返回修改]    [取消]                    │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

---

## 文档生成流程

### 生成顺序

```
1. harness-map.md (首先生成，作为骨架)
        │
        ▼
2. Platform Layer (基础文档)
   ├── design.md
   ├── architecture.md
   ├── brain.md
   ├── schema.md
   ├── prd.md
   ├── glossary.md
   ├── constraints.md
   ├── language.md
   ├── wireframe.md
   ├── prototype.md
   ├── search.md
   └── voice.md (条件生成)
        │
        ▼
3. Domain Layer (业务文档)
   ├── domain-model.md
   ├── business-rules.md
   ├── use-cases.md
   ├── bugs.md
   └── todos.md
        │
        ▼
4. Application Layer (实现文档)
   ├── project-structure.md
   ├── code-templates.md
   ├── test-strategy.md
   └── ci-cd.md
        │
        ▼
5. Interface Layer (交互文档)
   ├── user-guide.md
   ├── api-docs.md
   └── deployment.md
        │
        ▼
6. Memory Layer (记忆系统)
   ├── memory.md
   ├── decisions.md
   └── patterns.md
        │
        ▼
7. Agent Entry Points (入口文件)
   ├── AGENTS.md
   ├── CLAUDE.md
   ├── .cursor/rules/harness.mdc
   └── .windsurf/rules/harness.md
        │
        ▼
8. 更新 harness-map.md (最终索引更新)
```

### 条件生成逻辑

| 文档 | 生成条件 |
|------|---------|
| `voice.md` | `agentPersonality.voiceEnabled === true` |
| `wireframe.md` | 始终生成 |
| `prototype.md` | 始终生成 |
| `search.md` | 始终生成 |
| `language.md` | 始终生成（默认与访谈语言一致） |

---

## 跨 Agent 兼容性设计

### AGENTS.md 模板

```markdown
# Agent Instructions

This project uses the Harness Engineering documentation system.

## Navigation

Start with [harness-map.md](./harness-map.md) for a complete overview of all documentation.

## Core Documents

| Layer | Path | Purpose |
|-------|------|---------|
| Platform | [harness/platform/](./harness/platform/) | Design and architecture |
| Domain | [harness/domain/](./harness/domain/) | Business logic |
| Application | [harness/application/](./harness/application/) | Implementation |
| Interface | [harness/interface/](./harness/interface/) | User interaction |
| Memory | [memory/](./memory/) | Session context |

## Usage Instructions

1. Read `harness-map.md` to understand the project structure
2. Consult `harness/platform/design.md` for product vision
3. Check `memory/decisions.md` for architectural decisions
4. Follow conventions in `harness/application/code-templates.md`

## Agent-Specific Notes

- For code changes, check `harness/application/test-strategy.md` first
- For API modifications, update `harness/interface/api-docs.md`
- For new features, document in `harness/domain/use-cases.md`
```

### CLAUDE.md 模板

```markdown
# Claude Code Instructions

## Project Context

This project uses the Harness Engineering system. Start by reading [harness-map.md](./harness-map.md).

## Memory Integration

This project uses a three-layer memory architecture:

1. **In-Context**: Current conversation
2. **Memory Layer**: [memory/memory.md](./memory/memory.md) - Persistent context index
3. **Project Config**: This file (CLAUDE.md)

## Key Files

- Design: [harness/platform/design.md](./harness/platform/design.md)
- Architecture: [harness/platform/architecture.md](./harness/platform/architecture.md)
- Decisions: [memory/decisions.md](./memory/decisions.md)
- Patterns: [memory/patterns.md](./memory/patterns.md)

## Workflow

1. Before starting, read the relevant documents from harness/platform/
2. Check memory/decisions.md for existing architectural decisions
3. After making changes, update memory/decisions.md if needed
4. Run tests per harness/application/test-strategy.md
```

### .cursor/rules/harness.mdc 模板

```markdown
---
applyTo: "**/*"
---

# Cursor Rules for Harness Project

## Project Overview

Read [harness-map.md](../harness-map.md) for complete documentation structure.

## Coding Standards

See [harness/application/code-templates.md](../harness/application/code-templates.md) for code patterns.

## Testing

Follow test strategy in [harness/application/test-strategy.md](../harness/application/test-strategy.md).

## Architecture

Consult [harness/platform/architecture.md](../harness/platform/architecture.md) before structural changes.
```

---

## 错误处理设计

### 错误类型

```typescript
enum HarnessErrorType {
  // 访谈错误
  INTERVIEW_INTERRUPTED = 'INTERVIEW_INTERRUPTED',
  INVALID_RESPONSE = 'INVALID_RESPONSE',
  STATE_CORRUPTION = 'STATE_CORRUPTION',
  
  // 生成错误
  TEMPLATE_NOT_FOUND = 'TEMPLATE_NOT_FOUND',
  PERMISSION_DENIED = 'PERMISSION_DENIED',
  DISK_FULL = 'DISK_FULL',
  ENCODING_ERROR = 'ENCODING_ERROR',
  
  // 验证错误
  PATH_INVALID = 'PATH_INVALID',
  MARKDOWN_INVALID = 'MARKDOWN_INVALID',
}

interface HarnessError {
  type: HarnessErrorType;
  message: string;
  context: {
    phase?: string;
    document?: string;
    path?: string;
  };
  recoverable: boolean;
  recoveryOptions?: string[];
}
```

### 错误恢复策略

| 错误类型 | 恢复策略 |
|---------|---------|
| INTERVIEW_INTERRUPTED | 从状态文件恢复，继续上次进度 |
| INVALID_RESPONSE | 显示验证错误，重新提示 |
| TEMPLATE_NOT_FOUND | 使用默认模板，记录警告 |
| PERMISSION_DENIED | 显示权限错误，提供解决方案 |
| DISK_FULL | 保留已生成文档，提示清理空间 |

---

## 性能考量

### 优化策略

1. **渐进式生成**：按层级顺序生成，用户可使用部分输出
2. **模板缓存**：预加载常用模板到内存
3. **并行生成**：同一层级内的文档可并行生成
4. **增量更新**：重新生成时只更新变化的文档

### 性能目标

| 指标 | 目标值 |
|------|--------|
| 访谈响应时间 | < 2 秒 |
| 单文档生成时间 | < 5 秒 |
| 完整生成时间 | < 60 秒 |
| 状态文件大小 | < 100 KB |
| 总输出大小 | < 5 MB |

---

## 安全考量

### 文件操作安全

1. **路径验证**：所有路径必须在项目目录内
2. **覆盖确认**：已存在的文件需要用户确认才能覆盖
3. **权限检查**：生成前检查写权限

### 数据安全

1. **本地存储**：所有访谈数据仅存储在本地
2. **状态文件清理**：生成完成后删除状态文件
3. **无外部传输**：不向外部服务器发送任何数据

---

## 测试策略

### 单元测试

- Interview Orchestrator 状态转换
- Response Collector 数据验证
- Template Engine 占位符解析
- Path Resolver 路径验证

### 集成测试

- 完整访谈流程
- 文档生成端到端
- 状态持久化和恢复
- 跨 Agent 文件兼容性

### 端到端测试

- 从访谈到生成的完整流程
- 不同项目类型的文档输出
- 中断恢复场景

---

## 附录

### A. 文档类型清单

| 层级 | 文档 | 必需 | 条件 |
|------|------|------|------|
| Platform | design.md | ✓ | - |
| Platform | architecture.md | ✓ | - |
| Platform | brain.md | ✓ | - |
| Platform | schema.md | ✓ | - |
| Platform | prd.md | ✓ | - |
| Platform | glossary.md | ✓ | - |
| Platform | constraints.md | ✓ | - |
| Platform | language.md | ✓ | - |
| Platform | wireframe.md | ✓ | - |
| Platform | prototype.md | ✓ | - |
| Platform | search.md | ✓ | - |
| Platform | voice.md | ✗ | voiceEnabled=true |
| Domain | domain-model.md | ✓ | - |
| Domain | business-rules.md | ✓ | - |
| Domain | use-cases.md | ✓ | - |
| Domain | bugs.md | ✓ | - |
| Domain | todos.md | ✓ | - |
| Application | project-structure.md | ✓ | - |
| Application | code-templates.md | ✓ | - |
| Application | test-strategy.md | ✓ | - |
| Application | ci-cd.md | ✓ | - |
| Interface | user-guide.md | ✓ | - |
| Interface | api-docs.md | ✓ | - |
| Interface | deployment.md | ✓ | - |
| Memory | memory.md | ✓ | - |
| Memory | decisions.md | ✓ | - |
| Memory | patterns.md | ✓ | - |
| Entry | AGENTS.md | ✓ | - |
| Entry | CLAUDE.md | ✓ | - |
| Entry | .cursor/rules/ | ✓ | - |
| Entry | .windsurf/rules/ | ✓ | - |

### B. 参考资源

- [Agent Skills Specification](https://agentskills.io/specification)
- [Kiro Skills Documentation](https://kiro.dev/docs/skills/)
- [Claude Code Memory Architecture](https://www.mindstudio.ai/blog/claude-code-source-leak-memory-architecture)
- [Voice AI Prompting Guide](https://docs.vapi.ai/prompting-guide)
- [WireScript Documentation](https://wirescript.org/)
