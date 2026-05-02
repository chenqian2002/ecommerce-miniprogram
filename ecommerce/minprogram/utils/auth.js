// utils/auth.js
import { getStorage } from './storage';

export function hasToken() {
  return !!getStorage('token');
}

export function getUserRole() {
  const userInfo = getStorage('userInfo') || {};
  if (userInfo.isMerchant || userInfo.role === 'merchant') return 'merchant';
  return userInfo.role || getStorage('userRole') || 'customer';
}

export function isMerchantUser() {
  const userInfo = getStorage('userInfo') || {};
  return !!userInfo.isMerchant || userInfo.role === 'merchant' || getStorage('isMerchant') === true;
}

export function ensureLoggedIn(options = {}) {
  const { merchant = false } = options;
  if (hasToken()) return true;

  wx.showToast({ title: '请先登录', icon: 'none' });
  setTimeout(() => {
    wx.reLaunch({
      url: merchant ? '/pages/login/login?entry=merchant' : '/pages/login/login'
    });
  }, 800);
  return false;
}

export function ensureMerchantLogin() {
  if (!ensureLoggedIn({ merchant: true })) return false;
  if (!isMerchantUser()) {
    wx.showToast({ title: '请使用商家账号登录', icon: 'none' });
    setTimeout(() => {
      wx.reLaunch({ url: '/pages/login/login?entry=merchant' });
    }, 800);
    return false;
  }
  return true;
}
