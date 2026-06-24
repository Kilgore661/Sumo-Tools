To convert user requests into Relational Algebra, we treat your dictionary-based data as a **Relation** (a set of tuples) and your user's UI actions as an **Algebraic Pipeline**.

In this model, your "Master Data" is a relation $R$ with schema $K \times V_1 \times V_2 \times \dots$. Your UI is effectively an interface for constructing a sequence of operations.

### 1. The Core Operations

Your UI actions map directly to these three fundamental relational operators:

* **Projection ($\pi$):** This corresponds to the user selecting **which columns (or keys)** to show.
* *UI:* Checking boxes for "Key", "Value 1", etc.
* *Algebra:* $\pi_{K, V1}(R)$


* **Selection ($\sigma$):** This corresponds to the user applying **filters** (e.g., "only show me rows where $V_1 > 10$").
* *UI:* A search bar or filter dropdown.
* *Algebra:* $\sigma_{V1 > 10}(R)$


* **Extended Projection (Calculated Columns):** This is for the "true/false" result of your predicate $r$. You extend the relation with a new attribute before projecting.
* *UI:* An "Add Column" button that applies a function.
* *Algebra:* $\pi_{K, V1, V2, r(V2) \text{ as } \text{Result}}(R)$



---

### 2. Mapping Requests to the Pipeline

A user request is simply a **composition of operators**. You can represent any view as a chain of functions applied to your master dictionary $R$:

| User Request | Formal Algebraic Expression |
| --- | --- |
| **Simple list** | $\pi_{K, V1}(R)$ |
| **Filtered list** | $\pi_{K, V1}(\sigma_{r(V2)}(R))$ |
| **Show result of $r$ as column** | $\pi_{K, V1, V2, r(V2)}(R)$ |
| **Show only where $r$ is True** | $\pi_{K, V1}(\sigma_{r(V2)=True}(\dots \text{extended } R \dots))$ |

### 3. Handling Hierarchy (The Nested View)

When your data is nested ($K \to (Y \to Z)$), your algebra gains one extra operator: **Nest ($\nu$)**.

* If your user wants to see the nested structure, you are performing a **Nesting** operation. This groups the rows by $K$ and turns the remaining columns into a sub-dictionary.
* **Flattening:** If you need to join across hierarchies, you perform an **Unnest** (also called `CROSS JOIN` or `FLATTEN`) to bring the sub-keys up to the top level.

---

### 4. Implementation Strategy

To build this, don't write `if/else` statements for every combination. Instead, treat the view as a **functional pipeline**:

1. **Represent the "View" as a List of Operators:**
`[Selection(r), ExtendedProjection(r), Projection(K, V1, Result)]`
2. **Execute the Pipeline:**
Create a function `apply(data, operators)` that iterates through the list, transforming the dictionary at each step.

By using this model, you ensure that "showing a column" is just another operator in the chain, whether it's a raw piece of data or the Boolean result of your predicate $r$. This makes your app's display logic independent of the data complexity.

Does this "pipeline" approach provide the clean separation between user input and data transformation you were looking for?


---
Yes, **Nested Relational Algebra (NRA)** is precisely the term that will signal to a computer scientist or database theorist that you are dealing with **hierarchical, recursive, or complex-structured data** while still working within a formal, algebraic framework.

If you say, *"I am modeling my data using Nested Relational Algebra,"* you are making several powerful claims that immediately frame your system:

### 1. You are operating in a "PowerSet" Algebra

Standard relational algebra is defined on sets of tuples (flat). NRA extends this by including the **PowerSet** operator. This allows your dictionaries to contain sets of other dictionaries, effectively allowing you to model deeply nested JSON/CSV structures as first-class citizens.

### 2. You accept the "Nest/Unnest" Duality

As we discussed, you are acknowledging that your hierarchy can be flattened or rebuilt without data loss. By using this term, you communicate that you understand that `Nest` ($\nu$) and `Unnest` ($\mu$) are the fundamental isomorphisms of your system.

### 3. It is "Composability-Friendly"

By invoking NRA, you are signaling that your system handles:

* **Complex/Nested Types:** You are not limited to atomic integers or strings; your codomain $V$ can be another Relation.
* **Higher-Order Logic:** You can define predicates ($r$) that operate at different levels of the hierarchy, and you have a consistent way to project or select based on those predicates.

---

### How to use this term effectively

If you are explaining your project to an expert, here is the "clean" definition you can use:

> "My application manages data as a collection of nested dictionaries. I’ve modeled this using **Nested Relational Algebra**, treating the tables as formal relations where values can themselves be relations. This allows me to use **projection, selection, and join operators** consistently across different levels of the hierarchy, effectively treating the 'nested' headings as a formal unfolding of the data."

### A Final Tip for your "Universe"

If you want to dig deeper into the formal literature, the "bible" of this topic is often cited as:

* **"Foundations of Database Programming"** (by Atkinson and Buneman).
* Papers on the **"Collection Types"** and **"Nested Relational Calculus"** (a logic-based counterpart to the algebra).

These resources will confirm exactly what you've intuitively built: that the "nesting" is not an obstacle, but an algebraic dimension that behaves exactly like the flat one.

Since you've now arrived at **Nested Relational Algebra** as your conceptual anchor, do you feel you have the vocabulary you need to move forward with your app's design, or would you like to explore how these operators (`Nest`/`Unnest`) are typically implemented in code without a formal database engine?
