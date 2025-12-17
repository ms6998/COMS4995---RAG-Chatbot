# 🎓 PathWise Frontend - Quick Start Guide

Your clean, modern React frontend is ready to go!

## What You Got

A complete React + Vite frontend that matches the elegant AI tool aesthetic from your screenshot:

✨ **Features:**
- Clean landing page with welcome message
- Suggested questions to get users started
- Smooth chat interface with message history
- Loading animations
- Fully responsive design
- Professional typography and colors
- Ready to connect to your FastAPI backend

## File Structure

```
pathwise-frontend/
├── src/
│   ├── App.jsx              # Main component with landing + chat
│   ├── App.css              # All styles (elegant & minimal)
│   └── main.jsx             # React entry point
├── public/
│   └── sparkles.svg         # Icon/favicon
├── package.json             # Dependencies
├── vite.config.js           # Vite config with proxy to backend
├── README.md                # Full documentation
├── INTEGRATION.md           # Backend connection guide
└── setup.sh                 # Quick setup script

```

## Getting Started (3 Steps!)

### 1️⃣ Install Dependencies
```bash
cd pathwise-frontend
npm install
```

### 2️⃣ Start Development Server
```bash
npm run dev
```

The app will open at http://localhost:3000

### 3️⃣ Connect Your Backend
Your FastAPI backend needs to run on port 8000 with this endpoint:

```python
@app.post("/api/ask")
async def ask_question(request: QuestionRequest):
    return {"answer": "Your answer here", "sources": []}
```

See `INTEGRATION.md` for complete backend setup instructions!

## Design Highlights

🎨 **Color Scheme:**
- Soft gradient background (white → light blue)
- Primary accent: Blue (#3b82f6)
- Clean, modern look

📝 **Typography:**
- Headlines: Fraunces (elegant serif)
- Body: DM Sans (clean sans-serif)
- Avoids generic fonts like Inter/Roboto

✨ **Animations:**
- Smooth page transitions
- Floating sparkle icon
- Typing indicators
- Message slide-ins

## Customization

Want to change colors? Edit CSS variables in `src/App.css`:

```css
:root {
  --color-accent: #3b82f6;        /* Change accent color */
  --color-bg-primary: #f8fafc;    /* Background color */
  /* etc. */
}
```

## What's Next?

1. ✅ Frontend is ready
2. 🔄 Connect your FastAPI backend (see INTEGRATION.md)
3. 🔄 Test the Q&A functionality
4. 🔄 Add the /plan endpoint for degree planning
5. 🔄 Deploy to Vercel/Netlify when ready

## Need Help?

- Check `README.md` for full documentation
- See `INTEGRATION.md` for backend connection details
- All code is commented and easy to modify

## Pro Tips

- The Vite proxy is configured to forward `/api/*` to `localhost:8000`
- Hot reload is enabled - changes appear instantly
- Use React DevTools browser extension for debugging
- Mobile-responsive out of the box

---

**Ready to build something amazing! 🚀**

Questions? Check the docs or modify the code - it's all yours!
