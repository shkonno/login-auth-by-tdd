'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

export default function GoogleCallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('認証中...')

  useEffect(() => {
    const code = searchParams.get('code')
    const error = searchParams.get('error')

    if (error) {
      setStatus('error')
      setMessage(`認証エラー: ${error}`)
      return
    }

    if (!code) {
      setStatus('error')
      setMessage('認証コードが取得できませんでした')
      return
    }

    // バックエンドAPIを呼び出してトークンを取得
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
    const apiUrl = `${backendUrl}/auth/google/callback?code=${encodeURIComponent(code)}`
    console.log('バックエンドAPI呼び出し:', apiUrl)
    
    fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(async (response) => {
        console.log('APIレスポンス:', response.status, response.statusText)
        if (!response.ok) {
          const errorText = await response.text()
          console.error('APIエラーレスポンス:', errorText)
          let errorData
          try {
            errorData = JSON.parse(errorText)
          } catch {
            errorData = { detail: errorText || '認証に失敗しました' }
          }
          throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
        }
        return response.json()
      })
      .then((data) => {
        // トークンをlocalStorageに保存
        if (data.access_token) {
          localStorage.setItem('access_token', data.access_token)
        }
        if (data.refresh_token) {
          localStorage.setItem('refresh_token', data.refresh_token)
        }
        setStatus('success')
        setMessage('認証に成功しました。ダッシュボードにリダイレクトします...')
        // ダッシュボードにリダイレクト（またはホームに戻る）
        setTimeout(() => {
          router.push('/')
        }, 2000)
      })
      .catch((error) => {
        setStatus('error')
        console.error('認証エラー:', error)
        setMessage(`認証に失敗しました: ${error.message || '不明なエラー'}`)
      })
  }, [searchParams, router])

  return (
    <main style={{ padding: '2rem', maxWidth: '400px', margin: '0 auto', textAlign: 'center' }}>
      <h1>Google認証</h1>
      <div style={{ marginTop: '2rem' }}>
        {status === 'loading' && <p>{message}</p>}
        {status === 'success' && (
          <div>
            <p style={{ color: 'green' }}>{message}</p>
          </div>
        )}
        {status === 'error' && (
          <div>
            <p style={{ color: 'red' }}>{message}</p>
            <button
              onClick={() => router.push('/login')}
              style={{
                marginTop: '1rem',
                padding: '0.5rem 1rem',
                fontSize: '1rem',
                cursor: 'pointer'
              }}
            >
              ログインページに戻る
            </button>
          </div>
        )}
      </div>
    </main>
  )
}

