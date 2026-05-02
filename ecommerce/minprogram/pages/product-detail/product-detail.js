// pages/product-detail/product-detail.js
import { get, post } from '../../utils/request';
import { getStorage, setStorage } from '../../utils/storage';
import { ensureLoggedIn } from '../../utils/auth';
import { CUSTOMER_SERVICE_WECHAT, CUSTOMER_SERVICE_QR_CODE } from '../../utils/config';

Page({
  data: {
    productId: null,
    product: null,
    loading: false,
    isFavorite: false,
    quantity: 1,
    addingToCart: false,
    buyingNow: false,
    customerWechat: CUSTOMER_SERVICE_WECHAT,
    customerQrCode: CUSTOMER_SERVICE_QR_CODE
  },

  onLoad(options) {
    const productId = parseInt(options.productId || options.id || options.pid) || null;
    if (!productId) {
      wx.showToast({ title: '商品参数错误', icon: 'none' });
      return;
    }

    this.setData({ productId });
    this.loadProduct(productId);
    this.loadPublicSettings();
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
        const stock = Number(product?.stock || 0);
        this.setData({
          product: {
            ...product,
            stock,
            isSoldOut: stock <= 0
          }
        });
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

  loadPublicSettings() {
    get('/settings/public')
      .then(settings => {
        this.setData({
          customerWechat: settings.customer_service_wechat || CUSTOMER_SERVICE_WECHAT,
          customerQrCode: settings.customer_service_qr_code || CUSTOMER_SERVICE_QR_CODE
        });
      })
      .catch(err => {
        console.error('Load public settings error:', err);
      });
  },

  copyCustomerWechat() {
    wx.setClipboardData({
      data: this.data.customerWechat || CUSTOMER_SERVICE_WECHAT,
      success: () => wx.showToast({ title: '微信号已复制', icon: 'success' })
    });
  },

  previewCustomerQrCode() {
    const url = this.data.customerQrCode || CUSTOMER_SERVICE_QR_CODE;
    if (!url) return;
    wx.previewImage({ current: url, urls: [url] });
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

  // 数量选择器
  handleDecreaseQty() {
    if (this.data.quantity > 1) {
      this.setData({ quantity: this.data.quantity - 1 });
    }
  },

  handleIncreaseQty() {
    const { product, quantity } = this.data;
    const maxStock = product ? Number(product.stock || 0) : 99;
    if (quantity < maxStock) {
      this.setData({ quantity: quantity + 1 });
    } else {
      wx.showToast({ title: '已达到库存上限', icon: 'none' });
    }
  },

  addToCart(showToast = true) {
    const { product, quantity, addingToCart, buyingNow } = this.data;
    if (!product) return Promise.resolve();
    if (addingToCart || buyingNow) return Promise.resolve();

    if (Number(product.stock || 0) <= 0) {
      wx.showToast({ title: '商品已售罄', icon: 'none' });
      return Promise.resolve();
    }

    this.setData({ addingToCart: showToast, buyingNow: !showToast });

    return get('/cart')
      .then(res => {
        const cartItems = Array.isArray(res) ? res : (res.data || []);
        const existing = cartItems.find(item => item.product_id === product.id);
        const cartQty = existing ? existing.quantity : 0;

        if (cartQty + quantity > Number(product.stock || 0)) {
          wx.showToast({ title: '购物车中已添加最大数量', icon: 'none' });
          throw new Error('cart_limit');
        }

        return post('/cart/add', {
          product_id: product.id,
          quantity: quantity
        });
      })
      .then(() => {
        if (showToast) {
          wx.showToast({ title: `已添加 ${quantity} 件到购物车`, icon: 'success' });
        }
      })
      .catch(error => {
        if (error === 'cart_limit' || (error && error.message === 'cart_limit')) return;
        console.error('Add to cart error:', error);
        wx.showToast({ title: error?.message || '加入失败', icon: 'none' });
        throw error;
      })
      .finally(() => {
        this.setData({ addingToCart: false, buyingNow: false });
      });
  },

  buyNow() {
    const { product, addingToCart, buyingNow } = this.data;
    if (addingToCart || buyingNow) return;

    if (!product || Number(product.stock || 0) <= 0) {
      wx.showToast({ title: '商品已售罄', icon: 'none' });
      return;
    }

    this.addToCart(false)
      .then(() => {
        wx.navigateTo({ url: '/pages/checkout/checkout' });
      })
      .catch(() => {});
  }
});