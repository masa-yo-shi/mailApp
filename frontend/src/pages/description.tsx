import type { FormEvent } from 'react'
import { useState } from 'react'
import { useLocation } from 'react-router-dom'

type Mail = {
    id: number
    title: string
    description: string
    created_at: string
    category?: string | null
    user_id: number
}

type MaildetailProps = {
    mail?: Mail | null
}

function Maildetail({ mail }: MaildetailProps) {
    const location = useLocation()
    const mailFromState = (location.state as { mail?: Mail } | null)?.mail
    const resolvedMail = mail ?? mailFromState ?? null
    const [responseTitle, setResponseTitle] = useState('')
    const [responseDescription, setResponseDescription] = useState('')
    const [submitError, setSubmitError] = useState('')
    const [submitSuccess, setSubmitSuccess] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)

    const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
    const submitResponse = async (mailId: number, responseTitle: string, responseDescription: string) => {
        const res = await fetch(`${apiBase}/mails/${mailId}/response`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                response_title: responseTitle,
                response_description: responseDescription,
            }),
        })

        if (!res.ok) {
            throw new Error(`Failed: ${res.status}`)
        }
        return res.json()
    }

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        setSubmitError('')
        setSubmitSuccess('')

        if (!resolvedMail) {
            setSubmitError('返信対象のメールが見つかりません。')
            return
        }

        const trimmedTitle = responseTitle.trim()
        const trimmedDescription = responseDescription.trim()

        if (!trimmedTitle && !trimmedDescription) {
            setSubmitError('返信タイトルか本文のどちらかを入力してください。')
            return
        }

        try {
            setIsSubmitting(true)
            await submitResponse(resolvedMail.id, trimmedTitle, trimmedDescription)
            setSubmitSuccess('返信を送信しました。')
            setResponseTitle('')
            setResponseDescription('')
        } catch (error) {
            if (error instanceof Error) {
                setSubmitError(error.message)
            } else {
                setSubmitError('Unknown error')
            }
        } finally {
            setIsSubmitting(false)
        }
    }

    if (!resolvedMail) {
        return (
            <div className="mail-detail-content">
                <h2>メールの内容</h2>
                <p>表示するメールがありません。</p>
            </div>
        )
    }

    return (
        <div className="mail-detail-content">
            <h2>メールの内容</h2>
            <p>{resolvedMail.title}</p>
            <p>{resolvedMail.description}</p>
            <form onSubmit={handleSubmit} className="mail-response-form">
                <h3>返信内容</h3>
                <label>
                    件名
                    <input
                        type="text"
                        value={responseTitle}
                        onChange={(event) => setResponseTitle(event.target.value)}
                        placeholder="返信の件名"
                    />
                </label>
                <label>
                    本文
                    <textarea
                        value={responseDescription}
                        onChange={(event) => setResponseDescription(event.target.value)}
                        placeholder="返信内容を入力"
                        rows={4}
                    />
                </label>
                {submitError && <p role="alert">{submitError}</p>}
                {submitSuccess && <p>{submitSuccess}</p>}
                <button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? '送信中...' : '返信を送信'}
                </button>
            </form>
        </div>
    )
}

export default Maildetail
  
