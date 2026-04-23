I re-parsed the uploaded docs and code, and I think the answer is:

**the code does a substantial amount of the right thing, but it does not yet implement the current GSSWD account cleanly or fully.**

My overall judgement is:

* **engine / publication side:** fairly strong
* **browser side:** real and coherent, but still half in the old model
* **fit to current requirements/spec:** partial, with several visible mismatches

So this is not “hardly anything works”. It is more: **there is a working system, but the current docs are ahead of the current UI contract.**   

## What the code clearly does do

The broad architecture does match the intended shape. The spec says the browser should consume precomputed published artefacts and not calculate standings from raw history, and that is basically what the code does: Python computes and publishes CSV/JSON, and the browser loads, filters, sorts, and renders them.   

The publication flow is real, not imaginary. `publisher.py` generates a site config, generates one CSV/JSON pair per supported basho window, and deploys the assets to a local web root. That is a proper static-publication pipeline, and it aligns well with the requirements and rationale docs.    

The data model is richer than the current page needs, which is good. `multiple_basho_view.py` computes:

* credited and fought wins
* expected and available bouts
* selected-basho and containing-basho averages
* display identity from the most recent selected basho containing the rikishi
* win percentage
* various statistical extras

That means the backend is already carrying a lot of the conceptual machinery discussed in the rationale and the older metric distinctions.   

The browser also does the important client-side jobs correctly in principle:

* load config and selected window
* filter by division
* sort by columns
* recompute visible competition positions after filtering
* switch views
* show/hide notes by view

That matches the general design intent quite well.  

So at the structural level, there is a credible product skeleton here.

## Where it does not yet do what it is supposed to

The main problem is that the **browser contract and page semantics still reflect an earlier design**, while the docs now define a cleaner GSSWD contract.

The most obvious mismatch is the view model. The spec says the three views are **Standard, Percentages, Combined**, with specific columns and semantics. The code and HTML use **standard, percentages, full**, and the HTML labels the third option “Full”, not “Combined”. That is not just wording drift; it shows the UI is still rooted in an earlier conception.   

There is also a direct mismatch in the standard and percentages tables. The spec says:

* Standard: `Pos. | Shikona | Chii | Wins | Average`
* Percentages: `Pos. | Shikona | Chii | Wins | Bouts | Win %`
* Combined: row number plus both ranking systems

But the rendered rows in JS always begin with a row index column, even in standard and percentages mode. In standard mode the JS renders row index, shikona, chii, wins, average, and then the average rank. In percentages mode it renders row index, shikona, chii, wins, bouts, win %, and then the percentage rank. That means standard and percentages currently behave much more like “table with row number plus rank column” than the specified dedicated leaderboards.  

Related to that, the HTML headers still say **Mean** and **Rank**, not **Average** and **Pos.**, and the product title still says **Grand Sumo Standings by Win Count**, not the current provisional product name. Those are small on their own, but together they show that terminology has not been harmonised. The design doc itself explicitly says label harmonisation is still a next step, which is accurate.   

The spec also says that if a change of view hides the active sort key, the table should revert to the default sort. I do not see that implemented in the browser code. The view change handler updates `state.viewMode`, applies view columns and notes, and calls `render()`, but there is no logic resetting sort when the active key becomes hidden. The design note flags this as something that “may still need hardening”, and that appears to be true.   

The reporting-period labelling is only partly there. The spec says the page should clearly identify selected basho count, start, and end. The JS does compute a title like “Standings (Last N basho, start to end)”, so that part exists. But it also blanks out `range-label`, and the metadata presentation is thinner than the docs imply. So this is more “implemented in a minimal way” than “fully realised”.  

## A more subtle mismatch: ranking basis

This is the most interesting gap.

The **spec** defines Standard as ranking by **Average**, and from section 6 that Average means wins divided by the **selected number of basho**. In other words, standard-view semantics are now based on the selected-window basis. 

But the **backend view ordering** in `multiple_basho_view.py` still ranks rows by the **containing** averages, not the selected averages, when building the published row order and position field. For credited wins, the primary key is `containing_average_credited_wins`, not `selected_average_credited_wins`. 

Now, the browser usually sorts independently using `selected_average_credited_wins` as the default sort column, so the visible order on the page can still line up with the spec. But this means the backend’s own `position` field and ordering are no longer semantically aligned with the page’s intended default ranking. In practice, the UI is rescuing the result. Architecturally, though, this is a sign of drift between the old analytical model and the new product model.  

That is exactly the kind of thing your current docs are trying to clean up.

## What is better than the docs make it sound

The design-and-implementation notes are too pessimistic in one respect: they understate how much of the essential behaviour already exists.

You do already have:

* static deployment
* supported basho windows
* division filtering
* current/end-period identity display
* expected-bout calculation
* visible competition ranking
* mode-specific notes visibility
* a single-state, single-render style browser client

That is a meaningful amount of product, not just scraps.    

In fact, the code is stronger on **architecture** than on **finished outward behaviour**.

## What is weaker than the docs imply

The docs present a rather neat, unified GSSWD product. The code is not there yet at the UX level.

The visible issues are:

* old naming persists: “Win Count”, “Mean”, “Full”, “Ozumo Standings”
* standard/percentages/combined semantics are not yet implemented exactly as specified
* row number / position semantics are muddled in the current DOM/rendering contract
* sort fallback on hidden columns is not implemented
* the notes are present, but not yet at the minimum completeness the spec now wants

So the outward product is still transitional.   

## My blunt assessment

If the question is:

**“Does the code do what the old evolving project was trying to do?”**

Then the answer is: **mostly yes**. There is a functioning standings publication-and-display system here.

If the question is:

**“Does the code now implement the current GSSWD requirements/spec/design account?”**

Then the answer is: **only partially**.

My rough split would be:

* **architecture and pipeline:** about 80–85% aligned
* **backend metrics support:** about 75–85% aligned, maybe more
* **frontend externally visible behaviour against current spec:** about 50–60% aligned
* **terminology and semantic coherence:** about 40–50% aligned

So overall: **solid underlying progress, but not yet a coherent finished implementation of the current story.**

## The single most important conclusion

The biggest issue is not “the code is missing”.

It is:

**the codebase still embodies two different conceptions of the product at once**—

* the older exploratory/analytical standings tool
* the newer simplified GSSWD browser product

The engine/publisher side still carries the older richness; the spec now defines the newer simpler product; and the browser sits awkwardly between them. That diagnosis fits both the code and the design note’s own admission of terminology drift and mixed legacy assumptions.  

So I would not say “hardly what is required” full stop. I would say:

**there is already enough here to justify the GSSWD account, but the UI and browser contract now need to be brought into line with it.**

The next useful thing would be for me to turn this into a precise gap list: **implemented / partially implemented / not implemented / implemented but semantically wrong**.
