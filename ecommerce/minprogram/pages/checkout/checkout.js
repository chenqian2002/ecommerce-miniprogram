// pages/checkout/checkout.js
import { get, post, put } from '../../utils/request';

Page({
  data: {
    cart: [],
    addresses: [],
    selectedAddressId: null,
    totalPrice: 0,
    submitting: false,
    loadingCart: false,
    loadingAddresses: false,
    debugOrderRes: null,
    debugPayRes: null
  },

  onLoad() {
    this.setData({ selectedAddressId: null });
    this.loadCheckoutData();
  },

  onShow() {
    this.setData({ selectedAddressId: null });
    this.loadCheckoutData();
  },

  onPullDownRefresh() {
    this.setData({ selectedAddressId: null });
    this.loadCheckoutData(true);
  },

  loadCheckoutData(fromPullDown = false) {
    this.setData({ loadingCart: true });
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
        const totalPrice = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
        this.setData({ cart, totalPrice });
        this.loadAddresses();
      })
      .catch(error => {
        console.error('Load cart error:', error);
        this.setData({ cart: [], totalPrice: 0 });
        wx.showToast({ title: '购物车加载失败', icon: 'none' });
      })
      .finally(() => {
        this.setData({ loadingCart: false });
        if (fromPullDown) wx.stopPullDownRefresh();
      });
  },

  loadAddresses() {
    this.setData({ loadingAddresses: true });
    get('/addresses')
      .then(res => {
        const rawAddresses = Array.isArray(res) ? res : (res.data || []);
        const addresses = rawAddresses.filter(item => item && item.id && item.receiver_name && item.phone);
        this.setData({ addresses });

        if (!this.data.selectedAddressId && addresses.length > 0) {
          const defaultAddress = addresses.find(item => item.is_default) || addresses[0];
          this.setData({ selectedAddressId: defaultAddress.id });
        }
      })
      .catch(error => {
        console.error('Load addresses error:', error);
        this.setData({ addresses: [] });
        wx.showToast({ title: '地址加载失败', icon: 'none' });
      })
      .finally(() => {
        this.setData({ loadingAddresses: false });
      });
  },

  goToAddAddress() {
    wx.navigateTo({ url: '/pages/address-add/address-add' });
  },

  editAddress(e) {
    const addressId = parseInt(e.currentTarget.dataset.addressId);
    wx.navigateTo({ url: `/pages/address-add/address-add?addressId=${addressId}` });
  },

  handleSelectAddress(e) {
    const addressId = parseInt(e.currentTarget.dataset.addressId);
    this.setData({ selectedAddressId: addressId });
  },

  handleSubmitOrder() {
    const { cart, selectedAddressId, submitting } = this.data;

    if (submitting) return;
    if (!cart.length) {
      wx.showToast({ title: '购物车为空，请先添加商品', icon: 'none' });
      return;
    }
    if (!selectedAddressId) {
      wx.showToast({ title: '请选择收货地址', icon: 'none' });
      return;
    }

    this.setData({ submitting: true, debugOrderRes: null, debugPayRes: null });
    this.debugPrint('submit-start', { selectedAddressId, cartLength: cart.length, totalPrice: this.data.totalPrice });

    wx.showLoading({ title: '正在创建订单...' });
    this.createOrderStep(selectedAddressId)
      .then(orderRes => {
        this.debugPrint('order-response', orderRes);
        this.setData({ debugOrderRes: orderRes });

        const orderData = orderRes?.order || orderRes?.data?.order || orderRes?.data || orderRes;
        const orderId = orderData?.id;
        if (!orderId) {
          throw new Error('创建订单成功，但未返回订单ID');
        }

        wx.hideLoading();
        wx.showLoading({ title: '正在完成支付...' });
        return this.payMockOrder(orderId).then(payRes => ({ orderData, payRes }));
      })
      .then(({ orderData, payRes }) => {
        this.debugPrint('payment-response', payRes);
        this.setData({ debugPayRes: payRes });

        wx.hideLoading();
        wx.showToast({ title: '下单成功', icon: 'success' });
        setTimeout(() => {
          wx.switchTab({ url: '/pages/orders/orders' });
        }, 1200);
      })
      .catch(error => {
        wx.hideLoading();
        const message = this.getErrorMessage(error, '下单失败');
        this.debugPrint('submit-error', error);
        wx.showToast({
          title: message,
          icon: 'none',
          duration: 2000
        });
      })
      .finally(() => {
        wx.hideLoading();
        this.setData({ submitting: false });
      });
  }
});