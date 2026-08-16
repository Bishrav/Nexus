# NEXUS user-validation kit

Status: **Planned — no participant results recorded**

This kit is for validating whether the local NEXUS workflow solves a real
repository-context problem for Python developers who use AI coding tools. It
does not create market-fit evidence by itself.

## Participant profile

Recruit Python developers or small-team engineers who regularly use an AI
coding assistant and have recently checked or corrected an AI-generated change.
Aim for at least five participants before drawing a directional conclusion.

Do not record confidential source code, employer names, credentials, or other
private information in the repository.

## Session protocol

Use the same representative fixture and task for each participant:

1. Explain that NEXUS currently indexes one Python file and exposes symbols,
   relationships, and source locations.
2. Ask the participant to identify what calls `Greeter` in the fixture using the
   documented `analyze` and `impact` commands.
3. Ask what they would need before trusting this workflow on a real repository.
4. Ask them to compare the workflow with their current way of checking AI
   repository context.
5. Record observations immediately after the session using the template below.

The facilitator should not imply that NEXUS is production-ready or that market
fit has already been demonstrated.

## Evidence to collect

For every session, record only the minimum non-sensitive information:

- Participant code, such as `P01`; never a real name in the repository
- Date and approximate session duration
- Whether the participant completed the task without facilitator help
- What they found useful or confusing
- The concrete workflow they would try next, if any
- Blocking concerns and requested capabilities
- Whether they would voluntarily repeat the workflow

Do not convert opinions into metrics unless the scale and question are defined
before collection. Do not report aggregate results until the underlying session
notes exist and are reviewed for consistency.

## Results template

Copy this section for each completed session outside the source tree, then
prepare an anonymized summary for the repository only after consent and review:

```text
Participant: P__
Date:
Duration:
Task completed: yes / no / with help
Useful:
Confusing:
Would repeat: yes / no / unsure
Requested next capability:
Blocking concern:
```

## Decision rule

After the planned sessions, summarize evidence as one of:

- **Continue MVP** — repeated concrete use case and manageable blockers
- **Revise workflow** — problem is real but the current interaction is unclear
- **Change target problem** — participants do not recognize the problem or need
- **Insufficient evidence** — too few relevant participants or inconsistent task

None of these outcomes is valid until actual participant sessions are completed
and documented. Until then, NEXUS remains an engineering prototype with a
product hypothesis, not a market-validated product.
