// Public Rating Changes table runtime facade.

export {
  buildRatingChangesPresentationModel,
  selectedRatingChangesEntry,
} from "./rating-changes/model.js";

export {
  renderRatingChangesPresentationTable,
} from "./rating-changes/render.js";

export {
  wireRatingChangesPresentationSorting,
} from "./rating-changes/sorting.js";

export {
  DEFAULT_RATING_CHANGES_SORT_PATH,
  PRESENTATION as RATING_CHANGES_PRESENTATION,
  RATING_CHANGES_TABLE_SPEC,
} from "./rating-changes/table-spec.js";
