import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

function Login() {
    const navigate = useNavigate()
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const isDisabled = loading || !username.trim() || !password

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        if (isDisabled) {
            return
        }

        setLoading(true)
        setError('')

        try {
            const body = new URLSearchParams({
                username: username.trim(),
                password,
            })

            const response = await fetch(`${apiBase}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body,
                credentials: 'include',
            })

            if (!response.ok) {
                if (response.status === 401) {
                    setError('ユーザー名またはパスワードが違います。')
                    return
                }
                setError('ログインに失敗しました。もう一度お試しください。')
                return
            }

            navigate('/')
        } catch (fetchError) {
            setError('ネットワークエラーが発生しました。接続を確認してください。')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="login-page">
            <div className="login-shell">
                <div className="login-panel">
                    <header>
                        <h1>Mail Classifier</h1>
                    </header>
                    <p className="login-subtitle">
                        受信メールの整理を続けるにはログインしてください。
                    </p>

                    <form className="login-form" onSubmit={handleSubmit}>
                        <label className="login-field">
                            <span>ユーザー名</span>
                            <input
                                autoComplete="username"
                                value={username}
                                onChange={(event) => setUsername(event.target.value)}
                                placeholder="例: johndoe"
                                required
                            />
                        </label>

                        <label className="login-field">
                            <span>パスワード</span>
                            <input
                                type="password"
                                autoComplete="current-password"
                                value={password}
                                onChange={(event) => setPassword(event.target.value)}
                                placeholder="8文字以上"
                                required
                            />
                        </label>

                        {error && <p className="login-error">{error}</p>}

                        <button className="login-button" type="submit" disabled={isDisabled}>
                            {loading ? 'ログイン中…' : 'ログイン'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    )
}

export default Login
