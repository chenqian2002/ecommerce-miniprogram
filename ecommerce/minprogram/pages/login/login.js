// pages/login/login.js
import { post } from '../../utils/request';
import { setStorage, setUserInfo } from '../../utils/storage';

Page({
  data: {
    phone: '13800138000',
    password: '123456',
    loading: false,
    entry: ''
  },

  onLoad(options) {
    this.setData({
      entry: options.entry || ''
    });
  },

  handlePhoneChange(e) {
    this.setData({ phone: e.detail.value });
  },

  handlePasswordChange(e) {
    this.setData({ password: e.detail.value });
  },

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
      wx.showToast({ 
        title: error?.message || '登录失败', 
        icon: 'none'
      });
    } finally {
      this.setData({ loading: false });
    }
  },

  async handleWechatLogin() {
    if (this.data.loading) return;

    this.setData({ loading: true });

    try {
      const loginRes = await new Promise((resolve, reject) => {
        wx.login({
          success: resolve,
          fail: reject
        });
      });

      if (!loginRes.code) {
        throw new Error('获取微信登录凭证失败');
      }

      const profileRes = await new Promise((resolve, reject) => {
        wx.getUserProfile({
          desc: '用于完善会员资料',
          success: resolve,
          fail: reject
        });
      });

      const res = await post('/auth/wechat-login', {
        code: loginRes.code,
        userInfo: profileRes.userInfo || {}
      });

      this.handleLoginSuccess(res);
    } catch (error) {
      console.error('Wechat login error:', error);
      wx.showToast({
        title: error?.message || '微信登录失败',
        icon: 'none'
      });
    } finally {
      this.setData({ loading: false });
    }
  },

      handleLoginSuccess(res) {
    const user = res.user || {};
    const isMerchant = !!user.isMerchant || user.role === 'merchant';
    const isMerchantEntry = this.data.entry === 'merchant';

    if (isMerchantEntry && !isMerchant) {
      wx.showToast({ title: '请使用商家账号登录', icon: 'none' });
      return;
    }

    setStorage('token', res.token);
    setUserInfo(user);
    setStorage('userRole', user.role || (user.isMerchant ? 'merchant' : 'customer'));
    setStorage('isMerchant', !!user.isMerchant);

    wx.showToast({ 
      title: '登录成功', 
      icon: 'success',
      duration: 1500
    });

    setTimeout(() => {
      if (isMerchant) {
        wx.reLaunch({
          url: '/pages/merchant/merchant'
        });
      } else {
        wx.reLaunch({
          url: '/pages/products/products'
        });
      }
    }, 1500);
  }


});



