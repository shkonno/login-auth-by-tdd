'use client'

import { useState } from 'react'

export default function LoginPage() {
  const [emailError, setEmailError] = useState('')
  const [passwordError, setPasswordError] = useState('')

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const email = formData.get('email') as string
    const password = formData.get('password') as string
    
    if (!email || email.trim() === '') {
      setEmailError('メールアドレスは必須です')
      return
    }
    
    if (!password || password.trim() === '') {
      setPasswordError('パスワードは必須です')
      return
    }
    
    setEmailError('')
    setPasswordError('')
    
    // API呼び出し
    fetch('http://localhost:8000/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email,
        password
      })
    })
      .then(async (response) => {
        if (!response.ok) {
          const data = await response.json()
          if (response.status === 401) {
            // 認証エラー
            setEmailError('メールアドレスまたはパスワードが正しくありません')
            setPasswordError('')
          } else {
            // その他のエラー
            setEmailError('ログインに失敗しました')
            setPasswordError('')
          }
          return
        }
        const data = await response.json()
        // トークンをlocalStorageに保存
        if (data.access_token) {
          localStorage.setItem('access_token', data.access_token)
        }
      })
      .catch((error) => {
        console.error('エラー:', error)
      })
  }

  return (
    <div>
      <h1>ログイン</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="email">メールアドレス</label>
        <input type="email" id="email" name="email" />
        {emailError && <div>{emailError}</div>}
        <label htmlFor="password">パスワード</label>
        <input type="password" id="password" name="password" />
        {passwordError && <div>{passwordError}</div>}
        <button type="submit">ログイン</button>
      </form>
    </div>
  )
}

