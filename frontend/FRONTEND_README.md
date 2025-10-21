# ShopX Analytics Frontend

Beautiful React-based sales analytics dashboard with real-time data visualization.

## Features

- **Dashboard Overview**: Real-time revenue metrics, order stats, and trend charts
- **Product Insights**: Product management with low stock alerts and performance tracking
- **Customer Analytics**: Customer segmentation, lifetime value analysis, and behavioral insights
- **Sales Rep Leaderboard**: Team performance tracking with conversion metrics
- **Real-time Updates**: Apollo Client integration with GraphQL subscriptions
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **Beautiful Charts**: Interactive visualizations with Recharts

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Apollo Client** - GraphQL client
- **Recharts** - Data visualization
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Headless UI** - Accessible components
- **Heroicons** - Icons

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env` file:

```bash
cp .env.example .env
```

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   ├── layout/         # Layout components (Sidebar, Header)
│   │   ├── dashboard/      # Dashboard-specific components
│   │   ├── products/       # Product components
│   │   ├── customers/      # Customer components
│   │   └── salesreps/      # Sales rep components
│   ├── pages/              # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Products.tsx
│   │   ├── Customers.tsx
│   │   └── SalesReps.tsx
│   ├── graphql/            # GraphQL queries and mutations
│   │   ├── queries.ts
│   │   └── mutations.ts
│   ├── lib/                # Third-party configurations
│   │   └── apollo-client.ts
│   └── utils/              # Utility functions
│       └── dateHelpers.ts
```

## Pages

### 1. Dashboard (`/dashboard`)
- Revenue metrics with growth indicators
- Order statistics
- Revenue trend chart
- Top 5 products table

### 2. Products (`/products`)
- Complete product inventory
- Low stock alerts
- Search and filtering
- Profit margin calculation

### 3. Customers (`/customers`)
- Customer list with LTV
- Segment distribution chart
- Segment analytics
- Search functionality

### 4. Sales Reps (`/sales-reps`)
- Performance leaderboard
- Revenue and conversion metrics
- Team statistics
- Top 3 highlighting

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
