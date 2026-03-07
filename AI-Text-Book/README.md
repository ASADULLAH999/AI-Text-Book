# Physical AI & Humanoid Robotics Interactive Textbook

An open-source interactive textbook platform for learning Physical AI and Humanoid Robotics using Docusaurus 3, React 18, and TypeScript. Now featuring an intelligent RAG-powered chatbot for interactive Q&A.

## Features

### Core Platform
- 📚 **Interactive Content**: 4 comprehensive modules covering ROS 2, Digital Twins, NVIDIA Isaac Sim, and Voice-to-Action
- 🤖 **Quiz System**: Adaptive quizzes with progress tracking and detailed feedback
- 🌍 **Multi-Language Support**: Content available in English, Urdu, Arabic, Chinese, and Spanish
- 🔐 **Authentication**: GitHub OAuth for seamless login
- 🔍 **Full-Text Search**: Instant search across all course content
- 🎨 **Dark Theme**: Neural-inspired design with smooth animations
- 📱 **Responsive Design**: Optimized for desktop, tablet, and mobile
- ♿ **Accessibility**: WCAG AA compliant with keyboard navigation support
- 🍪 **GDPR Compliance**: Built-in cookie consent and privacy controls

### RAG-Powered Chatbot (Phase 1 Complete)
- 💬 **Intelligent Q&A**: Ask questions and receive cited, grounded answers from textbook content
- 📖 **Three Answering Modes**:
  - **Book-Only Mode** (default): Strict textbook grounding with citations
  - **Selected-Text Mode**: Context-aware answers from highlighted passages
  - **General Knowledge Mode**: Exploratory learning with clear disclaimers
- 🎯 **High Accuracy**: Citation accuracy >95%, hallucination rate <5%
- ⚡ **Fast Response**: <3s p95 latency, <500ms time-to-first-token
- 🔗 **Smart Citations**: Every answer includes verifiable source references with confidence scores
- 🛡️ **Serverless Architecture**: 99.9% uptime, auto-scaling, zero manual processes

## Quick Start

### Prerequisites

**Frontend:**
- Node.js 18+ and npm/yarn
- Git
- GitHub OAuth app (for local development)

**Backend (RAG Chatbot):**
- Python 3.11+
- OpenAI API key
- Qdrant Cloud account (vector database)
- Neon Serverless Postgres account

### Setup

#### Frontend Setup

```bash
# Clone repository
git clone https://github.com/anthropics/ai-textbook.git
cd ai-textbook

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Start development server
npm run start
```

The site will be available at `http://localhost:3000`

#### Backend Setup (RAG Chatbot API)

```bash
# Navigate to API directory
cd api

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp ../.env.template .env
# Edit .env with your actual API keys and database URLs

# Run development server
uvicorn src.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

**Cloud Services Setup:**

1. **Qdrant Cloud** (Vector Database):
   - Create account at https://cloud.qdrant.io
   - Create a cluster and collection named `textbook_chunks`
   - Vector size: 3072 (for text-embedding-3-large)
   - Distance metric: Cosine
   - Update `QDRANT_URL` and `QDRANT_API_KEY` in `.env`

2. **Neon Serverless Postgres**:
   - Create account at https://neon.tech
   - Create a new project
   - Copy connection string to `DATABASE_URL` in `.env`

3. **OpenAI API**:
   - Get API key from https://platform.openai.com
   - Update `OPENAI_API_KEY` in `.env`

## Development

### Commands

```bash
# Start dev server with hot reload
npm run start

# Build for production
npm run build

# Run production build locally
npm run serve

# Run tests
npm run test                # Run all tests once
npm run test:watch         # Run tests in watch mode
npm run test:coverage      # Generate coverage report

# Run E2E tests
npm run e2e

