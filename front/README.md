# EmptyBay Manager - React Frontend

A modern, responsive React frontend for the EmptyBay Manager authentication system.

## Features

- 🔐 **User Authentication**: Login and registration forms
- 🎨 **Modern UI**: Clean, responsive design with gradient backgrounds
- 📱 **Mobile Friendly**: Responsive design that works on all devices
- 🚀 **Fast Performance**: Built with React hooks and modern patterns
- 🔒 **Secure**: Token-based authentication with localStorage
- 📊 **Dashboard**: User information and system status display

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- EmptyBay FastAPI backend running on `http://localhost:8000`

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The app will open in your browser at `http://localhost:3000`.

## Backend Connection

This frontend is designed to work with the EmptyBay FastAPI backend. Make sure your backend is running on `http://localhost:8000` before testing the frontend.

### API Endpoints Used

- `POST /login` - User authentication
- `POST /register` - User registration  
- `GET /me` - Get current user info
- `GET /status` - System status

## Project Structure

```
src/
├── components/          # React components
│   ├── Login.js        # Login form
│   ├── Register.js     # Registration form
│   ├── Dashboard.js    # User dashboard
│   ├── Navbar.js       # Navigation bar
│   ├── Auth.css        # Authentication styles
│   ├── Dashboard.css   # Dashboard styles
│   └── Navbar.css      # Navigation styles
├── context/            # React context
│   └── AuthContext.js  # Authentication state management
├── App.js              # Main application component
├── App.css             # Global styles
└── index.js            # Application entry point
```

## Available Scripts

- `npm start` - Start development server
- `npm test` - Run tests
- `npm run build` - Build for production
- `npm run eject` - Eject from Create React App

## Styling

The frontend uses custom CSS with:
- Modern gradient backgrounds
- Smooth animations and transitions
- Responsive grid layouts
- Consistent color scheme
- Mobile-first design approach

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

To modify the styling or add new features:

1. Edit the component files in `src/components/`
2. Update the corresponding CSS files
3. The changes will automatically reload in development mode

## Production Build

To create a production build:

```bash
npm run build
```

This creates an optimized build in the `build/` folder that can be deployed to any static hosting service.

## Troubleshooting

### Common Issues

1. **Backend Connection Error**: Ensure your FastAPI backend is running on port 8000
2. **CORS Issues**: The backend should allow requests from `http://localhost:3000`
3. **Port Already in Use**: Change the port by setting `PORT=3001` before running `npm start`

### Getting Help

If you encounter issues:
1. Check the browser console for error messages
2. Verify the backend is running and accessible
3. Check that all dependencies are installed correctly
