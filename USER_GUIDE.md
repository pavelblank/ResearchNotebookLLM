# Research NotebookLM: User Guide

**Version 2.1 · Pavel Blank (pavelblank@gmail.com)**

---

## What is Research NotebookLM?

Research NotebookLM is your **private AI research assistant** that lives entirely on your own computer. You give it documents (PDFs, web articles, YouTube videos) and it reads them for you. Then you can ask it anything about those documents and it will answer using only what it found inside them. No guessing, no making things up.

Think of it like having a very fast, very thorough reading assistant who:
- Reads all your documents so you don't have to read every word
- Remembers everything across all of them at once
- Answers your questions with direct quotes and references
- Never invents facts; if it can't find the answer, it says so

Everything stays on your machine. Nothing is sent to the cloud.

---

## The Three-Panel Workspace

When you open a project (notebook), you see three panels side by side:

```
┌─────────────────┬──────────────────────────┬─────────────────┐
│   LEFT PANEL    │      CENTRE PANEL        │   RIGHT PANEL   │
│                 │                          │                 │
│   Sources       │    Research Chat         │  Notebook Guide │
│   Upload        │                          │                 │
│   Files         │  Ask questions here.     │  AI-generated   │
│   Notes         │  AI answers from your    │  summaries,     │
│                 │  documents only.         │  FAQs, timelines│
└─────────────────┴──────────────────────────┴─────────────────┘
```

You can **hide** either side panel using the buttons in the top bar to get more reading space.

---

## Left Panel: Your Sources

This panel has four tabs:

### Sources Tab
Lists every document you have added to this project. Click on any source to read it in a preview panel above the chat. Each source shows:
- An icon for its type (📄 PDF, 🔗 URL, ▶️ YouTube, 📝 Text)
- The document title
- A **∑ button** (appears when you hover) to ask the AI to summarise just that one source

### Upload Tab
Add new material to your project:
- **Drop a file or click to browse**: supports PDF, Word documents (.docx), plain text (.txt), and Markdown (.md)
- **URLs & YouTube Links**: paste any web page address or YouTube link, one per line, then click **Add Sources**. The system will fetch the page or transcribe the video and make it searchable.

### Files Tab
Shows the raw files that have been saved to your project folder on disk. Mostly for reference; you do not need to use this tab regularly.

### Notes Tab
Your personal notebook within the project. Notes can come from:
- Clicking **Save as Note** on any AI answer in the chat
- Clicking **Save to Notes** on any Guide output
- Typing directly in the text box at the bottom and clicking **Save Note**

Notes are stored permanently in your project and survive page refreshes.

---

## Centre Panel: Research Chat

This is where you talk to the AI about your documents.

**How to use it:**
1. Type your question in the box at the bottom
2. Press **Enter** (or click **Send**)
3. The AI reads through your documents, finds the most relevant passages, and writes an answer
4. Below each AI answer you will see **source chips**, small labels showing which documents the answer came from
5. Hover over any AI answer to see two buttons: **Save as Note** and **Copy**

**Tips:**
- Ask specific questions: *"What does the Smith paper say about carbon emissions?"* works better than *"Tell me about climate"*
- Ask comparative questions: *"How do these sources differ on the topic of pricing?"*
- Ask for evidence: *"What statistics are mentioned about user growth?"*
- If the AI says **"Not found in provided sources"** it means none of your documents contain that information; the system will never guess

**Clear Chat** (bin icon, top right of chat) wipes the conversation history but does not delete your sources or notes.

**Analyse All** button (bottom of left panel) asks the AI to write a full structured analysis of everything in all your sources at once.

---

## Right Panel: Notebook Guide

The Notebook Guide generates structured AI outputs from your sources. It has five tabs:

| Tab | What it generates |
|-----|-------------------|
| 📋 **Briefing** | A short executive summary: what the sources cover, key findings, gaps, and a bottom line. Good for a quick overview before a meeting. |
| 🏷️ **Themes** | The 5-8 main topics or ideas that appear across your sources, with evidence. |
| ❓ **FAQ** | Six questions a researcher would ask, with detailed answers from the sources. Gets progressively deeper. |
| 📚 **Study Guide** | A structured study document with key definitions, main arguments, evidence, connections between sources, and review questions. |
| 📅 **Timeline** | All dates and events mentioned in the sources, in chronological order. If no dates exist, shows a logical progression of ideas instead. |

