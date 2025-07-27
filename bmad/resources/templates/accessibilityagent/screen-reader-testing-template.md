# Screen Reader Testing Template

## Screen Reader Compatibility Checklist

### Basic Navigation
- [ ] **Tab Navigation**: All interactive elements reachable
- [ ] **Arrow Key Navigation**: Arrow keys work for complex components
- [ ] **Enter/Space Activation**: Elements activate with Enter or Space
- [ ] **Escape Key**: Escape key closes modals and dropdowns
- [ ] **Focus Indicators**: Focus is visible and logical

### Announcements
- [ ] **Element Purpose**: Purpose is clearly announced
- [ ] **Element State**: Current state is communicated
- [ ] **Element Type**: Element type is identified
- [ ] **Element Value**: Current value is announced
- [ ] **Element Description**: Additional context is provided

### Dynamic Content
- [ ] **Live Regions**: Dynamic content is announced
- [ ] **State Changes**: State changes are communicated
- [ ] **Loading States**: Loading states are announced
- [ ] **Error Messages**: Errors are properly announced
- [ ] **Success Messages**: Success messages are announced

## Screen Reader Testing Guide

### NVDA (Windows)
1. **Installation**: Download from nvaccess.org
2. **Basic Commands**:
   - Tab: Navigate interactive elements
   - Arrow keys: Navigate within components
   - Enter/Space: Activate elements
   - Escape: Close modals
   - Ctrl+Home: Go to top of page
   - Ctrl+End: Go to bottom of page

3. **Testing Steps**:
   - Open application in Chrome/Firefox
   - Start NVDA (Ctrl+Alt+N)
   - Navigate using Tab key
   - Listen for proper announcements
   - Test all interactive elements
   - Verify state changes

### JAWS (Windows)
1. **Installation**: Commercial screen reader
2. **Basic Commands**:
   - Tab: Navigate interactive elements
   - Arrow keys: Navigate within components
   - Enter: Activate elements
   - Escape: Close modals
   - Home: Go to top of page
   - End: Go to bottom of page

3. **Testing Steps**:
   - Open application in Chrome/Firefox
   - Start JAWS
   - Navigate using Tab key
   - Listen for proper announcements
   - Test all interactive elements
   - Verify state changes

### VoiceOver (macOS)
1. **Activation**: Cmd+F5 or System Preferences
2. **Basic Commands**:
   - Tab: Navigate interactive elements
   - Arrow keys: Navigate within components
   - Space: Activate elements
   - Escape: Close modals
   - Cmd+Home: Go to top of page
   - Cmd+End: Go to bottom of page

3. **Testing Steps**:
   - Open application in Safari
   - Activate VoiceOver
   - Navigate using Tab key
   - Listen for proper announcements
   - Test all interactive elements
   - Verify state changes

### TalkBack (Android)
1. **Activation**: Settings > Accessibility > TalkBack
2. **Basic Commands**:
   - Swipe right/left: Navigate elements
   - Double tap: Activate elements
   - Swipe up/down: Navigate by type
   - Two-finger swipe: Scroll

3. **Testing Steps**:
   - Open application in Chrome
   - Activate TalkBack
   - Navigate using swipe gestures
   - Listen for proper announcements
   - Test all interactive elements
   - Verify state changes

## Component Testing Scenarios

### Button Testing
```jsx
// Test Button Component
<button onClick={handleClick}>Submit Form</button>

// Expected Announcement: "Submit Form, button"
// Test Steps:
// 1. Tab to button
// 2. Listen for announcement
// 3. Press Enter/Space
// 4. Verify action occurs
```

### Input Testing
```jsx
// Test Input Component
<input 
  type="text"
  aria-label="Email address"
  aria-required="true"
/>

// Expected Announcement: "Email address, edit text, required"
// Test Steps:
// 1. Tab to input
// 2. Listen for announcement
// 3. Type text
// 4. Verify text is announced
```

### Select Testing
```jsx
// Test Select Component
<select aria-label="Choose country">
  <option value="">Select country</option>
  <option value="us">United States</option>
</select>

// Expected Announcement: "Choose country, combo box"
// Test Steps:
// 1. Tab to select
// 2. Listen for announcement
// 3. Press Space to open
// 4. Use arrow keys to navigate
// 5. Press Enter to select
```

### Modal Testing
```jsx
// Test Modal Component
<div role="dialog" aria-modal="true">
  <h2>Confirm Action</h2>
  <button>Cancel</button>
  <button>Confirm</button>
</div>

// Expected Announcement: "Confirm Action, dialog"
// Test Steps:
// 1. Modal opens automatically
// 2. Focus is trapped in modal
// 3. Tab navigation works within modal
// 4. Escape key closes modal
// 5. Focus returns to trigger
```

## Common Issues and Solutions

### Missing Announcements
```jsx
// ❌ Bad - No announcement
<div onClick={handleClick}>Click me</div>

// ✅ Good - Proper announcement
<button onClick={handleClick}>Click me</button>
```

### Unclear Purpose
```jsx
// ❌ Bad - Unclear purpose
<button aria-label="Click">×</button>

// ✅ Good - Clear purpose
<button aria-label="Close dialog">×</button>
```

### Missing State Information
```jsx
// ❌ Bad - No state information
<button onClick={toggle}>Toggle</button>

// ✅ Good - State information
<button 
  onClick={toggle}
  aria-expanded={isExpanded}
  aria-pressed={isPressed}
>
  Toggle
</button>
```

### Inaccessible Dynamic Content
```jsx
// ❌ Bad - No live region
<div>{notification}</div>

// ✅ Good - Live region
<div aria-live="polite">{notification}</div>
```

## Testing Checklist

### Navigation Testing
- [ ] **Tab Order**: Logical tab order
- [ ] **Focus Indicators**: Visible focus indicators
- [ ] **Skip Links**: Skip navigation links work
- [ ] **Landmarks**: Proper landmark navigation
- [ ] **Headings**: Heading navigation works

### Interaction Testing
- [ ] **Button Activation**: Buttons activate with Enter/Space
- [ ] **Link Activation**: Links activate with Enter
- [ ] **Form Submission**: Forms submit with Enter
- [ ] **Modal Interaction**: Modals work with keyboard
- [ ] **Dropdown Interaction**: Dropdowns work with keyboard

### Content Testing
- [ ] **Text Content**: All text is announced
- [ ] **Images**: Images have alt text
- [ ] **Tables**: Tables are navigable
- [ ] **Lists**: Lists are properly announced
- [ ] **Forms**: Form labels are associated

### Dynamic Content Testing
- [ ] **Live Regions**: Dynamic content is announced
- [ ] **State Changes**: State changes are communicated
- [ ] **Error Messages**: Errors are announced
- [ ] **Success Messages**: Success messages are announced
- [ ] **Loading States**: Loading states are announced

## Performance Considerations

### Announcement Performance
- **Minimize Announcements**: Only announce necessary information
- **Batch Updates**: Group related announcements
- **Appropriate Live Regions**: Use correct live region types
- **Focus Management**: Efficient focus restoration

### Testing Performance
- **Automated Testing**: Use automated tools for basic checks
- **Manual Testing**: Regular manual testing with screen readers
- **Continuous Integration**: Include accessibility in CI/CD
- **Performance Monitoring**: Track accessibility metrics 