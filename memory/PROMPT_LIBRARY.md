# Expert Claude Prompt Library

This document serves as a repository of high-signal, expert-level prompt templates for the Personal AI Brain. These prompts are used by the Agency layer (Phase 5) to perform specialized tasks and can also be used manually by the user.

---

## Writing and Content

### 1. Expert Article Writer
**Role:** Senior tech journalist writing for founders and developers. Direct, opinionated, no corporate hedging.
**Template:**
```markdown
<role>You are a senior tech journalist writing for founders and developers. Direct, opinionated, no corporate hedging.</role>
<task>Write a 1,200-word article arguing that [TOPIC].</task>
<context>Audience: technical founders at Series A. They care about speed, ROI, and real examples, not theory.</context>
<format>One strong hook sentence, then 4 H2 sections, then a 2-sentence punchy close.</format>
<constraints>No passive voice. No “in today’s landscape.” No generic CTAs. No unsupported claims.</constraints>
```

### 2. Voice-Preserving Editor
**Task:** Edit draft to be tighter and clearer while preserving voice exactly.
**Template:**
```markdown
<task>Edit this draft to be tighter and clearer. Preserve my voice exactly.</task>
<context>My writing style: conversational, direct, uses short sentences for emphasis. Never formal.</context>
<draft>[PASTE YOUR DRAFT]</draft>
<constraints>Do not change sentence structure unless genuinely confusing. No filler words. Flag every cut with a one-line note explaining why.</constraints>
```

### 3. LinkedIn Post Generator
**Role:** B2B content strategist who writes LinkedIn posts that generate leads, not likes.
**Template:**
```markdown
<role>You are a B2B content strategist who writes LinkedIn posts that generate leads, not likes.</role>
<task>Write 3 LinkedIn post variations about [TOPIC].</task>
<context>My audience: [JOB TITLE] at [COMPANY SIZE] companies. My goal: [OUTCOME YOU WANT].</context>
<format>Each post: hook line, 3–5 short paragraphs, 1 question CTA. Under 300 words each.</format>
<constraints>No emojis. No “I am excited to share.” No buzzwords. Start each post differently.</constraints>
```

### 4. Email Subject Line Factory
**Task:** Generate 20 email subject lines for campaign goals.
**Template:**
```markdown
<task>Generate 20 email subject lines for [CAMPAIGN GOAL].</task>
<context>Product: [WHAT YOU SELL]. Audience: [WHO RECEIVES THIS]. Tone: [FORMAL/CASUAL/URGENT].</context>
<format>Group in 4 categories: curiosity, urgency, benefit-led, question. 5 per category.</format>
<constraints>Under 50 characters each. No clickbait. Must feel human, not automated.</constraints>
```

### 5. Newsletter Section Writer
**Role:** Weekly newsletter writer for niche readers who value depth over noise.
**Template:**
```markdown
<role>You write weekly newsletters for [NICHE] readers who value depth over noise.</role>
<task>Write a 400-word newsletter section covering [THIS WEEK’S TOPIC].</task>
<context>My newsletter tone: knowledgeable friend, never preachy. I use specific data, not broad claims.</context>
<format>Lead with the most surprising insight. Then 2 supporting points. End with one practical takeaway.</format>
```

---

## Coding and Engineering

### 6. Code Review Like a Senior Engineer
**Role:** Senior developer reviewing a junior engineer’s pull request. Educational and constructive.
**Template:**
```markdown
<role>You are a senior developer reviewing a junior engineer’s pull request. Educational and constructive.</role>
<task>Review this code.</task>
<code>[PASTE YOUR CODE]</code>
<format>Cover: correctness, efficiency, readability, security, missing edge cases. For each issue: explain problem, show improved code, explain why it is better.</format>
```

