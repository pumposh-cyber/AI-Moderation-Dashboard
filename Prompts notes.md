# **AI Development SOP & Resource Hub**

This document provides a Standard Operating Procedure (SOP) for building full-stack applications with AI, followed by a curated list of resources for prompt engineering and AI-assisted development.

## **SOP: The Phased Full-Stack Application Build**

This document provides a complete Standard Operating Procedure (SOP) for building, testing, and deploying a modern full-stack application using Cursor.

These phases should be executed sequentially. For each step, the provided prompt template must be copied, and its placeholders (e.g., \[PLACEHOLDERS\]) must be populated with project-specific details. The completed prompt is then executed using the @vibe command within the Cursor environment.

### **Phase 1: Backend Scaffolding**

**Goal:** The objective of this phase is to establish the foundational backend API, including data models and directory structure.

**Instructions:** This prompt should be executed from the project's root directory, which must be empty.

**Prompt:**

Create the **backend** for a **\[APP\_NAME, e.g., "Notes App"\]** in a new /backend folder.

**Plan:**

1. **Stack:** Use **\[BACKEND\_FRAMEWORK, e.g., FastAPI\]** with **\[LANGUAGE, e.g., Python\]**.  
2. **Database:** Set up **\[ORM, e.g., SQLAlchemy\]** to connect to a **\[DATABASE\_TYPE, e.g., SQLite\]** database file (backend/dev.db). This is for development only.  
3. **Models:** Define a database model for **\[PRIMARY\_MODEL, e.g., "Note"\]** with fields: **\[e.g., id: int, content: str, created\_at: datetime\]**.  
4. **API:** Create CRUD API endpoints (GET list, GET one, POST, PUT, DELETE) for the **\[PRIMARY\_MODEL\]** under an /api prefix (e.g., /api/notes).  
5. **Middleware:** Add **CORS** middleware allowing all origins (\*) for development.  
6. **Dependencies:** Create a **\[DEPENDENCY\_FILE, e.g., requirements.txt\]** with all necessary libraries (fastapi, uvicorn, sqlalchemy, etc.).

### **Phase 2: Backend Testing & CI**

**Goal:** This phase introduces unit testing and a Continuous Integration (CI) pipeline to validate backend reliability prior to frontend development.

**Instructions:** This prompt must be executed from within the newly created /backend directory.

**Prompt:**

Let's add testing and CI to our /backend project.

**Plan:**

1. **Test Setup:** Add **\[TEST\_FRAMEWORK, e.g., pytest\]** and **\[HTTP\_CLIENT, e.g., httpx\]** to requirements.txt.  
2. **Test File:** Create a test\_main.py file.  
3. **Test Case:** Write a simple unit test for the GET /api/\[PRIMARY\_MODEL\_PLURAL, e.g., notes\] endpoint. Use the TestClient to make a request and assert a 200 status code.  
4. **CI Pipeline:** Create a GitHub Actions workflow at .github/workflows/backend.yml.  
5. **CI Triggers:** Trigger the workflow on: push and pull\_request for paths in backend/\*\*.  
6. **CI Job:** The job should run on ubuntu-latest, set up Python, set the working-directory to ./backend, install dependencies, and run **\[TEST\_COMMAND, e.g., pytest\]**.

### **Phase 3: Frontend Scaffolding**

**Goal:** The objective of this phase is to construct the frontend application that will consume the backend API.

**Instructions:** This prompt should be executed from the root directory (which contains the /backend folder).

**Prompt:**

Create the **frontend** for our **\[APP\_NAME\]** in a new /frontend folder.

**Plan:**

1. **Stack:** Use **\[FRONTEND\_FRAMEWORK, e.g., React\]** with **\[BUILD\_TOOL, e.g., Vite\]**.  
2. **Styling:** Install and configure **\[STYLING\_SOLUTION, e.g., Tailwind CSS\]**.  
3. **API Client:** Install **\[HTTP\_CLIENT, e.g., axios\]**.  
4. **Main Component:** In src/App.jsx, create a component to manage the **\[PRIMARY\_MODEL\_PLURAL\]**.  
5. **UI:** Render a simple UI with:  
   * A form/input to create a new **\[PRIMARY\_MODEL\]**.  
   * A list to display all **\[PRIMARY\_MODEL\_PLURAL\]**.  
