// pages/cart/cart.js
import { get, put, del } from '../../utils/request';
import { ensureLoggedIn } from '../../utils/auth';


Page({
    data: {
    cart: [],
    totalPrice: 0,
        loading: false,
    skeletonCartItems: [1, 2, 3],
    actioningItemId: null,

    checkingOut: false
  },


    onLoad() {
    if (!ensureLoggedIn()) return;
    this.loadCart();
  },


      onShow() {
    if (!ensureLoggedIn()) return;
    this.loadCart();
  },


  onPullDownRefresh() {
    this.loadCart(true);
  },

  loadCart(fromPullDown = false) {
    this.setData({ loading: true });
    get('/cart')
      .then(res => {
        const rawCart = Array.isArray(res) ? res : (res.data || []);
        const cart = rawCart
          .filter(item => item && item.id && item.product_id && (item.quantity || 0) > 0)
          .map(item => ({
            ...item,
            price: Number(item.price || 0),
            quantity: Number(item.quantity || 0)
          }));
        const totalPrice = cart.reduce((total, item) => total + (item.price * item.quantity), 0);
        this.setData({ cart, totalPrice });
      })
      .catch(error => {
        console.error('Load cart error:', error);
        this.setData({ cart: [], totalPrice: 0 });
        wx.showToast({ title: '购物车加载失败', icon: 'none' });
      })
      .finally(() => {
        this.setData({ loading: false });
        if (fromPullDown) wx.stopPullDownRefresh();
      });
  },

    handleIncreaseQuantity(e) {
    const itemId = parseInt(e.currentTarget.dataset.itemId);
    if (this.data.actioningItemId) return;

    const item = this.data.cart.find(i => i.id === itemId);
    if (!item) return;

    this.setData({ actioningItemId: itemId });
    put(`/cart/${itemId}`, {
      product_id: item.product_id,
      quantity: item.quantity + 1
    })
      .then(() => this.loadCart())
      .catch(error => {
        console.error('Update cart error:', error);
        wx.showToast({ title: error.message || '修改失败', icon: 'none' });
      })
      .finally(() => {
        this.setData({ actioningItemId: null });
      });
  },


    handleReduceQuantity(e) {
    const itemId = parseInt(e.currentTarget.dataset.itemId);
    if (this.data.actioningItemId) return;

    const item = this.data.cart.find(i => i.id === itemId);
    if (!item) return;

    this.setData({ actioningItemId: itemId });
    if (item.quantity <= 1) {
      del(`/cart/${itemId}`)
        .then(() => {
          this.loadCart();
          wx.showToast({ title: '已删除', icon: 'success' });
        })
        .catch(error => {
          console.error('Delete cart item error:', error);
          wx.showToast({ title: error.message || '删除失败', icon: 'none' });
        })
        .finally(() => {
          this.setData({ actioningItemId: null });
        });
      return;
    }

    put(`/cart/${itemId}`, {
      product_id: item.product_id,
      quantity: item.quantity - 1
    })
      .then(() => this.loadCart())
      .catch(error => {
        console.error('Update cart error:', error);
        wx.showToast({ title: error.message || '修改失败', icon: 'none' });
      })
      .finally(() => {
        this.setData({ actioningItemId: null });
      });
  },


    handleRemoveItem(e) {
    const itemId = parseInt(e.currentTarget.dataset.itemId);
    if (this.data.actioningItemId) return;

    this.setData({ actioningItemId: itemId });
    del(`/cart/${itemId}`)
      .then(() => {
        this.loadCart();
        wx.showToast({ title: '已删除', icon: 'success' });
      })
      .catch(error => {
        console.error('Delete cart item error:', error);
        wx.showToast({ title: error.message || '删除失败', icon: 'none' });
      })
      .finally(() => {
        this.setData({ actioningItemId: null });
      });
  },


    handleCheckout() {
      if (this.data.checkingOut) return;

      if (this.data.cart.length === 0) {
        wx.showToast({ title: '购物车是空的', icon: 'none' });
        return;
      }

      this.setData({ checkingOut: true });
      wx.navigateTo({
        url: '/pages/checkout/checkout',
        complete: () => {
          this.setData({ checkingOut: false });
        }
      });
    },

    goToProducts() {
      wx.switchTab({ url: '/pages/products/products' });
    }


});
