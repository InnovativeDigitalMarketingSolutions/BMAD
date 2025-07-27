# Shadcn/ui Design Tokens Template

## Color Tokens

### Primary Colors
```css
:root {
  --primary: 222.2 84% 4.9%;
  --primary-foreground: 210 40% 98%;
}
```

### Secondary Colors
```css
:root {
  --secondary: 210 40% 96%;
  --secondary-foreground: 222.2 84% 4.9%;
}
```

### Accent Colors
```css
:root {
  --accent: 210 40% 96%;
  --accent-foreground: 222.2 84% 4.9%;
}
```

### Destructive Colors
```css
:root {
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;
}
```

### Muted Colors
```css
:root {
  --muted: 210 40% 96%;
  --muted-foreground: 215.4 16.3% 46.9%;
}
```

### Background Colors
```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
}
```

### Card Colors
```css
:root {
  --card: 0 0% 100%;
  --card-foreground: 222.2 84% 4.9%;
}
```

### Popover Colors
```css
:root {
  --popover: 0 0% 100%;
  --popover-foreground: 222.2 84% 4.9%;
}
```

### Border Colors
```css
:root {
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;
}
```

## Spacing Tokens

### Base Spacing
```css
:root {
  --radius: 0.5rem;
}
```

### Spacing Scale
- `xs`: 0.25rem (4px)
- `sm`: 0.5rem (8px)
- `md`: 1rem (16px)
- `lg`: 1.5rem (24px)
- `xl`: 2rem (32px)
- `2xl`: 3rem (48px)

## Typography Tokens

### Font Family
```css
:root {
  --font-family: Inter, system-ui, -apple-system, sans-serif;
}
```

### Font Sizes
```css
:root {
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  --font-size-4xl: 2.25rem;   /* 36px */
}
```

### Font Weights
```css
:root {
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
}
```

### Line Heights
```css
:root {
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}
```

## Component-Specific Tokens

### Button Tokens
```css
.button {
  --button-padding-x: 1rem;
  --button-padding-y: 0.5rem;
  --button-border-radius: var(--radius);
  --button-font-weight: var(--font-weight-medium);
}
```

### Input Tokens
```css
.input {
  --input-padding-x: 0.75rem;
  --input-padding-y: 0.5rem;
  --input-border-radius: var(--radius);
  --input-border-width: 1px;
}
```

### Card Tokens
```css
.card {
  --card-padding: 1.5rem;
  --card-border-radius: var(--radius);
  --card-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
}
```

## Dark Mode Tokens

### Dark Mode Colors
```css
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  
  --card: 222.2 84% 4.9%;
  --card-foreground: 210 40% 98%;
  
  --popover: 222.2 84% 4.9%;
  --popover-foreground: 210 40% 98%;
  
  --primary: 210 40% 98%;
  --primary-foreground: 222.2 84% 4.9%;
  
  --secondary: 217.2 32.6% 17.5%;
  --secondary-foreground: 210 40% 98%;
  
  --muted: 217.2 32.6% 17.5%;
  --muted-foreground: 215 20.2% 65.1%;
  
  --accent: 217.2 32.6% 17.5%;
  --accent-foreground: 210 40% 98%;
  
  --destructive: 0 62.8% 30.6%;
  --destructive-foreground: 210 40% 98%;
  
  --border: 217.2 32.6% 17.5%;
  --input: 217.2 32.6% 17.5%;
  --ring: 212.7 26.8% 83.9%;
}
```

## Usage Guidelines

### Component Development
1. **Use CSS Variables**: Always use CSS variables for consistent theming
2. **Semantic Naming**: Use semantic names that describe the purpose
3. **Dark Mode Support**: Ensure all tokens work in both light and dark modes
4. **Accessibility**: Maintain sufficient contrast ratios

### Token Organization
1. **Group by Category**: Colors, spacing, typography, etc.
2. **Consistent Naming**: Use kebab-case for CSS variables
3. **Documentation**: Document the purpose and usage of each token
4. **Version Control**: Track changes to design tokens

### Implementation
1. **CSS Custom Properties**: Use CSS custom properties for dynamic theming
2. **Fallbacks**: Provide fallback values for older browsers
3. **Testing**: Test tokens across different components and contexts
4. **Performance**: Minimize the number of custom properties 