# Shadcn/ui Accessibility Testing Template

## Component Accessibility Checklist

### Basic Accessibility
- [ ] **Semantic HTML**: Component uses appropriate HTML elements
- [ ] **ARIA Labels**: All interactive elements have descriptive labels
- [ ] **ARIA Roles**: Proper ARIA roles are assigned
- [ ] **ARIA States**: Dynamic states are properly managed
- [ ] **Keyboard Navigation**: Full keyboard accessibility
- [ ] **Focus Management**: Clear focus indicators and logical tab order

### Visual Accessibility
- [ ] **Color Contrast**: Meets WCAG AA standards (4.5:1 for normal text, 3:1 for large text)
- [ ] **Focus Indicators**: Visible focus indicators (2px solid border minimum)
- [ ] **Touch Targets**: Minimum 44px touch targets for mobile
- [ ] **Spacing**: Adequate spacing between interactive elements
- [ ] **Typography**: Readable font sizes and line heights

### Screen Reader Compatibility
- [ ] **Announcements**: Component purpose is clearly announced
- [ ] **State Changes**: Dynamic changes are properly communicated
- [ ] **Navigation**: Screen reader navigation works correctly
- [ ] **Descriptions**: Complex components have proper descriptions
- [ ] **Live Regions**: Dynamic content uses appropriate live regions

### Design Token Accessibility

#### Color Tokens
```css
/* Primary Colors */
--primary: hsl(var(--primary)); /* Ensure 4.5:1 contrast ratio */
--primary-foreground: hsl(var(--primary-foreground));

/* Secondary Colors */
--secondary: hsl(var(--secondary));
--secondary-foreground: hsl(var(--secondary-foreground));

/* Destructive Colors */
--destructive: hsl(var(--destructive));
--destructive-foreground: hsl(var(--destructive-foreground));

/* Muted Colors */
--muted: hsl(var(--muted));
--muted-foreground: hsl(var(--muted-foreground));
```

#### Spacing Tokens
```css
/* Touch Targets */
--spacing-xs: 0.25rem;  /* 4px - minimum for fine controls */
--spacing-sm: 0.5rem;   /* 8px - minimum for touch targets */
--spacing-md: 1rem;     /* 16px - comfortable touch target */
--spacing-lg: 1.5rem;   /* 24px - large touch target */
--spacing-xl: 2rem;     /* 32px - extra large touch target */
```

#### Typography Tokens
```css
/* Font Sizes */
--font-size-xs: 0.75rem;    /* 12px - minimum readable size */
--font-size-sm: 0.875rem;   /* 14px - body text */
--font-size-base: 1rem;     /* 16px - standard body text */
--font-size-lg: 1.125rem;   /* 18px - large text */
--font-size-xl: 1.25rem;    /* 20px - heading text */

/* Line Heights */
--line-height-tight: 1.25;  /* For headings */
--line-height-normal: 1.5;  /* For body text */
--line-height-relaxed: 1.75; /* For long content */
```

#### Focus Tokens
```css
/* Focus Indicators */
--focus-ring: 2px solid hsl(var(--primary));
--focus-ring-offset: 2px;
--focus-ring-radius: var(--radius);
```

## Component-Specific Testing

### Button Component
- [ ] **Default State**: Proper button announcement
- [ ] **Disabled State**: Disabled state clearly communicated
- [ ] **Loading State**: Loading state properly announced
- [ ] **Icon Buttons**: Icon buttons have aria-label
- [ ] **Button Groups**: Group relationships properly defined

### Input Component
- [ ] **Label Association**: Input has associated label
- [ ] **Error States**: Error messages are properly announced
- [ ] **Required Fields**: Required state is communicated
- [ ] **Validation**: Real-time validation is announced
- [ ] **Autocomplete**: Autocomplete attributes are set

### Select Component
- [ ] **Dropdown Announcement**: Dropdown state is announced
- [ ] **Option Navigation**: Arrow keys work for option selection
- [ ] **Option Announcement**: Each option is properly announced
- [ ] **Selection State**: Selected option is clearly indicated
- [ ] **Keyboard Shortcuts**: Enter and Escape work correctly

### Modal Component
- [ ] **Focus Trap**: Focus is trapped within modal
- [ ] **Focus Restoration**: Focus returns to trigger element
- [ ] **Escape Key**: Modal closes with Escape key
- [ ] **Announcement**: Modal purpose is announced
- [ ] **Backdrop**: Backdrop interaction is handled

### Tabs Component
- [ ] **Tab List**: Tab list role is properly set
- [ ] **Tab Navigation**: Arrow keys work for tab navigation
- [ ] **Tab Panel**: Tab panel is properly associated
- [ ] **Active Tab**: Active tab is clearly indicated
- [ ] **Tab Content**: Tab content is properly announced

## Testing Tools and Methods

### Automated Testing
- **axe-core**: Automated accessibility testing
- **jest-axe**: Unit testing for accessibility
- **pa11y**: Command-line accessibility testing
- **Lighthouse**: Chrome DevTools accessibility audit

### Manual Testing
- **NVDA**: Windows screen reader testing
- **JAWS**: Windows screen reader testing
- **VoiceOver**: macOS screen reader testing
- **TalkBack**: Android screen reader testing

### Keyboard Testing
- **Tab Navigation**: All interactive elements reachable
- **Arrow Keys**: Arrow key navigation works
- **Enter/Space**: Activation keys work
- **Escape**: Escape key functionality
- **Focus Indicators**: Visible focus indicators

### Color Contrast Testing
- **WebAIM Contrast Checker**: Online contrast testing
- **Chrome DevTools**: Built-in contrast checking
- **axe DevTools**: Automated contrast checking
- **Manual Verification**: Visual inspection

## Common Issues and Solutions

### Missing ARIA Labels
```jsx
// ❌ Bad
<button><Icon /></button>

// ✅ Good
<button aria-label="Close dialog"><Icon /></button>
```

### Insufficient Color Contrast
```css
/* ❌ Bad - Low contrast */
--muted-foreground: hsl(215 16% 47%);

/* ✅ Good - High contrast */
--muted-foreground: hsl(215 16% 35%);
```

### Missing Focus Indicators
```css
/* ❌ Bad - No focus indicator */
.button:focus {
  outline: none;
}

/* ✅ Good - Clear focus indicator */
.button:focus {
  outline: 2px solid hsl(var(--primary));
  outline-offset: 2px;
}
```

### Inaccessible Touch Targets
```css
/* ❌ Bad - Too small */
.icon-button {
  width: 24px;
  height: 24px;
}

/* ✅ Good - Adequate size */
.icon-button {
  width: 44px;
  height: 44px;
  padding: 8px;
}
```

## Performance Considerations

### Accessibility Performance
- **ARIA Updates**: Minimize ARIA attribute changes
- **Live Regions**: Use appropriate live region types
- **Focus Management**: Efficient focus restoration
- **Screen Reader**: Optimize for screen reader performance

### Testing Performance
- **Automated Tests**: Fast feedback on accessibility issues
- **Manual Testing**: Regular manual accessibility audits
- **Continuous Integration**: Accessibility testing in CI/CD
- **Performance Monitoring**: Track accessibility metrics 