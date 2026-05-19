import { Routes, Route, useNavigate } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import Login from './pages/login'
import Maildetail from './pages/description'

const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const apiURL = `${apiBase}/mails`

type Mail = {
  id: number
  title: string
  description: string
  created_at: string
  category?: string | null
  user_id: number
}

const formatDateTime = (value: string) => {
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return value
  }
  return parsed.toLocaleString('ja-JP', { dateStyle: 'medium', timeStyle: 'short' })
}

function MailList() {
  const [mails, setMails] = useState<Mail[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [selectedMailId, setSelectedMailId] = useState<number | null>(null)
  const navigate = useNavigate()

  const selectedMail = useMemo(
    () => mails.find((mail) => mail.id === selectedMailId) ?? null,
    [mails, selectedMailId]
  )

  const handleMailClick = (mail: Mail) => {
    setSelectedMailId(mail.id)
    navigate(`/mails/${mail.id}`, { state: { mail } })
  }

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

        const data = (await response.json()) as Mail[]
        setMails(data)
        if (selectedMailId !== null && !data.some((mail) => mail.id === selectedMailId)) {
          setSelectedMailId(null)
        }
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
        {error && <p role="alert">{error}</p>}
        {!loading && !error && (
          <table className="mail-table" aria-label="受信メール一覧">
            <thead>
              <tr>
                <th scope="col">件名</th>
                <th scope="col">作成日時</th>
                <th scope="col">カテゴリ</th>
              </tr>
            </thead>
            <tbody>
              {mails.map((mail) => (
                <tr
                  key={mail.id}
                  className={mail.id === selectedMailId ? 'is-selected' : ''}
                >
                  <td>
                    <button
                      type="button"
                      className="mail-title-button"
                      onClick={() => handleMailClick(mail)}
                      aria-current={mail.id === selectedMailId ? 'true' : undefined}
                    >
                      {mail.title}
                    </button>
                  </td>
                  <td>{formatDateTime(mail.created_at)}</td>
                  <td>{mail.category ?? '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

      {!loading && !error && (

        <section className="mail-detail" aria-live="polite">
          {selectedMail ? (
            <Maildetail mail={selectedMail} />
          ) : (
            <p className="mail-detail-empty">件名をクリックすると本文が表示されます。</p>
          )}

        </section>
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
      <Route path="/mails/:id" element={<Maildetail />} />
    </Routes>
  )
}

export default App
    