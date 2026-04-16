// pages/products/products.js
import { get } from '../../utils/request';
import { getCart, setCart } from '../../utils/storage';

Page({
  data: {
    products: [],
    categories: [],
    currentCategoryId: 0,
    loading: false
  },

  onLoad() {
    console.log('Products page loaded');
    // 并行加载分类和产品，设置超时保护
    Promise.all([
      this.loadCategories().catch(e => {
        console.error('Categories load failed:', e);
        return [];
      }),
      this.loadProducts().catch(e => {
        console.error('Products load failed:', e);
        return [];
      })
    ]).catch(e => console.error('Init error:', e));
  },

  onShow() {
    // 页面显示时只更新产品
    if (this.data.products.length === 0) {
      this.loadProducts();
    }
  },

  loadCategories() {
    return new Promise((resolve, reject) => {
      // 设置5秒超时
      const timeout = setTimeout(() => {
        reject(new Error('Categories load timeout'));
      }, 5000);

      get('/categories')
        .then(res => {
          clearTimeout(timeout);
          let categories = Array.isArray(res) ? res : (res.data || []);
          
          // 添加"全部"选项
          const allCategory = { id: 0, name: '全部' };
          categories = [allCategory, ...categories];
          
          this.setData({ categories });
          console.log('Categories loaded:', categories.length);
          resolve(categories);
        })
        .catch(e => {
          clearTimeout(timeout);
          console.error('Load categories error:', e);
          // 使用默认分类
          this.setData({ 
            categories: [
              { id: 0, name: '全部' },
              { id: 1, name: '热销' },
              { id: 2, name: '新品' }
            ]
          });
          reject(e);
        });
    });
  },

  loadProducts() {
    return new Promise((resolve, reject) => {
      this.setData({ loading: true });
      
      // 设置5秒超时
      const timeout = setTimeout(() => {
        this.setData({ loading: false });
        reject(new Error('Products load timeout'));
      }, 5000);

      get('/products')
        .then(res => {
          clearTimeout(timeout);
          let products = Array.isArray(res) ? res : (res.data || []);
          
          // 为每个商品添加默认描述
          products = products.map(p => ({
            ...p,
            description: p.description || '热销商品，好评如潮'
          }));
          
          this.setData({ products });
          console.log('Products loaded:', products.length);
          resolve(products);
        })
        .catch(e => {
          clearTimeout(timeout);
          console.error('Load products error:', e);
          wx.showToast({ 
            title: '加载失败，请重试', 
            icon: 'none'
          });
          reject(e);
        })
        .finally(() => {
          this.setData({ loading: false });
        });
    });
  },

  selectCategory(e) {
    const categoryId = e.currentTarget.dataset.id;
    console.log('Select category:', categoryId);
    
    this.setData({ currentCategoryId: categoryId });
    
    // 未来可以根据分类ID过滤产品
    // this.loadProducts();
  },

  handleAddToCart(e) {
    const productId = parseInt(e.currentTarget.dataset.productId);
    const product = this.data.products.find(p => p.id === productId);
    
    if (!product) return;

    const cart = getCart();
    const existing = cart.find(item => item.product_id === productId);

    if (existing) {
      existing.quantity += 1;
    } else {
      cart.push({
        product_id: product.id,
        name: product.name,
        price: product.price,
        quantity: 1
      });
    }

    setCart(cart);
    wx.showToast({ 
      title: '已添加到购物车', 
      icon: 'success',
      duration: 1000
    });
  },

  goToCart() {
    wx.switchTab({
      url: '/pages/cart/cart'
    });
  }
});
