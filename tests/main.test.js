import { describe, it } from "node:test";
import assert from "node:assert";

describe("gentle smoke test", () => {
  it("should load the main module without error", async () => {
    assert.doesNotThrow(() => import("../src/main.js"));
  });
});