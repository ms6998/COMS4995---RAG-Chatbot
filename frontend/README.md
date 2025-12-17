# PathWise Frontend

A clean, modern React frontend for the ColumbiaCourse AI degree planning chatbot.

## Design Philosophy

- **Minimalist & Elegant**: Clean interface inspired by modern AI tools
- **Responsive**: Works seamlessly on desktop and mobile
- **Performant**: Built with Vite for lightning-fast development and builds
- **Accessible**: Semantic HTML and ARIA labels

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Lucide React** - Beautiful, consistent icons
- **CSS3** - Custom styling with CSS variables for theming

## Prerequisites

- Node.js 18+ and npm

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Development

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

### Project Structure

```
pathwise-frontend/
├── public/
│   └── sparkles.svg          # Favicon
├── src/
│   ├── App.jsx               # Main application component
│   ├── App.css               # Styles
│   └── main.jsx              # Entry point
├── index.html                # HTML template
├── vite.config.js            # Vite configuration
└── package.json              # Dependencies and scripts
```

## API Integration

The frontend expects a FastAPI backend running on `http://localhost:8000` with the following endpoints:

### POST `/api/ask`
Ask a question about degree requirements

**Request:**
```json
{
  "question": "What are the core courses for MS CS?"
}
```

**Response:**
```json
{
  "answer": "The core courses for MS CS are...",
  "sources": [...]
}
```

### POST `/api/plan` (Coming Soon)
Generate a personalized degree plan

## Features

### Landing Page
- Welcome message with AI branding
- Suggested questions to get started
- Smooth animations and transitions

### Chat Interface
- Real-time message display
- Loading indicators
- Smooth scrolling
- Message history

### Design Elements
- Custom gradient background
- Professional typography (DM Sans + Fraunces)
- Subtle animations and micro-interactions
- Responsive layout for all screen sizes

## Customization

### Colors
Edit CSS variables in `src/App.css`:

```css
:root {
  --color-bg-primary: #f8fafc;
  --color-accent: #3b82f6;
  /* ... */
}
```

### Typography
Fonts are loaded from Google Fonts. To change:

1. Update the import in `src/App.css`
2. Modify font-family declarations

## Building for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` directory, ready for deployment.

## Deployment

The built files can be deployed to any static hosting service:

- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront
- Any web server (nginx, Apache, etc.)

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

1. Keep the design clean and minimal
2. Maintain consistent spacing and typography
3. Test responsive behavior
4. Follow React best practices

## License

MIT