6. **API Connection:** Write the fetch, create, and delete functions using **\[HTTP\_CLIENT\]**. Hardcode the API baseURL to http://127.0.0.1:8000 for now.

### **Phase 4: Frontend Testing & CI**

**Goal:** This phase implements component tests and a parallel CI pipeline for the frontend application.

**Instructions:** This prompt must be executed from within the newly created /frontend directory.

**Prompt:**

Let's add testing and CI to our /frontend project.

**Plan:**

1. **Test Setup:** Install **\[TEST\_FRAMEWORK, e.g., vitest\]**, **\[TESTING\_LIBRARY, e.g., @testing-library/react\]**, and jsdom as dev dependencies.  
2. **Config:** Update vite.config.js to configure **\[TEST\_FRAMEWORK\]** (e.g., set globals: true, environment: 'jsdom').  
3. **package.json:** Add a "test": "\[TEST\_COMMAND, e.g., vitest\]" script.  
4. **Test File:** Create src/App.test.jsx.  
5. **Test Case:** Write a simple component test that renders the App component and asserts that the main title (e.g., "\[APP\_NAME\]") is visible on the screen.  
6. **CI Pipeline:** Create a GitHub Actions workflow at .github/workflows/frontend.yml.  
7. **CI Triggers:** Trigger it on: push and pull\_request for paths in frontend/\*\*.  
8. **CI Job:** The job should run on ubuntu-latest, set up Node.js, set the working-directory to ./frontend, run npm install, and run npm run test.

### **Phase 5: Production Readiness (Auth & DB)**

**Goal:** This phase secures the application with authentication and upgrades the database to a production-grade solution.

**Instructions:** Execute the following two prompts, one in each respective directory.

**Prompt for Backend (run in /backend):**

Upgrade the /backend for production.

1. **Auth:** Integrate **\[AUTH\_PROVIDER, e.g., Clerk\]**. Add clerk-python to requirements.txt.  
2. **Protection:** Create a dependency to protect all API endpoints (except health checks).  
3. **Model:** Modify the **\[PRIMARY\_MODEL\]** model to include a user\_id: str (with index=True).  
4. **Logic:** Update all CRUD endpoints to be user-specific (e.g., only fetch notes for the authenticated user, associate new notes with them).  
5. **Database:** Add psycopg2-binary (for Postgres) and python-dotenv. Change the SQLAlchemy DATABASE\_URL in main.py to read from a DATABASE\_URL environment variable.

**Prompt for Frontend (run in /frontend):**

Upgrade the /frontend for production.

1. **Auth:** Install **\[AUTH\_PROVIDER\_SDK, e.g., @clerk/clerk-react\]**.  
2. **Providers:** Wrap the app in \<ClerkProvider\>.  
3. **UI:** Use \<SignedIn\>, \<SignedOut\>, and \<UserButton\> to create a login flow and protect the app content.  
4. **API Client:** Create an axios interceptor that uses Clerk's getToken() hook to automatically add the Authorization header to all API requests.  
5. **Environment:** Create a .env file for VITE\_CLERK\_PUBLISHABLE\_KEY and VITE\_API\_URL.

### **Phase 6: Deployment & Observability**

**Goal:** This final phase prepares the applications for deployment and integrates monitoring/bug tracking services.

**Instructions:** Execute these two final prompts, one in each respective directory.

**Prompt for Backend (run in /backend):**

Prepare the /backend for deployment to **\[BACKEND\_HOST, e.g., Render\]**.

1. **Start Command:** Ensure uvicorn is set to run on host 0.0.0.0 and use the $PORT environment variable.  
2. **Monitoring:** Add the **\[MONITORING\_SDK, e.g., sentry-sdk\[fastapi\]\]** to requirements.txt.  
3. **Initialize:** Initialize the SDK in main.py, reading the DSN from a SENTRY\_DSN environment variable.  
4. **Health Check:** Add a new, unauthenticated GET /api/health endpoint that returns {"status": "ok"} for the hosting service.

**Prompt for Frontend (run in /frontend):**

