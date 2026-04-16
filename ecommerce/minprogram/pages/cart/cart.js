// pages/cart/cart.js
import { getCart, setCart } from '../../utils/storage';

Page({
  data: {
    cart: [],
    totalPrice: 0
  },

  onLoad() {
    this.loadCart();
  },

  onShow() {
    this.loadCart();
  },

  loadCart() {
    const cart = getCart();
    const totalPrice = cart.reduce((total, item) => {
      return total + (item.price * item.quantity);
    }, 0);

    this.setData({ cart, totalPrice });
  },

  handleIncreaseQuantity(e) {
    const productId = e.currentTarget.dataset.productId;
    const cart = this.data.cart;
    const item = cart.find(i => i.product_id === productId);

    if (item) {
      item.quantity += 1;
      setCart(cart);
      this.loadCart();
    }
  },

  handleReduceQuantity(e) {
    const productId = e.currentTarget.dataset.productId;
    const cart = this.data.cart;
    const item = cart.find(i => i.product_id === productId);

    if (item && item.quantity > 1) {
      item.quantity -= 1;
      setCart(cart);
      this.loadCart();
    }
  },

  handleRemoveItem(e) {
    const productId = e.currentTarget.dataset.productId;
    const cart = this.data.cart.filter(i => i.product_id !== productId);

    setCart(cart);
    this.loadCart();

    wx.showToast({ title: '已删除', icon: 'success' });
  },

  handleCheckout() {
    if (this.data.cart.length === 0) {
      wx.showToast({ title: '购物车是空的', icon: 'none' });
      return;
    }

    wx.navigateTo({
      url: '/pages/checkout/checkout'
    });
  }
});
