// pages/login/login.js
import { post } from '../../utils/request';
import { setStorage, setUserInfo } from '../../utils/storage';

Page({
  data: {
    phone: '13800138000',
    password: '123456',
    loading: false
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
      console.log('Logging in...');
      const res = await post('/auth/login', { phone, password });
      
      console.log('Login response:', res);

      setStorage('token', res.token);
      setUserInfo(res.user);

      wx.showToast({ 
        title: '登录成功', 
        icon: 'success',
        duration: 1500
      });

      setTimeout(() => {
        wx.reLaunch({
          url: '/pages/products/products'
        });
      }, 1500);

    } catch (error) {
      console.error('Login error:', error);
      wx.showToast({ 
        title: '登录失败', 
        icon: 'none'
      });
    } finally {
      this.setData({ loading: false });
    }
  }
});

