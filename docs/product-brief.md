# NEXUS product brief

Status: **In Development — Phase 7 productization and market validation**

This brief defines the product direction for the next phase. It is a product
hypothesis, not evidence of market fit.

## Target user

The initial target user is a Python developer or small engineering team that
uses AI coding tools and needs reliable repository context before changing
code.

The first user segment is intentionally narrow. Supporting every language,
repository size, and engineering workflow would make the product promise hard
to test.

## Problem

AI coding tools can produce plausible changes from incomplete or stale context.
Developers then spend time checking whether the tool understood symbol
locations, imports, calls, and the impact of a change.

The product hypothesis is that a deterministic repository-facts layer can make
AI-assisted engineering workflows more trustworthy by exposing inspectable
source evidence before model reasoning occurs.

## MVP promise

Given a Python repository revision, NEXUS should provide a developer with:

1. A repeatable index of files, symbols, imports, and calls.
2. A deterministic view of what changed between revisions.
3. Exact source locations and machine-readable facts that a future AI tool can
   cite.
4. Clear diagnostics when parsing or Git operations fail.

The MVP is a local developer tool. It does not promise autonomous code changes,
production-scale indexing, or model-generated answers.

## Product workflow to build

```text
Developer selects repository/revision
        |
        v
NEXUS indexes supported Python files
        |
        v
Developer asks for changed symbols and relationships
        |
        v
NEXUS returns deterministic facts with source locations
```

The current repository already implements the indexing foundation. The first
user-facing workflow is now available through `python -m nexus analyze` for one
Python file. `python -m nexus impact` adds a deterministic caller query with
source locations; broader repository and revision workflows remain next.

## Non-goals for the first product slice

- Supporting multiple programming languages immediately
- Replacing a developer's IDE or code review system
- Making autonomous edits to a repository
- Claiming semantic name resolution before it is implemented
- Adding an AI provider before deterministic evidence can be inspected
- Claiming market fit, production adoption, or business value without user
  validation

## Validation plan

Market validation should produce evidence outside the codebase:

1. Interview at least five Python developers who use AI coding tools about
   repository-context failures and current workarounds.
2. Show the local MVP workflow with a real or representative repository.
3. Record whether participants can identify a concrete task they would repeat
   with NEXUS.
4. Measure task completion time and error reports only after defining the task,
   fixture, environment, and collection method.
5. Treat willingness to reuse or integrate the workflow as a hypothesis to
   test, not as a result to assume.

No interview, adoption, satisfaction, or performance result is claimed by this
repository until it is actually collected and documented.

## Product acceptance criteria

The first product slice can be considered engineering-complete when a new user
can install NEXUS, run one documented repository-analysis workflow, inspect
source locations and relationships, and understand parser failures without
reading internal implementation code.

The [user-validation kit](user-validation.md) defines the study protocol. It
can only be considered market-validated after external user evidence is
collected and reported separately from engineering test results.
