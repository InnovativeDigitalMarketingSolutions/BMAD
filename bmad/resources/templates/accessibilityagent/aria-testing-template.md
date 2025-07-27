# ARIA Testing Template

## ARIA Validation Checklist

### ARIA Labels
- [ ] **aria-label**: All interactive elements have descriptive labels
- [ ] **aria-labelledby**: Elements are properly labeled by other elements
- [ ] **aria-describedby**: Elements have descriptive text
- [ ] **aria-title**: Elements have appropriate titles

### ARIA Roles
- [ ] **button**: Button elements have button role
- [ ] **link**: Link elements have link role
- [ ] **checkbox**: Checkbox elements have checkbox role
- [ ] **radio**: Radio elements have radio role
- [ ] **textbox**: Input elements have textbox role
- [ ] **combobox**: Select elements have combobox role
- [ ] **listbox**: List elements have listbox role
- [ ] **menuitem**: Menu items have menuitem role
- [ ] **tab**: Tab elements have tab role
- [ ] **tabpanel**: Tab panels have tabpanel role

### ARIA States
- [ ] **aria-expanded**: Expandable elements show expansion state
- [ ] **aria-selected**: Selected elements show selection state
- [ ] **aria-checked**: Checkable elements show checked state
- [ ] **aria-pressed**: Toggle buttons show pressed state
- [ ] **aria-hidden**: Hidden elements are properly hidden
- [ ] **aria-disabled**: Disabled elements show disabled state
- [ ] **aria-invalid**: Invalid elements show error state
- [ ] **aria-required**: Required elements show required state

### ARIA Properties
- [ ] **aria-required**: Required fields are marked
- [ ] **aria-invalid**: Invalid fields show error state
- [ ] **aria-describedby**: Error messages are associated
- [ ] **aria-controls**: Controlling elements are linked
- [ ] **aria-owns**: Parent-child relationships are defined
- [ ] **aria-activedescendant**: Active descendant is tracked

### ARIA Live Regions
- [ ] **aria-live**: Dynamic content is announced
- [ ] **aria-atomic**: Live region updates are atomic
- [ ] **aria-relevant**: Relevant changes are announced
- [ ] **aria-busy**: Loading states are communicated

## Component-Specific ARIA Testing

### Button Components
```jsx
// Standard Button
<button aria-label="Submit form">Submit</button>

// Icon Button
<button aria-label="Close dialog" aria-pressed="false">
  <Icon />
</button>

// Toggle Button
<button aria-pressed="true" aria-label="Toggle notifications">
  <BellIcon />
</button>
```

### Form Components
```jsx
// Text Input
<input 
  aria-label="Email address"
  aria-required="true"
  aria-invalid="false"
  aria-describedby="email-error"
/>

// Checkbox
<input 
  type="checkbox"
  aria-label="Accept terms and conditions"
  aria-checked="false"
/>

// Select
<select aria-label="Choose country" aria-required="true">
  <option value="">Select country</option>
  <option value="us">United States</option>
</select>
```

### Navigation Components
```jsx
// Tab Navigation
<div role="tablist" aria-label="Product categories">
  <button role="tab" aria-selected="true" aria-controls="panel-1">
    Overview
  </button>
  <button role="tab" aria-selected="false" aria-controls="panel-2">
    Details
  </button>
</div>

// Menu
<nav role="navigation" aria-label="Main navigation">
  <ul role="menubar">
    <li role="menuitem" aria-haspopup="true">
      Products
    </li>
  </ul>
</nav>
```

### Modal Components
```jsx
// Modal Dialog
<div 
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
  aria-describedby="modal-description"
>
  <h2 id="modal-title">Confirm Action</h2>
  <p id="modal-description">Are you sure you want to proceed?</p>
</div>
```

## Testing Methods

### Automated Testing
```javascript
// Using axe-core
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('should not have accessibility violations', async () => {
  const { container } = render(<MyComponent />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### Manual Testing
1. **Screen Reader Testing**
   - Navigate using Tab key
   - Listen for proper announcements
   - Test all interactive elements
   - Verify state changes are announced

2. **Keyboard Testing**
   - Tab through all elements
   - Use Enter/Space for activation
   - Use Arrow keys for navigation
   - Use Escape for closing

3. **Visual Testing**
   - Check focus indicators
   - Verify contrast ratios
   - Test with high contrast mode
   - Test with zoom levels

## Common ARIA Issues

### Missing Labels
```jsx
// ❌ Bad - No label
<input type="text" />

// ✅ Good - Has label
<input type="text" aria-label="Search query" />
```

### Incorrect Roles
```jsx
// ❌ Bad - Wrong role
<div role="button" onClick={handleClick}>Click me</div>

// ✅ Good - Semantic element
<button onClick={handleClick}>Click me</button>
```

### Missing States
```jsx
// ❌ Bad - No state
<button onClick={toggleMenu}>Menu</button>

// ✅ Good - Has state
<button 
  onClick={toggleMenu}
  aria-expanded={isOpen}
  aria-controls="menu"
>
  Menu
</button>
```

### Inaccessible Live Regions
```jsx
// ❌ Bad - No live region
<div>{notification}</div>

// ✅ Good - Has live region
<div aria-live="polite" aria-atomic="true">
  {notification}
</div>
```

## Validation Tools

### Browser DevTools
- **Chrome**: Accessibility panel
- **Firefox**: Accessibility inspector
- **Safari**: Accessibility inspector
- **Edge**: Accessibility panel

### Testing Libraries
- **axe-core**: Automated testing
- **jest-axe**: Unit testing
- **pa11y**: Command-line testing
- **Lighthouse**: Performance and accessibility

### Screen Readers
- **NVDA**: Windows
- **JAWS**: Windows
- **VoiceOver**: macOS
- **TalkBack**: Android

## Best Practices

### Semantic HTML First
```jsx
// ✅ Prefer semantic HTML
<button onClick={handleClick}>Click me</button>

// ❌ Avoid unnecessary ARIA
<div role="button" onClick={handleClick}>Click me</div>
```

### Descriptive Labels
```jsx
// ✅ Descriptive label
<button aria-label="Close user profile dialog">×</button>

// ❌ Generic label
<button aria-label="Close">×</button>
```

### State Management
```jsx
// ✅ Proper state management
<button 
  aria-expanded={isExpanded}
  aria-controls="content"
  onClick={toggle}
>
  Toggle
</button>
```

### Error Handling
```jsx
// ✅ Error association
<input 
  aria-invalid={hasError}
  aria-describedby={hasError ? "error-message" : undefined}
/>
{hasError && <div id="error-message">Error message</div>}
``` 