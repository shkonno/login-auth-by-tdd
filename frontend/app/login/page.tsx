'use client'

import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const router = useRouter()

  const handleGoogleLogin = () => {
    // Google OAuth認証URLを生成
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID
    if (!clientId) {
      alert('Google OAuth設定が完了していません。NEXT_PUBLIC_GOOGLE_CLIENT_IDが設定されていません。')
      console.error('NEXT_PUBLIC_GOOGLE_CLIENT_ID:', clientId)
      return
    }

    // リダイレクトURIはフロントエンドのコールバックページ
    const redirectUri = process.env.NEXT_PUBLIC_GOOGLE_REDIRECT_URI || `${window.location.origin}/auth/google/callback`
    console.log('Google OAuth設定:', {
      clientId: clientId ? `${clientId.substring(0, 20)}...` : '未設定',
      redirectUri,
      origin: window.location.origin
    })

    const scopes = [
      'openid',
      'https://www.googleapis.com/auth/userinfo.email',
      'https://www.googleapis.com/auth/userinfo.profile'
    ].join(' ')

    const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth')
    authUrl.searchParams.set('client_id', clientId)
    authUrl.searchParams.set('redirect_uri', redirectUri)
    authUrl.searchParams.set('response_type', 'code')
    authUrl.searchParams.set('scope', scopes)
    authUrl.searchParams.set('access_type', 'offline')
    authUrl.searchParams.set('prompt', 'consent')

    console.log('Google認証URL:', authUrl.toString())
    
    // Google認証ページにリダイレクト
    window.location.href = authUrl.toString()
  }

  return (
    <main style={{ padding: '2rem', maxWidth: '400px', margin: '0 auto' }}>
      <h1>ログイン</h1>
      <div style={{ marginTop: '2rem' }}>
        <button
          onClick={handleGoogleLogin}
          style={{
            padding: '0.75rem 1.5rem',
            fontSize: '1rem',
            backgroundColor: '#4285f4',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            width: '100%'
          }}
        >
          Googleでログイン
        </button>
      </div>
      <div style={{ marginTop: '1rem', textAlign: 'center' }}>
        <a href="/">ホームに戻る</a>
      </div>
    </main>
  )
}

