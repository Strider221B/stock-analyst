# Code Review: Stock Card Refactor & Recharts Integration
**Date**: 2026-04-03
**Changes**: Extract TickerCard → StockCard component + Add visualization with recharts

---

## Summary
This PR introduces a refactored `StockCard` component with integrated price charting via Recharts library. The changes extract the inline `TickerCard` component from `PortfolioSection.tsx` into a dedicated, feature-rich component with historical price visualization.

**Files Changed**:
- `frontend/package.json` (dependency addition)
- `frontend/package-lock.json` (lock file update)
- `frontend/src/components/portfolios/PortfolioSection.tsx` (refactoring)
- `frontend/src/components/portfolios/StockCard.tsx` (new component)
- `frontend/src/tests/StockCard.test.tsx` (new tests)

---

## ✅ Positive Aspects

### Component Architecture
- **Good separation of concerns**: TickerCard logic extracted into dedicated `StockCard` component
- **Reusability**: StockCard can now be used across other portfolio views
- **Props interface**: Clear, well-defined `StockCardProps` interface makes component flexible

### UI/UX Improvements
- **Price visualization**: Recharts integration provides quick visual insights into stock trends
- **Loading states**: Proper `<Loader2>` loading spinner during data fetch
- **Error handling**: User-friendly error message when chart fails to load
- **Price indicator**: Shows current price with color-coded direction (green/red for up/down)
- **Hover effects**: Smooth transitions and delete button reveal on hover
- **Responsive layout**: Grid-based responsive design maintained

### Code Quality
- **Error handling**: Try-catch blocks with proper error states
- **Unit tests**: Basic test coverage for new component (mocked dependencies)
- **Proper cleanup**: No memory leaks from useEffect hook
- **Accessibility**: Appropriate aria-labels and button roles

### UX Enhancements
- **Toast notifications**: Success feedback when removing ticker (`toast.success`)
- **Navigation ready**: Analyze button routes to `/analyze/{ticker}` placeholder

---

## ⚠️ Issues & Recommendations

### Critical/High Priority

#### 1. **Backend API Endpoint Not Verified**
```typescript
// StockCard.tsx:48
const response = await api.get<PricePoint[]>(`/api/marketdata/{ticker}/history`);
```
**Issue**: The endpoint `/api/marketdata/{ticker}/history` is not confirmed to exist.
**Action Required**:
- [ ] Verify backend implements this endpoint in `backend/routers/marketdata_routes.py`
- [ ] Check response format matches `PricePoint[]` interface
- [ ] Handle pagination if data sets are large (30+ days of data)

#### 2. **Missing Route Implementation**
```typescript
// StockCard.tsx:74
navigate(`/analyze/${ticker}`);
```
**Issue**: The `/analyze/{ticker}` route doesn't exist yet.
**Action Required**:
- [ ] Create analysis route/page in frontend routing
- [ ] Consider feature gating if analysis is not yet implemented

#### 3. **Bundle Size Impact**
**Issue**: Recharts adds ~60KB+ to bundle (with D3 dependencies).
**Recommendation**:
- [ ] Audit bundle size increase: `npm run build -- --visualize`
- [ ] Consider lazy-loading: `React.lazy(() => import('./StockCard'))`
- [ ] Evaluate alternative lightweight charting libs if size becomes problematic

---

### Medium Priority

#### 4. **Data Caching & Performance**
**Issue**: `StockCard` fetches data independently without caching - multiple instances trigger duplicate API calls.
**Recommendation**:
```typescript
// Consider using React Query / TanStack Query for caching
useQuery(['stock-history', ticker], () => fetchStockHistory(ticker))
```
Alternative: Implement local cache in `portfolioStore`.

#### 5. **Chart Configuration**
**Issue**: Chart styling is hardcoded; limited customization.
**Consider adding**:
- Time range selector (1D, 1W, 1M, 3M, 1Y)
- Configurable color scheme via props
- Volume/MACD overlays (future enhancement)

