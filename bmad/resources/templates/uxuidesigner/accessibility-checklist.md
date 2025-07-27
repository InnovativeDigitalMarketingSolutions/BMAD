# Accessibility Checklist

## Visual Design

### Color and Contrast
- [ ] **Color Contrast**: All text meets WCAG AA contrast ratios (4.5:1 for normal text, 3:1 for large text)
- [ ] **Color Independence**: Information is not conveyed by color alone
- [ ] **Focus Indicators**: Clear, visible focus indicators for all interactive elements
- [ ] **High Contrast Mode**: Design works in high contrast mode

### Typography
- [ ] **Font Size**: Minimum font size of 16px for body text
- [ ] **Line Height**: Adequate line height (1.5x for body text)
- [ ] **Font Scaling**: Text scales up to 200% without loss of functionality
- [ ] **Font Choice**: Clear, readable fonts with good character distinction

## Interactive Elements

### Buttons and Links
- [ ] **Touch Targets**: Minimum 44px touch targets for mobile
- [ ] **Spacing**: Adequate spacing between interactive elements
- [ ] **States**: Clear hover, focus, active, and disabled states
- [ ] **Labels**: Descriptive labels for all buttons and links

### Forms
- [ ] **Labels**: All form fields have associated labels
- [ ] **Error Messages**: Clear, descriptive error messages
- [ ] **Required Fields**: Clear indication of required fields
- [ ] **Validation**: Real-time validation with helpful feedback

### Navigation
- [ ] **Skip Links**: Skip navigation links for keyboard users
- [ ] **Breadcrumbs**: Clear navigation hierarchy
- [ ] **Menu Structure**: Logical menu structure and organization
- [ ] **Current Page**: Clear indication of current page/location

## Keyboard Navigation

### Tab Order
- [ ] **Logical Order**: Tab order follows logical reading order
- [ ] **No Traps**: No keyboard traps in modal dialogs or menus
- [ ] **Escape Key**: Escape key closes modals and dropdowns
- [ ] **Arrow Keys**: Arrow keys work for dropdowns and menus

### Keyboard Shortcuts
- [ ] **Documentation**: Keyboard shortcuts are documented
- [ ] **Consistency**: Shortcuts are consistent across the application
- [ ] **Conflicts**: No conflicts with browser or assistive technology shortcuts

## Screen Reader Support

### ARIA Labels
- [ ] **Descriptive Labels**: All interactive elements have descriptive ARIA labels
- [ ] **Landmarks**: Proper use of ARIA landmarks (header, nav, main, footer)
- [ ] **Roles**: Appropriate ARIA roles for custom components
- [ ] **States**: ARIA states for dynamic content (expanded, selected, etc.)

### Content Structure
- [ ] **Headings**: Proper heading hierarchy (h1, h2, h3, etc.)
- [ ] **Lists**: Proper list markup (ul, ol, dl)
- [ ] **Tables**: Proper table markup with headers
- [ ] **Images**: Alt text for all images

## Content and Media

### Images and Graphics
- [ ] **Alt Text**: Descriptive alt text for all images
- [ ] **Decorative Images**: Decorative images have empty alt text
- [ ] **Complex Images**: Complex images have detailed descriptions
- [ ] **SVG**: SVG graphics have proper accessibility attributes

### Video and Audio
- [ ] **Captions**: Video content has accurate captions
- [ ] **Transcripts**: Audio content has transcripts
- [ ] **Controls**: Media players have accessible controls
- [ ] **Auto-play**: No auto-playing media with sound

### Documents
- [ ] **PDF Accessibility**: PDF documents are properly tagged
- [ ] **Document Structure**: Documents have proper headings and structure
- [ ] **Language**: Document language is specified
- [ ] **Reading Order**: Logical reading order for screen readers

## Testing

### Automated Testing
- [ ] **Linting**: Accessibility linting tools are integrated
- [ ] **Contrast Checkers**: Color contrast is automatically checked
- [ ] **ARIA Validators**: ARIA attributes are validated
- [ ] **HTML Validation**: HTML is valid and semantic

### Manual Testing
- [ ] **Screen Reader Testing**: Tested with multiple screen readers
- [ ] **Keyboard Testing**: All functionality works with keyboard only
- [ ] **Zoom Testing**: Interface works at 200% zoom
- [ ] **Color Blind Testing**: Tested with color blindness simulators

## Documentation

### Guidelines
- [ ] **Accessibility Guidelines**: Team has access to accessibility guidelines
- [ ] **Training**: Team members are trained on accessibility
- [ ] **Review Process**: Accessibility is part of design and code review
- [ ] **Testing Plan**: Regular accessibility testing schedule 