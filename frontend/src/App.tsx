import { Routes, Route, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Login from './pages/login'

const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const apiURL = `${apiBase}/mails`

function MailList() {
  const navigate = useNavigate()
  const [mails, setMails] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')

  useEffect(() => {
    const fetchMails = async () => {
      setLoading(true)
      setError('')
      try {
        const url = new URL(apiURL)

        if (selectedCategory) {
          url.searchParams.set('mail_category', selectedCategory)
        }

        const response = await fetch(url.toString(), {
          credentials: 'include',
        })

        if (response.status === 401) {
          navigate('/login', { replace: true })
          return
        }

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        setMails(data)
      } catch (error) {
        if (error instanceof Error) {
          setError(error.message)
        } else {
          setError('Unknown error')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchMails()
  }, [selectedCategory, navigate])

  return (
  <div>
    <header className="App-header">
      <h1>メール分類アプリ</h1>
      <div className="category">
        <button onClick={() => setSelectedCategory('営業')}>営業</button>
        <button onClick={() => setSelectedCategory('製造')}>製造</button>
        <button onClick={() => setSelectedCategory('その他')}>その他</button>
      </div>
    </header>
    <main className="App">
      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}

      {!loading && !error && (
       <table>
          <thead>
            <tr>
              <th>件名</th>
              <th>詳細</th>
              <th>作成日時</th>
            </tr>
          </thead>
          <tbody>
            {mails.map((mail) => (
              <tr key={mail.id}>
                <td>{mail.title}</td>
                <td>{mail.description}</td>
                <td>{mail.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  </div>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<MailList />} />
      <Route path="/login" element={<Login />} />

    </Routes>
  )
}

export default App;
    