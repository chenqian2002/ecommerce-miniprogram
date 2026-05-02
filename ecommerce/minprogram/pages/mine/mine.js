// pages/mine/mine.js
import { get } from '../../utils/request';
import { getUserInfo, clearStorage } from '../../utils/storage';
import { ensureLoggedIn, ensureMerchantLogin } from '../../utils/auth';


Page({
  data: {
    userInfo: {},
    stats: {
      pending: 0,
      shipped: 0,
      received: 0
    },
    loading: false,
    featureCards: [
      { title: '我的收藏', icon: '❤️', key: 'favorites', desc: '收藏的商品会在这里展示' },
      { title: '地址管理', icon: '📍', key: 'address', desc: '管理收货地址，快捷下单' }
    ],
    quickActions: [
      { title: '设置', icon: '⚙️', key: 'settings' },
      { title: '关于我们', icon: 'ℹ️', key: 'about' },
      { title: '商家平台', icon: '🏬', key: 'merchant' }
    ]
  },

    onLoad() {
    if (!ensureLoggedIn()) return;
    this.loadProfile();
  },


    onShow() {
    if (!ensureLoggedIn()) return;
    this.loadProfile();
  },


  loadProfile() {
    this.setData({ loading: true });

    try {
      const userInfo = getUserInfo() || {};
      this.setData({ userInfo });
    } catch (error) {
      console.error('Load local user info error:', error);
    }

    get('/orders')
      .then(res => {
        const orders = Array.isArray(res) ? res : (res.data || []);
        const stats = {
          pending: orders.filter(o => o.status === 'pending').length,
          paid: orders.filter(o => o.status === 'paid').length,
          shipped: orders.filter(o => o.status === 'shipped').length,
          received: orders.filter(o => o.status === 'completed').length
        };
        this.setData({ stats });
      })
      .catch(error => {
        console.error('Load mine stats error:', error);
        this.setData({ stats: { pending: 0, shipped: 0, received: 0 } });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  goToOrders(e) {
    const status = e?.currentTarget?.dataset?.status || '';
    wx.switchTab({
      url: '/pages/orders/orders',
      success: () => {
        const pages = getCurrentPages();
        const ordersPage = pages[pages.length - 1];
        if (ordersPage && status) {
          ordersPage.setData({ orderStatus: status });
          ordersPage.loadOrders();
        }
      }
    });
  },

  goToAddress() {
    wx.navigateTo({
      url: '/pages/address-add/address-add'
    });
  },

  handleFavorites() {
    wx.navigateTo({ url: '/pages/favorites/favorites' });
  },

    handleMerchant() {
    if (!ensureMerchantLogin()) return;
    wx.navigateTo({ url: '/pages/merchant/merchant' });
  },


  handleSettings() {
    wx.navigateTo({ url: '/pages/settings/settings' });
  },

  handleAbout() {
    wx.navigateTo({ url: '/pages/about/about' });
  },

  handleFeature(e) {
    const key = e.currentTarget.dataset.key;
    const featureMap = {
      favorites: '/pages/favorites/favorites',
      address: '/pages/address-add/address-add',
      settings: '/pages/settings/settings',
      about: '/pages/about/about',
      merchant: '/pages/merchant/merchant'
    };
    const url = featureMap[key];
    if (url) {
      wx.navigateTo({ url });
      return;
    }
    wx.showToast({ title: '功能建设中', icon: 'none' });
  },

  handleQuickAction(e) {
    const key = e.currentTarget.dataset.key;
    if (key === 'settings') return this.handleSettings();
    if (key === 'about') return this.handleAbout();
    if (key === 'merchant') return this.handleMerchant();
  },

    logout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          clearStorage();
          wx.reLaunch({
            url: '/pages/login/login'
          });
        }
      }
    });
  }

});


