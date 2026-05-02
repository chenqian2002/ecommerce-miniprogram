// pages/checkout/checkout.js
import { get, post, put } from '../../utils/request';
import { ensureLoggedIn } from '../../utils/auth';
import { CUSTOMER_SERVICE_WECHAT, CUSTOMER_SERVICE_QR_CODE } from '../../utils/config';

Page({
  data: {
    cart: [],
    addresses: [],
    selectedAddressId: null,
    totalPrice: 0,
    submitting: false,
    loadingCart: false,
    loadingAddresses: false,
    serviceDialogVisible: false,
    customerWechat: CUSTOMER_SERVICE_WECHAT,
    customerQrCode: CUSTOMER_SERVICE_QR_CODE,
    latestOrderId: null
  },

  onLoad() {
    if (!ensureLoggedIn()) return;
    this.setData({ selectedAddressId: null });
    this.loadCheckoutData();
  },

  onShow() {
    if (!ensureLoggedIn()) return;
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

  copyCustomerWechat() {
    wx.setClipboardData({
      data: this.data.customerWechat,
      success: () => wx.showToast({ title: '微信号已复制', icon: 'success' })
    });
  },

  closeServiceDialog() {
    this.setData({ serviceDialogVisible: false });
    wx.reLaunch({ url: '/pages/orders/orders' });
  },

  viewLatestOrder() {
    const { latestOrderId } = this.data;
    this.setData({ serviceDialogVisible: false });
    if (latestOrderId) {
      wx.reLaunch({ url: `/pages/order-detail/order-detail?orderId=${latestOrderId}` });
      return;
    }
    wx.reLaunch({ url: '/pages/orders/orders' });
  },

  // 请求订阅消息授权
  requestSubscribe() {
    return new Promise((resolve) => {
      wx.requestSubscribeMessage({
        tmplIds: ['发货通知模板ID', '支付成功模板ID'],
        success(res) {
          console.log('[Subscribe] 用户授权结果:', res);
          resolve(res);
        },
        fail(err) {
          console.warn('[Subscribe] 授权失败:', err);
          resolve(null);
        }
      });
    });
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

    // 先请求订阅消息授权（不影响下单流程）
    this.requestSubscribe().then(() => {
      this.doSubmitOrder(selectedAddressId);
    });
  },

  doSubmitOrder(selectedAddressId) {
    const { cart } = this.data;
    this.setData({ submitting: true });

    wx.showLoading({ title: '正在创建订单...' });
    const cartItems = cart.map(item => ({
      product_id: item.product_id,
      quantity: item.quantity
    }));

    post('/orders', {
      address_id: selectedAddressId,
      payment_method: 'mock',
      cart_items: cartItems
    })
      .then(orderRes => {
        const orderId = orderRes?.order_id || orderRes?.order?.id;
        if (!orderId) throw new Error('创建订单成功，但未返回订单ID');

        wx.hideLoading();
        wx.showLoading({ title: '正在完成支付...' });
        return put(`/orders/${orderId}/pay`).then(payRes => ({ orderId, payRes }));
      })
      .then(({ orderId }) => {
        this.setData({ latestOrderId: orderId });
        wx.hideLoading();
        wx.showToast({ title: '下单成功', icon: 'success' });
        setTimeout(() => {
          this.setData({ serviceDialogVisible: true });
        }, 1000);
      })
      .catch(error => {
        wx.hideLoading();
        const message = error?.message || error?.detail || '下单失败';
        wx.showToast({ title: message, icon: 'none', duration: 2000 });
      })
      .finally(() => {
        wx.hideLoading();
        this.setData({ submitting: false });
      });
  }
});