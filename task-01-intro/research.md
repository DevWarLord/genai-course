# Research: Generative AI applications

Author: Adilet Askarov
Course: Generative AI for Software Development, practical task 1 (Intro)

In this report I looked at 8 areas where generative AI is already used in real products. For each one I wrote what value it gives to business, what is technically hard, what the weak points are, and a few existing tools. I focused more on software development cases because they are closer to my work, but I also added some cases outside of IT.

## 1. Code generation and AI assistants in the IDE

Tools like this suggest code right in the editor. They complete lines, write a whole function from a comment, explain unfamiliar code and answer questions in a chat panel. Under the hood it is an LLM that gets the current file and some nearby files as context and predicts the next tokens. For business the value is simple: developers spend less time on boilerplate, onboarding into a new codebase is faster, and routine stuff like mappers, DTOs or regex takes minutes instead of an hour. Many companies already buy Copilot licenses for all engineers, so it is basically a standard tool now. Non-developers also use these tools for so called vibe coding, when you describe an app in words and accept whatever is generated. It is fine for prototypes but not really for production.

The main technical problem is context. The model only sees what fits into its context window, so in a big project it often does not know about a helper that already exists and writes a duplicate. Suggestions can look correct but call methods that do not exist (hallucinations), use old library versions or have small bugs that are hard to notice. Some vendors offer models adapted to a company's own codebase, but this costs more. There are also concerns about code leaving the company network, licensing of generated code, and juniors who accept suggestions without understanding them. Speed matters too, if inference is slow and suggestions come after 3 seconds, nobody uses them. Companies with strict privacy rules sometimes run a smaller open model on their own servers instead.

Existing implementations:
- GitHub Copilot - https://github.com/features/copilot - AI pair programmer for VS Code, JetBrains and other IDEs, has code completion, chat and agent mode.
- Cursor - https://cursor.com - fork of VS Code built around AI, can edit several files at once from one prompt.
- Amazon Q Developer - https://aws.amazon.com/q/developer/ - coding assistant from AWS, also good for AWS specific questions and Java version upgrades.
- Tabnine - https://www.tabnine.com - code assistant that can be deployed on-premise, popular in companies with strict privacy requirements.

## 2. Coding agents (agentic development)

This is the next step after autocomplete. An AI agent gets a task in natural language ("fix this bug", "add an endpoint for X and cover it with tests"), plans the steps by itself, reads files, runs commands in the terminal, runs tests and changes the code until the task is done. In the lecture these tools were called agentic harnesses. Agents use tool calling to work with the file system, git and the browser, and through MCP they can connect to Jira, databases and other systems. The business value is bigger than for autocomplete. One developer can delegate whole tickets, run several tasks in parallel and spend more time on review and design. It is also useful for boring large scale work like migrations or dependency updates.

But agents are harder to control. Every step can go wrong and errors add up, so a long task can end with a big messy diff. They use a lot of tokens, so the cost can be high. Giving an agent access to a terminal is a security risk: a prompt injection hidden inside a README or an issue can make it run something dangerous. That is why you need guardrails like sandboxes, permission prompts and a human in the loop who reviews the result before merge. The quality also depends a lot on how well the task is described and on project instructions (files like CLAUDE.md or AGENTS.md).

Existing implementations:
- Claude Code - https://claude.com/product/claude-code - agentic coding tool from Anthropic, works in the terminal and IDE, can edit files, run commands and make commits.
- OpenAI Codex - https://openai.com/codex/ - coding agent from OpenAI, available as CLI, IDE extension and cloud agent that can work on tasks in parallel.
- Gemini CLI - https://github.com/google-gemini/gemini-cli - open source terminal agent from Google built on Gemini models.
- Devin - https://devin.ai - autonomous "AI software engineer" from Cognition that takes tickets and opens pull requests.

## 3. Test generation and QA automation

Here GenAI writes unit tests, integration tests and test data, or turns test cases written in plain English into automated scripts. It can look at a class and generate tests for edge cases that a person would forget, or help with TDD by writing tests first from the requirements. For business this means higher test coverage without hiring more QA engineers, faster regression and less legacy code that nobody wants to touch because there are no tests.

