/**
 * 全局应用状态
 */
import { create } from 'zustand'

interface AppState {
  // 侧边栏收起状态
  collapsed: boolean
  toggleCollapsed: () => void

  // 当前选中的菜单
  selectedMenu: string
  setSelectedMenu: (key: string) => void
}

export const useAppStore = create<AppState>((set) => ({
  collapsed: false,
  toggleCollapsed: () => set((state) => ({ collapsed: !state.collapsed })),

  selectedMenu: 'dashboard',
  setSelectedMenu: (key) => set({ selectedMenu: key }),
}))
