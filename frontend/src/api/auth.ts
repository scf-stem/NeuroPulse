/**
 * Tremor Guard - Auth API
 * 震颤卫士 - 认证 API
 */

import apiClient from './index'
import type { User, TokenResponse, RegisterRequest } from '@/types'

export const authApi = {
  /**
   * 用户登录
   */
  async login(email: string, password: string): Promise<TokenResponse> {
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)

    const response = await apiClient.post<TokenResponse>('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  /**
   * 用户注册
   * 注册成功后直接返回 Token（自动登录）
   */
  async register(data: RegisterRequest): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/register', data)
    return response.data
  },

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me')
    return response.data
  },

  /**
   * 登出
   */
  async logout(): Promise<void> {
    await apiClient.post('/auth/logout')
  },

  /**
   * 刷新 Token
   */
  async refreshToken(): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/refresh')
    return response.data
  },
}