Prepare the /frontend for deployment to **\[FRONTEND\_HOST, e.g., Vercel\]**.

1. **Monitoring:** Install **\[MONITORING\_SDK, e.g., @sentry/react\]**.  
2. **Initialize:** Initialize the SDK in main.jsx, reading the DSN from VITE\_SENTRY\_DSN.  
3. **Deployment Config:** Create a vercel.json file. Add a rewrites rule to proxy all requests from /api/:path\* to the production VITE\_API\_URL. This hides the backend URL from the user.

## **My Curated Resource List**

A collection of high-quality resources for AI-assisted development.

### **1\. General Prompt Engineering**

* [**dair-ai/Prompt-Engineering-Guide**](https://github.com/dair-ai/Prompt-Engineering-Guide)  
  * **What it is:** The most comprehensive and academic guide to prompt engineering. It covers everything from basic prompting to advanced techniques like Chain of Thought and RAG.  
  * **Use this for:** Gaining a deep theoretical understanding of prompt efficacy.  
* [**f/awesome-chatgpt-prompts**](https://github.com/f/awesome-chatgpt-prompts)  
  * **What it is:** A massive, community-driven list of prompts for various roles (e.g., "Act as a Linux Terminal," "Act as a JavaScript Developer").  
  * **Use this for:** Sourcing inspiration and locating pre-defined, role-specific prompts.  
* [**openai/openai-cookbook**](https://github.com/openai/openai-cookbook)  
  * **What it is:** The official collection of examples and code snippets from OpenAI.  
  * **Use this for:** Acquiring practical knowledge for API utilization, including function calling, embeddings, and fine-tuning.

### **2\. "Vibe Coding" & Cursor Resources**

* [**instructa/ai-prompts**](https://github.com/instructa/ai-prompts)  
  * **What it is:** A curated set of prompts and "rules" specifically for tools like Cursor, GitHub Copilot, and Zed.  
  * **Use this for:** Locating pre-configured .cursor/rules files for project integration to enforce consistent AI behavior (e.g., "Always use Tailwind CSS").  
* [**VibeCodex.io**](https://vibecodex.io/)  
  * **What it is:** A repository of practical, tactical prompts designed for rapid, generative coding sessions. It focuses on maintaining developer focus and productivity.  
  * **Use this for:** Situational prompts, such as code stub generation, style conversion, or rapid debugging.  
* [**The Ultimate Vibe Coding Guide (Reddit)**](https://www.reddit.com/r/ClaudeAI/comments/1kivv0w/the_ultimate_vibe_coding_guide/)  
  * **What it is:** An informative Reddit discussion detailing a comprehensive workflow for AI-assisted development. This resource emphasizes the overall process rather than individual prompt construction.  
  * **Use this for:** Understanding high-level strategies, including planning, rule implementation, and feature decomposition.

### **3\. AI-Driven Development & Agentic Frameworks**

* [**kyrolabs/awesome-agents**](https://github.com/kyrolabs/awesome-agents)  
  * **What it is:** A comprehensive list of autonomous AI agents and agentic frameworks, representing an advanced area beyond fundamental prompt engineering.  
  * **Use this for:** Discovering advanced agentic systems such as MetaGPT, OpenHands, and Devika that aim to automate complex development tasks.  
* [**Automating Cursor (Medium Article)**](https://medium.com/@nick.rios/my-new-three-step-process-for-creating-enterprise-apps-with-cursor-ide-1-000-ai-prompts-and-a-37013f8477a6)  
  * **What it is:** An in-depth analysis of utilizing Cursor to build a full-stack system from a "single source of truth" (like an OpenAPI specification).  
  * **Use this for:** Demonstrations of advanced techniques, such as prompting an AI to generate tests and components based on a predefined API contract.  
* [**How to Use Multi-Agents in Cursor 2.0 (Article)**](https://skywork.ai/blog/vibecoding/multi-agents-full-stack-projects/)  
  * **What it is:** A guide on using Cursor's agentic features for full-stack projects, including assigning distinct "agents" to frontend, backend, and database tasks.  
  * **Use this for:** A model for structuring AI-driven projects in a manner analogous to a human development team.