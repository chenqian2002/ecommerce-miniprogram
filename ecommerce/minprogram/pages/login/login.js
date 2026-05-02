// pages/login/login.js
import { post } from '../../utils/request';
import { setStorage, setUserInfo } from '../../utils/storage';
import { DEV_MODE } from '../../utils/config';

Page({
  data: {
    phone: '',
    password: '',
    loading: false,
    loginMode: 'user' // 'user' = 微信登录, 'merchant' = 账密登录
  },

  onLoad(options) {
    if (options.entry === 'merchant') {
      this.setData({ loginMode: 'merchant' });
    }
  },

  switchToMerchant() {
    this.setData({ loginMode: 'merchant' });
  },

  switchToUser() {
    this.setData({ loginMode: 'user' });
  },

  handlePhoneChange(e) {
    this.setData({ phone: e.detail.value });
  },

  handlePasswordChange(e) {
    this.setData({ password: e.detail.value });
  },

  // 买家测试账密登录
  async handleTestBuyerLogin() {
    const { phone, password } = this.data;
    if (!phone || !password) {
      wx.showToast({ title: '请输入手机号和密码', icon: 'none' });
      return;
    }
    this.setData({ loading: true });
    try {
      const res = await post('/auth/login', { phone, password });
      this.handleLoginSuccess(res);
    } catch (error) {
      console.error('Test buyer login error:', error);
      wx.showToast({ title: error?.message || '登录失败', icon: 'none' });
    } finally {
      this.setData({ loading: false });
    }
  },

  // 商家账密登录
  async handleLogin() {
    const { phone, password } = this.data;
    if (!phone || !password) {
      wx.showToast({ title: '请输入账号密码', icon: 'none' });
      return;
    }
    this.setData({ loading: true });
    try {
      const res = await post('/auth/login', { phone, password });
      this.handleLoginSuccess(res);
    } catch (error) {
      console.error('Login error:', error);
      wx.showToast({ title: error?.message || '登录失败', icon: 'none' });
    } finally {
      this.setData({ loading: false });
    }
  },

  // 用户微信登录
  async handleWechatLogin() {
    if (this.data.loading) return;
    this.setData({ loading: true });

    try {
      let code = '';

      if (DEV_MODE) {
        // 开发模式：直接用 test_code，跳过微信验证
        code = 'test_code';
      } else {
        const loginRes = await new Promise((resolve, reject) => {
          wx.login({ success: resolve, fail: reject });
        });
        if (!loginRes.code) {
          throw new Error('获取微信登录凭证失败');
        }
        code = loginRes.code;
      }

      const res = await post('/auth/wechat-login', {
        code: code,
        userInfo: { nickName: '微信用户', avatarUrl: '' }
      });

      this.handleLoginSuccess(res);
    } catch (error) {
      console.error('Wechat login error:', error);
      wx.showToast({ title: error?.message || '微信登录失败', icon: 'none' });
    } finally {
      this.setData({ loading: false });
    }
  },

  handleLoginSuccess(res) {
    const user = res.user || {};
    const isMerchant = !!user.isMerchant || user.role === 'merchant';

    setStorage('token', res.token);
    setUserInfo(user);
    setStorage('userRole', user.role || (isMerchant ? 'merchant' : 'customer'));
    setStorage('isMerchant', isMerchant);

    wx.showToast({ title: '登录成功', icon: 'success', duration: 1500 });

    setTimeout(() => {
      if (isMerchant) {
        wx.reLaunch({ url: '/pages/merchant/merchant' });
      } else {
        wx.reLaunch({ url: '/pages/index/index' });
      }
    }, 1500);
  }
});