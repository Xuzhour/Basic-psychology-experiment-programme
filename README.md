# Basic-psychology-experiment-programme
Experimental source code for the undergraduate thesis: "The Impact of Social Exclusion on Cooperative Behavior." Implements a 2×2×2 mixed design using PsychoPy, integrating Cyberball and Public Goods Game (PGG) paradigms to test Embodiment and Attribution theories.
# The Impact of Social Exclusion on Cooperative Behavior

**Author:** Wentian Ye (Nanjing Normal University)  
**Status:** Undergraduate Thesis Project (2026)

## 📌 Project Overview

This repository contains the experimental source code for the graduation thesis titled **"The Impact of Social Exclusion on Cooperative Behavior: An Integrative Mechanism of Embodiment Effects, Attribution Styles, and Situational Constraints"**.

[cite_start]This study constructs a multi-level integrated model to explore how physiological states (defensive body postures), cognitive processing (attribution styles), and external rules (situational constraints) jointly regulate cooperative behavior following social exclusion[cite: 23, 29, 30].

## 🧪 Experimental Design

[cite_start]The experiment employs a quantitative mixed design utilizing two classic psychological paradigms[cite: 31]:
1.  **Cyberball Paradigm:** Used to manipulate the experience of social exclusion vs. inclusion.
2.  **Public Goods Game (PGG):** Used to measure subsequent cooperative behavior.

### [cite_start]Key Variables [cite: 33]
* **Body Posture:** Defensive (e.g., crossed arms) vs. Neutral (Manipulated physically/instructionally).
* **Attribution Style:** Internal vs. External (Manipulated via feedback instructions).
* **Cooperative Necessity:** High vs. Low (Manipulated via PGG threshold rules).

## 📂 File Structure & Condition Mapping

The repository includes Python scripts (developed using **PsychoPy**) corresponding to different experimental conditions. The filenames follow the convention `Condition_Attribution_Necessity`.

| Filename | Social Condition | Attribution Style | Cooperative Necessity | Description |
| :--- | :--- | :--- | :--- | :--- |
| `Exc_Int_Low.py` | **Exclusion** | **Internal** | **Low** | Excluded participants given internal attribution feedback; PGG has low survival threshold. |
| `Exc_Int_High.py` | **Exclusion** | **Internal** | **High** | Excluded participants given internal attribution feedback; PGG has high survival threshold. |
| `Exc_Ext_Low.py` | **Exclusion** | **External** | **Low** | Excluded participants given external attribution feedback; PGG has low survival threshold. |
| `Exc_Ext_High.py` | **Exclusion** | **External** | **High** | Excluded participants given external attribution feedback; PGG has high survival threshold. |
| `Inc_Int_Low.py` | **Inclusion** | **Internal** | **Low** | Control condition (Included) with internal attribution consistency check. |
| `Inc_Ext_Low.py` | **Inclusion** | **External** | **Low** | Control condition (Included) with external attribution consistency check. |

> **Note:** The **Body Posture** variable (Defensive vs. Neutral) is manipulated via experimenter instruction and physical constraints before the task begins. It applies across these scripts depending on the participant's assignment group.

## 🛠️ Prerequisites & Installation

To run these experiments, you need a Python environment with the PsychoPy library installed.

### Recommended Environment
* **PsychoPy Standalone:** [Download Here](https://www.psychopy.org/download.html) (Recommended for stability).
* **Python Version:** Python 3.8+ (if running from source).

### Dependencies
```bash
pip install psychopy pandas numpy
