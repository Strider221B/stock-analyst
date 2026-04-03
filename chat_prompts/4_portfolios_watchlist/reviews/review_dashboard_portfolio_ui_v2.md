# Code Review — Dashboard & Portfolio UI (v2)

**Date:** 2026-04-03
**Reviewer:** Antigravity
**Branch:** `main` (unstaged + untracked changes)
**Scope:** Full review of all pending changes introducing the Dashboard page, Portfolio components, and dependency/refactoring changes. This supersedes `review_dashboard_portfolio_ui.md`.

---

## Summary of Changes

| File | Type | Status |
|---|---|---|
| `frontend/src/pages/Dashboard.tsx` | New | Dashboard page — orchestrates portfolio sections |
| `frontend/src/components/portfolios/CreatePortfolioModal.tsx` | New | Modal with react-hook-form + zod validation |
| `frontend/src/components/portfolios/AddTickerModal.tsx` | New | Modal with Enter-key support and local error state |
| `frontend/src/components/portfolios/PortfolioSection.tsx` | New | Per-portfolio card grid with AlertDialog confirmation |
| `frontend/src/components/ui/button.tsx` | Modified | Slot import fix + `lg` padding tweak |
| `frontend/src/api/axios.ts` | Modified | `any` → `unknown` in queue types |
| `frontend/src/store/authStore.ts` | Modified | `LoginCredentials` type + `any` → `unknown` |
| `frontend/src/pages/auth/LoginForm.tsx` | Modified | Pass typed `LoginCredentials`, `error: unknown` catch |
| `frontend/src/lib/utils.ts` | Modified | Add `formatAccountType()` utility |
| `frontend/src/App.tsx` | Modified | Wire real `Dashboard` component |
| `frontend/package.json` + `package-lock.json` | Modified | Add Radix UI peer deps |

---

## Previous Blocker Resolution Status

The following items were raised as **blockers** in the previous review (`review_dashboard_portfolio_ui.md`) and have been verified as **resolved** in this changeset:

| ID | Issue | Resolved? |
|---|---|---|
| B1 | `login` store typed as `any` | ✅ `LoginCredentials` interface defined and used |
| B2 | `onKeyPress` deprecated | ✅ Replaced with `onKeyDown` in `AddTickerModal` |
| B3 | `confirm()` for destructive action | ✅ Replaced with `AlertDialog` in `PortfolioSection` |
| W1 | Inline `BadgeComponent` fallback | ✅ `Badge` installed from shadcn, inline fallback removed |
| W2 | Submit errors swallowed silently | ✅ `submitError` state displayed in `CreatePortfolioModal` |
| W5 | Double `useState` import | ✅ Merged into single `import { useEffect, useState }` |
| W6 | Redundant `isLoading` in mutations | ✅ Mutations no longer set `isLoading: true` |
| S2 | Uppercase only applied at submit | ✅ `onChange` now uppercases immediately |
| S3 | Inline `account_type` formatting | ✅ Extracted to `formatAccountType()` in `lib/utils.ts` |

---

## 🟢 Positives

1. **`LoginCredentials` interface is well-typed and correctly placed.** Exporting it from `authStore.ts` is the right call — it's the canonical source of truth for authentication. The `LoginForm` no longer casts credentials to `any`.

2. **`AlertDialog`-based confirmation in `PortfolioSection` is the correct pattern.** The `tickerToRemove` state drives the dialog open/closed state cleanly, and the `onOpenChange` handler resets the state on cancel. Good use of controlled dialog.

3. **`createPortfolio` / `addTickerToPortfolio` / `removeTicker` no longer pollute global `isLoading`.** Each modal manages its own `isSubmitting` flag locally. The global `isLoading` is now exclusively owned by `fetchPortfolios`, which is clean separation.

4. **`formatAccountType` is a pure, testable utility.** Moving it to `lib/utils.ts` is the right SOLID-aligned decision (`S` — single responsibility): formatting logic belongs in utils, not inside a render function.

