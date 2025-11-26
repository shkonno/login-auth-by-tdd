/**登録フォームページの統合テスト
 * 
 * フロントエンドとバックエンドの統合をテストします。
 * 実際のAPIを呼び出して動作を確認します。
 * 
 * 【実行方法】
 * バックエンドサーバーが起動している必要があります。
 * docker-compose up -d backend で起動してください。
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import RegisterPage from './page'
import fetch from 'node-fetch'

// Node.js環境でfetchを使えるようにする
if (typeof global.fetch === 'undefined') {
  global.fetch = fetch as any
}

// 統合テストではfetchをモックしない（実際のAPIを呼び出す）
// ただし、テスト環境でバックエンドが起動していない場合はスキップする

describe('RegisterPage Integration Tests', () => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  let backendAvailable = false

  beforeAll(async () => {
    // バックエンドが起動しているか確認
    try {
      // Node.js環境でfetchが使えない場合は、node-fetchを使う
      const fetchFn = typeof fetch !== 'undefined' ? fetch : require('node-fetch')
      const response = await fetchFn(`${API_URL}/health`)
      backendAvailable = response.ok
    } catch (error) {
      backendAvailable = false
      console.warn('バックエンドサーバーに接続できません。統合テストをスキップします。', error)
    }
  })

  it('実際のAPIを呼び出してユーザー登録が成功する', async () => {
    if (!backendAvailable) {
      console.log('バックエンドが利用できないため、テストをスキップします')
      return
    }
    const user = userEvent.setup()
    render(<RegisterPage />)
    
    // 一意のメールアドレスを生成
    const uniqueEmail = `test_${Date.now()}@example.com`
    
    // 有効なデータを入力
    const emailInput = screen.getByLabelText(/メールアドレス/i)
    await user.clear(emailInput)
    await user.type(emailInput, uniqueEmail)
    
    const passwordInput = screen.getByLabelText(/パスワード/i)
    await user.clear(passwordInput)
    await user.type(passwordInput, 'password123')
    
    // フォーム送信
    const submitButton = screen.getByRole('button', { name: /登録/i })
    await user.click(submitButton)
    
    // 成功メッセージが表示されることを確認
    await waitFor(() => {
      expect(screen.getByText(/登録が完了しました/i)).toBeInTheDocument()
    }, { timeout: 5000 })
  })
})

