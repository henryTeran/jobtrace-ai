import { describe, expect, it } from "vitest";

import { cn } from "./cn";

describe("cn", () => {
  it("concatene les classes valides", () => {
    const hidden = false;
    expect(cn("a", undefined, "b", hidden ? "c" : undefined)).toBe("a b");
  });
});
