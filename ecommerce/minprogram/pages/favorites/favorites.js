// pages/favorites/favorites.js
import { getStorage, setStorage } from '../../utils/storage';
import { ensureLoggedIn } from '../../utils/auth';

Page({
  data: {
    favorites: [],
    loading: false
  },

  onShow() {
    if (!ensureLoggedIn()) return;
    this.loadFavorites();
  },

  onPullDownRefresh() {
    this.loadFavorites(true);
  },

  loadFavorites(fromPullDown = false) {
    this.setData({ loading: true });

    try {
      const favorites = getStorage('favorites') || [];
      this.setData({ favorites });
    } catch (error) {
      console.error('Load favorites error:', error);
      this.setData({ favorites: [] });
    } finally {
      this.setData({ loading: false });
      if (fromPullDown) wx.stopPullDownRefresh();
    }
  },

  goToDetail(e) {
    const productId = parseInt(e.currentTarget.dataset.productId);
    if (!productId) return;

    wx.navigateTo({
      url: `/pages/product-detail/product-detail?productId=${productId}`
    });
  },

  removeFavorite(e) {
    const productId = parseInt(e.currentTarget.dataset.productId);
    const favorites = (getStorage('favorites') || []).filter(item => item.id !== productId);
    setStorage('favorites', favorites);
    this.setData({ favorites });

    wx.showToast({ title: '已取消收藏', icon: 'success' });
  },

  goToProducts() {
    wx.switchTab({
      url: '/pages/products/products'
    });
  },

  goBack() {
    wx.switchTab({
      url: '/pages/products/products'
    });
  }
});
