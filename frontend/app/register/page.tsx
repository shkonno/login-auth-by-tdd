'use client'

import { useState } from 'react'

export default function RegisterPage() {
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
    
    if (!password || password.length < 8) {
      setPasswordError('パスワードは8文字以上で入力してください')
      return
    }
    
    setEmailError('')
    setPasswordError('')
    
    // API呼び出し
    fetch('http://localhost:8000/api/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email,
        password
      })
    })
  }

  return (
    <div>
      <h1>ユーザー登録</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="email">メールアドレス</label>
        <input type="email" id="email" name="email" />
        {emailError && <div>{emailError}</div>}
        <label htmlFor="password">パスワード</label>
        <input type="password" id="password" name="password" />
        {passwordError && <div>{passwordError}</div>}
        <button type="submit">登録</button>
      </form>
    </div>
  )
}

