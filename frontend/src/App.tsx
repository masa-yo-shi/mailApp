import { Routes, Route } from 'react-router-dom'
import { useEffect, useState } from 'react'

const apiURL = 'http://localhost:8000/mails/'

function MailList() {

  const [mails, setMails] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')

  useEffect(() => {
    const fetchMails = async () => {
      try {
        const response = await fetch(apiURL)

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
  }, [])

  const filterMailsByCategory = (category: string) => {
    return mails.filter((mail) => mail.category === category)
  }

  return (
  <div>
    <header className="App-header">
      <h1>メール分類アプリ</h1>
      <div className="category">
        <button onClick={() => setSelectedCategory('バイト')}>バイト</button>
        <button onClick={() => setSelectedCategory('図書館')}>図書館</button>
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
            {filterMailsByCategory(selectedCategory).map((mail) => (
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
    </Routes>
  )
}

export default App;
    