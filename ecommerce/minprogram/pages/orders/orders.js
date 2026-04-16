// pages/orders/orders.js
import { get } from '../../utils/request';

Page({
  data: {
    orders: [],
    orderStatus: 'all',
    loading: false
  },

  onLoad() {
    console.log('Orders page loaded');
    this.loadOrders();
  },

  onShow() {
    // 页面显示时刷新订单
    this.loadOrders();
  },

  switchTab(e) {
    const status = e.currentTarget.dataset.status;
    this.setData({ orderStatus: status });
    this.loadOrders();
  },

  loadOrders() {
    this.setData({ loading: true });

    try {
      // 模拟订单数据
      const mockOrders = [
        {
          id: 1,
          order_no: 'ORD20260416001',
          status: 'pending',
          status_text: '待付款',
          items: [
            { product_id: 1, name: '汉堡包', price: 15.99, quantity: 2 },
            { product_id: 2, name: '可乐', price: 5.99, quantity: 1 }
          ],
          total_items: 3,
          total_amount: 37.97,
          created_at: '2026-04-16 10:30:00'
        },
        {
          id: 2,
          order_no: 'ORD20260416002',
          status: 'shipped',
          status_text: '已发货',
          items: [
            { product_id: 3, name: '鸡腿套餐', price: 28.99, quantity: 1 }
          ],
          total_items: 1,
          total_amount: 28.99,
          created_at: '2026-04-15 15:20:00'
        },
        {
          id: 3,
          order_no: 'ORD20260416003',
          status: 'received',
          status_text: '已收货',
          items: [
            { product_id: 4, name: '薯条', price: 8.99, quantity: 3 }
          ],
          total_items: 3,
          total_amount: 26.97,
          created_at: '2026-04-14 12:00:00'
        }
      ];

      // 根据选择的状态过滤
      let filtered = mockOrders;
      if (this.data.orderStatus !== 'all') {
        filtered = mockOrders.filter(o => o.status === this.data.orderStatus);
      }

      this.setData({ 
        orders: filtered,
        loading: false
      });
      
      console.log('Orders loaded:', filtered.length);
    } catch (error) {
      console.error('Load orders error:', error);
      this.setData({ loading: false });
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      });
    }
  },

  detailOrder(e) {
    const orderId = e.currentTarget.dataset.orderId;
    wx.showToast({
      title: '订单详情功能开发中',
      icon: 'none'
    });
  },

  payOrder(e) {
    const orderId = e.currentTarget.dataset.orderId;
    wx.showToast({
      title: '支付功能开发中',
      icon: 'none'
    });
  }
});