The weak point is that generated tests often check what the code does, not what it should do. If the code has a bug, the AI can write a test that "confirms" the bug. Tests can be too shallow (only happy path) or too fragile because everything is mocked. Generated test data can contain made-up values that look realistic but break business rules. For UI tests the app changes all the time, so self-healing locators help, but not always. So a QA engineer still has to review what was generated and decide what is actually important to test.

Existing implementations:
- Diffblue Cover - https://www.diffblue.com - generates Java unit tests automatically (it uses reinforcement learning, not only LLMs).
- Qodo - https://www.qodo.ai - formerly CodiumAI, AI for test generation and code review, works as IDE plugin and in pull requests.
- testRigor - https://testrigor.com - you write end-to-end tests in plain English and AI executes and maintains them.

## 4. Code review and security fixes

AI reviewers look at a pull request and leave comments like a human reviewer: possible bugs, missing null checks, naming, performance, security issues. Security tools go further and suggest a fix for a vulnerability found by a scanner. For a company this saves time of senior developers, makes review faster (PRs do not wait for days) and catches some problems before production. For security teams it helps with huge backlogs of findings, because writing the fix is often slower than finding the issue.

Problems: AI review produces a lot of noise. Many comments are not useful or are just style preferences, and people start ignoring all comments, including the important ones. The model does not know the business logic and the decisions the team made before, so it can suggest "fixes" that break things. It can also miss real issues while sounding confident. For security a wrong fix is dangerous, so every autofix must be checked. Also the code has to be sent to a third party service, which is not always allowed by the client.

Existing implementations:
- CodeRabbit - https://www.coderabbit.ai - AI code review bot for GitHub and GitLab pull requests, writes a summary and line comments.
- GitHub Copilot Autofix - https://docs.github.com/en/code-security/concepts/code-scanning/copilot-autofix-for-code-scanning - suggests fixes for code scanning (CodeQL) alerts.
- Snyk Code (DeepCode AI) - https://snyk.io/platform/deepcode-ai/ - security scanner with AI generated fixes for found vulnerabilities.

## 5. Documentation and internal knowledge search

A big part of a developer's time goes to searching: where is this config, how does this service work, who owns it. GenAI can generate documentation from code (docstrings, README, API docs) and also answer questions over internal docs, Confluence, tickets and chats. Usually this works with RAG. Documents are split into chunks, converted into embeddings and stored in a vector database. For each question the system finds the most similar chunks and puts them into the prompt, so the answer is based on real company data and has links to the source. Business value is faster onboarding, fewer repeated questions to senior people and docs that are not two years out of date.

Technical challenges are mostly about data. If the docs are old or contradict each other, the answers will be wrong too (garbage in, garbage out). Chunking and search quality matter a lot: if retrieval brings the wrong pieces, the model still writes a confident answer. Access rights are tricky, the bot must not show a document to a person who has no access to it. Instead of RAG some teams try fine-tuning a model on their docs, but it is more expensive and the knowledge gets old quickly. Generated docs often describe what the code does in a very general way and miss the "why". And all this needs maintenance, indexes have to be updated when documents change.

Existing implementations:
- Mintlify - https://www.mintlify.com - documentation platform with AI writing help and an assistant that answers questions from the docs.
- Glean - https://www.glean.com - enterprise search and AI assistant over company apps (Slack, Drive, Jira etc.) that respects permissions.
- Notion AI - https://www.notion.com/product/ai - AI inside Notion for writing, summarizing and asking questions about workspace pages.

## 6. Customer support chatbots and AI agents

This is one of the most common uses. A support bot answers customer questions in chat or email, and newer AI agents can also do actions like checking an order status, issuing a refund or changing a booking, using tools connected to the company systems. Answers are grounded in help center articles and policies, often again with RAG. For business the value is very direct: a large part of tickets is resolved without a human, support works 24/7 in many languages, and human agents get help with drafting replies and summarizing long threads.

The risk is that the bot tells something wrong to a real customer, for example promises a refund that does not exist in the policy. There was a known case with Air Canada in 2024, when the company had to pay because its chatbot gave wrong information about a discount. So companies need strict guardrails, a clear handoff to a human when the bot is not sure, and regular evaluation of answers on real conversations. Customers also get annoyed when they cannot reach a person. Prompt injection from users is a real thing here, people try to make the bot ignore its instructions. And the cost per conversation must be lower than a human agent, otherwise there is no point.

