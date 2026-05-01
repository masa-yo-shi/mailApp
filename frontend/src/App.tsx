import { Routes, Route } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Baito from './pages/baito.tsx'

const apiURL = 'http://localhost:8000/mails/'

function MailList() {
  const [mails, setMails] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

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

  const renderCategoryTable = (category: string) => {
    const categoryMails = mails.filter((mail) => mail.category === category)

    if (categoryMails.length === 0) {
      return <p>{category} のメールはありません。</p>
    }

    return (
      <table className="mails">
        <thead>
          <tr>
            <th>Subject</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          {categoryMails.map((mail) => (
            <tr key={mail.id}>
              <td>{mail.title}</td>
              <td>{mail.description}</td>
            </tr>
          ))}
        </tbody>
      </table>
    )
  }

  return (
    <main className="App">
      <h1>Mails</h1>
      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}

      {!loading && !error && (
        <>
          <h2>バイト</h2>
          {renderCategoryTable('バイト')}

          <h2>図書館</h2>
          {renderCategoryTable('図書館')}

          <h2>その他</h2>
          {renderCategoryTable('その他')}
        </>
      )}
    </main>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<MailList />} />
      <Route path="/baito" element={<Baito />} />
    </Routes>
  )
}

export default App;
    