#### 6. **Empty State Handling**
**Issue**: If `history.length === 0`, chart shows nothing.
**Recommendation**:
```typescript
if (history.length === 0) {
    return <div className="text-muted-foreground text-xs">No data available</div>;
}
```

#### 7. **Props Callback Pattern**
**Issue**: The `onRemove` callback in props creates potential for duplicate removal logic.
```typescript
// StockCard.tsx:64-68
if (onRemove) {
    onRemove();  // ← Called but also calls removeTicker inside handler
    return;
}
```
**Recommendation**: Always use `onRemove` callback from parent for consistency.

---

### Low Priority / Nice-to-have

#### 8. **Test Coverage Gaps**
The test file (`StockCard.test.tsx`) has basic coverage but lacks:
- [ ] Interaction tests (click Analyze, click Remove)
- [ ] Error state tests
- [ ] Loading state tests
- [ ] Data fetching tests with mocked API responses

**Suggestion**: Add these tests before merging:
```typescript
it('calls handleAnalyze and navigates on button click', async () => {
    render(<StockCard {...props} />, { wrapper: BrowserRouter });
    const button = screen.getByText('Analyze Stock');
    await userEvent.click(button);
    expect(mockNavigate).toHaveBeenCalledWith('/analyze/AAPL');
});
```

#### 9. **Accessibility Considerations**
- [ ] Add `loading="lazy"` to chart containers (if using images)
- [ ] ARIA labels for chart data
- [ ] Keyboard navigation for buttons

#### 10. **Type Safety**
The `PricePoint` interface is good, but consider:
```typescript
interface PricePoint {
    date: string;      // Consider: ISO 8601 or Date type?
    price: number;
    // Missing: currency, volume, high/low?
}
```

---

## 🔍 Code Style & Patterns

### Follows Project Conventions ✅
- Component file naming: `StockCard.tsx` ✓
- Hook usage: `useState`, `useEffect` ✓
- Import organization: Correct ✓
- Styling: Tailwind classes appropriate ✓

### Potential Improvements
- Extract chart rendering into sub-component for testability
- Move icon constants to config file for maintainability

---

## ✏️ Non-Blocking Issues

1. **Type imports**: Could use type imports for better tree-shaking:
   ```typescript
   import type { PricePoint } from "../../types";
   ```

2. **Toast positioning**: Verify toast placement doesn't conflict with other UI elements

3. **Loading spinner**: Consider using skeleton instead of spinner for better UX

---

## 🧪 Pre-Merge Checklist

- [ ] Backend endpoint `/api/marketdata/{ticker}/history` exists and tested
- [ ] Bundle size verified (recharts impact acceptable)
- [ ] All tests pass locally: `./scripts/test.sh`
- [ ] No linting issues: `./scripts/lint.sh`
- [ ] Type checking passes: `./scripts/type-check.sh`
- [ ] Route `/analyze/{ticker}` created or feature-gated
- [ ] Manual testing: Add/remove portfolio item works end-to-end
- [ ] Navigation to analyze page works (or gracefully handles missing route)
- [ ] Mobile responsive verified (charts render correctly on small screens)

---

## 📋 Summary

**Status**: ⚠️ **Conditional Approval**
**Approve after**:
1. Backend endpoint verified/implemented
2. Missing route `/analyze/{ticker}` created or documented as future work
3. Bundle size impact acceptable (< 100KB additional)
4. All pre-merge checks pass

**Strengths**: Good component design, solid UX improvements, proper error handling
**Weaknesses**: Unverified dependencies, missing route, potential performance concerns with API caching

---

## 🎯 Next Steps (Post-Merge)

1. Implement backend endpoint with proper data validation
2. Create analysis page/route
3. Add React Query for data caching
4. Expand tests to cover interactions and edge cases
5. Monitor bundle size in production builds