5. **Error surfacing in `CreatePortfolioModal` is correct.** The Axios-aware error extraction pattern (`axios.isAxiosError`) is consistent with the rest of the codebase.

6. **`PortfolioSection` card UX is thoughtful.** Hover-reveal trash buttons (`opacity-0 group-hover:opacity-100`) keep the UI clean. The `aria-label` on the icon button is present and well-worded.

---

## 🔴 Blockers

### B1 — `formatAccountType` does not handle the `EMPLOYEE_EQUITY` case correctly

**File:** `frontend/src/lib/utils.ts` (line 7–9)

```typescript
export function formatAccountType(type: string): string {
  if (!type) return "";
  return type.charAt(0) + type.slice(1).toLowerCase().replace(/_/g, " ");
}
```

**Problem:** `EMPLOYEE_EQUITY` → `"Employee equity"` — the word after the underscore is not capitalised. The result looks like a bug to end users. The current implementation only capitalises the very first character of the entire string and lowercases the rest (replacing underscores with spaces). Expected: `"Employee Equity"`.

**Fix:** Use title-case formatting per word:
```typescript
export function formatAccountType(type: string): string {
  if (!type) return "";
  return type
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
}
```

---

### B2 — `AddTickerModal` error message does not reflect server detail

**File:** `frontend/src/components/portfolios/AddTickerModal.tsx` (lines 40–42)

```tsx
} catch (e: unknown) {
  console.error(e);
  setError("Failed to add ticker. Please check the symbol.");
}
```

**Problem:** The error message is always a static string regardless of what the server returned. If the backend sends a meaningful `detail` (e.g., `"Ticker XXXX not found"` or `"Already in portfolio"`), the user sees nothing specific. In contrast, `CreatePortfolioModal` correctly extracts `error.response?.data?.detail`.

**Fix:** Apply the same Axios-aware pattern:
```tsx
import axios from "axios";
// ...
} catch (e: unknown) {
  console.error(e);
  if (axios.isAxiosError(e)) {
    setError(e.response?.data?.detail || "Failed to add ticker. Please check the symbol.");
  } else {
    setError("An unexpected error occurred.");
  }
}
```

---

## 🟡 Warnings / Non-Blocking

### W1 — `button.tsx` `lg` padding change is undocumented

**File:** `frontend/src/components/ui/button.tsx` (line ~26)

```diff
- lg: "h-9 gap-1.5 px-2.5 has-data-[icon=inline-end]:pr-3 has-data-[icon=inline-start]:pl-3",
+ lg: "h-9 gap-1.5 px-4 has-data-[icon=inline-end]:pr-3 has-data-[icon=inline-start]:pl-3",
```

The horizontal padding was changed from `px-2.5` to `px-4` for the `lg` size, which is correct (the original was a bug — `lg` had *less* padding than the default `md` variant). However, there is no comment or commit note explaining it, making the intent unclear during future reviews.

**Recommendation:** Add an inline comment or mention it in the commit message so reviewers don't have to trace the history:
```typescript
// px-4: lg must have more padding than md (px-3.5). Corrects upstream shadcn typo.
lg: "h-9 gap-1.5 px-4 ...",
```

---

### W2 — `CreatePortfolioModal` does not reset `submitError` when the dialog is reopened

**File:** `frontend/src/components/portfolios/CreatePortfolioModal.tsx`

If a user attempts to create a portfolio, gets an error, closes the dialog, and reopens it, the stale `submitError` message is still visible before they have typed anything.

**Fix:** Add a `useEffect` that clears the error when `open` transitions to `true`:
```tsx
useEffect(() => {
  if (open) {
    setSubmitError(null);
    form.reset();
  }
}, [open, form]);
```
This also ensures the form fields are always clean on open.

---

### W3 — `PortfolioSection` does not surface `removeTicker` errors to the user

**File:** `frontend/src/components/portfolios/PortfolioSection.tsx` (lines 38–43)

