To improve Cursor (or any AI development workflow) to match Jason Liu’s approach and development style, focus on these core principles and techniques:

---

## Embrace Experimentation Over Deterministic Planning

- **Shift from Output to Input Metrics:** Instead of just setting accuracy targets, track how many experiments you run, how quickly you learn, and how often you document results. This fosters a culture of rapid iteration and learning, which is essential for AI projects where solutions are often unknown at the outset[1].
- **Time-Box Research Phases:** Set clear time limits for research sprints, define success/abandon criteria for each experiment, and make decisions based on learnings rather than waiting for perfect results[1].

---

## Build Modular and Swappable Systems

- **Maintain Option Value:** Design your system so components (retrievers, models, workflows) can be swapped out or improved independently. This modularity allows you to pivot quickly as new approaches or better models become available[1].
- **Structured Outputs and Workflows:** Use structured outputs (like schemas or directed acyclic graphs) to make workflows more controllable and easier to modify, rather than relying on open-ended or unstructured processes[6].

---

## Systematic Feedback and Evaluation

- **Synthetic and Real-World Evaluation:** Build synthetic datasets to pinpoint failure modes and supplement with real-world user feedback to continuously refine your models[5].
- **Automated Feedback Loops:** Design interfaces and systems that collect actionable feedback at every interaction, making it easy to identify what’s working and what needs improvement[5].

---

## Three Things Every Project Code Should Have

| Essential Element     | Why It Matters                                                                 |
|----------------------|--------------------------------------------------------------------------------|
| Clear Documentation  | Ensures anyone (human or AI) can understand, use, and extend the codebase[6].  |
| Automated Testing    | Guarantees reliability as the project evolves and new features are added[6].   |
| Modular Architecture | Allows for easy swapping, upgrading, and experimentation with components[1][6]. |

---

## How to Improve Your AI Project in Jason Liu’s Style

- **Run More, Smaller Experiments:** Focus on experiment velocity and learning rate, not just end results[1].
- **Document Learnings:** Treat every experiment as a learning opportunity, and document both successes and failures for future reference[1].
- **Balance Research and Product Needs:** Use dual metrics—track both research progress (experiments, learnings) and product metrics (accuracy, latency, cost)[1].
- **Prioritize Feedback:** Build systems that collect and use feedback to drive continuous improvement[5].
- **Stay Modular:** Architect your code so you can easily replace or upgrade models, tools, or workflows as the field evolves[1][6].

---

By adopting these principles, Cursor can become a more agile, robust, and effective AI development platform—mirroring Jason Liu’s proven, research-driven approach.

Citations:
[1] https://jxnl.co/writing/2024/10/25/running-effective-ai-standups/
[2] https://jxnl.co/writing/category/software-engineering/
[3] https://www.linkedin.com/posts/jxnlco_how-to-get-started-in-ai-consulting-jxnlco-activity-7258161282745282560-RNmh
[4] https://www.youtube.com/watch?v=USTG6sQlB6s
[5] https://maven.com/applied-llms/rag-playbook
[6] https://www.latent.space/p/instructor
[7] https://www.youtube.com/@jxnlco/videos
[8] https://www.youtube.com/watch?v=BgiLTtMHDjw

---
Answer from Perplexity: pplx.ai/share