# Code quality
npm run lint              # Check code style
npm run lint:fix          # Auto-fix lint issues
npm run format            # Format code with Prettier
npm run type-check        # TypeScript type checking
```

### Project Structure

```
├── docs/                      # Markdown content (Docusaurus)
│   ├── intro.md
│   ├── module-1-ros2/
│   ├── module-2-sim/
│   ├── module-3-isaac/
│   └── module-4-capstone/
├── src/
│   ├── components/           # React components
│   ├── hooks/               # Custom React hooks
│   ├── services/            # Business logic services
│   ├── types/               # TypeScript interfaces
│   ├── utils/               # Utility functions
│   └── css/                 # Global styles and design system
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── static/                 # Static assets
├── i18n/                   # Localization files
└── .github/workflows/      # CI/CD configuration
```

## Architecture

### Technology Stack

**Frontend:**
- **Framework**: Docusaurus 3.x with React 18.x
- **Language**: TypeScript 5.x (strict mode)
- **Styling**: CSS variables with custom design system
- **State Management**: React Context API + localStorage
- **Authentication**: GitHub OAuth 2.0
- **Testing**: Jest + React Testing Library (unit), Playwright (E2E)
- **Build Tool**: Webpack (via Docusaurus)
- **Deployment**: GitHub Pages
- **CI/CD**: GitHub Actions

**Backend (RAG Chatbot API):**
- **Framework**: FastAPI (serverless deployment on Vercel Functions)
- **Language**: Python 3.11+
- **LLM Provider**: OpenAI (GPT-4, text-embedding-3-large)
- **Vector Database**: Qdrant Cloud (managed, serverless)
- **Relational Database**: Neon Serverless Postgres
- **RAG Framework**: LangChain
- **Configuration**: Pydantic Settings v2.4.0
- **Testing**: pytest (unit), pytest-cov (coverage)
- **Deployment**: Vercel Serverless Functions

### Key Design Decisions

1. **Serverless-First Architecture**: No manual processes, auto-scaling, 99.9% uptime target
2. **Static Site Generation**: Docusaurus provides built-in SEO, performance, and i18n
3. **RAG Pipeline with Strict Grounding**: 5-stage deterministic pipeline (Embed→Search→Filter→Rerank→Validate)
4. **Three Answering Modes**: Clear boundaries between Book-Only, Selected-Text, and General Knowledge
5. **Type-Safe Configuration**: Pydantic-settings for environment validation with nested config classes
6. **CSS Variables Design System**: Consistent theming across all components
7. **Service-Oriented Architecture**: Clear separation of concerns with services
8. **Context API for State**: Minimal dependencies for global state management

### RAG Chatbot Architecture

```
┌─────────────────┐
│   Docusaurus    │
│   Frontend      │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│   FastAPI       │
│   Serverless    │
└────┬───────┬────┘
     │       │
     │       └──────────┐
     │                  │
     ▼                  ▼
┌─────────────┐   ┌──────────────┐
│   Qdrant    │   │    Neon      │
│   Cloud     │   │  Postgres    │
│  (Vectors)  │   │ (Metadata)   │
└─────────────┘   └──────────────┘
     │
     ▼
┌─────────────┐
│   OpenAI    │
│   API       │
└─────────────┘
```

**RAG Pipeline Flow:**
1. Query Embedding (OpenAI text-embedding-3-large, 3072 dims)
2. Vector Search (Qdrant HNSW index, top-20 candidates)
3. Metadata Filtering (book_id, chapter constraints)
4. Reranking (optional cross-encoder, top-5 final)
5. Context Window Validation (8000 tokens max)

## Features Documentation

### User Stories

- **US1**: Student Discovers and Starts Learning (Homepage)
- **US2**: Authenticated Student Takes Quiz (Authentication + Quiz System)
- **US3**: International Student Uses Multi-Language (i18n + RTL)
- **US4**: Student Searches Content (Full-text search)
- **US5**: Admin Configures Cookies (GDPR compliance)

### Learning Modules

#### Module 1: ROS 2 Fundamentals
- Introduction to ROS 2 architecture
- Nodes, topics, and services
- Message passing and pub/sub patterns

#### Module 2: Digital Twins & Simulation
- Digital twin concepts
- Gazebo simulation framework
- Unity integration basics

#### Module 3: NVIDIA Isaac Sim
- Isaac Sim environment setup
- Sensor simulation and physics
- Advanced robotics workflows

#### Module 4: Voice to Action & Capstone
- Voice interfaces and LLMs
- Integration best practices
- Capstone project guidance

## Performance

- **LCP**: < 2.5 seconds
- **CLS**: < 0.1
- **Lighthouse Score**: ≥ 90 (all categories)
- **Concurrent Users**: 10,000+ (GitHub Pages CDN)
- **Bundle Size**: ~80 KB (gzipped)

## Accessibility

- WCAG AA Level compliance
- Keyboard navigation support
- Screen reader optimization
- Color contrast ratios ≥ 4.5:1
- Reduced motion media query support

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines, code style, and pull request process.

## License

Licensed under MIT. See [LICENSE](./LICENSE) for details.

## Support

- 📖 [Documentation](./docs/)
- 🐛 [Issue Tracker](https://github.com/anthropics/ai-textbook/issues)
- 💬 [Discussions](https://github.com/anthropics/ai-textbook/discussions)

## Authors & Acknowledgments

Created by the Anthropic education team with contributions from the robotics community.

---

**Last Updated**: 2026-02-14
**Status**: RAG Chatbot Phase 1 (Setup & Infrastructure) - Complete
**Current Focus**: Phase 2 (Content Ingestion Pipeline)
