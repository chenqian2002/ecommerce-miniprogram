// pages/about/about.js
Page({
  data: {
    appName: '电商平台小程序',
    version: '1.0.0',
    intro: '这是一个基于微信小程序 + FastAPI 的电商演示项目。',
    sections: [
      '商品浏览与搜索',
      '购物车与结算下单',
      '订单管理与模拟支付',
      '商家商品管理（建设中）'
    ]
  },

  goBack() {
    wx.navigateBack();
  }
});
