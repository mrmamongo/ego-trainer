export function studentStubFromSolution(source: string): string {
  const lines = source.replace(/\r\n?/g, "\n").split("\n");
  const output: string[] = [];
  let foundDefinition = false;
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];
    const trimmed = line.trim();

    if (trimmed === "" || line !== line.trimStart()) {
      index += 1;
      continue;
    }

    if (/^import(?:\s|$)/.test(trimmed) || /^from\b.*\bimport\b/.test(trimmed)) {
      output.push(line);
      index += 1;
      continue;
    }

    if (/^(?:async\s+)?def\b/.test(trimmed)) {
      const signature: string[] = [];
      let terminated = false;

      while (index < lines.length) {
        const signatureLine = lines[index];
        signature.push(signatureLine);
        index += 1;

        if (signatureLine.trim().endsWith(":")) {
          terminated = true;
          break;
        }
      }

      if (!terminated) {
        throw new Error("Unterminated top-level function signature");
      }

      output.push(...signature, "    pass");
      foundDefinition = true;
      continue;
    }

    index += 1;
  }

  if (!foundDefinition) {
    throw new Error("No top-level def found");
  }

  return `${output.join("\n")}\n`;
}
