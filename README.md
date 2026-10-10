# Curated AI resources

A curated collection of AI assistants, models, creative tools, and learning resources. Entries describe useful capabilities rather than permanent rankings.

**Last reviewed: October 10, 2026.** Updated using official product documentation and repositories. Model versions are generally omitted so links remain useful between releases. Access, pricing, and model licenses can change; check the linked documentation when choosing a tool.

## Table of contents

- [Learning](#learning)
- [AI assistants](#ai-assistants)
- [Model families](#model-families)
- [Coding agents and app builders](#coding-agents-and-app-builders)
- [Writing](#writing)
- [Local language models](#local-language-models)
- [Search and research](#search-and-research)
- [Image generation and design](#image-generation-and-design)
  - [Hosted image tools](#hosted-image-tools)
  - [Local image models and interfaces](#local-image-models-and-interfaces)
- [Audio](#audio)
  - [Music and sound](#music-and-sound)
  - [Voice and speech](#voice-and-speech)
  - [Local speech models](#local-speech-models)
- [Video generation](#video-generation)
  - [Hosted video tools](#hosted-video-tools)
  - [Local video models](#local-video-models)
- [Personal agents](#personal-agents)
- [Agent development and integrations](#agent-development-and-integrations)
- [Inference and API providers](#inference-and-api-providers)
- [Evaluations and model discovery](#evaluations-and-model-discovery)
- [Communities and hubs](#communities-and-hubs)
- [Utilities](#utilities)

## Learning

- [NVIDIA: Generative AI Explained](https://learn.nvidia.com/courses/course-detail?course_id=course-v1:DLI+S-FX-07+V1) - Introductory course on generative AI.
- [HarvardX: CS50's Introduction to AI with Python](https://www.edx.org/learn/artificial-intelligence/harvard-university-cs50-s-introduction-to-artificial-intelligence-with-python) - Foundations of AI and machine learning with Python.
- [DeepLearning.AI: AI Python for Beginners](https://www.deeplearning.ai/short-courses/ai-python-for-beginners/) - Beginner course on Python with AI assistance.
- [Prompt Engineering Guide](https://www.promptingguide.ai/) - Prompting techniques, examples, and background on language models.
- [Hugging Face Agents Course](https://huggingface.co/learn/agents-course/en/unit0/introduction) - Free course on building agents that use tools and complete tasks.
- [Hugging Face MCP Course](https://huggingface.co/learn/mcp-course/en/unit0/introduction) - Free course on connecting AI applications to tools and data through the Model Context Protocol.

## AI assistants

- [ChatGPT](https://chatgpt.com/) - General assistant for text, code, images, voice, file analysis, and web research.
- [Claude](https://claude.ai/) - General assistant for writing, coding, document analysis, artifacts, and research.
- [Gemini](https://gemini.google.com/) - Google's multimodal assistant for text, images, voice, and research.
- [Grok](https://grok.com/) - xAI's assistant, with search and image generation through its Imagine models; distinct from the inference provider Groq.
- [DeepSeek](https://www.deepseek.com/en) - Assistant and model developer offering reasoning, coding, APIs, and downloadable model weights.
- [Kimi](https://www.kimi.com/) - Moonshot AI's assistant for research, coding, and knowledge work.
- [Mistral Vibe](https://chat.mistral.ai/) - Mistral's assistant with Work, Code, and Chat modes; [formerly Le Chat](https://help.mistral.ai/en/articles/682992-le-chat-is-now-vibe).

## Model families

Downloadable weights do not necessarily mean an unrestricted open-source model. Licenses can differ between sizes and variants within a family; check the specific model card before using or redistributing weights.

- [Llama](https://github.com/meta-llama/llama-models) - Meta's downloadable language and multimodal models under its community licenses.
- [Mistral](https://docs.mistral.ai/models) - Language, coding, and multimodal models with a mix of open-weight and hosted offerings; licenses vary by model.
- [Qwen](https://qwen.ai/) - Alibaba's language, coding, and multimodal model ecosystem, including downloadable models for local use.
- [Kimi models](https://github.com/MoonshotAI/Kimi-K3) - Moonshot AI's model family for coding, reasoning, and agent workflows.
- [Gemma](https://ai.google.dev/gemma/docs/core) - Google's downloadable model family, distinct from the hosted Gemini service.
- [GLM](https://github.com/zai-org/GLM-5) - Z.ai's model ecosystem for reasoning, coding, and agents.
- [DeepSeek models](https://www.deepseek.com/en/transparency/) - Official model cards and technical information for DeepSeek's downloadable models.

## Coding agents and app builders

- [GitHub Copilot](https://github.com/features/copilot) - Coding assistance and agents across editors, the terminal, and cloud workflows.
- [Claude Code](https://code.claude.com/docs/en/overview) - Coding agent that reads repositories, edits files, and runs commands across terminal, editor, desktop, and web workflows.
- [Codex](https://learn.chatgpt.com/docs/codex/cli) - OpenAI's coding agent for repository changes, command execution, code review, and automation, with CLI, IDE, desktop, and cloud workflows.
- [Cursor](https://cursor.com/docs/agent/overview) - Code editor and agents for repository exploration, implementation, and command execution.
- [Gemini CLI](https://github.com/google-gemini/gemini-cli) - Google's open-source terminal agent for coding and tool-based workflows.
- [OpenCode](https://opencode.ai/) - Open-source coding agent supporting multiple model providers and local endpoints.
- [Cline](https://cline.bot/) - Coding agent with editor and CLI workflows, multiple providers, and local model support.
- [Devin Desktop](https://devin.ai/desktop) - IDE and command center for local and cloud coding agents; the current destination of Windsurf's website.
- [Tabnine](https://www.tabnine.com/) - Coding assistance with enterprise [private deployment options](https://docs.tabnine.com/main/welcome/readme/architecture/deployment-options), including VPC, on-premises, and air-gapped installations.
- [v0](https://v0.app/) - Vercel's application builder, with UI generation, database connections, GitHub synchronization, and deployment.

## Writing

- [Novelcrafter](https://www.novelcrafter.com/features) - Novel planning, drafting, and revision with a story bible, configurable AI connections, and local model support. AI features use your own provider connection.
- [Sudowrite](https://sudowrite.com/) - Fiction writing assistant with story planning, prose generation, and revision tools.

## Local language models

Distinguish the model runtime from the chat interface. A locally installed application may also support cloud models; select local models and endpoints when offline use matters.

- [Ollama](https://docs.ollama.com/) - Model runner and manager with local APIs; also supports cloud models.
- [LM Studio](https://lmstudio.ai/docs/app) - Desktop interface for local models, offline document chat, and local API serving.
- [Open WebUI](https://docs.openwebui.com/) - Self-hosted chat interface with document retrieval, tools, and connections to Ollama or compatible local and hosted providers.
- [llama.cpp](https://github.com/ggml-org/llama.cpp) - Local inference engine with GGUF model support and an API server.
- [GPT4All](https://www.nomic.ai/gpt4all) - Desktop application for running language models locally.
- [text-generation-webui](https://github.com/oobabooga/text-generation-webui) - Web interface for local language models.
- [LocalGPT](https://github.com/PromtEngineer/localGPT) - Private document intelligence platform with local models, document parsing, and retrieval.

## Search and research

- [Perplexity](https://www.perplexity.ai/) - AI search and research with linked sources.
- [ChatGPT Search and research](https://learn.chatgpt.com/docs/web-search) - Web search and deeper investigations within ChatGPT.
- [Claude Research](https://claude.com/resources/articles/research) - Research across multiple sources with citations.
- [Google Search AI Mode](https://blog.google/products-and-platforms/products/search/search-io-2026/) - Conversational and multimodal search within Google Search.
- [Gemini Notebook](https://notebook.google/) - Research and learning grounded in your sources, with summaries and audio overviews; [formerly NotebookLM](https://blog.google/innovation-and-ai/products/gemini-notebook/notebooklm-gemini-notebook/).
- [Elicit](https://elicit.com/industries/edu) - Academic research assistant for finding papers and extracting evidence.
- [Perplexica](https://github.com/ItzCrazyKns/Perplexica) - Self-hosted AI search application.
- [You.com](https://you.com/) - AI search and research tools.

## Image generation and design

### Hosted image tools

- [Midjourney](https://www.midjourney.com/) - Image generation and editing with style and reference controls.
- [ChatGPT Images](https://chatgpt.com/) - Conversational image creation and editing; developers can use the [GPT Image API](https://developers.openai.com/api/docs/guides/image-prompting).
- [Imagen](https://deepmind.google/models/imagen/) - Google's image generation model family.
- [Gemini Image / Nano Banana](https://deepmind.google/models/gemini-image/) - Google's conversational image generation and editing models.
- [FLUX](https://bfl.ai/models/flux-3-image) - Black Forest Labs' hosted image generation and editing models; downloadable variants are listed below.
- [Seedream](https://seed.bytedance.com/en/) - ByteDance's image generation and editing model family.
- [Recraft](https://www.recraft.ai/ai-models/recraft) - Design-oriented image generation, including editable SVG vectors.
- [Ideogram](https://ideogram.ai/) - Image generation with typography and design tools.
- [LetzAI](https://letz.ai/) - Image generation and upscaling.
- [Magnific](https://magnific.ai/) - Image upscaling and enhancement.
- [Freepik](https://www.freepik.com/) - Creative platform with image generation, editing, and multiple model options.
- [Leonardo.Ai](https://leonardo.ai/) - Image generation and editing for creative workflows.
- [Affogato](https://affogato.ai/) - Image and video creation with character consistency tools; formerly RenderNet.

### Local image models and interfaces

- [Stable Diffusion](https://stability.ai/) - Downloadable image model family; commercial use depends on the specific [model license](https://stability.ai/license).
- [FLUX local models](https://github.com/black-forest-labs/flux2) - Downloadable image generation and editing models; some variants use Apache 2.0 while others have noncommercial licenses.
- [Qwen-Image](https://github.com/QwenLM/Qwen-Image-2.1) - Downloadable image generation and editing models; check the chosen weights' license and hardware requirements.
- [ComfyUI](https://www.comfy.org/) - Node-based interface for image, video, and other generative workflows.
- [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui) - Web interface for Stable Diffusion workflows.
- [Forge](https://github.com/lllyasviel/stable-diffusion-webui-forge) - Stable Diffusion web interface derived from AUTOMATIC1111.

## Audio

### Music and sound

- [Suno](https://suno.com/) - Music generation with editing and remix workflows; check current download and usage terms.
- [Udio](https://www.udio.com/) - Music generation. At the review date, [audio, video, and stem downloads are disabled](https://help.udio.com/en/articles/12683565-changes-associated-with-the-universal-music-group-umg-partnership).
- [AudioCraft](https://github.com/facebookresearch/audiocraft) - Meta's local research library for music and sound generation; code is MIT-licensed, while released weights use CC-BY-NC 4.0.

### Voice and speech

- [ElevenLabs](https://elevenlabs.io/) - Speech generation, voice cloning, dubbing, transcription, sound effects, music, and conversational voice agents.

### Local speech models

- [Chatterbox](https://github.com/resemble-ai/chatterbox) - Local speech generation and voice cloning with multilingual and low-latency variants.
- [Kokoro](https://github.com/hexgrad/kokoro) - Lightweight text-to-speech model with Apache-licensed weights.
- [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) - Local speech generation with voice cloning, voice design, and streaming support.
- [XTTS v2 / Coqui TTS](https://github.com/idiap/coqui-ai-TTS) - Local text-to-speech and voice cloning through the maintained Coqui TTS fork; model licenses are separate from the toolkit license.

## Video generation

### Hosted video tools

- [Runway](https://runwayml.com/) - Video generation and editing from text and image inputs.
- [Kling AI](https://kling.ai/quickstart) - Video generation with image references, audio, and scene controls.
- [Google Veo / Flow](https://deepmind.google/models/veo/) - Video generation with audio, reference images, and filmmaking workflows through Flow.
- [Seedance](https://seed.bytedance.com/en/) - ByteDance's video generation model family.
- [FLUX Video](https://bfl.ai/models/flux-3-video) - Black Forest Labs' hosted video generation models.
- [Hedra](https://www.hedra.com/) - Character and avatar video creation.
- [Luma Dream Machine](https://lumalabs.ai/dream-machine) - Video generation and editing with Luma's Ray models.

### Local video models

- [LTX](https://github.com/Lightricks/LTX-2) - Downloadable audio/video generation models and tools for local workflows.
- [Wan](https://github.com/Wan-Video/Wan2.2) - Downloadable video generation models for text and image inputs.

Check each model's license and hardware requirements. ComfyUI can provide workflows for supported video models.

## Personal agents

- [OpenClaw](https://openclaw.ai/) - Personal agent with persistent memory, messaging integrations, and browser, file, and shell tools.
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) - Personal agent with persistent memory, reusable skills, scheduled tasks, and multiple model providers.

## Agent development and integrations

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro) - Open protocol for connecting assistants and agents to tools and data sources.
- [LangChain](https://www.langchain.com/) - Framework and tooling for building language-model applications and agents.
- [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) - Stateful agent orchestration with persistence and human oversight.
- [Langflow](https://www.langflow.org/) - Visual builder for AI applications and agent workflows.

## Inference and API providers

- [Groq](https://console.groq.com/docs/models) - Hosted inference for language and speech models using Groq's hardware; distinct from the assistant Grok.
- [OpenRouter](https://openrouter.ai/) - Unified access to models from multiple developers and inference providers.
- [Replicate](https://replicate.com/docs/topics/models/run-a-model) - Run models through a web playground or API without managing the inference infrastructure.
- [fal](https://fal.ai/) - Hosted inference and APIs for generative image, video, audio, and 3D models.

## Evaluations and model discovery

- [Arena](https://arena.ai/leaderboard) - Human-preference comparisons and leaderboards across model categories.
- [Artificial Analysis](https://artificialanalysis.ai/models/capabilities) - Model capability benchmarks and comparisons, alongside pricing and performance information.

Use these as inputs to a choice, alongside tests on your own tasks. A leaderboard position is not a universal recommendation.

## Communities and hubs

- [Hugging Face](https://huggingface.co/) - Models, datasets, model cards, demos, and learning resources.
- [Civitai](https://civitai.com/) - Community image models, LoRAs, workflows, and examples.

## Utilities

- [Pinokio](https://pinokio.computer/) - Tool for installing and running AI applications locally.
- [prompts.chat](https://prompts.chat/) - Collection of reusable prompt examples, formerly Awesome ChatGPT Prompts.
