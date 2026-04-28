// pages/settings/settings.js
Page({
  data: {
    cacheInfo: '获取中...',
    version: '1.0.0',
    tips: [
      '清除缓存后会清掉本地登录态',
      '部分功能仍在建设中',
      '如遇问题可重新登录后再试'
    ]
  },

  onShow() {
    this.loadCacheInfo();
  },

  loadCacheInfo() {
    try {
      const info = wx.getStorageInfoSync();
      this.setData({
        cacheInfo: `已使用 ${info.currentSize}KB / 共 ${info.limitSize}KB`
      });
    } catch (error) {
      console.error('Load cache info error:', error);
      this.setData({ cacheInfo: '缓存信息获取失败' });
    }
  },

  clearCache() {
    wx.showModal({
      title: '清除缓存',
      content: '是否清除本地缓存？清除后需要重新登录。',
      success: (res) => {
        if (!res.confirm) return;

        wx.clearStorageSync();
        wx.showToast({ title: '已清除缓存', icon: 'success' });
        this.loadCacheInfo();
      }
    });
  },

  goToAbout() {
    wx.navigateTo({
      url: '/pages/about/about'
    });
  },

  goBack() {
    wx.navigateBack();
  }
});
