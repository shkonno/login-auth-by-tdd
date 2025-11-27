/**ダッシュボードページのテスト
 * 
 * t_wada形式のTDDで進めます。
 * 1. Red: 失敗するテストを書く
 * 2. Green: 最小限の実装でテストを通す
 * 3. Refactor: コードをきれいにする
 */

import { render, screen, waitFor } from '@testing-library/react'
import DashboardPage from './page'

// fetchをモック
global.fetch = jest.fn()

// localStorageをモック
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
})

describe('DashboardPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('ダッシュボードページが表示される', () => {
    // トークンがあることをモック
    mockLocalStorage.getItem.mockReturnValue('test-token-123')
    
    // API成功レスポンスをモック
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        id: '123',
        email: 'test@example.com'
      })
    })

    render(<DashboardPage />)
    
    // ページタイトルが表示されることを確認
    expect(screen.getByRole('heading', { name: /ダッシュボード/i })).toBeInTheDocument()
  })

  it('ユーザー情報が表示される', async () => {
    // トークンがあることをモック
    mockLocalStorage.getItem.mockReturnValue('test-token-123')
    
    const testUser = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      email: 'test@example.com'
    }
    
    // API成功レスポンスをモック
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => testUser
    })

    render(<DashboardPage />)
    
    // ユーザー情報が表示されることを確認
    await waitFor(() => {
      expect(screen.getByText(new RegExp(testUser.email))).toBeInTheDocument()
    })
    
    // APIが正しく呼ばれることを確認
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/users/me',
      expect.objectContaining({
        headers: {
          'Authorization': 'Bearer test-token-123'
        }
      })
    )
  })

  it('トークンがない場合、エラーメッセージが表示される', async () => {
    // トークンがないことをモック
    mockLocalStorage.getItem.mockReturnValue(null)
    
    render(<DashboardPage />)
    
    // エラーメッセージが表示されることを確認
    await waitFor(() => {
      expect(screen.getByText(/ログインが必要です/i)).toBeInTheDocument()
    })
  })

  it('APIエラーの場合、エラーメッセージが表示される', async () => {
    // トークンがあることをモック
    mockLocalStorage.getItem.mockReturnValue('test-token-123')
    
    // API 401エラーレスポンスをモック
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({
        detail: { error: 'Invalid or expired token' }
      })
    })

    render(<DashboardPage />)
    
    // エラーメッセージが表示されることを確認
    await waitFor(() => {
      expect(screen.getByText(/認証に失敗しました/i)).toBeInTheDocument()
    })
  })
})

