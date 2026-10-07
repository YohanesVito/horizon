"use client";

import { useEffect, useRef, useState } from "react";
import type { InputHTMLAttributes, RefObject } from "react";

type MoneyInputProps = Omit<
  InputHTMLAttributes<HTMLInputElement>,
  "type" | "value" | "defaultValue" | "onChange" | "min" | "max" | "step"
> & {
  value?: string | number;
  defaultValue?: string | number;
  min?: string;
  max?: string;
  step?: string;
  onValueChange?: (value: string) => void;
  inputRef?: RefObject<HTMLInputElement | null>;
  resetKey?: number;
};

function displayNumber(value: string) {
  if (!/^\d*(?:\.\d*)?$/.test(value)) return value.replaceAll(".", ",");
  const [whole, fraction] = value.split(".");
  return (
    whole.replace(/\B(?=(\d{3})+(?!\d))/g, ".") +
    (fraction === undefined ? "" : `,${fraction}`)
  );
}

function canonicalNumber(value: string) {
  return value.replaceAll(".", "").replace(",", ".");
}

function validation(value: string, min?: string, max?: string, step = "1") {
  if (!value) return ""; // Native required validation handles the empty field.
  if (!/^\d+(?:\.\d*)?$/.test(value))
    return "Gunakan angka positif; desimal memakai koma.";
  const number = Number(value);
  if (!Number.isFinite(number)) return "Angka terlalu besar.";
  if (min !== undefined && number < Number(min))
    return `Nilai minimum ${displayNumber(min)}.`;
  if (max !== undefined && number > Number(max))
    return `Nilai maksimum ${displayNumber(max)}.`;
  if (step !== "any") {
    const quotient = (number - Number(min ?? 0)) / Number(step);
    if (Math.abs(quotient - Math.round(quotient)) > 1e-7)
      return `Gunakan kelipatan ${displayNumber(step)} dari ${displayNumber(min ?? "0")}.`;
  }
  return "";
}

/** Indonesian display; forms and API callers receive an ungrouped decimal. */
export default function MoneyInput({
  value,
  defaultValue = "",
  onValueChange,
  inputRef,
  resetKey = 0,
  name,
  min,
  max,
  step,
  ...props
}: MoneyInputProps) {
  const input = useRef<HTMLInputElement | null>(null);
  const incoming = String(value ?? defaultValue);
  const [lastResetKey, setLastResetKey] = useState(resetKey);
  const [draft, setDraft] = useState({
    raw: incoming,
    source: incoming,
    error: "",
  });
  // External values and explicit copy actions replace the entire draft, even
  // when the copied number equals the current value. Local numeric callbacks
  // keep the blank/fraction intact while being edited.
  if (
    (value !== undefined && incoming !== draft.source) ||
    resetKey !== lastResetKey
  ) {
    setLastResetKey(resetKey);
    setDraft({ raw: incoming, source: incoming, error: "" });
  }
  const error = draft.error || validation(draft.raw, min, max, step);
  useEffect(() => {
    input.current?.setCustomValidity(error);
  }, [error]);

  return (
    <>
      <input
        {...props}
        ref={(element) => {
          input.current = element;
          if (inputRef) inputRef.current = element;
        }}
        type="text"
        inputMode={step === "any" ? "decimal" : "numeric"}
        value={displayNumber(draft.raw)}
        aria-invalid={!!error || undefined}
        title="Pemisah ribuan otomatis. Desimal memakai koma."
        onPaste={(event) => {
          const pasted = event.clipboardData.getData("text").trim();
          if (!/^(?:\d+|\d{1,3}(?:\.\d{3})+)(?:,\d*)?$/.test(pasted)) {
            event.preventDefault();
            setDraft((current) => ({
              ...current,
              error:
                "Gunakan angka positif; titik untuk ribuan dan koma untuk desimal.",
            }));
          }
        }}
        onKeyDown={(event) => {
          const element = event.currentTarget;
          const cursor = element.selectionStart ?? 0;
          if (cursor !== element.selectionEnd) return;
          // Backspace/Delete across a grouping dot also removes the adjacent
          // digit, so the separator does not trap the cursor during editing.
          if (event.key === "Backspace" && element.value[cursor - 1] === ".")
            element.setSelectionRange(Math.max(0, cursor - 2), cursor);
          if (event.key === "Delete" && element.value[cursor] === ".")
            element.setSelectionRange(cursor, cursor + 2);
        }}
        onChange={(event) => {
          const element = event.currentTarget;
          const typed = element.value;
          const cursor = element.selectionStart ?? typed.length;
          const characters = typed.slice(0, cursor).replaceAll(".", "").length;
          const raw = canonicalNumber(typed);
          const validSyntax = /^\d*(?:\.\d*)?$/.test(raw);
          const source = !validSyntax
            ? incoming
            : typeof value === "number"
              ? String(Number(raw))
              : raw;
          setDraft({ raw, source, error: "" });
          if (validSyntax) onValueChange?.(raw);
          const formatted = displayNumber(raw);
          let nextCursor = 0;
          let seen = 0;
          while (nextCursor < formatted.length && seen < characters) {
            if (formatted[nextCursor] !== ".") seen++;
            nextCursor++;
          }
          // Set the DOM display immediately so cursor restoration precedes the
          // next keystroke, even when formatting inserts a grouping separator.
          element.value = formatted;
          element.setSelectionRange(nextCursor, nextCursor);
          element.setCustomValidity(validation(raw, min, max, step));
        }}
      />
      {name && <input type="hidden" name={name} value={draft.raw} />}
    </>
  );
}
