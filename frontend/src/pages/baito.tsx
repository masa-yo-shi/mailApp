import { useEffect, useState } from 'react'

type Mail = {
  id: string | number
  title: string
  description?: string
  category?: string
}

const apiURL = 'http://localhost:8000/mails/'

export default function Baito() {
  const [mails, setMails] = useState<Mail[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchMails = async () => {
      try {
        const res = await fetch(apiURL)
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
        const data: Mail[] = await res.json()
        setMails(data)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }
    fetchMails()
  }, [])

  const baito = mails.filter((m) => m.category === 'バイト')

  return (
    <main className="BaitoPage">
      <h1>バイトのメール</h1>
      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      {!loading && !error && (
        <>
          {baito.length === 0 ? (
            <p>バイト のメールはありません。</p>
          ) : (
            <table className="mails">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {baito.map((mail) => (
                  <tr key={mail.id}>
                    <td>{mail.title}</td>
                    <td>{mail.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </main>
  )
}