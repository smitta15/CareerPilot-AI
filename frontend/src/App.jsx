import { createBrowserRouter, Outlet, RouterProvider } from 'react-router-dom'
import { CareerPilotProvider } from './context/CareerPilotContext'
import TopBar from './components/TopBar'
import HomePage from './pages/HomePage'
import ResultsPage from './pages/ResultsPage'
import ApplicationsPage from './pages/ApplicationsPage'

function RootLayout() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <TopBar />
      <Outlet />
    </div>
  )
}

const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      { path: '/', element: <HomePage /> },
      { path: '/results', element: <ResultsPage /> },
      { path: '/applications', element: <ApplicationsPage /> },
    ],
  },
])

function App() {
  return (
    <CareerPilotProvider>
      <RouterProvider router={router} />
    </CareerPilotProvider>
  )
}

export default App
