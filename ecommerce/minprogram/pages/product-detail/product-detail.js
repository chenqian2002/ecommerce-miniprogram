// pages/product-detail/product-detail.js
import { get, post } from '../../utils/request';
import { getStorage, setStorage } from '../../utils/storage';

Page({
  data: {
    productId: null,
    product: null,
    loading: false,
    isFavorite: false
  },

  onLoad(options) {
    const productId = options.productId ? parseInt(options.productId) : null;
    if (!productId) {
      wx.showToast({ title: '商品参数错误', icon: 'none' });
      return;
    }

    this.setData({ productId });
    this.loadProduct(productId);
    this.checkFavorite(productId);
  },

  onPullDownRefresh() {
    if (this.data.productId) {
      this.loadProduct(this.data.productId, true);
      this.checkFavorite(this.data.productId);
    } else {
      wx.stopPullDownRefresh();
    }
  },


  onShareAppMessage() {
    const { product } = this.data;
    if (!product) {
      return {
        title: '电商平台小程序',
        path: '/pages/products/products'
      };
    }

    return {
      title: `${product.name} - 电商平台`,
      path: `/pages/product-detail/product-detail?productId=${product.id}`
    };
  },

  loadProduct(productId, fromPullDown = false) {
    this.setData({ loading: true });

    get(`/products/${productId}`)
      .then(res => {
        const product = res.data || res;
        this.setData({ product });
      })
      .catch(error => {
        console.error('Load product detail error:', error);
        wx.showToast({ title: '商品加载失败', icon: 'none' });
      })
      .finally(() => {
        this.setData({ loading: false });
        if (fromPullDown) wx.stopPullDownRefresh();
      });
  },

  checkFavorite(productId) {
    try {
      const favorites = getStorage('favorites') || [];
      const isFavorite = favorites.some(item => item.id === productId);
      this.setData({ isFavorite });
    } catch (error) {
      console.error('Check favorite error:', error);
    }
  },

  toggleFavorite() {
    const { product, isFavorite } = this.data;
    if (!product) return;

    try {
      const favorites = getStorage('favorites') || [];
      let nextFavorites = [];

      if (isFavorite) {
        nextFavorites = favorites.filter(item => item.id !== product.id);
        wx.showToast({ title: '已取消收藏', icon: 'success' });
      } else {
        const exists = favorites.some(item => item.id === product.id);
        nextFavorites = exists ? favorites : [product, ...favorites];
        wx.showToast({ title: '已加入收藏', icon: 'success' });
      }

      setStorage('favorites', nextFavorites);
      this.setData({ isFavorite: !isFavorite });
    } catch (error) {
      console.error('Toggle favorite error:', error);
      wx.showToast({ title: '操作失败', icon: 'none' });
    }
  },

  addToCart(showToast = true) {
    const { product } = this.data;
    if (!product) return Promise.resolve();

    return post('/cart/add', {
      product_id: product.id,
      quantity: 1
    })
      .then(() => {
        if (showToast) {
          wx.showToast({ title: '已加入购物车', icon: 'success' });
        }
      })
      .catch(error => {
        console.error('Add to cart error:', error);
        wx.showToast({ title: '加入失败', icon: 'none' });
        throw error;
      });
  },

  buyNow() {
    this.addToCart(false)
      .then(() => {
        wx.navigateTo({
          url: '/pages/checkout/checkout'
        });
      })
      .catch(() => {
        // 已在 addToCart 中提示失败
      });
  }
});
