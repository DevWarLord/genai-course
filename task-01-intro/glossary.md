# Glossary

Terms I picked from my research report (research.md) and the intro lecture. I tried to explain them the way I understand them now, I plan to update this file during the course.

**LLM (Large Language Model)** - a big neural network trained on a huge amount of text. It takes text in and gives text out. Most AI tools for developers (Copilot, chat assistants, agents) are built on top of some LLM.

**Token** - a small piece of text that the model works with. It can be a whole word, part of a word or a symbol. Models count input and output in tokens, and API pricing and limits are also in tokens.

**Next-token prediction** - the main idea of how an LLM generates text. It looks at everything before and guesses the most likely next token, adds it, and repeats. A long answer is just this step repeated many times.

**Context window** - the maximum amount of text (in tokens) the model can "see" at once: the prompt, chat history, files, tool results. Everything outside of it the model simply does not know about.

**Prompt** - the input you give to the model: a question, an instruction, examples, code. The result depends a lot on how the prompt is written.

**Prompt engineering** - the skill of writing prompts so the model gives good and stable results. For example giving clear instructions, examples, the expected format, or splitting a task into steps.

**Hallucination** - when the model generates something that looks convincing but is false. For example a method that does not exist or a made-up link. It happens because the model predicts likely text, it does not check facts.

**Grounding** - giving the model real data (documents, search results, code) so its answer is based on facts and not only on what it remembers from training.

**RAG (Retrieval-Augmented Generation)** - an approach where the system first searches for relevant pieces of information in your own data and then adds them into the prompt. This way the model can answer about internal docs that it never saw in training.

**Embedding** - a list of numbers (a vector) that represents the meaning of a text. Texts with similar meaning have close vectors, so you can search by meaning and not only by exact words.

**Vector database** - a database that stores embeddings and can quickly find the most similar ones. Used in RAG. Examples: Pinecone, Qdrant, pgvector.

**Fine-tuning** - additional training of an already trained model on your own smaller dataset, so it gets better at a specific task or style. More expensive and harder to update than RAG.

**Inference** - running an already trained model to get an answer. Training happens once, inference happens on every request, so speed and cost of inference matter a lot in real products.

**AI agent** - a system where the LLM not only answers but decides what to do next by itself: makes a plan, calls tools, checks the result and continues until the goal is reached.

**Agentic harness** - the program around the model that makes it an agent: gives it tools, access to files and terminal, memory, planning, plugins. Claude Code, Codex CLI and Gemini CLI are examples from the lecture.

**Tool calling (function calling)** - the ability of a model to ask the application to run a function, for example "read file X" or "run tests", and get the result back. This is how agents act in the real world.

**MCP (Model Context Protocol)** - an open standard for connecting AI tools to external systems (Jira, GitHub, databases etc.). One MCP server can be used by different AI clients, like a common plug.

**Guardrails** - rules and checks around the model that limit what it can say or do. For example blocking certain topics, asking permission before running a command, or using a sandbox.

**Prompt injection** - an attack where someone hides instructions in the input (a web page, a document, an issue) and the model follows them instead of the original instructions. Very dangerous for agents with access to tools.

**Human in the loop** - a person checks or approves the AI result at important steps before it goes further, for example code review before merge or approving a refund.

**Evals (LLM evaluation)** - testing the quality of an AI system on a set of example tasks with expected results. Like unit tests, but for model answers, to see if a new prompt or model made things better or worse.

**Multimodal model** - a model that works with more than just text: images, audio, video. For example you can send a screenshot and ask to write the HTML for it.

**SLM (Small Language Model)** - a smaller and cheaper model that can run locally or on edge devices. Not as smart as big models but good enough for many simple tasks and better for privacy. Qwen and Nemotron small versions were mentioned in the lecture.

**Vibe coding** - building software by describing what you want in natural language and mostly accepting what the AI generates, without reading the code in detail. Fast for prototypes, risky for production.