**How to generate a guide:**
1. Select the tab you want (e.g. 📋 Briefing)
2. Click the **Generate** button at the bottom of the panel
3. Wait 10-30 seconds while the AI works
4. Read the output; it uses only your documents, no outside knowledge
5. Click **📝** (save icon) to save the output to your Notes

You can generate a different guide type by switching tabs and clicking Generate again. Each tab is independent.

---

## Typical Research Workflow

Here is the recommended step-by-step approach for a new research topic:

**Step 1: Create a project**
On the home page, click **New Project** and give it a name (e.g. "Climate Policy Research").

**Step 2: Add your sources**
Open the project and go to the **Upload** tab. Add:
- Key PDFs (research papers, reports)
- Important web pages (news articles, documentation)
- YouTube talks or interviews

Wait for each source to finish processing (the status message will confirm).

**Step 3: Start with the Briefing**
Switch to the right panel, make sure **📋 Briefing** is selected, and click Generate. This gives you a quick summary of everything, good for understanding what you have before diving in.

**Step 4: Explore themes**
Click the **🏷️ Themes** tab and generate. This shows you what the dominant ideas are across all your documents.

**Step 5: Ask specific questions**
Use the chat to go deeper on what interests you. Ask follow-up questions. Explore contradictions between sources.

**Step 6: Save important findings**
Hit **Save as Note** on any answer worth keeping. You can also write your own notes in the Notes tab.

**Step 7: Generate study materials**
If you need to present or study the material, use **📚 Study Guide** or **❓ FAQ** to create structured outputs.

---

## Settings: AI Engines

Go to **Settings** (from the home page or sidebar) to configure which AI service the system uses.

The system supports a **fallback chain**: you can add multiple AI providers (e.g. OpenRouter, NVIDIA NIM) in priority order. If the first one fails or is unavailable, it automatically tries the next one. The last fallback is always Ollama (a local AI that runs entirely on your machine with no internet needed).

To add an AI provider you need:
- The API URL of the provider
- An API key (obtained from the provider's website)
- The model name (e.g. `meta-llama/llama-3.1-8b-instruct`)

Providers with better, larger models will give higher quality answers. Local Ollama models work offline but may be slower.

---

## Hiding and Showing Panels

| Button | What it does |
|--------|--------------|
| **☰ Menu** (top left) | Hides or shows the left sidebar (project list) |
| **□ Hide Guide / Show Guide** (top right) | Hides or shows the Notebook Guide panel |

On mobile phones, the sidebar slides in from the left as an overlay. Tap the **☰ Menu** button to open it and tap outside it or press ☰ again to close it.

On tablets (portrait orientation), the Guide panel is automatically hidden to give more space to the chat.

Your panel preferences are remembered; if you hide the Guide, it stays hidden when you come back.

---

## Frequently Asked Questions

**Q: Will the AI make up facts?**
No. It is specifically instructed to answer only from your documents. If the information is not there, it says "Not found in provided sources."

**Q: How many documents can I add?**
There is no hard limit. Performance may slow slightly with very large collections (100+ large PDFs) but it will still work.

**Q: Can I add a YouTube video?**
Yes, paste the YouTube URL in the Upload tab. The system transcribes the video and makes it searchable. This requires an internet connection.

**Q: Does my data leave my computer?**
Your documents stay on your machine. The AI queries (your questions and the source text) are sent to whatever AI provider you have configured. If you use a local Ollama model, nothing leaves your machine at all.

**Q: How do I delete a project?**
On the home page, there is a delete button on each project. Deleted projects go to **Trash** (accessible from Settings). You can restore them or permanently delete from there.

**Q: The AI says "All providers failed" - what do I do?**
Check your Settings page. Make sure at least one provider is enabled and has a valid API key. If using Ollama, make sure the Ollama service is running on your computer.

**Q: How do I start the system?**
Run the `startclaude.bat` file in `C:\F- Drive\`. If accessing remotely via SSH, connect via Tailscale and run the bat file from the command line.

---

*Research NotebookLM v2.1, Built for Pavel Blank · pavelblank@gmail.com*
