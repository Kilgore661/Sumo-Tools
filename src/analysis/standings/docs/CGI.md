This proposal outlines the transition from a "volatile" client-side state to a "persistent" URL-driven state, effectively giving your JavaScript application the linkability of a classic CGI script.

### 1. What exists now

The current implementation in `standings.js` uses a **One-Way, Volatile Flow**:

* **Initialization:** The script loads `site_config.json`, sets a hardcoded default state (e.g., 6 basho, Makuuchi division), and renders the view.
* **Interaction:** When a user interacts with a dropdown or radio button, the script updates a local JavaScript `state` object, fetches new data, and re-renders the table.
* **The Problem:** The browser's address bar remains static (e.g., `index.html`). If the user hits "Refresh" or shares the link, all customizations (filters, sorting, view modes) are lost, returning the page to the defaults.

### 2. What we’d like

We want a **Bidirectional, Persistent Flow**:

* **Deep Linking:** The URL should always reflect the current view (e.g., `index.html?num_basho=12&division=juryo&view=combined`).
* **History Support:** The "Back" and "Forward" buttons should move through the user’s previous filter selections as if they were separate pages.
* **Bookmarkability:** Copying the URL at any point should allow another person to see exactly what the sender is seeing.

### 3. Broad Principles

To achieve this without the "flicker" or "slow load" of a traditional CGI script, we apply three modern principles:

* **URL as an Override:** During initialization, the script should look at the URL. If parameters exist, they take precedence over the defaults in `site_config.json`.
* **Push-State Synchronization:** Every time the `state` object changes via a UI click, the script silently updates the browser's address bar using the `history.pushState` API. This updates the URL without a page reload.
* **The "Popstate" Listener:** The script must listen for the browser's "Back" and "Forward" actions. When these occur, the script reads the "new" URL, updates the `state`, and re-renders the page.

### 4. What we actually need to do

To implement this, the following modifications to `standings.js` are required:

1. **Create a "State-to-URL" Serializer:** A function that takes the current `state` object and produces a query string.
2. **Create a "URL-to-State" Parser:** A function (using `URLSearchParams`) that reads the query string and updates the `state` variables.
3. **Modify `init()`:** * Call the parser immediately after `applyConfigDefaultsToState()`.
   * Ensure the UI controls (dropdowns/radios) are visually updated to match these new values before the first data fetch.
4. **Update Event Listeners:** * Every listener (like `el.division.onchange`) should trigger a `history.pushState()` call using the Serializer.
5. **Add a `popstate` Event Listener:**
   * Attach a listener to `window`. When triggered, it runs the Parser and calls the render logic.

### 5. Things to watch out for

When "tinkering" with these modifications, several edge cases emerge that are not currently relevant in a static-URL environment:

* **Type Casting (Strings vs. Numbers):** URL parameters are always strings. Since your script uses numbers for `state.currentNumBasho` and booleans for `state.currentOnly`, you must explicitly cast these values (e.g., `Number(param)`) or your `===` comparisons in the sorting and filtering logic will fail.
* **The "Forward" Logic:** If a user goes back three times and then clicks a new filter, the "Forward" history is traditionally wiped out. The browser handles this, but your code must be robust enough to handle rapid state transitions.
* **Validation of URL Input:** A user can manually edit a URL to something invalid (e.g., `?division=clowns`). Your parser must validate incoming values against your known divisions/modes to prevent the script from attempting to fetch non-existent files like `data/6_clowns.csv`.
* **The Initial Entry:** On the very first page load (with no parameters), you may want to use `history.replaceState()` to "clean" the URL so it immediately shows the defaults, ensuring that even the first view is bookmarkable.
* **Redundant Fetches:** Ensure that the `popstate` listener doesn't trigger a data fetch if the only thing that changed was the `viewMode` (which is purely CSS/DOM-based), while ensuring it *does* trigger a fetch if the `num_basho` changed.
