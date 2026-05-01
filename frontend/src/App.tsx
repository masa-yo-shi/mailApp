import { Routes, Route } from 'react-router-dom'
import Category from './pages/category.tsx'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<div>Top page</div>} />
      <Route path="/category" element={<Category />} />
    </Routes>
  )
}
    