Existing implementations:
- Intercom Fin - https://www.intercom.com/fin - AI support agent that answers customers using the company knowledge base and hands off to humans when needed.
- Zendesk AI agents - https://www.zendesk.com/service/ai/ - AI agents and a copilot for support teams inside Zendesk.
- Salesforce Agentforce - https://www.salesforce.com/agentforce/ - platform for building AI agents that work with CRM data in service and sales.

## 7. Data analysis and text-to-SQL

Here the user asks a question in normal language, like "what were sales by region last quarter", and the system writes SQL or Python, runs it and shows a table or a chart. It helps managers and analysts who do not know SQL well, and data teams that are tired of simple ad-hoc requests. The model can also summarize results and point to unusual things, for example a sudden drop in some metric. The business value is faster decisions and less dependency on a small data team.

The hard part is that the model does not know what the columns really mean. "Revenue" can be calculated in three different ways in the same company. Without a semantic layer or good descriptions of tables it writes queries that run fine but return wrong numbers, and this is worse than an error because nobody notices. Large datasets do not fit into the context, so the model works only with schemas and samples. Data privacy is another concern, sending customer data to an external model may not be allowed, so some teams run models locally. Results must be checkable, so good tools always show the generated query.

Existing implementations:
- Databricks AI/BI Genie - https://www.databricks.com/product/ai-bi/genie - business users ask questions about their data in natural language and get answers with the SQL behind them.
- Snowflake Cortex Analyst - https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst - converts questions into SQL using LLMs plus a semantic model that describes business terms.
- Julius AI - https://julius.ai - AI data analyst for spreadsheets and CSV files, builds charts and runs Python for you.

## 8. Content generation: text, images, video, voice

Multimodal models can create marketing texts, product images, training videos with an AI avatar and voiceovers in different languages. For companies this cuts the cost and time of content production. A training video can be made and translated into 20 languages without a studio, and marketing can test many versions of an ad. In software projects it is also used for UI mockups, icons and placeholder content.

Weak points: copyright questions about training data and the output, deepfake risk (voice cloning especially), keeping the brand style consistent, and the "generic" look of AI content that people already recognize. Images still have artifacts, and text inside images is often broken. Image and video generation need a lot of GPU compute, so it gets expensive at scale. Many companies require human review and labeling of AI generated content before publishing.

Existing implementations:
- Adobe Firefly - https://www.adobe.com/products/firefly.html - image and video generation built into Photoshop and other Adobe tools, trained on licensed content.
- Synthesia - https://www.synthesia.io - makes videos with AI avatars from a text script, often used for corporate training.
- ElevenLabs - https://elevenlabs.io - voice generation, voice cloning and dubbing into many languages.
- Midjourney - https://www.midjourney.com - text-to-image model known for high quality artistic images.

## Summary

| # | Use case | Main value | Main risk |
|---|----------|------------|-----------|
| 1 | Code assistants in IDE | less routine coding, faster onboarding | wrong or outdated code, privacy |
| 2 | Coding agents | whole tasks delegated | cost, security, hard to control |
| 3 | Test generation | more coverage with same team | tests that confirm bugs |
| 4 | Code review / security | faster review, faster fixes | noise, wrong fixes |
| 5 | Docs and knowledge search | faster onboarding, less searching | old data, access rights |
| 6 | Support bots | tickets solved without humans | wrong promises to customers |
| 7 | Data analysis / text-to-SQL | self-service analytics | wrong numbers nobody notices |
| 8 | Content generation | cheaper content, localization | copyright, deepfakes |

My conclusions:
- The most mature cases right now are coding assistants and support bots. They have clear ROI and a lot of real products.
- Almost every case has the same core problems: hallucinations, limited context, data privacy and cost.
- The trend is moving from "assistant suggests" to "agent does it". This needs more guardrails and human review, not less.
- The result depends a lot on the data and context you give to the model. In the lecture GenAI was compared to lossy compression, and I think this explains well why a model can be confident and wrong at the same time.
