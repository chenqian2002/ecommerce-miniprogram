// pages/mine/mine.js
import { getUserInfo } from '../../utils/storage';

Page({
  data: {
    userInfo: {},
    stats: {
      pending: 2,
      shipped: 1,
      received: 5
    }
  },

  onLoad() {
    console.log('Mine page loaded');
    this.loadUserInfo();
  },

  onShow() {
    // 页面显示时刷新用户信息
    this.loadUserInfo();
  },

  loadUserInfo() {
    try {
      const userInfo = getUserInfo();
      console.log('User info:', userInfo);
      
      this.setData({ 
        userInfo: userInfo || {}
      });
    } catch (error) {
      console.error('Load user info error:', error);
    }
  },

  goToOrders(e) {
    const status = e.currentTarget.dataset.status;
    if (status) {
      wx.switchTab({
        url: '/pages/orders/orders',
        success() {
          // 传递状态给订单页面
          const pages = getCurrentPages();
          const ordersPage = pages[pages.length - 1];
          if (ordersPage) {
            ordersPage.setData({ orderStatus: status });
            ordersPage.loadOrders();
          }
        }
      });
    } else {
      wx.switchTab({
        url: '/pages/orders/orders'
      });
    }
  },

  handleAddresses() {
    wx.showToast({
      title: '收货地址管理开发中',
      icon: 'none'
    });
  },

  handleFavorites() {
    wx.showToast({
      title: '我的收藏功能开发中',
      icon: 'none'
    });
  },

  handleCoupon() {
    wx.showToast({
      title: '优惠券功能开发中',
      icon: 'none'
    });
  },

  handleSettings() {
    wx.showToast({
      title: '设置功能开发中',
      icon: 'none'
    });
  },

  handleAbout() {
    wx.showToast({
      title: '关于我们功能开发中',
      icon: 'none'
    });
  },

  logout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');
          
          wx.reLaunch({
            url: '/pages/login/login'
          });
        }
      }
    });
  }
});
