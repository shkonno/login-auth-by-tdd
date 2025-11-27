'use client'

import { useState, useEffect } from 'react'

export default function DashboardPage() {
  const [user, setUser] = useState<{ id: string; email: string } | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    
    if (!token) {
      setError('ログインが必要です')
      setLoading(false)
      return
    }

    // API呼び出し
    fetch('http://localhost:8000/api/users/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(async (response) => {
        if (!response.ok) {
          setError('認証に失敗しました')
          return
        }
        const data = await response.json()
        setUser(data)
      })
      .catch((error) => {
        console.error('エラー:', error)
        setError('認証に失敗しました')
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div>
        <h1>ダッシュボード</h1>
        <p>読み込み中...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <h1>ダッシュボード</h1>
        <div>{error}</div>
      </div>
    )
  }

  return (
    <div>
      <h1>ダッシュボード</h1>
      {user && (
        <div>
          <p>メールアドレス: {user.email}</p>
        </div>
      )}
    </div>
  )
}