### 7. Bug Explainer and Fixer
**Task:** Debug code, explain error in plain English, and provide corrected version.
**Template:**
```markdown
<task>Debug this code. Explain the error in plain English, identify the exact line, provide a corrected version with comments.</task>
<error>[PASTE ERROR MESSAGE]</error>
<code>[PASTE CODE]</code>
<constraints>Do not rewrite the entire file. Only fix what is broken. Explain each change.</constraints>
```

### 8. Function Builder with Edge Cases
**Task:** Build a function with error handling and edge cases.
**Template:**
```markdown
<task>Build a [LANGUAGE] function that [WHAT IT SHOULD DO].</task>
<requirements>Handle edge cases: [LIST THEM]. Include error handling. Add docstrings. Follow [LANGUAGE] best practices.</requirements>
<format>Code block first, then a brief explanation of design decisions.</format>
```

### 9. Code Explainer for Non-Technical Readers
**Task:** Explain code to a complete beginner.
**Template:**
```markdown
<task>Explain this code to a complete beginner who has never programmed before.</task>
<code>[PASTE CODE]</code>
<format>For each section: what it does, why it is written this way, what would happen if removed. Then show a simplified version with detailed comments.</format>
```

### 10. Architecture Advisor
**Role:** Software architect with 12 years of experience building scalable SaaS products.
**Template:**
```markdown
<role>You are a software architect with 12 years of experience building scalable SaaS products.</role>
<task>Review my system design and identify the 3 biggest risks before I build it.</task>
<design>[DESCRIBE YOUR ARCHITECTURE]</design>
<format>Risk, severity (high/medium/low), mitigation steps. Then one alternative architecture I should consider.</format>
```

---

## Business and Strategy

### 11. Competitive Analysis
**Task:** Analyze competitive landscape for a product/market.
**Template:**
```markdown
<task>Analyze the competitive landscape for [PRODUCT/SERVICE] targeting [MARKET].</task>
<context>My product: [BRIEF DESCRIPTION]. Stage: [EARLY/GROWTH/ESTABLISHED].</context>
<format>Table comparing top 5 competitors: pricing, target customer, key feature, weakness, my potential advantage.</format>
<constraints>Do not include companies I cannot compete with at my stage.</constraints>
```

### 12. Meeting Agenda Builder
**Task:** Create a timed meeting agenda with clear decisions.
**Template:**
```markdown
<task>Create a 45-minute meeting agenda for [MEETING PURPOSE].</task>
<context>Attendees: [ROLES]. Decision needed: [WHAT MUST BE DECIDED]. Background: [1–2 SENTENCES].</context>
<format>Timed slots, discussion questions for each, pre-read material suggestions. Include a parking lot section.</format>
```

### 13. Investor Memo Writer
**Role:** Startup advisor who has helped 30 companies raise Series A rounds.
**Template:**
```markdown
<role>You are a startup advisor who has helped 30 companies raise Series A rounds.</role>
<task>Write a 500-word internal memo making the case for [INITIATIVE].</task>
<context>Company stage: [STAGE]. Resources requested: [WHAT YOU NEED]. Problem: [PROBLEM].</context>
<format>Opportunity, evidence, risks, financial projections, the ask. One section each.</format>
```

### 14. Pareto Task Auditor
**Task:** Apply 80/20 rule to a task list.
**Template:**
```markdown
<task>Apply the 80/20 rule to my task list. Find the 20% of tasks driving 80% of my actual goals.</task>
<tasks>[PASTE YOUR TASK LIST]</tasks>
<context>My current goals: [LIST YOUR TOP 3 GOALS]. My role: [YOUR TITLE].</context>
<format>High-impact 20% (keep), low-impact 80% sorted into: delegate, automate, or drop. Reasoning for each.</format>
```

### 15. Weekly Review Template
**Task:** Create a personalized weekly review template.
**Template:**
```markdown
<task>Create a personalized weekly review template I can use every Friday.</task>
<context>I manage [DESCRIBE YOUR WORK]. Key metrics: [LIST THEM]. Biggest challenges: [CURRENT BOTTLENECKS].</context>
<format>5 questions to reflect, 3 questions to plan ahead, one momentum tracker. Under 15 minutes to complete.</format>
```

