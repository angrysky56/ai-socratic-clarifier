# Socratic Reasoning Customization

This document explains how to customize the Socratic reasoning capabilities in the AI-Socratic-Clarifier system.

## Overview

The Socratic reasoning module is at the core of the AI-Socratic-Clarifier. It analyzes text input to identify logical issues, vague language, or assumptions, then generates thought-provoking Socratic questions to encourage deeper reflection.

## New Customization Features

You can now customize the following aspects of the Socratic reasoning:

1. **Enable/Disable Socratic Reasoning**: Toggle Socratic reasoning on or off system-wide.
2. **Customize System Prompt**: Modify the prompt that guides the LLM in generating Socratic questions.
3. **Adjust Reasoning Depth**: Choose from different levels of reasoning depth (standard, deep, technical, creative).

## How to Access Customization

1. Navigate to the **Settings** tab in the main interface
2. Look for the **Socratic Reasoning Settings** card
3. Adjust settings as needed
4. Click "Save Socratic Settings" to apply changes

## System Prompt Customization

The system prompt guides how the LLM generates Socratic questions. You can customize it to:

- Focus on specific types of logical issues
- Adjust the questioning style (e.g., more direct, more gentle)
- Emphasize certain aspects of critical thinking

### Default System Prompt

```
You are a master of Socratic questioning who helps people improve their critical thinking. 
Your purpose is to craft precise, thoughtful questions that identify potential issues in people's statements. 
Based on the text and specific issues detected, create thought-provoking questions that will:
1) Encourage the person to recognize their own assumptions
2) Help them examine whether generalizations account for exceptions
3) Prompt consideration of evidence for claims made
4) Lead them to clarify vague or imprecise language
5) Guide reflection on normative statements that impose values
Make each question genuinely useful for deepening understanding, not rhetorical.
Each question should directly address a specific issue identified in the text.
```

## Reasoning Depth Levels

- **Standard**: Basic Socratic questioning focused on clarity and assumptions
- **Deep**: More philosophical exploration of underlying premises and worldviews
- **Technical**: More detail-oriented analysis focusing on specifics and evidence
- **Creative**: Employs creative analogies and hypotheticals to explore ideas

## Implementation Details

The Socratic reasoning settings are stored in the `config.json` file under the `settings.socratic_reasoning` section:

```json
"socratic_reasoning": {
    "enabled": true,
    "system_prompt": "...",
    "reasoning_depth": "deep"
}
```

When analyzing text, the system will:
1. Check if Socratic reasoning is enabled
2. Use the custom system prompt if provided
3. Apply the specified reasoning depth

## Example Applications

### Educational Context

Customize the prompt to emphasize pedagogical aspects:

```
You are a supportive educator using Socratic questioning. Your goal is not to criticize 
but to help students discover insights themselves. Create gentle, guiding questions that:
1) Help students identify gaps in their reasoning
2) Encourage them to make connections between concepts
3) Foster deeper examination of assumptions
4) Guide them toward discovering principles rather than just facts
```

### Technical Discussions

For technical or scientific discussions:

```
You are an analytical scientific thinker using Socratic questioning to improve reasoning. 
Create precise, evidence-focused questions that:
1) Identify where claims lack sufficient empirical support
2) Probe the methodology behind assertions
3) Examine potential alternative explanations
4) Question the operational definitions of key terms
5) Explore whether conclusions follow logically from premises
```

## Recommendations

- Start with small adjustments to the default prompt
- Test different reasoning depths to find what works best for your use case
- Consider creating specialized prompts for different domains (education, technical analysis, philosophical exploration)
