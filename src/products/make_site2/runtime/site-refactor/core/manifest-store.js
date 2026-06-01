// In-memory runtime manifest store.

let runtimeManifest = null;

export function setRuntimeManifest(manifest) {
  runtimeManifest = manifest;
}

export function getRuntimeManifest() {
  if (!runtimeManifest) throw new Error("Site manifest has not been loaded.");
  return runtimeManifest;
}