---

## Research and Analysis

### 16. Document Summarizer
**Task:** Summarize document into 5 actionable points.
**Template:**
```markdown
<task>Summarize this document into the 5 most important points I need to act on.</task>
<document>[PASTE TEXT OR DESCRIBE UPLOADED FILE]</document>
<context>I am a [ROLE] and I need this summary to [PURPOSE].</context>
<format>5 bullet points, each under 50 words, each ending with one concrete action. Then a 2-sentence overall summary.</format>
```

### 17. Keyword Research Assistant
**Task:** Generate long-tail keyword variations.
**Template:**
```markdown
<task>Generate 50 long-tail keyword variations for: [SEED KEYWORD].</task>
<format>Organize into 5 clusters by search intent: informational, navigational, commercial, transactional, local. For each: rough search volume (low/medium/high), competition, content type to create.</format>
```

### 18. Research Synthesizer
**Task:** Synthesize findings from multiple articles.
**Template:**
```markdown
<task>I am going to paste 5 articles on [TOPIC]. Synthesize the key findings into a single coherent brief.</task>
<articles>[PASTE ALL ARTICLES]</articles>
<format>Where sources agree, where they conflict, what is missing from all of them, and the one insight a non-expert would miss.</format>
```

### 19. Survey Question Generator
**Task:** Write survey questions to measure specific metrics.
**Template:**
```markdown
<task>Write 15 survey questions to measure [WHAT YOU WANT TO MEASURE] among [TARGET AUDIENCE].</task>
<context>Business goal: [WHY YOU ARE RUNNING THIS SURVEY]. What you will do with findings: [ACTION].</context>
<format>Mix of Likert scale, multiple choice, and open-ended. Flag which 3 questions are most important.</format>
```

### 20. Interview Question Builder
**Role:** Senior hiring manager who has built engineering teams at Series B+.
**Template:**
```markdown
<role>You are a senior hiring manager who has built 10 engineering teams at Series B+ startups.</role>
<task>Create 20 interview questions for a [JOB TITLE] role at [COMPANY TYPE].</task>
<context>Must-have skills: [LIST]. Nice-to-have: [LIST]. Red flags I want to surface: [LIST].</context>
<format>Questions grouped by: technical skills, problem solving, culture fit, growth mindset. Include what a strong vs. weak answer looks like.</format>
```

---

## Creativity and Repurposing

### 21. Content Repurposer
**Task:** Repurpose source content into 5 platform-native formats.
**Template:**
```markdown
<task>Repurpose this [ARTICLE/TALK/REPORT] into 5 different content formats.</task>
<source>[PASTE ORIGINAL CONTENT]</source>
<format>Produce: 1 LinkedIn post, 1 Twitter/X thread (5 tweets), 1 email newsletter section, 1 short-form video script, 1 pull quote.</format>
<constraints>Each format must be platform-native. No copy-pasting across formats. Each should stand alone.</constraints>
```

### 22. Story Angle Generator
**Task:** Generate unique story angles for a topic.
**Template:**
```markdown
<task>Give me 10 unique story angles for writing about [TOPIC].</task>
<context>Target reader: [DESCRIBE THEM]. What they already know: [BASELINE]. What they find boring about this topic: [PAIN POINT].</context>
<format>For each angle: hook sentence, why it is interesting, which emotion it triggers (curiosity/urgency/relatability).</format>
```

### 23. Product Description Writer
**Role:** E-commerce copywriter specializing in conversions.
**Template:**
```markdown
<role>You are an e-commerce copywriter who specializes in conversions, not just descriptions.</role>
<task>Write 3 product description variations for [PRODUCT NAME].</task>
<context>Key feature: [WHAT MAKES IT UNIQUE]. Buyer motivation: [WHY THEY BUY]. Common objection: [WHAT STOPS THEM].</context>
<format>Version A: benefit-led. Version B: problem-solution. Version C: social proof-anchored. Under 150 words each.</format>
```

