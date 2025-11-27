/**ログインフォームページのテスト
 * 
 * t_wada形式のTDDで進めます。
 * 1. Red: 失敗するテストを書く
 * 2. Green: 最小限の実装でテストを通す
 * 3. Refactor: コードをきれいにする
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LoginPage from './page'

// fetchをモック
global.fetch = jest.fn()

describe('LoginPage', () => {
  it('ログインフォームページが表示される', () => {
    render(<LoginPage />)
    
    // ページタイトルが表示されることを確認
    expect(screen.getByRole('heading', { name: /ログイン/i })).toBeInTheDocument()
  })

  it('メールアドレス入力フィールドが表示される', () => {
    render(<LoginPage />)
    
    // メールアドレス入力フィールドが存在することを確認
    expect(screen.getByLabelText(/メールアドレス/i)).toBeInTheDocument()
  })

  it('パスワード入力フィールドが表示される', () => {
    render(<LoginPage />)
    
    // パスワード入力フィールドが存在することを確認
    expect(screen.getByLabelText(/パスワード/i)).toBeInTheDocument()
  })

  it('メールアドレスが空の場合、エラーメッセージが表示される', async () => {
    const user = userEvent.setup()
    render(<LoginPage />)
    
    // パスワードのみ入力
    const passwordInput = screen.getByLabelText(/パスワード/i)
    await user.type(passwordInput, 'password123')
    
    // フォーム送信
    const submitButton = screen.getByRole('button', { name: /ログイン/i })
    await user.click(submitButton)
    
    // エラーメッセージが表示されることを確認
    expect(screen.getByText(/メールアドレスは必須です/i)).toBeInTheDocument()
  })

  it('パスワードが空の場合、エラーメッセージが表示される', async () => {
    const user = userEvent.setup()
    render(<LoginPage />)
    
    // メールアドレスのみ入力
    const emailInput = screen.getByLabelText(/メールアドレス/i)
    await user.type(emailInput, 'test@example.com')
    
    // フォーム送信
    const submitButton = screen.getByRole('button', { name: /ログイン/i })
    await user.click(submitButton)
    
    // エラーメッセージが表示されることを確認
    expect(screen.getByText(/パスワードは必須です/i)).toBeInTheDocument()
  })

  it('有効なデータで送信するとAPIが呼ばれる', async () => {
    const user = userEvent.setup()
    // API成功レスポンスをモック
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        access_token: 'test-token-123'
      })
    })

    render(<LoginPage />)
    
    // 有効なデータを入力
    const emailInput = screen.getByLabelText(/メールアドレス/i)
    await user.type(emailInput, 'test@example.com')
    const passwordInput = screen.getByLabelText(/パスワード/i)
    await user.type(passwordInput, 'password123')
    
    // フォーム送信
    const submitButton = screen.getByRole('button', { name: /ログイン/i })
    await user.click(submitButton)
    
    // APIが呼ばれることを確認
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/login',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'password123'
          })
        })
      )
    })
  })

  it('存在しないメールアドレスで送信するとエラーメッセージが表示される', async () => {
    const user = userEvent.setup()
    // API 401エラーレスポンスをモック
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({
        detail: 'Invalid email or password'
      })
    })

    render(<LoginPage />)
    
    // 有効なデータを入力
    const emailInput = screen.getByLabelText(/メールアドレス/i)
    await user.type(emailInput, 'nonexistent@example.com')
    const passwordInput = screen.getByLabelText(/パスワード/i)
    await user.type(passwordInput, 'password123')
    
    // フォーム送信
    const submitButton = screen.getByRole('button', { name: /ログイン/i })
    await user.click(submitButton)
    
    // エラーメッセージが表示されることを確認
    await waitFor(() => {
      expect(screen.getByText(/メールアドレスまたはパスワードが正しくありません/i)).toBeInTheDocument()
    })
  })

  it('間違ったパスワードで送信するとエラーメッセージが表示される', async () => {
    const user = userEvent.setup()
    // API 401エラーレスポンスをモック
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({
        detail: 'Invalid email or password'
      })
    })

    render(<LoginPage />)
    
    // 有効なデータを入力
    const emailInput = screen.getByLabelText(/メールアドレス/i)
    await user.type(emailInput, 'test@example.com')
    const passwordInput = screen.getByLabelText(/パスワード/i)
    await user.type(passwordInput, 'wrongpassword')
    
    // フォーム送信
    const submitButton = screen.getByRole('button', { name: /ログイン/i })
    await user.click(submitButton)
    
    // エラーメッセージが表示されることを確認
    await waitFor(() => {
      expect(screen.getByText(/メールアドレスまたはパスワードが正しくありません/i)).toBeInTheDocument()
    })
  })

  it('ログイン成功時にトークンが保存される', async () => {
    const user = userEvent.setup()
    // localStorageをモック
    const mockLocalStorage = {
      setItem: jest.fn(),
      getItem: jest.fn(),
      removeItem: jest.fn(),
    }
    Object.defineProperty(window, 'localStorage', {
      value: mockLocalStorage,
      writable: true,
    })

    // API成功レスポンスをモック
    const testToken = 'test-access-token-123'
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        access_token: testToken
      })
    })

    render(<LoginPage />)
    
    // 有効なデータを入力
    const emailInput = screen.getByLabelText(/メールアドレス/i)
    await user.type(emailInput, 'test@example.com')
    const passwordInput = screen.getByLabelText(/パスワード/i)
    await user.type(passwordInput, 'password123')
    
    // フォーム送信
    const submitButton = screen.getByRole('button', { name: /ログイン/i })
    await user.click(submitButton)
    
    // トークンがlocalStorageに保存されることを確認
    await waitFor(() => {
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('access_token', testToken)
    })
  })
})

