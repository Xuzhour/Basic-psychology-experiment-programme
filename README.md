# The Impact of Social Exclusion on Cooperative Behavior

**Author:** Wentian Ye (Nanjing Normal University)  
**Status:** Undergraduate Thesis Project (2026)

## 📌 Project Overview

This repository contains the experimental source code for the graduation thesis titled **"The Impact of Social Exclusion on Cooperative Behavior: An Integrative Mechanism of Embodiment Effects, Attribution Styles, and Situational Constraints"**.

This study constructs a multi-level integrated model to explore how physiological states (defensive body postures), cognitive processing (attribution styles), and external rules (situational constraints) jointly regulate cooperative behavior following social exclusion.

## 🧪 Experimental Design

The experiment employs a quantitative mixed design utilizing two classic psychological paradigms:
1.  **Cyberball Paradigm:** Used to manipulate the experience of social exclusion vs. inclusion.
2.  **Public Goods Game (PGG):** Used to measure subsequent cooperative behavior.

### Key Variables
* **Body Posture:** Defensive (e.g., crossed arms) vs. Neutral (Manipulated physically/instructionally by the ID).
* **Attribution Style:** Internal vs. External (Manipulated via feedback instructions).
* **Cooperative Necessity:** High vs. Low (Manipulated via PGG threshold rules).

## ⚙️ Program Workflow

The experiment follows a linear sequence designed to measure the carry-over effects of social exclusion on cooperative decision-making. Below is the logic flow implemented in the Python scripts:

```mermaid
graph TD
    A["Start: Input Subject ID"] --> B["Phase 1: Instructions & Cover Story"]
    B --> C{"Phase 2: Cyberball Task"}
    
    C -->|"Condition: Exclusion"| D["Agents stop throwing ball to Subject"]
    C -->|"Condition: Inclusion"| E["Agents toss ball equally to Subject"]
    
    D --> F["Phase 3: Attribution Manipulation"]
    E --> F
    
    F -->|"Group: Internal"| G["Feedback: 'You were ignored due to your personality'"]
    F -->|"Group: External"| H["Feedback: 'You were ignored due to technical issues'"]
    
    G --> I["Phase 4: Public Goods Game (PGG)"]
    H --> I
    
    I --> J{"Cooperative Necessity Check"}
    J -->|"High Necessity"| K["Threshold: Must reach 80% to keep points"]
    J -->|"Low Necessity"| L["Threshold: No minimum required"]
    
    K --> M["Trial Loop: Investment -> Outcome -> Feedback"]
    L --> M
    
    M --> N["End: Data Logging .csv"]