```tsx
const handleRemoveTicker = async () => {
    if (tickerToRemove) {
        await removeTicker(portfolio.id, tickerToRemove);
        setTickerToRemove(null);
    }
};
```

If `removeTicker` throws (e.g., network failure), the error is silently swallowed. The `AlertDialog` closes, the dialog confirms, but the ticker is still in the list on the next fetch. The user gets no feedback.

**Fix:** Wrap in try/catch and show a toast or inline error:
```tsx
const handleRemoveTicker = async () => {
    if (!tickerToRemove) return;
    try {
        await removeTicker(portfolio.id, tickerToRemove);
        setTickerToRemove(null);
    } catch {
        // Surface this — consider a toast notification
        console.error("Failed to remove ticker");
    }
};
```

---

### W4 — `eslint-disable react-refresh/only-export-components` in `button.tsx` still lacks issue reference

**File:** `frontend/src/components/ui/button.tsx` (line 1)

As flagged in the previous review (W3), this disable comment still has no justification comment or issue reference. Per `AGENTS.md`: *"Adding `# noqa` without issue reference"* is a forbidden shortcut.

**Fix:** Add a justification comment:
```typescript
// eslint-disable-next-line react-refresh/only-export-components -- buttonVariants is a shared styling utility, not a component
```
Or configure the rule to allow named exports from `components/ui/**` in `eslint.config.js`.

---

### W5 — `Dashboard.tsx` has no error state for `fetchPortfolios` failure

**File:** `frontend/src/pages/Dashboard.tsx`

The `portfolioStore` exposes an `error` field which is populated on fetch failures, but `Dashboard.tsx` does not read or render it. If the API is unreachable, the user sees an empty state ("You don't have any portfolios yet."), which is misleading.

**Fix:**
```tsx
const { portfolios, fetchPortfolios, isLoading, error } = usePortfolioStore();

// Render:
{error && (
  <div className="text-destructive text-center py-4">{error}</div>
)}
```

---

## 🔵 Suggestions (Nice-to-Have)

### S1 — Add `useCallback` to `fetchPortfolios` in `Dashboard.tsx`

**File:** `frontend/src/pages/Dashboard.tsx` (line 14–15)

```tsx
useEffect(() => {
    fetchPortfolios();
}, [fetchPortfolios]);
```

`fetchPortfolios` is a Zustand action — it's stable by default (Zustand actions are not recreated on render). The `useEffect` dep array is technically correct but a warning-free approach is to wrap selectors with `useCallback` if they are derived. This is low priority but worth noting for future linting strictness.

### S2 — `AddTickerModal` should clear its state on close

**File:** `frontend/src/components/portfolios/AddTickerModal.tsx`

When the modal closes (cancelled or submitted), the `ticker` input and `error` state are not reset. If the user re-opens the modal, the previous ticker or error is still visible. Add an `onOpenChange` effect or call `setTicker("")` and `setError(null)` when `open` becomes `false`.

### S3 — Consider extracting the ticker card into its own component

**File:** `frontend/src/components/portfolios/PortfolioSection.tsx` (lines 69–98)

The per-ticker `<Card>` block nested inside `PortfolioSection` is ~30 lines. Extracting it to a `TickerCard` component would improve readability and make each component's responsibility clear (SOLID `S`).

---

## Pre-Merge Checklist

- [ ] **B1** — Fix `formatAccountType` to title-case each word (affects `EMPLOYEE_EQUITY`)
- [ ] **B2** — Extract server `detail` in `AddTickerModal` error handler
- [ ] **W2** — Reset `submitError` (and form) on dialog open in `CreatePortfolioModal`
- [ ] **W3** — Catch and surface `removeTicker` errors in `PortfolioSection`
- [ ] **W4** — Add eslint-disable justification comment in `button.tsx`
- [ ] **W5** — Render `error` from portfolio store in `Dashboard.tsx`
- [ ] Run `./scripts/check-all.sh` — exit 0 required before commit
