---
Smartness Rating: 9/10
Main Features:
- Mistake Tracking: Storing past errors and their corrections as a specific data type.
- Procedural Learning: Adjusting advice based on what hasn't worked for the user before.
- Proactive Warning: Alerting the user when they are about to repeat a documented mistake.
---

# Opinion: Proactive Error & Correction Memory

## 1. Description
A key feature of human intelligence is learning from mistakes. The system should specifically index errors, corrected code, and lessons learned to ensure the user (and the AI) never makes the same mistake twice.

## 2. Technical Implementation
* **Error Log:** A dedicated namespace in the memory store for "Mistakes & Corrections."
* **Retrospective Analysis:** After a task, the AI asks, "What went wrong here?" and stores the answer.
* **Pre-Task Check:** When a new task starts, the AI searches the Error Log for relevant past failures.

## 3. Benefits
* **Accelerated Learning:** Reducing the cycle time of education.
* **Personalized Guidance:** The AI knows your specific blind spots.
