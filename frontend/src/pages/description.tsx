import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
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

type MailReplyTemplate = {
    id: number
    user_id: number
    template_name: string
    template_title: string
    template_description: string
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
    const [templates, setTemplates] = useState<MailReplyTemplate[]>([])
    const [selectedTemplateId, setSelectedTemplateId] = useState('')
    const [templatesError, setTemplatesError] = useState('')
    const [isTemplatesLoading, setIsTemplatesLoading] = useState(true)
    const [templateName, setTemplateName] = useState('')
    const [templateSaveError, setTemplateSaveError] = useState('')
    const [templateSaveSuccess, setTemplateSaveSuccess] = useState('')
    const [isTemplateSaving, setIsTemplateSaving] = useState(false)

    const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

    const temporaryTemplateLog = (message: string) => {
        setTemplateSaveSuccess(message)
        setTimeout(() => {
            setTemplateSaveSuccess('')
        }, 3000)
    }

    const temporarySubmitLog = (message: string) => {
        setSubmitSuccess(message)
        setTimeout(() => {
            setSubmitSuccess('')
        }, 3000)
    }

    
        

    useEffect(() => {
        const fetchTemplates = async () => {
            setTemplatesError('')
            setIsTemplatesLoading(true)

            try {
                const res = await fetch(`${apiBase}/mail-reply-templates`, {
                    credentials: 'include',
                })

                if (res.status === 401) {
                    setTemplates([])
                    setSelectedTemplateId('')
                    setTemplatesError('テンプレートの取得にはログインが必要です。')
                    return
                }

                if (!res.ok) {
                    throw new Error(`Failed: ${res.status}`)
                }

                const data = (await res.json()) as MailReplyTemplate[]
                setTemplates(data)
            } catch (error) {
                setTemplates([])
                setSelectedTemplateId('')
                if (error instanceof Error) {
                    setTemplatesError(error.message)
                } else {
                    setTemplatesError('Unknown error')
                }
            } finally {
                setIsTemplatesLoading(false)
            }
        }

        fetchTemplates()
    }, [apiBase])
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

    const saveTemplate = async (
        name: string,
        title: string,
        description: string
    ): Promise<MailReplyTemplate> => {
        const res = await fetch(`${apiBase}/mail-reply-templates`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                template_name: name,
                template_title: title,
                template_description: description,
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
            temporarySubmitLog('返信を送信しました。')
            setResponseTitle('')
            setResponseDescription('')
            setSelectedTemplateId('')
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

    const handleSaveTemplate = async () => {
        setTemplateSaveError('')
        setTemplateSaveSuccess('')

        const trimmedName = templateName.trim()
        const trimmedTitle = responseTitle.trim()
        const trimmedDescription = responseDescription.trim()

        if (!trimmedName) {
            setTemplateSaveError('テンプレート名を入力してください。')
            return
        }

        if (!trimmedTitle && !trimmedDescription) {
            setTemplateSaveError('テンプレートの件名か本文のどちらかを入力してください。')
            return
        }

        try {
            setIsTemplateSaving(true)
            const createdTemplate = await saveTemplate(
                trimmedName,
                trimmedTitle,
                trimmedDescription
            )
            setTemplates((prev) => [createdTemplate, ...prev])
            setSelectedTemplateId(String(createdTemplate.id))
            setTemplateName('')
            temporaryTemplateLog('テンプレートに追加しました。')
        } catch (error) {
            if (error instanceof Error) {
                setTemplateSaveError(error.message)
            } else {
                setTemplateSaveError('Unknown error')
            }
        } finally {
            setIsTemplateSaving(false)
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
            <div className="mail-message">
                <h2 className="mail-message-title">{resolvedMail.title}</h2>
                <div className="mail-message-body">{resolvedMail.description}</div>
            </div>

            <form onSubmit={handleSubmit} className="mail-response-form">
                <h3 className="form-title">返信内容</h3>

                <div className="form-row form-row-template">
                    <label className="form-label" htmlFor="template-select">
                        テンプレート
                    </label>
                    <select
                        id="template-select"
                        className="form-select"
                        value={selectedTemplateId}
                        onChange={(event) => {
                            const selectedId = event.target.value
                            setSelectedTemplateId(selectedId)

                            if (!selectedId) {
                                setResponseTitle('')
                                setResponseDescription('')
                                return
                            }

                            const selectedTemplate = templates.find(
                                (template) => String(template.id) === selectedId
                            )

                            if (selectedTemplate) {
                                setResponseTitle(selectedTemplate.template_title)
                                setResponseDescription(selectedTemplate.template_description)
                            }
                        }}
                        disabled={isTemplatesLoading || templates.length === 0}
                    >
                        <option value="">テンプレートを選択</option>
                        {templates.map((template) => (
                            <option key={template.id} value={template.id}>
                                {template.template_name}
                            </option>
                        ))}
                    </select>
                </div>
                {templatesError && <p className="form-message error" role="alert">{templatesError}</p>}
                {!isTemplatesLoading && templates.length === 0 && !templatesError && (
                    <p className="form-message">テンプレートがありません。</p>
                )}

                <div className="form-row">
                    <label className="form-label" htmlFor="response-title">
                        件名
                    </label>
                    <input
                        id="response-title"
                        className="form-input"
                        type="text"
                        value={responseTitle}
                        onChange={(event) => setResponseTitle(event.target.value)}
                        placeholder="返信の件名"
                    />
                </div>

                <div className="form-row form-row-textarea">
                    <label className="form-label" htmlFor="response-description">
                        本文
                    </label>
                    <textarea
                        id="response-description"
                        className="form-textarea"
                        value={responseDescription}
                        onChange={(event) => setResponseDescription(event.target.value)}
                        placeholder="返信内容を入力"
                        rows={4}
                    />
                </div>

                <div className="form-row form-row-template-name">
                    <label className="form-label" htmlFor="template-name">
                        テンプレート名
                    </label>
                    <input
                        id="template-name"
                        className="form-input"
                        type="text"
                        value={templateName}
                        onChange={(event) => setTemplateName(event.target.value)}
                        placeholder="例: お礼の返信"
                    />
                </div>

                {templateSaveError && (
                    <p className="form-message error" role="alert">{templateSaveError}</p>
                )}
                {templateSaveSuccess && <p className="form-message">{templateSaveSuccess}</p>}

                <div className="form-actions">
                    <button
                        type="button"
                        className="button secondary"
                        onClick={handleSaveTemplate}
                        disabled={isTemplateSaving}
                    >
                        {isTemplateSaving ? '保存中...' : 'テンプレートに追加'}
                    </button>
                    <button type="submit" className="button primary" disabled={isSubmitting}>
                        {isSubmitting ? '送信中...' : '返信を送信'}
                    </button>
                </div>

                {submitError && <p className="form-message error" role="alert">{submitError}</p>}
                {submitSuccess && <p className="form-message">{submitSuccess}</p>}
            </form>
        </div>
    )
}

export default Maildetail
  