### 24. Cold Email Sequence
**Task:** Write 5-email cold outreach sequence.
**Template:**
```markdown
<task>Write a 5-email cold outreach sequence for [PRODUCT/SERVICE].</task>
<context>Target: [JOB TITLE] at [COMPANY TYPE]. Pain point: [SPECIFIC PROBLEM]. My proof: [RESULT/CASE STUDY].</context>
<format>Email 1: pattern interrupt. Email 2: value add (no ask). Email 3: social proof. Email 4: objection handler. Email 5: breakup. Include subject line for each.</format>
<constraints>No “I hope this finds you well.” No more than 120 words per email.</constraints>
```

### 25. Brand Voice Guide Creator
**Task:** Analyze writing samples to build a brand voice guide.
**Template:**
```markdown
<task>Analyze these 5 writing samples and build a brand voice guide from them.</task>
<samples>[PASTE 5 EXAMPLES OF YOUR WRITING]</samples>
<format>Tone adjectives (3–5), what we say vs. what we avoid (table format), 3 before/after rewrite examples.</format>
```

---

## Productivity and Personal

### 26. Day Planner
**Task:** Organize day based on mental queue.
**Template:**
```markdown
<task>Organize my day based on everything in my mental queue.</task>
<queue>[BRAIN DUMP EVERYTHING: meetings, tasks, calls, deadlines in any order]</queue>
<context>My most productive hours: [TIME RANGE]. Energy level today: [HIGH/MEDIUM].</context>
<format>Morning block, afternoon block, buffer time flagged. Flag if day is overloaded. Do not add unsolicited advice.</format>
```

### 27. Decision Framework
**Task:** Structured framework to decide between options.
**Template:**
```markdown
<task>Help me decide between [OPTION A] and [OPTION B] using a structured framework.</task>
<context>What I care most about: [YOUR VALUES/GOALS]. Constraints: [BUDGET, TIME, TEAM]. What I am afraid of getting wrong: [THE RISK].</context>
<format>Table comparing both options across my stated criteria. Recommendation with one-paragraph reasoning. Devil’s advocate for the option you did not recommend.</format>
```

### 28. Habit System Designer
**Role:** Behavioral design coach using implementation intentions.
**Template:**
```markdown
<task>Design a 30-day habit system for [DESIRED HABIT].</task>
<context>My current routine: [DESCRIBE YOUR DAY]. Previous attempts that failed: [WHAT YOU TRIED]. Available time: [MINUTES PER DAY].</context>
<format>Trigger, habit, reward for each week. Week 1: minimum viable. Week 2: build. Week 3: lock in. Week 4: test without tracking.</format>
```

### 29. Feedback Giver
**Role:** Direct, constructive manager giving feedback on a deliverable.
**Template:**
```markdown
<role>You are a direct, constructive manager giving feedback on a deliverable.</role>
<task>Review this [DOCUMENT/CODE/DESIGN/PLAN] and give me honest feedback.</task>
<work>[PASTE YOUR WORK]</work>
<context>This is for [PURPOSE]. Audience: [WHO WILL SEE IT]. My goal: [WHAT YOU WERE TRYING TO ACHIEVE].</context>
<format>What works (specific), what to improve (with fixes), overall verdict in one sentence.</format>
```

### 30. Skill-Building Roadmap
**Task:** 90-day learning roadmap for a new skill.
**Template:**
```markdown
<task>Build a 90-day learning roadmap for [SKILL I WANT TO LEARN].</task>
<context>My current level: [BEGINNER/INTERMEDIATE/ADVANCED]. Why I want this: [GOAL]. Time available: [HOURS PER WEEK]. Learning style: [READING/VIDEO/PROJECTS].</context>
<format>Month 1: foundations. Month 2: applied practice. Month 3: real project. Include 3 specific resources per month. Flag common beginner mistakes to avoid.</format>
```
