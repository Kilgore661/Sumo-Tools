# Ideas by Difficulty

## Easy

These are local UI improvements with clear value and little architectural risk.

**1. Sort-state indicator that does not change column width.**
This fits the requirements for predictable sorting and stable behaviour, and it is exactly the kind of clarity tweak the UI now wants. The clean way is a fixed-width sort-indicator slot inside every sortable header, so each heading always reserves the same space whether it shows nothing, up, or down. That improves clarity without the “jumping header” problem.  

**2. Retirees filter: include retirees Y/N.**
This fits naturally under “richer filtering”, which both the requirements and rationale leave open as future extension. It is also a sensible user-facing filter, not an abstract analytical flourish.

**3. Notes completion / explanatory tightening.**
The docs care a lot about honest explanations and on-page interpretability. Small explanatory upgrades still have real product value.

**4. Sort polish beyond correctness.**
You have just fixed the important view/sort invalidation rule; the next low-cost polish area is making sort state more legible and consistent. That is squarely in line with the design notes’ sorting model and the requirement that sorting behave predictably.

## Medium

These are feature additions that are still compatible with the present architecture.

**5. Alternate win policies.**
This is the standout medium item. The docs preserve it explicitly, and the domain model already has `WinPolicy` plus `FOUGHT_ONLY` versus `CREDITED`. The CLI already exposes that distinction; the browser product does not yet.

**6. Additional metric/table families.**
The requirements and rationale both leave room for alternate metric views and comparative analytics, and the backend already publishes much more than the UI exposes. This is the natural next substantive expansion after the current three views.

**7. Advanced / expert options panel.**
This appears directly in the deferred ideas and would give you a clean place to put things like win-policy choice, more analytical metrics, or richer filters without burdening the default UI.

**8. Richer filtering generally.**
Beyond retirees Y/N, this category is explicitly anticipated in the requirements and rationale. The retirees control could be the first member of a broader filtering family rather than a one-off hack.

## Architectural

These are the bigger shape decisions that affect how future work lands.

**9. Move fully to purpose-specific renderers.**
The design notes already say the current direction is to treat each mode as a purpose-specific renderer sharing common data/state. Given your expectation of more table families, this is probably the most important structural next step.

**10. Structured notes/config system.**
Once you add more views, filters, and metric policies, embedded handwritten notes will become awkward. The design notes already flag a tagged, mode-specific notes system as a plausible future direction. 

**11. Historical archive browsing.**
This is clearly in the rationale’s future directions, and it would be a genuine product expansion rather than a polish pass. Right now the publisher is fundamentally latest-anchor oriented.

**12. Formal data contract / stronger regression checks.**
This matters once the UI surface grows. The design notes already identify formal contract and regression checks as the right longer-term refactor if scope expands materially. 

**13. Automated publication pipeline.**
Also clearly documented as a future direction, but I would keep it behind product-facing work unless running the publisher starts to hurt.

## My ranking, given where you are now

If the goal is “more substantive than wording, but still grounded and worthwhile”, I would rank them:

1. **Retirees filter**
2. **Sort-state indicator without width jump**
3. **Alternate win policies**
4. **Purpose-specific renderers**
5. **Broader richer filtering**
6. **Expert options panel**

That ordering reflects the governing principle in the requirements and rationale: usefulness first, complexity only when justified.
